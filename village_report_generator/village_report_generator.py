# main script, to be run every day by the cron job
# step 1: for each active configuration file (one per project), generate the
#         quarto file and render it to HTML. Each project is independent: if
#         one fails, the others are still generated.
# step 2: create a report about the temperature and humidity data
# step 3: update the index.html file with the calendar
# step 4: commit the changes to the repository and push to GitHub
#
# Usage (from the root of the repository):
#   python -m village_report_generator.village_report_generator
#   python -m village_report_generator.village_report_generator --date 2026-05-25 --push False
#   python -m village_report_generator.village_report_generator --projects nuo_COT_cannula_GAD2_data --push False
#   python -m village_report_generator.village_report_generator --sample   (sample data, about a minute)

import datetime
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import List, Optional, Sequence, Union

import fire

from village_report_generator.generate_quarto_file import DOCS_PATH, generate_quarto_file
from village_report_generator.temperature_and_humidity_scripts import generate_temphum_quarto_file
from village_report_generator.update_index import generate_index_html_with_calendar

REPO_PATH = Path(__file__).parent.parent
ACTIVE_CONFIG_FILES_PATH = Path(__file__).parent / "active_configuration_files"
# small copy of real data, to try changes quickly (see sample_data/README.md)
SAMPLE_DATA_PATH = REPO_PATH / "sample_data"
SAMPLE_DATE = "2026-05-25"
SAMPLE_REPORTS_PATH = REPO_PATH / "sample_reports"
# environment variable read by lecilab_behavior_analysis.io.server.get_outpath
DATA_PATH_VARIABLE = "LECILAB_DATA_PATH"


def render(qmd_path: Path) -> None:
    """Renders a .qmd file to HTML with quarto (raises if quarto fails)."""
    subprocess.run(["quarto", "render", str(qmd_path)], check=True)


def make_report(config_file: Path, date: str, docs_path: Path) -> Path:
    """Generates and renders the report of one project. Returns the HTML file."""
    qmd_path = generate_quarto_file(config_file, date, docs_path)
    render(qmd_path)
    html_path = qmd_path.with_suffix(".html")
    if not html_path.exists():
        raise FileNotFoundError(f"quarto did not create {html_path}")
    return html_path


def main(
    date: Optional[str] = None,
    projects: Optional[Union[str, Sequence[str]]] = None,
    config_path: Union[str, Path] = ACTIVE_CONFIG_FILES_PATH,
    docs_path: Union[str, Path] = DOCS_PATH,
    data_path: Optional[Union[str, Path]] = None,
    temperature: bool = True,
    push: bool = True,
    sample: bool = False,
) -> List[str]:
    """
    Generates the reports of every active project for a date and publishes them.

    Args:
        date: date of the report (YYYY-MM-DD). Defaults to yesterday.
        projects: names of the configuration files to use (without .json).
            Defaults to every file in config_path.
        config_path: folder with the configuration files.
        docs_path: folder of the website.
        data_path: folder with the data of the projects. Defaults to the
            folder of this computer (get_outpath of lecilab_behavior_analysis).
        temperature: also make the temperature and humidity report.
        push: commit and push the new reports to GitHub.
        sample: make the reports of the sample data (sample_data/) in
            sample_reports/, without pushing (the other options are ignored).

    Returns the names of the reports that failed (empty if all worked).
    """
    if sample:
        date, projects, config_path = SAMPLE_DATE, None, SAMPLE_DATA_PATH / "configs"
        data_path, docs_path, push = SAMPLE_DATA_PATH, SAMPLE_REPORTS_PATH, False
    if data_path is not None:
        # quarto runs the reports in a new process, which inherits it
        os.environ[DATA_PATH_VARIABLE] = str(Path(data_path).resolve())
    date = date or (datetime.datetime.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")
    docs_path = Path(docs_path)
    config_files = sorted(Path(config_path).glob("*.json"))
    if projects is not None:
        names = [projects] if isinstance(projects, str) else list(projects)
        config_files = [f for f in config_files if f.stem in names]
    if not config_files:
        print(f"No configuration files found in {config_path}.")
        return []

    print(f"Generating reports for date: {date}")
    done, failed = [], []
    for config_file in config_files:
        print(f"Using configuration file: {config_file}")
        start = time.time()
        try:
            make_report(config_file, date, docs_path)
            done.append(config_file.stem)
            print(f"Report {config_file.stem} generated in {time.time() - start:.0f} s.")
        except Exception as error:  # one project must not stop the others
            failed.append(config_file.stem)
            print(f"Report {config_file.stem} FAILED after {time.time() - start:.0f} s: {type(error).__name__}: {error}")

    if temperature:
        try:
            render(generate_temphum_quarto_file(date, docs_path))
            print("Temperature and humidity report generated.")
        except Exception as error:
            failed.append("temperature_and_humidity")
            print(f"Temperature and humidity report FAILED: {type(error).__name__}: {error}")

    if done:
        if docs_path.resolve() != Path(DOCS_PATH).resolve() and (Path(DOCS_PATH) / "assets").exists():
            # the logo of the index, when the reports are written somewhere else
            shutil.copytree(Path(DOCS_PATH) / "assets", docs_path / "assets", dirs_exist_ok=True)
        generate_index_html_with_calendar(docs_path)
        print("Index HTML file updated.")

    if push and done:
        subprocess.run(["git", "add", "."], check=True, cwd=REPO_PATH)
        subprocess.run(["git", "commit", "-m", f"Update report for {date}"], check=True, cwd=REPO_PATH)
        # commits made on GitHub (e.g. the documentation, built by an action)
        # would otherwise make the push fail
        subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True, cwd=REPO_PATH)
        subprocess.run(["git", "push"], check=True, cwd=REPO_PATH)
        print("Changes committed and pushed to GitHub.")

    if failed:
        print(f"Reports that failed: {', '.join(failed)}")
    return failed


def cli() -> None:
    failed = fire.Fire(main)
    # a non-zero exit code makes cron report the failure
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    cli()
