"""
Projects of the website: which are active and which are archived, the days
with a report and the days with new data of each one, and the report of
archived projects.

- A project is active if its configuration is in active_configuration_files,
  and archived if it has reports on the website (or a configuration in
  archived_configuration_files) but no active configuration.
- New data: the boxes send each session to the data folder, so a project has
  new data on a day if one of its subjects has a session that day (see
  lecilab_behavior_analysis.io.loading.load_session_dates).
- An archived project gets one report (<name>_archive.html): the overview as
  of its last day with data, and for each subject its last day with data and
  its last 48 hours of training. Once it exists, the daily reports of the
  project are removed from the website (their .qmd files are kept, small,
  as the record of the days that had a report).
- What is known about each project is kept in docs/calendar_days.json, so
  that the calendars keep their days even if the data is removed from the
  data folder.
"""

import json
import re
import shutil
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set

ARCHIVED_CONFIG_FILES_PATH = Path(__file__).parent / "archived_configuration_files"
STATE_FILE = "calendar_days.json"
DAILY_REPORT = re.compile(r"^(?P<name>.+)_(?P<date>\d{4}-\d{2}-\d{2})\.(?P<ext>html|qmd)$")


def report_days(docs_path: Path, extensions=("html", "qmd")) -> Dict[str, Set[str]]:
    """Days with a daily report (.html or .qmd) of each project, from the file names."""
    days: Dict[str, Set[str]] = {}
    folder = Path(docs_path) / "quarto_files"
    if not folder.exists():
        return days
    for path in folder.iterdir():
        match = DAILY_REPORT.match(path.name)
        if match and match["ext"] in extensions:
            days.setdefault(match["name"], set()).add(match["date"])
    return days


def load_state(docs_path: Path) -> dict:
    path = Path(docs_path) / STATE_FILE
    return json.loads(path.read_text()) if path.exists() else {}


def save_state(docs_path: Path, state: dict) -> None:
    path = Path(docs_path) / STATE_FILE
    path.write_text(json.dumps(state, indent=1, sort_keys=True) + "\n")


def session_dates(config: dict):
    """Start of every session of the subjects of a project (lecilab_behavior_analysis)."""
    from lecilab_behavior_analysis.io.loading import load_session_dates

    return load_session_dates(config["project_name"], config["subjects"])


def update_data_days(state: dict, name: str, config: dict) -> Optional[dict]:
    """
    Adds the days with new data of a project to the state (days already
    known are kept). Returns the dates read (None if they could not be read).
    """
    try:
        dates = session_dates(config)
    except Exception as error:
        print(f"Could not read the session dates of {name}: {type(error).__name__}: {error}")
        return None
    days = set(dates["date"].dt.strftime("%Y-%m-%d"))
    entry = state.setdefault(name, {})
    entry["data_days"] = sorted(days | set(entry.get("data_days", [])))
    last = dates.groupby("subject")["date"].max().dt.strftime("%Y-%m-%d").to_dict() if len(dates) else {}
    return {"last_day": max(last.values()) if last else None, "subject_last_days": last, "dates": dates}


def find_archived_config(name: str, config_paths: List[Path]) -> Optional[Path]:
    for folder in config_paths:
        path = Path(folder) / f"{name}.json"
        if path.exists():
            return path
    return None


def remove_daily_reports(docs_path: Path, name: str) -> List[str]:
    """
    Removes the daily reports of a project from the website (.html and its
    _files folder), keeping the .qmd files. Returns the days removed.
    """
    folder = Path(docs_path) / "quarto_files"
    removed = []
    for day in sorted(report_days(docs_path, extensions=("html",)).get(name, set())):
        (folder / f"{name}_{day}.html").unlink(missing_ok=True)
        shutil.rmtree(folder / f"{name}_{day}_files", ignore_errors=True)
        removed.append(day)
    return removed


def archive_projects(
    active_names: Set[str],
    docs_path: Path,
    state: dict,
    make_archive_report: Callable[[Path, str, Dict[str, str]], Path],
    config_paths: Optional[List[Path]] = None,
) -> List[str]:
    """
    Archives the projects that are not active: makes (or updates) their
    archive report and then removes their daily reports. Updates the state.
    Returns the names of the projects that could not be archived.

    The archive report is made again when there is newer data than the one it
    shows (e.g. a box that sent its data late). A project without
    configuration in config_paths, or without data, keeps its daily reports
    (the calendar then links to its last one).
    """
    config_paths = config_paths or [ARCHIVED_CONFIG_FILES_PATH]
    names = set(report_days(docs_path)) | {p.stem for folder in config_paths for p in Path(folder).glob("*.json")}
    failed = []
    for name in sorted(names - set(active_names)):
        entry = state.setdefault(name, {})
        entry["status"] = "archived"
        entry["report_days"] = sorted(set(entry.get("report_days", [])) | report_days(docs_path).get(name, set()))
        config_file = find_archived_config(name, config_paths)
        if config_file is None:
            print(f"Archived project {name}: no configuration in {', '.join(map(str, config_paths))}, "
                  "its daily reports are kept.")
            continue
        from village_report_generator.generate_quarto_file import read_config

        last = update_data_days(state, name, read_config(config_file))
        if not last or not last["last_day"]:
            print(f"Archived project {name}: no data found, its daily reports are kept.")
            continue
        report = Path(docs_path) / "quarto_files" / f"{name}_archive.html"
        archive = entry.get("archive", {})
        if not report.exists() or archive.get("last_day") != last["last_day"]:
            try:
                make_archive_report(config_file, last["last_day"], last["subject_last_days"])
            except Exception as error:
                print(f"Archive report of {name} FAILED: {type(error).__name__}: {error}")
                failed.append(name)
                continue
            if not report.exists():
                failed.append(name)
                continue
            entry["archive"] = {"report": f"quarto_files/{report.name}",
                                "last_day": last["last_day"], "subject_last_days": last["subject_last_days"]}
        removed = remove_daily_reports(docs_path, name)
        if removed:
            print(f"Archived project {name}: removed {len(removed)} daily reports (the .qmd files are kept).")
    return failed


def update_active_projects(configs: Dict[str, dict], docs_path: Path, state: dict, date: Optional[str] = None) -> None:
    """
    Days with a report and days with new data of the active projects, and
    the setups that collected data for them on date (the day of the
    reports): active_setups.
    """
    days = report_days(docs_path, extensions=("html",))
    for name, config in configs.items():
        entry = state.setdefault(name, {})
        entry["status"] = "active"
        entry.pop("archive", None)
        entry["report_days"] = sorted(days.get(name, set()))
        read = update_data_days(state, name, config)
        if read is not None and date is not None:
            dates = read["dates"]
            on_date = dates[dates["date"].dt.strftime("%Y-%m-%d") == date]
            entry["active_setups"] = sorted({s for s in on_date["setup"].dropna() if s})
