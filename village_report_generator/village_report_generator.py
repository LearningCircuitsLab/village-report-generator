# main script, to be run every day by the cron job
# step 1: generate the quarto file
# step 2: render the quarto file to HTML
# step 3: create a report about the temperature and humidity data
# step 4: update the index.html file with the calendar
# step 5: commit the changes to the repository and push to GitHub

# import necessary libraries
from village_report_generator.generate_quarto_file import generate_quarto_file
from village_report_generator.update_index import generate_index_html_with_calendar
from village_report_generator.temperature_and_humidity_scripts import generate_temphum_quarto_file
import datetime
import subprocess
from pathlib import Path

def main():
    # define the path to the active configuration files
    active_config_files_path = 'village_report_generator/active_configuration_files'
    # list all config files in the active configuration files directory
    config_files = [f for f in Path(active_config_files_path).glob('*.json')]
    if not config_files:
        print("No configuration files found in the active configuration files directory.")
        return

    for config_file in config_files:
        # Step 1: Generate the quarto file
        print(f"Using configuration file: {config_file}")
        # Get previous day date in YYYY-MM-DD format
        date = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
        print(f"Generating report for date: {date}")
        # Generate the quarto file
        generate_quarto_file(config_file, date)

        # Step 2: Render the quarto file to HTML
        # make sure the quarto file is there
        config_file_name = Path(config_file).stem
        quarto_files_path = Path(f'docs/quarto_files/{config_file_name}_{date}.qmd')
        if not quarto_files_path.exists():
            print(f"Quarto file {quarto_files_path} does not exist. Please check the configuration.")
            return

        subprocess.run(['quarto', 'render', str(quarto_files_path)], check=True)

    # Step 3: Create a report about the temperature and humidity data
    temp_hum_quarto_path = generate_temphum_quarto_file(date)
    subprocess.run(['quarto', 'render', str(temp_hum_quarto_path.with_suffix('.qmd'))], check=True)
    print("Temperature and humidity report generated.")

    # Step 4: Update the index.html file
    # make sure the quarto report is generated
    html_file_path = Path(f'docs/quarto_files/{config_file_name}_{date}.html')
    if not html_file_path.exists():
        print(f"HTML file {html_file_path} does not exist. Please check the rendering step.")
        return
    generate_index_html_with_calendar()
    print("Index HTML file updated.")

    # Step 5: Commit the changes to the repository and push to GitHub
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f'Update report for {date}'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("Changes committed and pushed to GitHub.")

if __name__ == "__main__":
    main()
