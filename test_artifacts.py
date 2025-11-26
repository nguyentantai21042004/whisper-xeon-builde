import ctypes
import os
import sys


def test_library_loading(lib_path):
    print(f"Testing library loading: {lib_path}")
    if not os.path.exists(lib_path):
        print(f"Error: Library file not found at {lib_path}")
        return False

    try:
        lib = ctypes.CDLL(lib_path)
        print("Success: Library loaded via ctypes.")
        return True
    except Exception as e:
        print(f"Error loading library: {e}")
        return False


def main():
    base_dir = os.path.abspath("artifacts")

    # Test Small Model Artifacts
    small_dir = os.path.join(base_dir, "whisper_small_xeon")
    small_lib = os.path.join(small_dir, "libwhisper.so")

    # Pre-load dependencies in order
    deps = ["libggml-base.so.0", "libggml-cpu.so.0", "libggml.so.0"]
    for dep in deps:
        dep_path = os.path.join(small_dir, dep)
        if os.path.exists(dep_path):
            try:
                ctypes.CDLL(dep_path, mode=ctypes.RTLD_GLOBAL)
                print(f"Pre-loaded dependency: {dep}")
            except Exception as e:
                print(f"Warning: Failed to pre-load {dep}: {e}")

    if not test_library_loading(small_lib):
        sys.exit(1)

    # Test Medium Model Artifacts
    medium_dir = os.path.join(base_dir, "whisper_medium_xeon")
    medium_lib = os.path.join(medium_dir, "libwhisper.so")

    # Pre-load dependencies
    for dep in deps:
        dep_path = os.path.join(medium_dir, dep)
        if os.path.exists(dep_path):
            try:
                ctypes.CDLL(dep_path, mode=ctypes.RTLD_GLOBAL)
            except Exception as e:
                print(f"Warning: Failed to pre-load {dep}: {e}")

    if not test_library_loading(medium_lib):
        sys.exit(1)

    print("\nAll artifact library tests passed!")


if __name__ == "__main__":
    main()
