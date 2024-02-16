from __future__ import annotations

project = "load-atoms"
copyright = "2024, John Gardner"
author = "John Gardner"
release = "0.1.7"


extensions = [
    "sphinx.ext.duration",
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "nbsphinx",
    "sphinx.ext.mathjax",
    "sphinx.ext.napoleon",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
    "sphinx_design",
    "sphinx.ext.viewcode",
    "sphinx_codeautolink",
]


intersphinx_mapping = {
    "ase": ("https://wiki.fysik.dtu.dk/ase/", None),
    "python": ("https://docs.python.org/3", None),
    "numpy": ("https://numpy.org/doc/stable/", None),
}


html_theme = "furo"
html_static_path = ["_static"]
html_logo = "logo.svg"

blue = "#5599ff"
red = "#ff5555"

html_theme_options = {
    "sidebar_hide_name": True,
    "light_css_variables": {
        "color-brand-primary": blue,
        "color-brand-content": blue,
        "color-problematic": red,
    },
    "dark_css_variables": {
        "color-brand-primary": blue,
        "color-brand-content": blue,
        "color-problematic": red,
    },
}
# autodoc_typehints = "description"
autodoc_member_order = "bysource"
html_title = "load-atoms"

pygments_dark_style = "monokai"
html_css_files = ["custom.css"]
html_favicon = "favicon.svg"
