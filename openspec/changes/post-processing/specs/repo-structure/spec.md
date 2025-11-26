# Spec: Repository Structure

## ADDED Requirements

### Requirement: Whitelist-based Pruning
The repository MUST be pruned using a whitelist strategy to retain only essential files for the Xeon builder workflow.

#### Scenario: Preserved Paths
The following paths MUST be preserved:
- `Dockerfile`
- `src/`
- `ggml/`
- `include/`
- `Makefile`
- `CMakeLists.txt`
- `.github/`
- `scripts/` (if applicable)
- `push_to_minio.py` (or `.sh`)
- `maintenance_prune.py`
- `.cursor` (and related config files)
- `.claude` (and related config files)
- `.agent` (and related config files)

### Requirement: Pruning Audit
The pruning process MUST provide visibility into what is being preserved and why.

#### Scenario: Logging
The `maintenance_prune.py` script MUST log each preserved file along with the whitelist rule that matched it (e.g., "Keeping src/whisper.cpp (Matched: src/)").

#### Scenario: Removed Paths
The following paths MUST be removed:
- `bindings/`
- `tests/`
- `samples/`
- `models/`
- `examples/` (except essential build dependencies if any)
