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
4. `update_index.py` rewrites `docs/index.html`, with a calendar per project.
5. The new files are committed and pushed; GitHub Pages publishes the `docs/`
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
