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

# Common attributes that should be available from backends
# Access these via __getattr__ below to avoid lazy_loader timing issues
_COMMON_ATTRS = [
    "Plotter",
    "read",
    "wrap",
    "Actor",
    "UnstructuredGrid",
    "PolyData",
    "StructuredGrid",
    "RectilinearGrid",
    "MultiBlock",
    "Texture",
    "Light",
    "Camera",
    "Color",
]

# Re-export all public attributes from the loaded backend
__all__ = getattr(_pv, "__all__", [])
if not __all__:
    # If __all__ is not defined, export all non-private attributes
    __all__ = [name for name in dir(_pv) if not name.startswith("_")]

# Ensure common attributes are included in __all__ for documentation
for _attr in _COMMON_ATTRS:
    if _attr not in __all__:
        __all__.append(_attr)


# Dynamically re-export all attributes from the backend module
def __getattr__(name: str) -> Any:
    """Lazy load attributes from the backend module."""
    return getattr(_pv, name)


def __dir__() -> list[str]:
    """Return list of available attributes."""
    return sorted(set(dir(_pv) + list(globals().keys()) + _COMMON_ATTRS))


# Version info
__version__ = "0.2.0"
__backend__ = _pv.__name__
