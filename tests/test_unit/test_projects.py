import json

import pandas as pd
import pytest

import village_report_generator.projects as projects
from village_report_generator.update_index import GREEN, GREY, RED, generate_index_html_with_calendar

CONFIG = {
    "project_name": "proj_data",
    "subjects": ["A", "B"],
    "general_template": "visual_and_COT_quarto_general_template.txt",
    "subject_template": "visual_and_COT_quarto_subject_template.txt",
}


def fake_dates(*rows):
    return pd.DataFrame(rows, columns=["subject", "date"]).assign(date=lambda d: pd.to_datetime(d["date"]))


@pytest.fixture
def docs(tmp_path):
    folder = tmp_path / "docs" / "quarto_files"
    folder.mkdir(parents=True)
    return tmp_path / "docs"


def add_daily_report(docs, name, day):
    folder = docs / "quarto_files"
    (folder / f"{name}_{day}.html").write_text("<html></html>")
    (folder / f"{name}_{day}.qmd").write_text("qmd")
    (folder / f"{name}_{day}_files" / "figure-html").mkdir(parents=True)


def test_report_days(docs):
    add_daily_report(docs, "proj", "2026-05-24")
    add_daily_report(docs, "proj", "2026-05-25")
    (docs / "quarto_files" / "proj_archive.html").write_text("")
    assert projects.report_days(docs) == {"proj": {"2026-05-24", "2026-05-25"}}


def test_active_projects_record_days_with_data(docs, monkeypatch):
    add_daily_report(docs, "proj", "2026-05-24")
    add_daily_report(docs, "proj", "2026-05-25")
    monkeypatch.setattr(projects, "session_dates", lambda config: fake_dates(["A", "2026-05-24 10:00"]))
    state = {}
    projects.update_active_projects({"proj": CONFIG}, docs, state)
    assert state["proj"] == {"status": "active", "report_days": ["2026-05-24", "2026-05-25"],
                             "data_days": ["2026-05-24"]}
    # the index: green with new data, red without
    projects.save_state(docs, state)
    generate_index_html_with_calendar(docs, ["proj"])
    index = (docs / "index.html").read_text()
    assert f'href="quarto_files/proj_2026-05-24.html" title="2026-05-24: new data" style="background:{GREEN}"' in index
    assert f'href="quarto_files/proj_2026-05-25.html" title="2026-05-25: no new data" style="background:{RED}"' in index
    assert "Archive</h2>" not in index


@pytest.fixture
def archived(docs, tmp_path, monkeypatch):
    configs = tmp_path / "archived"
    configs.mkdir()
    (configs / "old.json").write_text(json.dumps(CONFIG))
    add_daily_report(docs, "old", "2026-06-04")
    add_daily_report(docs, "old", "2026-06-05")
    dates = fake_dates(["A", "2026-06-04 09:00"], ["A", "2026-06-11 13:00"], ["B", "2026-06-05 12:00"])
    monkeypatch.setattr(projects, "session_dates", lambda config: dates)
    calls = []

    def make_report(config_file, last_day, subject_dates):
        calls.append((last_day, subject_dates))
        report = docs / "quarto_files" / "old_archive.html"
        report.write_text("<html></html>")
        return report

    return configs, make_report, calls


def test_archive_project(docs, archived):
    configs, make_report, calls = archived
    state = {}
    assert projects.archive_projects({"proj"}, docs, state, make_report, [configs]) == []
    # one report: last day of the project, and the last day of each subject
    assert calls == [("2026-06-11", {"A": "2026-06-11", "B": "2026-06-05"})]
    # the daily reports are removed, their .qmd kept
    names = sorted(p.name for p in (docs / "quarto_files").iterdir())
    assert names == ["old_2026-06-04.qmd", "old_2026-06-05.qmd", "old_archive.html"]
    assert state["old"]["status"] == "archived"
    assert state["old"]["data_days"] == ["2026-06-04", "2026-06-05", "2026-06-11"]
    assert state["old"]["report_days"] == ["2026-06-04", "2026-06-05"]
    # not made again without new data
    projects.archive_projects({"proj"}, docs, state, make_report, [configs])
    assert len(calls) == 1
    # the index: every grey day links to the archive report
    projects.save_state(docs, state)
    generate_index_html_with_calendar(docs, ["proj"])
    index = (docs / "index.html").read_text()
    assert "Archive</h2>" in index
    assert index.count(f'href="quarto_files/old_archive.html" title') == 3
    assert f'title="2026-06-11: data collected" style="background:{GREY}"' in index


def test_archive_is_made_again_with_newer_data(docs, archived, monkeypatch):
    configs, make_report, calls = archived
    state = {}
    projects.archive_projects(set(), docs, state, make_report, [configs])
    monkeypatch.setattr(projects, "session_dates",
                        lambda config: fake_dates(["A", "2026-06-12 10:00"], ["B", "2026-06-05 12:00"]))
    projects.archive_projects(set(), docs, state, make_report, [configs])
    assert [c[0] for c in calls] == ["2026-06-11", "2026-06-12"]


def test_daily_reports_kept_when_archive_fails(docs, archived):
    configs, _, _ = archived

    def broken(config_file, last_day, subject_dates):
        raise RuntimeError("quarto failed")

    assert projects.archive_projects(set(), docs, {}, broken, [configs]) == ["old"]
    assert (docs / "quarto_files" / "old_2026-06-05.html").exists()


def test_daily_reports_kept_without_configuration(docs, tmp_path):
    add_daily_report(docs, "unknown", "2026-01-01")
    state = {}
    projects.archive_projects(set(), docs, state, lambda *a: None, [tmp_path])
    assert (docs / "quarto_files" / "unknown_2026-01-01.html").exists()
    projects.save_state(docs, state)
    generate_index_html_with_calendar(docs, [])
    assert 'href="quarto_files/unknown_2026-01-01.html"' in (docs / "index.html").read_text()
