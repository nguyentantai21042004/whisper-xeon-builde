# Implementation Tasks

## 1. Repository Pruning

- [ ] 1.1 Create `maintenance_prune.py` script
    - [ ] Define whitelist (Dockerfile, src, ggml, include, build configs, scripts, .cursor, .claude, .agent)
    - [ ] Implement recursive deletion logic for non-whitelisted items
    - [ ] Implement **logging mechanism** to print "Keeping <file> (Reason: <rule>)" for every preserved file
    - [ ] Implement dry-run mode to preview changes before deletion
    - [ ] Preserve `examples/quantize` and `examples/main` source files if feasible, or just essential build deps
    - [ ] Fixed: Added whitelist for bindings/javascript/package-tmpl.json (required by CMakeLists.txt)
    - [ ] Fixed: Updated Dockerfile to disable tests building (-DWHISPER_BUILD_TESTS=OFF)
    - [ ] Fixed: Created minimal bindings structure to satisfy CMake requirements
- [ ] 1.2 Execute pruning script
    - [ ] Run script to clean up repository (ready to execute - tested in dry-run mode)
    - [ ] Verify essential files remain and project still builds (Docker build verified working)
- [ ] 1.3 Commit cleanup changes
    - [ ] Commit with message "chore: prune unused sources for xeon builder focus"

## 2. Documentation Overhaul

- [ ] 2.1 Backup/Remove old README.md
- [ ] 2.2 Create new `README.md`
    - [ ] Title: Whisper Xeon Builder
    - [ ] Project Goal: Build and package Whisper for Intel Xeon
    - [ ] Pipeline Diagram: Code -> Docker -> Artifacts -> MinIO
    - [ ] Usage: Docker build, artifact extraction, MinIO config
    - [ ] Structure: Explanation of output artifacts

## 3. Verification

- [ ] 3.1 Verify Docker build still works after pruning
- [ ] 3.2 Verify `push_to_minio.sh` (or py) still works
- [ ] 3.3 Verify README instructions are accurate
