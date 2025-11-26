import os
import shutil
import argparse
import sys

# Configuration
WHITELIST_ROOT_FILES = [
    "Dockerfile",
    "Makefile",
    "CMakeLists.txt",
    "maintenance_prune.py",
    "push_to_minio.sh",
    "README.md",
    "LICENSE",
    "AUTHORS",
    "CLAUDE.md",
    "BUILD_ARTIFACTS_USAGE.md",
    "PRUNING_FIXES.md",
    "BUILD_FIX_SUMMARY.md",
    "COMPLETE_WORKFLOW.md",
    ".gitignore",
    ".dockerignore",
    ".gitmodules",
]

WHITELIST_ROOT_DIRS = [
    "src",
    "ggml",
    "include",
    ".github",
    "scripts",
    ".git",
    ".cursor",
    ".claude",
    ".agent",
    ".devops",
    "cmake",
    "openspec",
]

# Specific whitelist rules for subdirectories
WHITELIST_PATTERNS = {
    "examples": [
        "examples/quantize",
        "examples/common.cpp",
        "examples/common.h",
        "examples/common-ggml.cpp",
        "examples/common-ggml.h",
        "examples/CMakeLists.txt",
    ],
    "models": [
        "models/download-ggml-model.sh",
        "models/download-ggml-model.cmd",
        "models/.gitignore",
    ],
    "bindings": ["bindings/javascript/package-tmpl.json"],
}


def is_whitelisted(path, root_dir):
    rel_path = os.path.relpath(path, root_dir)

    # Check root files
    if os.path.dirname(rel_path) == "":
        if rel_path in WHITELIST_ROOT_FILES:
            return f"Root whitelist file: {rel_path}"
        return None

    # Check root directories
    top_level_dir = rel_path.split(os.sep)[0]
    if top_level_dir in WHITELIST_ROOT_DIRS:
        return f"Root whitelist directory: {top_level_dir}"

    # Check specific patterns
    for pattern_key, patterns in WHITELIST_PATTERNS.items():
        if rel_path.startswith(pattern_key):
            # Check if the path matches any of the specific patterns
            # We need to handle both exact matches (files) and directory prefixes
            for pattern in patterns:
                if rel_path == pattern or rel_path.startswith(pattern + os.sep):
                    return f"Essential file/dir: {pattern}"

            # Special case: keep the parent directory itself if it contains whitelisted items
            # But we don't want to keep *everything* in it, just the directory structure
            # This logic is handled by the walker: if we are visiting a directory, we check if it *contains* whitelisted items?
            # Actually, simpler: if the directory itself is in the whitelist keys (e.g. "examples"), we don't delete the directory *itself*,
            # but we filter its contents.
            if rel_path == pattern_key:
                return f"Parent directory of whitelisted items: {pattern_key}"

    return None


def prune_repository(root_dir, dry_run=False):
    print(f"Pruning repository at: {root_dir}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print("-" * 40)

    items_kept = 0
    items_removed = 0

    # Walk top-down so we can prune directories
    for root, dirs, files in os.walk(root_dir, topdown=True):
        # Skip .git directory traversal
        if ".git" in dirs:
            dirs.remove(".git")

        # Process files
        for file in files:
            file_path = os.path.join(root, file)
            reason = is_whitelisted(file_path, root_dir)

            if reason:
                print(
                    f"✓ Keeping: {os.path.relpath(file_path, root_dir)} (Reason: {reason})"
                )
                items_kept += 1
            else:
                print(f"✗ Removing: {os.path.relpath(file_path, root_dir)}")
                if not dry_run:
                    os.remove(file_path)
                items_removed += 1

        # Process directories
        # We need to modify 'dirs' in-place to prevent walking into pruned directories
        dirs_to_remove = []
        for d in dirs:
            dir_path = os.path.join(root, d)
            reason = is_whitelisted(dir_path, root_dir)

            # Special check: if a directory is NOT explicitly whitelisted,
            # but it is a parent of a whitelisted item (e.g. 'examples' or 'bindings'), we must keep it
            # but continue traversing to prune its siblings.
            # The is_whitelisted function handles 'examples' key check.

            if not reason:
                # Check if this directory is a parent of any specific whitelist pattern
                rel_path = os.path.relpath(dir_path, root_dir)
                is_parent = False
                for patterns in WHITELIST_PATTERNS.values():
                    for pattern in patterns:
                        if pattern.startswith(rel_path + os.sep):
                            is_parent = True
                            reason = f"Parent of whitelisted item: {pattern}"
                            break
                    if is_parent:
                        break

            if reason:
                print(
                    f"✓ Keeping: {os.path.relpath(dir_path, root_dir)} (Reason: {reason})"
                )
                items_kept += 1
            else:
                print(f"✗ Removing directory: {os.path.relpath(dir_path, root_dir)}")
                if not dry_run:
                    shutil.rmtree(dir_path)
                items_removed += 1
                dirs_to_remove.append(d)

        for d in dirs_to_remove:
            dirs.remove(d)

    print("-" * 40)
    print(f"Summary: Kept {items_kept}, Removed {items_removed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Prune repository to essential files.")
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview changes without deleting."
    )
    args = parser.parse_args()

    prune_repository(os.getcwd(), dry_run=args.dry_run)
