"""Integration-style tests for pyvista_x in different scenarios."""

import sys
from unittest.mock import MagicMock, patch

import pytest


class TestRealWorldScenarios:
    """Tests that simulate real-world usage scenarios."""

    def test_import_works_with_standard_pyvista(self):
        """Test that 'import pyvista_x as pv' works with standard pyvista."""
        mock_pv = MagicMock()
        mock_pv.__name__ = "pyvista"
        mock_pv.__all__ = []
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

        with patch("sys.platform", "linux"):
            with patch.dict("sys.modules", {"pyvista": mock_pv}):
                # Remove pyvista_x from cache to ensure fresh import
                modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pyvista_x")]
                for mod in modules_to_remove:
                    del sys.modules[mod]

                import pyvista_x as pv

                # Test that common operations work
                assert hasattr(pv, "Plotter")
                assert hasattr(pv, "read")
                assert hasattr(pv, "wrap")
                assert pv.__backend__ == "pyvista"

    def test_wasm_environment_priority(self):
        """Test WASM environment correctly prioritizes JS backends."""
        mock_js = MagicMock()
        mock_js.__name__ = "pyvista_js"
        mock_js.__all__ = []
        mock_js.Plotter = MagicMock
        mock_js.read = MagicMock()

        mock_wasm = MagicMock()
        mock_wasm.__name__ = "pyvista_wasm"
        mock_wasm.__all__ = []
        mock_wasm.Plotter = MagicMock
        mock_wasm.read = MagicMock()

        with patch("sys.platform", "emscripten"):
            with patch.dict(
                "sys.modules",
                {"pyvista_js": mock_js, "pyvista_wasm": mock_wasm},
            ):
                modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pyvista_x")]
                for mod in modules_to_remove:
                    del sys.modules[mod]

                import pyvista_x as pv

                # Should prefer pyvista_js over pyvista_wasm
                assert pv.__backend__ == "pyvista_js"

    def test_graceful_fallback_in_wasm(self):
        """Test graceful fallback to standard pyvista when JS backends fail."""
        mock_pv = MagicMock()
        mock_pv.__name__ = "pyvista"
        mock_pv.__all__ = []
        mock_pv.Plotter = MagicMock
        mock_pv.read = MagicMock()

        with patch("sys.platform", "emscripten"):
            with patch.dict("sys.modules", {"pyvista": mock_pv}):
                modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pyvista_x")]
                for mod in modules_to_remove:
                    del sys.modules[mod]

                import pyvista_x as pv

                # Should fallback to standard pyvista
                assert pv.__backend__ == "pyvista"

    def test_error_message_on_complete_failure(self):
        """Test that error message is helpful when no backends available."""
        with patch("sys.platform", "linux"):
            # Clear all pyvista-related modules
            modules_to_clear = {
                k: v
                for k, v in sys.modules.items()
                if k not in ["pyvista", "pyvista_js", "pyvista_wasm"]
            }

            with patch.dict("sys.modules", modules_to_clear, clear=True):
                modules_to_remove = [k for k in sys.modules.keys() if k.startswith("pyvista_x")]
                for mod in modules_to_remove:
                    if mod in sys.modules:
                        del sys.modules[mod]

                with pytest.raises(ImportError) as exc_info:
                    import pyvista_x
                    import importlib

                    importlib.reload(pyvista_x)

                error_msg = str(exc_info.value)
                assert "Could not load any PyVista backend" in error_msg
                assert "pyvista" in error_msg
                assert "pyvista-js" in error_msg or "pyvista_js" in error_msg
                assert "pyvista-wasm" in error_msg or "pyvista_wasm" in error_msg
