import os
import datetime
import pandas as pd
import plotly_calplot
from collections import defaultdict

def generate_index_html_with_calendar():
    quarto_files_path = "docs/quarto_files"
    index_file_path = "docs/index.html"

    # Get all .html files in the quarto_files directory
    html_files = [f for f in os.listdir(quarto_files_path) if f.endswith(".html")]

    # Group files by project name
    project_to_files_map = defaultdict(list)
    for html_file in html_files:
        try:
            project_name = html_file[:-16]  # Extract project name
            date_str = html_file.split("_")[-1].split(".")[0]
            date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")
            project_to_files_map[project_name].append((date_obj.date(), html_file))
        except ValueError:
            pass

    # Start building the index.html content
    index_content = """<!DOCTYPE html>
<html lang="en">
<head>
<body>
        <header style="text-align: center; margin-bottom: 20px;">
            <h1 style="font-family: Arial, sans-serif; color: #2a3f5f;">Training Village Reports</h1>
            <img src="assets/logo.png" alt="Village Report Logo" style="width: 150px; height: auto; margin-top: 10px;">
        </header>
        <main style="font-family: Arial, sans-serif; color: #4a4a4a; line-height: 1.6;">
            <p style="text-align: center; font-size: 18px;">
                Use the interactive calendars below to select a date and view the corresponding report.
            </p>
            <p style="text-align: center; font-size: 16px;">
                For more information, visit the <a href="https://github.com/LearningCircuitsLab/village-report-generator" style="color: #007bff; text-decoration: none;">Github repo</a>.
            </p>
            </br>
    """

    # Generate a calendar for each project
    for project_name, files in project_to_files_map.items():
        # Create a DataFrame for the calendar
        dates = [file[0] for file in files]
        df = pd.DataFrame({
            "date": dates,
            "value": [1] * len(dates)
        })

        # Generate the calendar plot and attach the real dates as customdata
        fig = plotly_calplot.calplot(
            df,
            x="date",
            y="value",
            # title=project_name + " Calendar",
            colorscale="Greys",
        )

        # Inject customdata (the date strings) into each day's data
        for trace in fig.data:
            if "customdata" not in trace:
                trace.customdata = [[d] for d in df["date"].dt.strftime("%Y-%m-%d")]

        # Save the calendar plot as HTML string
        calendar_html = fig.to_html(full_html=False, include_plotlyjs="cdn", div_id=f"calendar_plot_{project_name}")

        # Add the project title and calendar to the index content
        index_content += f"""
        <section style="margin-bottom: 40px;">
            <h2 style="text-align: center; font-family: Arial, sans-serif; color: #2a3f5f;">{project_name}</h2>
            {calendar_html}
        </section>
        <script>
            var calendarDiv = document.getElementById('calendar_plot_{project_name}');
            calendarDiv.on('plotly_click', function(data) {{
                var point = data.points[0];
                var dateStr = point.customdata[0];
                if (dateStr) {{
                    var link = `quarto_files/{project_name}_${{dateStr}}.html`;
                    window.location.href = link;
                }}
            }});
        </script>
        """

    # Close the HTML content
    index_content += """
        </main>
</body>
</html>
"""

    # Write the index.html file
    with open(index_file_path, "w") as index_file:
        index_file.write(index_content)

if __name__ == "__main__":
    generate_index_html_with_calendar()
