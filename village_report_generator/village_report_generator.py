# main script, to be run every day by the cron job
# step 1: generate the quarto file
# step 2: render the quarto file to HTML
# step 3: update the index.html file with the calendar
# step 4: commit the changes to the repository and push to GitHub

# import necessary libraries
from village_report_generator.generate_quarto_file import generate_quarto_file
from village_report_generator.update_index import generate_index_html_with_calendar
import datetime
import subprocess
from pathlib import Path

def main():
    # Step 1: Generate the quarto file
    active_config_files_path = 'village_report_generator/active_configuration_files'
    # list all config files in the active configuration files directory
    config_files = [f for f in Path(active_config_files_path).glob('*.json')]
    if not config_files:
        print("No configuration files found in the active configuration files directory.")
        return
    if len(config_files) > 1:
        print("Multiple configuration files found. Please ensure only one is present. To be changed!!")
        return
    config_file = config_files[0]  # Assuming only one config file is present
    print(f"Using configuration file: {config_file}")
    # Get today's date in YYYY-MM-DD format
    date = datetime.datetime.now().strftime('%Y-%m-%d')
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
    
    subprocess.run(['/home/hvergara/script_test.sh'], check=True)  # Assuming script_test.sh handles the rendering

    subprocess.run(['quarto', 'render', str(quarto_files_path)], check=True)

    # Step 3: Update the index.html file
    # make sure the quarto report is generated
    html_file_path = Path(f'docs/quarto_files/{config_file_name}_{date}.html')
    if not html_file_path.exists():
        print(f"HTML file {html_file_path} does not exist. Please check the rendering step.")
        return
    generate_index_html_with_calendar()
    print("Index HTML file updated.")

    # Step 4: Commit the changes to the repository and push to GitHub
    subprocess.run(['git', 'add', '.'], check=True)
    subprocess.run(['git', 'commit', '-m', f'Update report for {date}'], check=True)
    subprocess.run(['git', 'push'], check=True)
    print("Changes committed and pushed to GitHub.")

if __name__ == "__main__":
    main()
