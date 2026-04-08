"""Test configuration and fixtures for pyvista_x tests."""

import sys
from unittest.mock import MagicMock

import pytest


@pytest.fixture
def mock_pyvista():
    """Create a mock pyvista module for testing."""
    mock_pv = MagicMock()
    mock_pv.__name__ = "pyvista"
    mock_pv.__all__ = [
        "Plotter",
        "read",
        "wrap",
        "Actor",
        "UnstructuredGrid",
        "PolyData",
    ]
    mock_pv.Plotter = MagicMock
    mock_pv.read = MagicMock()
    mock_pv.wrap = MagicMock()
    mock_pv.Actor = MagicMock
    mock_pv.UnstructuredGrid = MagicMock
    mock_pv.PolyData = MagicMock
    mock_pv.StructuredGrid = MagicMock
    mock_pv.RectilinearGrid = MagicMock
    mock_pv.MultiBlock = MagicMock
    mock_pv.Texture = MagicMock
    mock_pv.Light = MagicMock
    mock_pv.Camera = MagicMock
    mock_pv.Color = MagicMock
    return mock_pv


@pytest.fixture
def mock_pyvista_js():
    """Create a mock pyvista_js module for testing."""
    mock_pv = MagicMock()
    mock_pv.__name__ = "pyvista_js"
    mock_pv.__all__ = [
        "Plotter",
        "read",
        "wrap",
    ]
    mock_pv.Plotter = MagicMock
    mock_pv.read = MagicMock()
    mock_pv.wrap = MagicMock()
    return mock_pv


@pytest.fixture
def mock_pyvista_wasm():
    """Create a mock pyvista_wasm module for testing."""
    mock_pv = MagicMock()
    mock_pv.__name__ = "pyvista_wasm"
    mock_pv.__all__ = [
        "Plotter",
        "read",
    ]
    mock_pv.Plotter = MagicMock
    mock_pv.read = MagicMock()
    return mock_pv


@pytest.fixture
def clean_module_cache():
    """Remove pyvista_x and backend modules from sys.modules to ensure fresh imports."""
    # Remove pyvista_x modules
    modules_to_remove = [key for key in sys.modules if key.startswith("pyvista_x")]
    # Also remove backend modules to ensure mocks are used
    backend_modules = ["pyvista", "pyvista_js", "pyvista_wasm"]
    for mod in list(sys.modules.keys()):
        if any(mod.startswith(backend) for backend in backend_modules):
            modules_to_remove.append(mod)
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]
    yield
    # Cleanup after test
    modules_to_remove = [key for key in sys.modules if key.startswith("pyvista_x")]
    for mod in modules_to_remove:
        if mod in sys.modules:
            del sys.modules[mod]
