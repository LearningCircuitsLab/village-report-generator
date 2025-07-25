# this script generates a quarto file, that then is used by quarto to generate the report

# import necessary libraries
from lecilab_behavior_analysis import utils
import fire
import json
from pathlib import Path

def generate_quarto_file(config_file: str, date: str) -> None:
    """
    Generates a quarto file based on the provided configuration file.
    
    Args:
        config_file (str): Path to the configuration file.
        date (str): Date in the format 'YYYY-MM-DD'.
    """
    # TODO: add checkups for the inputs
    # Load the configuration file
    config_dict = json.load(open(config_file, 'r'))
    # get the path to the template files
    general_template_path = Path(__file__).parent / 'quarto_templates' / config_dict['general_template']
    subject_template_path = Path(__file__).parent / 'quarto_templates' / config_dict['subject_template']

    # load the general template file, that are txt
    with open(general_template_path, 'r') as f:
        quarto_content = f.read()
    # load the subject template file, that are txt
    with open(subject_template_path, 'r') as f:
        subject_template_content = f.read()
    
    # substitute the project name in the general template
    quarto_content = quarto_content.replace('[[[project_name]]]', config_dict['project_name'])
    # substitute the subjects in the general template
    quarto_content = quarto_content.replace('[[[subjects]]]', str(config_dict['subjects']))
    # substitute the date in the general template
    quarto_content = quarto_content.replace('[[[date]]]', date)

    # for each subject, substitute the subject and date and append to the content
    for subject in config_dict['subjects']:
        subject_content = subject_template_content.replace('[[[subject]]]', subject)
        subject_content = subject_content.replace('[[[project_name]]]', config_dict['project_name'])
        subject_content = subject_content.replace('[[[date]]]', date)

        # append the subject content to the general content
        quarto_content += '\n' + subject_content
    
    quarto_content += '\n' + ":::"

    # write the final content to a .qmd file
    config_file_name = Path(config_file).stem
    output_file = Path(__file__).parent.parent / "docs" / "quarto_files" / f"{config_file_name}_{date}.qmd"
    with open(output_file, 'w') as f:
        f.write(quarto_content)

if __name__ == "__main__":
    # Use fire to create a command line interface
    fire.Fire(generate_quarto_file)
    # Print a message indicating that the script has finished running
    print("Quarto file generation complete.")