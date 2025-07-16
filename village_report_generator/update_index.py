import os
import datetime
import pandas as pd
import plotly_calplot

def generate_index_html_with_calendar():
    quarto_files_path = "docs/quarto_files"
    index_file_path = "docs/index.html"

    # Get all .html files in the quarto_files directory
    html_files = [f for f in os.listdir(quarto_files_path) if f.endswith(".html")]

    # Extract dates and map them to filenames
    date_to_file_map = {}
    for html_file in html_files:
        try:
            date_str = html_file.split("_")[-1].split(".")[0]
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            date_to_file_map[date_obj.date()] = html_file
        except ValueError:
            pass

    # Create a DataFrame for the calendar
    df = pd.DataFrame({
        "date": list(date_to_file_map.keys()),
        "value": [1] * len(date_to_file_map)
    })

    # Generate the calendar plot and attach the real dates as customdata
    fig = plotly_calplot.calplot(
        df,
        x="date",
        y="value",
        title="Village Report Calendar",
        colorscale="Viridis",
    )

    # Inject customdata (the date strings) into each day's data
    for trace in fig.data:
        if "customdata" not in trace:
            trace.customdata = [[d] for d in df["date"].dt.strftime("%Y-%m-%d")]

    # Save the calendar plot as HTML string
    calendar_html = fig.to_html(full_html=False, include_plotlyjs="cdn", div_id="calendar_plot")

    # HTML with proper JS click handling
    index_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Village Report Generator</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
</head>
<body>
    <h1>Village Report Generator</h1>
    <p>Click on a date in the calendar to view the corresponding report:</p>
    {calendar_html}
    <script>
        var calendarDiv = document.getElementById('calendar_plot');
        calendarDiv.on('plotly_click', function(data) {{
            var point = data.points[0];
            var dateStr = point.customdata[0];
            if (dateStr) {{
                var link = `quarto_files/hernando_visual_and_COT_${{dateStr}}.html`;
                window.location.href = link;
            }}
        }});
    </script>
</body>
</html>
"""

    # Write the index.html file
    with open(index_file_path, "w") as index_file:
        index_file.write(index_content)

if __name__ == "__main__":
    generate_index_html_with_calendar()
