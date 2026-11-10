# How it works

`village_report_generator.py` (run every day by cron, see [Running](running)):

1. For each configuration file in `village_report_generator/active_configuration_files/`
   (one per project), `generate_quarto_file.py` writes
   `docs/quarto_files/<configuration>_<date>.qmd` from the templates in
   `quarto_templates/`:
   - the general template: the Overview tab,
   - the subject template, once per subject: one tab each,
   - `problems_template.txt`: the Problems tab.
2. Quarto runs the code of the `.qmd` file (Python) and writes the `.html` report.
3. The temperature and humidity report is made the same way.
4. `projects.py` records the days with new data of each project and archives
   the projects that are no longer active (see below).
5. `update_index.py` rewrites `docs/index.html`, with a calendar per project.
6. The new files are committed and pushed; GitHub Pages publishes the `docs/`
   folder.

## Nothing stops the other reports

- **Each project is rendered on its own.** If one fails, the others are still
  made. The script ends with exit code 1 and the list of the reports that
  failed, so that cron reports it.
- **Inside a report**, each cell and each panel of a figure that fails shows a
  red *Could not generate ...* message where it should be, and is listed in
  the **Problems** tab. The rest of the report is drawn.
- Subjects without trials, and projects without events or sessions summary,
  are noted at the top of the Overview.

## Where the data comes from

The cells read the data folder of the computer
(`/storage/training_village` on the cluster, see `get_outpath()` in
lecilab-behavior-analysis, or the `LECILAB_DATA_PATH` environment variable):

```
<data folder>/<project>/sessions/<subject>/<subject>.csv   trials
<data folder>/<project>/<setup>/events.csv (+ old_events/)  events of a box
<data folder>/<project>/<setup>/sessions_summary.csv        sessions of a box
```

The **setups** (boxes) of a project are found automatically: every folder of
the project with an `events.csv` or a `sessions_summary.csv` (e.g.
`village01` and `village02` when the mice train in two boxes). Their events
and sessions are read together.

## The calendars of the index

Every day of a calendar with a report is a link to it.

- **Active projects** (a configuration in `active_configuration_files/`):
  light green if new data was collected that day, light red if there is a
  report but no new data (nothing was sent from the boxes). The title shows,
  in parentheses, the setups that collected data for the project on the day
  of the last report (a setup used earlier but not that day is not shown).
- **Archive**: the days with data, in grey. Every day links to the one report
  of the archived project.

New data: the boxes send each session to the data folder, so a project has
new data on a day if one of its subjects has a session that day in the
sessions summary of one of its setups (or, without a sessions summary, in
its trials file). The days are kept in `docs/calendar_days.json`.

## The archive

A project whose configuration is no longer in `active_configuration_files/`
goes to the archive. With its configuration in
`village_report_generator/archived_configuration_files/`, the next daily run:

1. makes one report, `<project>_archive.html`: the Overview as of the last day
   with data of the project and, in the tab of each subject, its training
   history up to its own last day with data and its **last 48 hours of
   training**;
2. removes the daily reports of the project from the website (the `.qmd`
   files, a few kB each, are kept as the record of the days that had a
   report).

The archive report is made again if newer data appears (e.g. a box that sent
its data late). A project without configuration in
`archived_configuration_files/`, or without data, keeps its daily reports,
and its calendar links to the last one.

## Size of the reports

GitHub Pages publishes at most 10 GB, so the reports are kept small:

- figures are drawn at normal resolution (`fig-format: png`, `fig-dpi: 96`
  in the templates; Quarto's default, retina, doubles it) and saved with 256
  colours after rendering (`shrink_images`), about 7 times smaller in total;
- the interactive performance plot of the Overview has at most 1000 points
  per subject (consecutive trials are grouped), so it does not grow with
  training;
- archived projects keep one report instead of one per day.

## The tab of each subject

1. **Sessions** of the day of the report (or, in the archive, the last 48
   hours of training), with links to the same subject in the reports of the
   previous and the next day.
2. **Training history** up to that day.

A link to a report ending in `#<subject>` (e.g.
`nuo_COT_cannula_GAD2_data_2026-11-09.html#NUO057`) opens the tab of that
subject, and the address of a report shows the tab that is open, so it can be
copied and shared.
