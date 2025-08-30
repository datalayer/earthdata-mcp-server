"""
Tests for the earthdata-mcp-server composition functionality.

This package contains tests that validate the integration of earthdata
and jupyter MCP server tools through composition.
"""

from .test_composition import run_composition_validation

__all__ = ['run_composition_validation']
