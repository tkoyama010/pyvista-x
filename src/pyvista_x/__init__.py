"""PyVista-X: A library that provides switching between multiple PyVista backends.

This module automatically selects the appropriate backend based on the environment:
- pyvista: Standard desktop 3D visualization library
- pyvista-js: JavaScript-based visualization for Pyodide environment
- pyvista-wasm: WebAssembly-based visualization for Pyodide environment
"""

import sys
import types
from typing import Any


def _is_wasm_environment() -> bool:
    """Check if running in a WebAssembly/Pyodide environment."""
    return sys.platform == "emscripten" or "wasm" in sys.platform.lower()


def _load_backend() -> types.ModuleType:
    """Load the appropriate PyVista backend based on environment."""
    errors = []

    # Try WASM backends first if in WASM environment
    if _is_wasm_environment():
        # Try pyvista-js first (JavaScript backend)
        try:
            import pyvista_js

            return pyvista_js  # type: ignore[no-any-return]
        except ImportError as e:
            errors.append(f"pyvista-js: {e}")

        # Try pyvista-wasm next (WebAssembly backend)
        try:
            import pyvista_wasm

            return pyvista_wasm  # type: ignore[no-any-return]
        except ImportError as e:
            errors.append(f"pyvista-wasm: {e}")

    # Try standard pyvista (desktop/backend)
    try:
        import pyvista

        return pyvista  # type: ignore[no-any-return]
    except ImportError as e:
        errors.append(f"pyvista: {e}")

    # If we get here, no backend could be loaded
    raise ImportError(
        "Could not load any PyVista backend. "
        f"Errors: {'; '.join(errors)}. "
        "Please install pyvista, pyvista-js, or pyvista-wasm."
    )


# Load the appropriate backend
_pv = _load_backend()

# Re-export all public attributes from the loaded backend
__all__ = getattr(_pv, "__all__", [])
if not __all__:
    # If __all__ is not defined, export all non-private attributes
    __all__ = [name for name in dir(_pv) if not name.startswith("_")]


# Dynamically re-export all attributes from the backend module
def __getattr__(name: str) -> Any:
    """Lazy load attributes from the backend module."""
    return getattr(_pv, name)


def __dir__() -> list[str]:
    """Return list of available attributes."""
    return sorted(set(dir(_pv) + list(globals().keys())))


# Explicitly re-export commonly used functions and classes
# These will be available when doing: import pyvista_x as pv
Plotter = _pv.Plotter
read = _pv.read
wrap = _pv.wrap
Actor = _pv.Actor
UnstructuredGrid = _pv.UnstructuredGrid
PolyData = _pv.PolyData
StructuredGrid = _pv.StructuredGrid
RectilinearGrid = _pv.RectilinearGrid
MultiBlock = _pv.MultiBlock
Texture = _pv.Texture
Light = _pv.Light
Camera = _pv.Camera
Color = _pv.Color

# Version info
__version__ = "0.2.0"
__backend__ = _pv.__name__
