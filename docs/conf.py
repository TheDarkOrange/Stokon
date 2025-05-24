import os
import sys
sys.path.insert(0, os.path.abspath('../src'))

project = 'Daily Equities Trading System'
author = 'Your Name'
release = '1.0.0'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinxcontrib.mermaid',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'alabaster'
