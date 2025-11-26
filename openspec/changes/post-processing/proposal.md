# Change: Repository Pruning & Documentation Update

## Why
The current repository contains a significant amount of unused code, bindings, examples, and documentation inherited from the original `whisper.cpp` project. This creates noise and confusion, as the primary purpose of this fork is to serve as a specialized "Whisper Xeon Builder" for orchestration and artifact generation.

## What Changes
- **Repository Pruning**: Implement a "whitelist" strategy to remove all non-essential files and directories.
    - **Keep**: `Dockerfile`, `src/`, `ggml/`, `include/`, `Makefile`, `CMakeLists.txt`, `.github/`, and essential scripts.
    - **Remove**: `bindings/`, `tests/`, `samples/`, `models/`, and most `examples/`.
- **Automation**: Create `maintenance_prune.py` to automate the cleanup process.
- **Documentation Overhaul**: Replace the existing `README.md` with a concise, purpose-driven guide focusing on the build and deployment pipeline.

## Impact
- **Affected specs**: `repo-structure` (new), `documentation` (new)
- **Affected code**:
    - **Delete**: Large portions of the codebase (`bindings/`, `tests/`, `samples/`).
    - **Modify**: `README.md`.
    - **New**: `maintenance_prune.py`.
- **Dependencies**: None.
- **Deliverables**: A lean repository structure and updated documentation.
