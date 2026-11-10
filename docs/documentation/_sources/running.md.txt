# Running

## On the cluster

Cron runs every day, as the user `training_village` on `minibaps`, from the
root of the repository:

```bash
python -m village_report_generator.village_report_generator
```

It makes the reports of the day before, commits them and pushes them (it
first pulls, so that commits made on GitHub, such as the documentation, do
not block the push). The Python that Quarto uses (the `python3` Jupyter
kernel) needs lecilab-behavior-analysis and village installed. The user needs
writing access to the repository.

## Options

```bash
# a given date and project, without pushing
python -m village_report_generator.village_report_generator --date 2026-05-25 --projects nuo_COT_cannula_GAD2_data --push False

# write the reports somewhere else, without touching the website
python -m village_report_generator.village_report_generator --date 2026-05-25 --docs_path /tmp/docs --push False

# read the data from another folder
python -m village_report_generator.village_report_generator --data_path /path/to/data --push False
```

| Option | |
|---|---|
| `--date` | Date of the reports (YYYY-MM-DD). Default: yesterday. |
| `--projects` | Names of the configuration files to use (default: all). |
| `--config_path` | Folder with the configuration files. |
| `--docs_path` | Folder of the website (default: `docs/`). |
| `--data_path` | Folder with the data (default: the folder of this computer). |
| `--archived_config_path` | Folder with the configuration files of the archived projects. |
| `--temperature False` | Skip the temperature and humidity report. |
| `--archive False` | Do not archive the projects that are not active. |
| `--push False` | Do not commit and push. |
| `--sample` | Reports of the sample data (see below). |

## Trying changes with the sample data

`sample_data/` has four days of two mice of a real project (trained in two
boxes), with its events, sessions and temperatures, and the last days of two
mice of a finished project, which goes to the archive (5 MB). It renders in
about a minute:

```bash
python -m village_report_generator.village_report_generator --sample
```

The reports go to `sample_reports/` (not tracked by git); open
`sample_reports/index.html`. It makes a report with subject tabs, an
overview-only report (habituation template), the archive report and the
temperature report. `--date` changes the day of the daily reports (the data
ends on 2026-05-25; a later day shows a day without new data, in light red).

## Tests

```bash
pip install -e ".[dev]"
python -m pytest tests -o addopts=""
```
