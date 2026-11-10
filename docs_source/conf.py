# Configuration file for the Sphinx documentation builder.
# Build locally with:  sphinx-build docs_source docs/documentation
# The GitHub action (.github/workflows/documentation.yml) also renders the
# reports of the sample data into _extra/sample_report/ before building, so
# that the site has an example report made with the current code.
import os
import sys

sys.path.insert(0, os.path.abspath(".."))

project = "village-report-generator"
copyright = "2025, Learning Circuits Lab"
author = "Hernando M Vergara"

extensions = [
    "sphinx.ext.napoleon",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.viewcode",
    "myst_parser",
]
myst_enable_extensions = ["colon_fence", "deflist", "linkify", "html_image"]
myst_heading_anchors = 3
templates_path = ["_templates"]
autosummary_generate = True
autodoc_mock_imports = ["pandas"]
add_module_names = False
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
exclude_patterns = ["_extra"]
# the example report rendered by the action, copied as it is
html_extra_path = ["_extra"] if os.path.isdir(os.path.join(os.path.dirname(__file__), "_extra")) else []

# same look as the Training Village documentation
html_theme = "shibuya"
html_title = "village-report-generator"
html_theme_options = {
    "color_mode": "light",
    "github_url": "https://github.com/LearningCircuitsLab/village-report-generator",
    "nav_links": [
        {"title": "Reports", "url": "https://learningcircuitslab.github.io/village-report-generator/"},
        {"title": "Example report", "url": "example"},
        {"title": "Analysis package", "url": "https://learningcircuitslab.github.io/lecilab-behavior-analysis/"},
    ],
}
