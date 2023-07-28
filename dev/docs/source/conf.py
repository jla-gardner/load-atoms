# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "load-atoms"
copyright = "2023, John Gardner"
author = "John Gardner"
release = "0.0.14"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "nbsphinx",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
]
templates_path = ["_templates"]
exclude_patterns = []

intersphinx_mapping = {
    # ASE
    "ase": ("https://wiki.fysik.dtu.dk/ase/", None),
    # Python
    "python": ("https://docs.python.org/3", None),
    # NumPy
    "numpy": ("https://numpy.org/doc/stable/", None),
}

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "furo"
html_static_path = ["_static"]
html_logo = "logo.svg"

our_colour = "#ef9940"
html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": our_colour,
        "color-brand-content": our_colour,
    },
    "dark_css_variables": {
        "color-brand-primary": our_colour,
        "color-brand-content": our_colour,
    },
}

# Other stuff

copybutton_prompt_text = r">>> |\.\.\. |\$ "
copybutton_prompt_is_regexp = True
