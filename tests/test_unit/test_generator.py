import json
from pathlib import Path

import pytest

import village_report_generator.village_report_generator as vrg
from village_report_generator.generate_quarto_file import build_quarto_content, generate_quarto_file

CONFIGS = Path(vrg.__file__).parent / "active_configuration_files"


def tabs_of(content):
    """Headings of level 1 (tabs of the report), ignoring comments inside code cells."""
    tabs, in_code = [], False
    for line in content.splitlines():
        if line.startswith("```"):
            in_code = not in_code
        elif not in_code and line.startswith("# "):
            tabs.append(line)
    return tabs


@pytest.fixture
def config():
    return {
        "project_name": "my_project",
        "setup_name": "village01",
        "subjects": ["A001", "A002"],
        "general_template": "visual_and_COT_quarto_general_template.txt",
        "subject_template": "visual_and_COT_quarto_subject_template.txt",
    }


def test_every_placeholder_is_replaced(config):
    content = build_quarto_content(config, "2026-05-25")
    assert "[[[" not in content
    assert 'project = "my_project"' in content
    assert "subjects = ['A001', 'A002']" in content
    assert 'report_date = "2026-05-25"' in content


def test_one_tab_per_subject_and_problems_tab_last(config):
    content = build_quarto_content(config, "2026-05-25")
    assert tabs_of(content) == ["# Overview", "# A001", "# A002", "# Problems"]
    assert content.rstrip().endswith(":::")


def test_cell_labels_are_unique(config):
    # quarto refuses to render a document with two cells with the same label
    content = build_quarto_content(config, "2026-05-25")
    labels = [line for line in content.splitlines() if line.startswith("#| label:")]
    assert len(labels) == len(set(labels))


def test_without_subject_template(config):
    del config["subject_template"]
    assert tabs_of(build_quarto_content(config, "2026-05-25")) == ["# Overview", "# Problems"]


@pytest.mark.parametrize("config_file", sorted(CONFIGS.glob("*.json")), ids=lambda p: p.stem)
def test_active_configurations_generate(config_file, tmp_path):
    qmd = generate_quarto_file(config_file, "2026-05-25", tmp_path)
    assert qmd == tmp_path / "quarto_files" / f"{config_file.stem}_2026-05-25.qmd"
    assert "[[[" not in qmd.read_text()


def test_missing_configuration_key(config, tmp_path):
    del config["subjects"]
    path = tmp_path / "broken.json"
    path.write_text(json.dumps(config))
    with pytest.raises(KeyError, match="subjects"):
        generate_quarto_file(path, "2026-05-25", tmp_path)


@pytest.fixture
def two_projects(tmp_path, config):
    configs = tmp_path / "configs"
    configs.mkdir()
    for name in ["broken_project", "good_project"]:
        (configs / f"{name}.json").write_text(json.dumps(config))
    return configs


def test_a_failing_project_does_not_stop_the_others(two_projects, tmp_path, monkeypatch):
    rendered = []

    def fake_render(qmd_path):
        if "broken_project" in qmd_path.name:
            raise RuntimeError("quarto failed")
        qmd_path.with_suffix(".html").write_text("<html></html>")
        rendered.append(qmd_path.name)

    monkeypatch.setattr(vrg, "render", fake_render)
    monkeypatch.setattr(vrg, "generate_index_html_with_calendar", lambda docs_path, active=None: None)
    monkeypatch.setattr(vrg, "update_active_projects", lambda configs, docs_path, state: None)
    monkeypatch.setattr(vrg, "archive_projects", lambda *args: [])
    failed = vrg.main(date="2026-05-25", config_path=two_projects, docs_path=tmp_path / "docs",
                      temperature=False, push=False)
    assert failed == ["broken_project"]
    assert rendered == ["good_project_2026-05-25.qmd"]


def test_select_projects(two_projects, tmp_path, monkeypatch):
    rendered = []

    def fake_render(qmd_path):
        qmd_path.with_suffix(".html").write_text("<html></html>")
        rendered.append(qmd_path.name)

    monkeypatch.setattr(vrg, "render", fake_render)
    monkeypatch.setattr(vrg, "generate_index_html_with_calendar", lambda docs_path, active=None: None)
    monkeypatch.setattr(vrg, "update_active_projects", lambda configs, docs_path, state: None)
    monkeypatch.setattr(vrg, "archive_projects", lambda *args: [])
    vrg.main(date="2026-05-25", projects="good_project", config_path=two_projects,
             docs_path=tmp_path / "docs", temperature=False, push=False)
    assert rendered == ["good_project_2026-05-25.qmd"]


def test_setups_found_automatically_unless_given(config):
    del config["setup_name"]
    assert "setups = None" in build_quarto_content(config, "2026-05-25")
    config["setup_name"] = "village01"
    assert "setups = ['village01']" in build_quarto_content(config, "2026-05-25")
    config["setup_name"] = ["village01", "village02"]
    assert "setups = ['village01', 'village02']" in build_quarto_content(config, "2026-05-25")


def test_habituation_template_has_only_the_overview(config):
    config["general_template"] = "habituation_general_template.txt"
    del config["subject_template"]
    assert tabs_of(build_quarto_content(config, "2026-05-25")) == ["# Overview", "# Problems"]


def test_sample_option(monkeypatch, tmp_path):
    rendered = []

    def fake_render(qmd_path):
        qmd_path.with_suffix(".html").write_text("<html></html>")
        rendered.append(qmd_path)

    monkeypatch.setattr(vrg, "render", fake_render)
    monkeypatch.setattr(vrg, "generate_index_html_with_calendar", lambda docs_path, active=None: None)
    monkeypatch.setattr(vrg, "update_active_projects", lambda configs, docs_path, state: None)
    monkeypatch.setattr(vrg, "archive_projects", lambda *args: [])
    monkeypatch.setattr(vrg, "generate_temphum_quarto_file", lambda date, docs_path: tmp_path / "t.qmd")
    monkeypatch.setattr(vrg, "SAMPLE_REPORTS_PATH", tmp_path / "sample_reports")
    monkeypatch.delenv("LECILAB_DATA_PATH", raising=False)
    assert vrg.main(sample=True) == []
    assert sorted(p.name for p in rendered if p.suffix == ".qmd" and p.parent.name == "quarto_files") == [
        "sample_COT_cannula_GAD2_2026-05-25.qmd", "sample_habituation_2026-05-25.qmd"]
    assert vrg.os.environ["LECILAB_DATA_PATH"] == str(vrg.SAMPLE_DATA_PATH.resolve())
    monkeypatch.delenv("LECILAB_DATA_PATH")


def test_archive_report_content(config, tmp_path):
    path = tmp_path / "proj.json"
    path.write_text(json.dumps(config))
    qmd = generate_quarto_file(path, "2026-06-11", tmp_path, subject_dates={"A001": "2026-06-11", "A002": "2026-06-05"})
    assert qmd.name == "proj_archive.qmd"
    text = qmd.read_text()
    assert "2026-06-11 Archive" in text and "Archived project: data up to 2026-06-11" in text
    assert 'subject_date = "2026-06-05"' in text and "session_hours = 48" in text
    daily = build_quarto_content(config, "2026-06-11")
    assert "session_hours = None" in daily and 'archive_note = ""' in daily and "2026-06-11 Report" in daily


def test_shrink_images(tmp_path):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import numpy as np
    from PIL import Image

    figures = tmp_path / "report_files" / "figure-html"
    figures.mkdir(parents=True)
    fig, ax = plt.subplots(figsize=(6, 4))
    x = np.linspace(0, 10, 2000)
    ax.plot(x, np.sin(x) + np.random.default_rng(0).normal(0, 0.2, x.size))
    ax.fill_between(x, -1, 1, alpha=0.2)
    fig.savefig(figures / "plot.png", dpi=96)
    before = (figures / "plot.png").stat().st_size
    (tmp_path / "report.html").write_text("<html></html>")
    assert vrg.shrink_images(tmp_path / "report.html") > 0
    assert (figures / "plot.png").stat().st_size < before
    with Image.open(figures / "plot.png") as image:
        assert image.mode == "P" and image.size == (576, 384)
    assert vrg.shrink_images(tmp_path / "missing.html") == 0
