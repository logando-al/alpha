"""Utility functions for resource path resolution."""
import sys
from pathlib import Path


def get_resource_path(relative_path: str) -> Path:
    """
    Get the absolute path to a resource, works for dev and PyInstaller bundles.
    
    When running from source, resources are relative to the project root.
    When packaged with PyInstaller, resources are extracted to sys._MEIPASS.
    """
    if hasattr(sys, '_MEIPASS'):
        # PyInstaller bundled app
        base_path = Path(sys._MEIPASS)
    else:
        # Running from source - project root is parent of 'alpha' package
        base_path = Path(__file__).parent.parent
    
    return base_path / relative_path
