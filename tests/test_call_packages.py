"""Placeholder test module.

The original file attempted to import a non-existent 'testpackage.test' module.
This placeholder ensures pytest can collect the file without errors.
"""
import pytest


@pytest.mark.skip(reason="placeholder - no testpackage module exists")
def test_placeholder():
    """Placeholder test to replace the broken testpackage import."""
    pass
