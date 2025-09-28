import os
import sys
sys.path.insert(0, os.path.abspath('..'))

project = 'AstroSaveConverter'
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.autosummary',
]
templates_path = ['_templates']
exclude_patterns = []

autosummary_generate = True
html_theme = 'sphinx_rtd_theme'
