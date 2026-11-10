from pathlib import Path
from typing import Optional, Union

import fire

def decide_which_setup_to_use():
    """
    Decides which setup to use for the temperature and humidity report.
    This is a placeholder function and should be implemented based on actual logic.
    
    Returns:
        str: The setup name to use.
    """
    # Placeholder implementation
    return "village01"

def decide_which_project_to_use():
    """
    Decides which project to use for the temperature and humidity report.
    This is a placeholder function and should be implemented based on actual logic.
    
    Returns:
        str: The project name to use.
    """
    # Placeholder implementation
    return "COT_cannula_GAD2_data"


def generate_temphum_quarto_file(date: str, docs_path: Optional[Union[str, Path]] = None) -> Path:
    """
    Generates the quarto file of the temperature and humidity report, in
    <docs_path>/temperature_and_humidity/ (docs_path defaults to the docs
    folder of this repository), and returns its path.
    """
    setup_name = decide_which_setup_to_use()
    quarto_template_general_path = Path(__file__).parent / 'quarto_templates' / 'temperature_humidity_general_template.txt'
    quarto_template_room_path = Path(__file__).parent / 'quarto_templates' / 'temperature_humidity_room_template.txt'
    room_names = ["Cellex 4A"]
    project_name = decide_which_project_to_use()

    # load the general template file, that are txt
    with open(quarto_template_general_path, 'r') as f:
        quarto_content = f.read()
    # load the room template file, that are txt
    with open(quarto_template_room_path, 'r') as f:
        room_template_content = f.read()
    # substitute the project name in the general template
    quarto_content = quarto_content.replace('[[[project_name]]]', project_name)
    # substitute the date in the general template
    quarto_content = quarto_content.replace('[[[date]]]', date)
    
    # for each room, substitute the room name and date and append to the content
    for room_name in room_names:
        room_content = room_template_content.replace('[[[room_name]]]', room_name)
        room_content = room_content.replace('[[[project_name]]]', project_name)
        room_content = room_content.replace('[[[date]]]', date)
        room_content = room_content.replace('[[[setup_name]]]', setup_name)

        # append the room content to the general content
        quarto_content += '\n' + room_content
    
    quarto_content += '\n' + ":::"

    # write the final content to a .qmd file
    docs_path = Path(docs_path) if docs_path is not None else Path(__file__).parent.parent / "docs"
    output_file = docs_path / "temperature_and_humidity" / "temperature_and_humidity.qmd"
    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(quarto_content)

    return output_file


if __name__ == "__main__":
    fire.Fire(generate_temphum_quarto_file)
    print("Temperature and humidity quarto file generation complete.")

