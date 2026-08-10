"""Compatibility shim for notebook imports.

The cadquery-simpleviewer package exposes module `cadquery_simpleviewer`.
Course notebooks import `cadquery_simple_viewer`, so this file bridges both.
"""

from cadquery_simpleviewer import *  # noqa: F401,F403
