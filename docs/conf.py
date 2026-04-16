from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parent / "extensions"))

project = "oauthcord.py"
author = "Soheab"
description = "Typed async Discord OAuth2 wrapper for Python."

try:
    release = importlib.metadata.version("oauthcord.py")
except importlib.metadata.PackageNotFoundError:
    release = "0.0.0"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx_design",
    "scope_directive",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

autodoc_member_order = "bysource"
autodoc_typehints = "description"
autodoc_typehints_description_target = "documented_params"
napoleon_numpy_docstring = True
napoleon_use_ivar = True
autodoc_default_options = {"undoc-members": True, "show-inheritance": False}

html_title = project
html_theme = "shibuya"
html_theme_options = {
    "announcement": "Active development: public APIs may still change before the first stable release.",
    "accent_color": "sky",
    "dark_code": True,
    "globaltoc_expand_depth": 1,
    "github_url": "https://github.com/Soheab/oauthcord.py",
    "light_logo": "_static/logo.svg",
    "dark_logo": "_static/logo.svg",
    "nav_links": [
        {
            "title": "Reference",
            "url": "client",
            "children": [
                {
                    "title": "Client",
                    "url": "client",
                    "summary": "OAuth URLs, token exchange, and authorised sessions.",
                },
                {
                    "title": "Builders",
                    "url": "builders",
                    "summary": "Structured request builders for Discord payloads.",
                },
                {
                    "title": "Enums",
                    "url": "enums/_index",
                    "summary": "Grouped enum reference for serialized Discord values.",
                },
                {
                    "title": "Errors",
                    "url": "errors",
                    "summary": "Exception types raised by the wrapper.",
                },
                {
                    "title": "Utils",
                    "url": "utils",
                    "summary": "Shared conversion and helper utilities.",
                },
            ],
        },
        {
            "title": "Models",
            "url": "models/_index",
            "children": [
                {
                    "title": "Models",
                    "url": "models/_index",
                    "summary": "Browse every public model module separately.",
                },
                {
                    "title": "Types",
                    "url": "types/_index",
                    "summary": "Internal payload aliases and TypedDict response shapes.",
                },
            ],
        },
        {
            "title": "GitHub",
            "url": "https://github.com/Soheab/oauthcord.py",
            "external": True,
        },
    ],
    "nav_links_align": "center",
    "show_ai_links": True,
}
html_context = {
    "source_type": "github",
    "source_user": "Soheab",
    "source_repo": "oauthcord.py",
    "source_docs_path": "/docs/",
    "source_version": "main",
}
html_favicon = "_static/logo.svg"
html_sidebars = {
    "**": [
        "sidebars/localtoc.html",
        "sidebars/repo-stats.html",
        "sidebars/edit-this-page.html",
    ],
}
nitpick_ignore = [
    ("py:class", "type"),
    ("py:obj", "type"),
]
html_static_path = ["_static"]
html_css_files = ["custom.css"]

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "aiohttp": ("https://docs.aiohttp.org/en/stable/", None),
}
