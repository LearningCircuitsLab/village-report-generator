# this script generates a quarto file, that then is used by quarto to generate the report

import json
from pathlib import Path
from typing import List, Optional, Union

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


def build_quarto_content(config: dict, date: str) -> str:
    """
    Text of the .qmd report of a project for a date (YYYY-MM-DD), from the
    templates named in its configuration: the general template (the overview)
    and, if there is one, the subject template, repeated for each subject.
    """
    general = (TEMPLATES_PATH / config["general_template"]).read_text()
    content = (
        general.replace("[[[project_name]]]", config["project_name"])
        .replace("[[[subjects]]]", str(config["subjects"]))
        .replace("[[[date]]]", date)
        .replace("[[[setups]]]", str(config_setups(config)))
    )

    if "subject_template" in config:
        subject_template = (TEMPLATES_PATH / config["subject_template"]).read_text()
        for subject in config["subjects"]:
            subject_content = (
                subject_template.replace("[[[subject]]]", subject)
                .replace("[[[project_name]]]", config["project_name"])
                .replace("[[[date]]]", date)
            )
            content += "\n" + subject_content

    content += "\n" + (TEMPLATES_PATH / PROBLEMS_TEMPLATE).read_text()
    content += "\n" + ":::"
    return content


def generate_quarto_file(config_file: Union[str, Path], date: str, docs_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Writes the .qmd report of the project of config_file for a date
    (YYYY-MM-DD) to <docs_path>/quarto_files/<config name>_<date>.qmd and
    returns its path.

    Args:
        config_file: path to the configuration file (.json).
        date: date in the format 'YYYY-MM-DD'.
        docs_path: folder of the website (defaults to the docs folder of this repository).
    """
    config = json.loads(Path(config_file).read_text())
    for key in ("project_name", "subjects", "general_template"):
        if key not in config:
            raise KeyError(f"{config_file} has no '{key}'")

    docs_path = Path(docs_path) if docs_path is not None else DOCS_PATH
    output_file = docs_path / "quarto_files" / f"{Path(config_file).stem}_{date}.qmd"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text(build_quarto_content(config, date))
    return output_file


if __name__ == "__main__":
    # Use fire to create a command line interface
    fire.Fire(generate_quarto_file)
    print("Quarto file generation complete.")
