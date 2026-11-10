# this script generates a quarto file, that then is used by quarto to generate the report

import json
from pathlib import Path
from typing import Dict, List, Optional, Union

import fire

TEMPLATES_PATH = Path(__file__).parent / "quarto_templates"
DOCS_PATH = Path(__file__).parent.parent / "docs"
# last tab of every report: the panels and cells that could not be generated
PROBLEMS_TEMPLATE = "problems_template.txt"


def config_setups(config: dict) -> Optional[List[str]]:
    """
    Setups (boxes) of a project to read the events and sessions summary from.
    None (the default) means every setup found in the project folder when the
    report is rendered. "setup_name" in the configuration (a name or a list)
    limits it to those setups.
    """
    names = config.get("setup_name")
    if names is None:
        return None
    return [names] if isinstance(names, str) else list(names)


# hours of training shown for each subject in the report of an archived project
ARCHIVE_SESSION_HOURS = 48


def build_quarto_content(config: dict, date: str, subject_dates: Optional[Dict[str, str]] = None) -> str:
    """
    Text of the .qmd report of a project for a date (YYYY-MM-DD), from the
    templates named in its configuration: the general template (the overview)
    and, if there is one, the subject template, repeated for each subject.

    With subject_dates ({subject: YYYY-MM-DD}), it is the report of an
    archived project: the overview is as of date (the last day with data of
    the project) and the tab of each subject shows its training history up to
    its own last day with data, and its last ARCHIVE_SESSION_HOURS hours of
    training.
    """
    archive = subject_dates is not None
    if archive:
        note = (f"Archived project: data up to {date}. The tab of each subject shows its last day "
                f"with data and its last {ARCHIVE_SESSION_HOURS} hours of training.")
    general = (TEMPLATES_PATH / config["general_template"]).read_text()
    content = (
        general.replace("[[[project_name]]]", config["project_name"])
        .replace("[[[subjects]]]", str(config["subjects"]))
        .replace("[[[date]]]", date)
        .replace("[[[setups]]]", str(config_setups(config)))
        .replace("[[[report_kind]]]", "Archive" if archive else "Report")
        .replace("[[[archive_note]]]", note if archive else "")
    )

    if "subject_template" in config:
        subject_template = (TEMPLATES_PATH / config["subject_template"]).read_text()
        for subject in config["subjects"]:
            subject_date = subject_dates.get(subject, date) if archive else date
            subject_content = (
                subject_template.replace("[[[subject]]]", subject)
                .replace("[[[project_name]]]", config["project_name"])
                .replace("[[[date]]]", date)
                .replace("[[[subject_date]]]", subject_date)
                .replace("[[[session_hours]]]", str(ARCHIVE_SESSION_HOURS) if archive else "None")
            )
            content += "\n" + subject_content

    content += "\n" + (TEMPLATES_PATH / PROBLEMS_TEMPLATE).read_text()
    content += "\n" + ":::"
    return content


def read_config(config_file: Union[str, Path]) -> dict:
    """Configuration of a project (.json), checking the required fields."""
    config = json.loads(Path(config_file).read_text())
    for key in ("project_name", "subjects", "general_template"):
        if key not in config:
            raise KeyError(f"{config_file} has no '{key}'")
    return config


def generate_quarto_file(
    config_file: Union[str, Path],
    date: str,
    docs_path: Optional[Union[str, Path]] = None,
    subject_dates: Optional[Dict[str, str]] = None,
) -> Path:
    """
    Writes the .qmd report of the project of config_file for a date
    (YYYY-MM-DD) to <docs_path>/quarto_files/<config name>_<date>.qmd and
    returns its path.

    With subject_dates, it is the report of an archived project (see
    build_quarto_content), written to <config name>_archive.qmd.

    Args:
        config_file: path to the configuration file (.json).
        date: date in the format 'YYYY-MM-DD'.
        docs_path: folder of the website (defaults to the docs folder of this repository).
        subject_dates: last day with data of each subject (archived projects).
    """
    config = read_config(config_file)
    docs_path = Path(docs_path) if docs_path is not None else DOCS_PATH
    suffix = "archive" if subject_dates is not None else date
    output_file = docs_path / "quarto_files" / f"{Path(config_file).stem}_{suffix}.qmd"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(build_quarto_content(config, date, subject_dates))
    return output_file


if __name__ == "__main__":
    # Use fire to create a command line interface
    fire.Fire(generate_quarto_file)
    print("Quarto file generation complete.")
