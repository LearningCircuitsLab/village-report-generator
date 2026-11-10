"""
Writes docs/index.html: a calendar for each project, active ones first and
then the archive. Every day with a report is a link to it.

- Active projects: light green if the project had new data that day, light
  red if it had a report but no new data (nothing was collected).
- Archive: the days with data, in grey; every day links to the one report
  of the archived project (its last data).

The days come from docs/calendar_days.json (see projects.py) and from the
report files. The calendars are plain HTML (no JavaScript).
"""

import calendar
import datetime
import html
import os
from typing import Dict, List, Optional

from village_report_generator.projects import load_state, report_days

DOCS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs")

GREEN, RED, GREY, EMPTY = "#b7e1b7", "#f4c2c2", "#bdbdbd", "#f2f2f2"

STYLE = """
<style>
  body { font-family: Arial, sans-serif; color: #4a4a4a; line-height: 1.6; margin: 0 16px; }
  header, .intro { text-align: center; }
  h1, h2 { color: #2a3f5f; }
  h2.section { text-align: center; margin-top: 40px; border-bottom: 1px solid #ddd; padding-bottom: 4px; }
  a { color: #007bff; text-decoration: none; }
  .legend { text-align: center; font-size: 14px; }
  .legend span.box { display: inline-block; width: 12px; height: 12px; margin: 0 4px 0 12px; vertical-align: middle; }
  section.project { margin: 24px auto; max-width: 1100px; }
  section.project h3 { margin-bottom: 0; color: #2a3f5f; }
  .year { display: flex; flex-wrap: wrap; gap: 12px; align-items: flex-start; margin-top: 8px; }
  .year-label { font-weight: bold; width: 100%; }
  .month { font-size: 11px; }
  .month-name { text-align: center; }
  .days { display: grid; grid-template-columns: repeat(7, 14px); gap: 2px; }
  .days a, .days span { width: 14px; height: 14px; display: block; border-radius: 2px; }
</style>
"""


def _month_html(year: int, month: int, colors: Dict[str, str], links: Dict[str, str], titles: Dict[str, str]) -> str:
    cells = []
    first_weekday, n_days = calendar.monthrange(year, month)  # Monday = 0
    cells += ['<span></span>'] * first_weekday
    for day in range(1, n_days + 1):
        key = f"{year}-{month:02d}-{day:02d}"
        color = colors.get(key, EMPTY)
        title = html.escape(titles.get(key, key))
        if key in links:
            cells.append(f'<a href="{links[key]}" title="{title}" style="background:{color}"></a>')
        else:
            cells.append(f'<span title="{title}" style="background:{color}"></span>')
    return (f'<div class="month"><div class="month-name">{calendar.month_abbr[month]}</div>'
            f'<div class="days">{"".join(cells)}</div></div>')


def calendar_html(colors: Dict[str, str], links: Dict[str, str], titles: Dict[str, str]) -> str:
    """Months of every year with a coloured day, Monday to Sunday in columns."""
    if not colors:
        return "<p>No days yet.</p>"
    days = sorted(colors)
    first = datetime.date.fromisoformat(days[0])
    last = datetime.date.fromisoformat(days[-1])
    parts = []
    for year in range(first.year, last.year + 1):
        start = first.month if year == first.year else 1
        end = last.month if year == last.year else 12
        months = "".join(_month_html(year, m, colors, links, titles) for m in range(start, end + 1))
        parts.append(f'<div class="year"><div class="year-label">{year}</div>{months}</div>')
    return "".join(parts)


def _project_html(name: str, colors: Dict[str, str], links: Dict[str, str], titles: Dict[str, str],
                  subtitle: str) -> str:
    return (f'<section class="project"><h3 id="{html.escape(name)}">{html.escape(name)}</h3>'
            f"<div>{subtitle}</div>{calendar_html(colors, links, titles)}</section>")


def active_project_html(name: str, days: List[str], data_days: set) -> str:
    colors, links, titles = {}, {}, {}
    for day in days:
        has_data = day in data_days
        colors[day] = GREEN if has_data else RED
        links[day] = f"quarto_files/{name}_{day}.html"
        titles[day] = f"{day}: {'new data' if has_data else 'no new data'}"
    last = f'Last report: <a href="{links[days[-1]]}">{days[-1]}</a>' if days else "No reports yet."
    return _project_html(name, colors, links, titles, last)


def archived_project_html(name: str, entry: dict, html_days: List[str]) -> str:
    days = entry.get("data_days") or entry.get("report_days") or html_days
    archive = entry.get("archive")
    if archive:
        target = archive["report"]
        subtitle = f'<a href="{target}">Archive report</a> (last data: {archive["last_day"]})'
    elif html_days:  # not archived yet (no configuration or no data): its last daily report
        target = f"quarto_files/{name}_{html_days[-1]}.html"
        subtitle = f'Last report: <a href="{target}">{html_days[-1]}</a>'
    else:
        target, subtitle = None, "No report available."
    colors = {day: GREY for day in days}
    links = {day: target for day in days} if target else {}
    titles = {day: f"{day}: data collected" for day in days}
    return _project_html(name, colors, links, titles, subtitle)


def generate_index_html_with_calendar(docs_path=DOCS_PATH, active_names: Optional[List[str]] = None) -> None:
    """
    Writes <docs_path>/index.html. active_names: the active projects; the
    others with reports or in docs/calendar_days.json go to the archive.
    """
    state = load_state(docs_path)
    html_days = {name: sorted(days) for name, days in report_days(docs_path, extensions=("html",)).items()}
    if active_names is None:
        active_names = [n for n, e in state.items() if e.get("status") == "active"] or list(html_days)
    active = sorted(active_names)
    archived = sorted((set(state) | set(html_days)) - set(active))

    legend = (
        f'<p class="legend"><span class="box" style="background:{GREEN}"></span>report, new data collected'
        f'<span class="box" style="background:{RED}"></span>report, no new data'
        f'<span class="box" style="background:{GREY}"></span>archived project: data collected</p>'
    )
    body = [f'<h2 class="section">Active projects</h2>{legend}']
    for name in active:
        body.append(active_project_html(name, html_days.get(name, []), set(state.get(name, {}).get("data_days", []))))
    if archived:
        body.append('<h2 class="section">Archive</h2>'
                    '<p class="intro">Projects that are no longer updated. Every day links to the report of their last data.</p>')
        for name in archived:
            body.append(archived_project_html(name, state.get(name, {}), html_days.get(name, [])))

    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Training Village Reports</title>
{STYLE}
</head>
<body>
<header>
  <h1>Training Village Reports</h1>
  <img src="assets/logo.png" alt="Village Report Logo" style="width: 150px; height: auto;">
</header>
<main>
  <p class="intro" style="font-size: 18px;">Click a day of a calendar to open its report.</p>
  <p class="intro">For more information, visit the
    <a href="https://github.com/LearningCircuitsLab/village-report-generator">Github repo</a> and the
    <a href="documentation/">documentation</a>.</p>
  <p class="intro">Check out the
    <a href="temperature_and_humidity/temperature_and_humidity.html">Temperature and Humidity Reports</a>.</p>
  {"".join(body)}
</main>
</body>
</html>
"""
    with open(os.path.join(docs_path, "index.html"), "w") as index_file:
        index_file.write(index_content)


if __name__ == "__main__":
    generate_index_html_with_calendar()
