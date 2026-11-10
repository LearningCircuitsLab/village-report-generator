# village-report-generator

**[Documentation and example report](https://learningcircuitslab.github.io/village-report-generator/documentation/)** ·
**[Reports](https://learningcircuitslab.github.io/village-report-generator/)**

Every day, on the cluster, this repository makes an HTML report of each
active project of the [Training Village](https://braincircuitsbehaviorlab.github.io/village/)
and publishes it on the [reports website](https://learningcircuitslab.github.io/village-report-generator/),
with a calendar to choose the day.

- **Overview** tab: corridor plot of the last days, TV report (detections,
  sessions, water and weight), trials per training stage, trials and
  performance of the last days, box occupancy, performance of the cohort.
- One tab per **subject**: training history and the session of the day.
- **Problems** tab: everything that could not be drawn.
- A separate **temperature and humidity** report.

The analysis and figures come from
[lecilab-behavior-analysis](https://github.com/LearningCircuitsLab/lecilab-behavior-analysis);
this repository decides what goes in each report, renders it with
[Quarto](https://quarto.org/) and publishes it.

## How it works

1. For each configuration file in `village_report_generator/active_configuration_files`
   (one per project), `generate_quarto_file.py` writes
   `docs/quarto_files/<configuration>_<date>.qmd` from the templates in
   `quarto_templates/`.
2. Quarto runs it and writes the HTML report. The data is read from the data
   folder of the computer (`/storage/training_village` on the cluster); the
   setups (boxes) of each project are found automatically.
3. The temperature and humidity report and the calendar of `docs/index.html`
   are updated, and everything is committed and pushed. GitHub Pages
   publishes `docs/`.

Nothing in a report stops the others: each project is rendered on its own,
and a cell or figure panel that fails shows a red message and is listed in
the Problems tab. The script ends with exit code 1, naming the reports that
failed, so that cron reports it.

A configuration file:

```json
{
    "project_name": "COT_cannula_GAD2_data",
    "subjects": ["NUO057", "NUO058"],
    "general_template": "visual_and_COT_quarto_general_template.txt",
    "subject_template": "visual_and_COT_quarto_subject_template.txt"
}
```

Without `subject_template` the report only has the overview (e.g. with
`habituation_general_template.txt`). `setup_name` (a setup or a list) is
optional, to read only some setups.

## Running

Cron runs it every day as the user `training_village` on `minibaps` (it needs
writing access to this repository, and lecilab-behavior-analysis and village
installed in the Python of the `python3` Jupyter kernel):

```bash
python -m village_report_generator.village_report_generator
```

To try changes, render the reports of the sample data (`sample_data/`: four
days of two mice of a real project, 2.5 MB) in about half a minute; they go
to `sample_reports/` (not tracked):

```bash
python -m village_report_generator.village_report_generator --sample
```

Other options: `--date 2026-05-25`, `--projects <configuration name>`,
`--docs_path <folder>`, `--data_path <folder>`, `--temperature False`,
`--push False` (see the
[documentation](https://learningcircuitslab.github.io/village-report-generator/documentation/running.html)).

## Tests

```bash
pip install -e ".[dev]"
python -m pytest tests -o addopts=""
```

## Documentation

The documentation (`docs_source/`) is built by a GitHub action
(`.github/workflows/documentation.yml`) on every push to main that changes
the code, the sample data or the documentation. The action also renders the
sample reports with the current code, as the example of the documentation,
and commits the site to `docs/documentation/`.
