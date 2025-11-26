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

#### Scenario: Removed Paths
The following paths MUST be removed:
- `bindings/`
- `tests/`
- `samples/`
- `models/`
- `examples/` (except essential build dependencies if any)
