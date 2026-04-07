# pyvista-x

A library that provides switching between multiple PyVista backends:

- **pyvista** - The standard desktop 3D visualization library
- **pyvista-js** - JavaScript-based visualization for Pyodide environment
- **pyvista-wasm** - WebAssembly-based visualization for Pyodide environment

This library automatically selects the appropriate backend based on the environment and available dependencies.
