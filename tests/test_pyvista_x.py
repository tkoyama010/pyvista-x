"""Tests for pyvista_x module initialization and backend loading."""

from unittest.mock import MagicMock, patch

import pytest


class TestWasmEnvironmentDetection:
    """Tests for _is_wasm_environment function."""

    def test_detects_emscripten_platform(self, mock_pyvista_js):
        """Test that emscripten platform is detected as WASM."""
        with patch("sys.platform", "emscripten"):
            with patch.dict("sys.modules", {"pyvista_js": mock_pyvista_js}):
                # Need to reimport after patching
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x._is_wasm_environment() is True

    def test_detects_wasm_in_platform(self, mock_pyvista_js):
        """Test that platforms containing 'wasm' are detected."""
        with patch("sys.platform", "wasm32"):
            with patch.dict("sys.modules", {"pyvista_js": mock_pyvista_js}):
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x._is_wasm_environment() is True

    def test_non_wasm_platform(self, mock_pyvista):
        """Test that regular platforms are not detected as WASM."""
        with patch("sys.platform", "linux"):
            with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x._is_wasm_environment() is False

    def test_windows_platform(self, mock_pyvista):
        """Test that Windows platform is not detected as WASM."""
        with patch("sys.platform", "win32"):
            with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x._is_wasm_environment() is False

    def test_darwin_platform(self, mock_pyvista):
        """Test that macOS platform is not detected as WASM."""
        with patch("sys.platform", "darwin"):
            with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x._is_wasm_environment() is False


class TestBackendLoading:
    """Tests for _load_backend function."""

    def test_loads_standard_pyvista_on_non_wasm(self, mock_pyvista):
        """Test that standard pyvista is loaded on non-WASM platforms."""
        with patch("sys.platform", "linux"):
            with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)
                assert pyvista_x.__backend__ == "pyvista"

    def test_loads_pyvista_js_in_wasm_first(self, mock_pyvista_js):
        """Test that pyvista_js is tried first in WASM environment."""
        with (
            patch("sys.platform", "emscripten"),
            patch.dict(
                "sys.modules",
                {"pyvista_js": mock_pyvista_js},
            ),
        ):
            import importlib

            import pyvista_x

            importlib.reload(pyvista_x)
            assert pyvista_x.__backend__ == "pyvista_js"

    def test_loads_pyvista_wasm_when_js_unavailable(self, mock_pyvista_wasm):
        """Test fallback to pyvista_wasm when pyvista_js is not available."""
        # Mock pyvista_js to None to force ImportError and test fallback to pyvista_wasm
        with (
            patch("sys.platform", "emscripten"),
            patch.dict(
                "sys.modules",
                {"pyvista_js": None, "pyvista_wasm": mock_pyvista_wasm},
            ),
        ):
            import importlib

            import pyvista_x

            importlib.reload(pyvista_x)
            assert pyvista_x.__backend__ == "pyvista_wasm"

    def test_raises_error_when_no_backend_available(self):
        """Test that ImportError is raised when no backend can be loaded."""
        # Mock all backends to None to force ImportError
        with (
            patch("sys.platform", "linux"),
            patch.dict(
                "sys.modules",
                {"pyvista": None, "pyvista_js": None, "pyvista_wasm": None},
            ),
        ):
            with pytest.raises(ImportError) as exc_info:
                import importlib

                import pyvista_x

                importlib.reload(pyvista_x)

            assert "Could not load any PyVista backend" in str(exc_info.value)

    def test_fallback_to_standard_pyvista_in_wasm(self, mock_pyvista):
        """Test that standard pyvista is used in WASM if JS backends unavailable."""
        with (
            patch("sys.platform", "emscripten"),
            patch.dict(
                "sys.modules",
                {"pyvista": mock_pyvista, "pyvista_js": None, "pyvista_wasm": None},
            ),
        ):
            import importlib

            import pyvista_x

            importlib.reload(pyvista_x)
            assert pyvista_x.__backend__ == "pyvista"


class TestModuleExports:
    """Tests for module exports and re-exports."""

    def test_version_is_defined(self, mock_pyvista, clean_module_cache):
        """Test that __version__ is defined."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            assert hasattr(pyvista_x, "__version__")
            assert pyvista_x.__version__ == "0.2.1"

    def test_backend_info_is_defined(self, mock_pyvista, clean_module_cache):
        """Test that __backend__ is defined."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            assert hasattr(pyvista_x, "__backend__")
            assert pyvista_x.__backend__ == "pyvista"

    def test_common_classes_exported(self, mock_pyvista, clean_module_cache):
        """Test that common classes are explicitly exported."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            assert hasattr(pyvista_x, "Plotter")
            assert hasattr(pyvista_x, "Actor")
            assert hasattr(pyvista_x, "UnstructuredGrid")
            assert hasattr(pyvista_x, "PolyData")
            assert hasattr(pyvista_x, "StructuredGrid")
            assert hasattr(pyvista_x, "RectilinearGrid")
            assert hasattr(pyvista_x, "MultiBlock")
            assert hasattr(pyvista_x, "Texture")
            assert hasattr(pyvista_x, "Light")
            assert hasattr(pyvista_x, "Camera")
            assert hasattr(pyvista_x, "Color")

    def test_common_functions_exported(self, mock_pyvista, clean_module_cache):
        """Test that common functions are explicitly exported."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            assert hasattr(pyvista_x, "read")
            assert hasattr(pyvista_x, "wrap")

    def test_dir_returns_attributes(self, mock_pyvista, clean_module_cache):
        """Test that __dir__ returns expected attributes."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            dir_result = pyvista_x.__dir__()
            assert "Plotter" in dir_result
            assert "read" in dir_result
            assert "__version__" in dir_result
            assert "__backend__" in dir_result

    def test_getattr_loads_backend_attributes(self, mock_pyvista, clean_module_cache):
        """Test that __getattr__ can load attributes from backend."""
        mock_pyvista.new_attribute = "test_value"
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            assert pyvista_x.new_attribute == "test_value"


class TestAllExports:
    """Tests for __all__ exports."""

    def test_all_contains_common_items(self, mock_pyvista, clean_module_cache):
        """Test that __all__ contains expected common items."""
        with patch.dict("sys.modules", {"pyvista": mock_pyvista}):
            import pyvista_x

            expected_items = ["Plotter", "read", "wrap", "Actor"]
            for item in expected_items:
                assert item in pyvista_x.__all__

    def test_all_from_backend_when_defined(self, clean_module_cache):
        """Test that __all__ uses backend's __all__ when available."""
        mock_pv = MagicMock()
        mock_pv.__name__ = "pyvista"
        mock_pv.__all__ = ["custom_item1", "custom_item2"]
        mock_pv.custom_item1 = MagicMock()
        mock_pv.custom_item2 = MagicMock()

        with patch.dict("sys.modules", {"pyvista": mock_pv}):
            import pyvista_x

            assert "custom_item1" in pyvista_x.__all__
            assert "custom_item2" in pyvista_x.__all__
