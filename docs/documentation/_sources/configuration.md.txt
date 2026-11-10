# Configuration

Each active project has a `.json` file in
`village_report_generator/active_configuration_files/`. To stop making the
reports of a project, move its file to `archived_configuration_files/`: the
project goes to the archive of the index, with one report of its last data
(see [How it works](how_it_works)).

```json
{
    "project_name": "COT_cannula_GAD2_data",
    "subjects": ["NUO057", "NUO058", "NUO059"],
    "general_template": "visual_and_COT_quarto_general_template.txt",
    "subject_template": "visual_and_COT_quarto_subject_template.txt"
}
```

| Field | |
|---|---|
| `project_name` | Folder of the project in the data folder. |
| `subjects` | Subjects to include (a subject without data is noted, not an error). |
| `general_template` | Template of the Overview tab. |
| `subject_template` | Optional: template of the tab of each subject. Without it, the report only has the Overview (e.g. for habituation). |
| `setup_name` | Optional: a setup or a list of setups to read the events and sessions from. By default, every setup of the project. |

## Templates

| Template | |
|---|---|
| `visual_and_COT_quarto_general_template.txt` | Overview of a training project. |
| `habituation_general_template.txt` | Overview for habituation projects (use it without a subject template). |
| `visual_and_COT_quarto_subject_template.txt` | Training history and session of the day of a subject. |
| `problems_template.txt` | Problems tab, added to every report. |
| `temperature_humidity_*_template.txt` | Temperature and humidity report. |

Templates are Quarto documents with placeholders (`[[[project_name]]]`,
`[[[subjects]]]`, `[[[setups]]]`, `[[[date]]]`, `[[[subject]]]`). Each cell
calls a function of lecilab-behavior-analysis (`reports.overview`,
`figure_maker`) that never raises; to add a figure to the reports, add it
there and call it from a template. Cell labels must be unique in a report
(the subject template adds the subject to its labels).
