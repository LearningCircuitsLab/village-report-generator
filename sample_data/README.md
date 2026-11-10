# Sample data

A small copy of real data to render the reports in about a minute, to check
changes before they run on the cluster:

```bash
python -m village_report_generator.village_report_generator --sample
```

The reports are written to `sample_reports/` (not tracked by git).

Contents (same layout as the data folder on the cluster, see `get_outpath()`):

- `COT_cannula_GAD2_data/sessions/`: trials of NUO057 (trained on the report
  date, 2026-05-25) and NUO060 (last trained on 2026-05-22) from 2026-05-22 to
  2026-05-25, compressed (`<subject>.csv.gz`).
- `COT_cannula_GAD2_data/village01/` and `village02/`: events (including the
  old_events), sessions summary and temperatures from 2026-05-18 to
  2026-05-25. The mice of this project trained in both boxes.
- `COT_cannula_data/`: the last 4 days of trials of NUO001 (last data
  2026-06-11) and NUO003 (2026-06-05), their sessions summary (all their
  sessions, without the settings column) and the events of their last days.
  A finished project: it goes to the archive.
- `configs/`: a report with a tab per subject, and an overview-only report
  (habituation template).
- `archived_configs/`: the archived project.

`--date` changes the day of the daily reports; the data of the active project
ends on 2026-05-25, so a later day has no new data (light red in the index).
