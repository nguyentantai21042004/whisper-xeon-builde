#!/usr/bin/env python3
"""
Test script to verify VAD is disabled in whisper.cpp artifacts.

This script tests the built libwhisper.so to ensure:
1. Library loads correctly
2. Model loads correctly  
3. whisper_full() works without VAD errors

Usage:
    python test_vad_disabled.py [artifact_dir]
"""

import ctypes
import os
import sys
import math

# Constants from whisper.h
WHISPER_SAMPLE_RATE = 16000
WHISPER_SAMPLING_GREEDY = 0


def generate_test_audio(duration_sec=2.0, frequency=440.0):
    """Generate a simple sine wave audio for testing."""
    n_samples = int(WHISPER_SAMPLE_RATE * duration_sec)
    samples = []
    for i in range(n_samples):
        t = i / WHISPER_SAMPLE_RATE
        sample = 0.3 * math.sin(2 * math.pi * frequency * t)
        samples.append(sample)
    return (ctypes.c_float * n_samples)(*samples), n_samples


# Define whisper_full_params structure (simplified - key fields only)
# This matches the C struct layout for x86_64 Linux
class WhisperFullParams(ctypes.Structure):
    _fields_ = [
        ("strategy", ctypes.c_int),
        ("n_threads", ctypes.c_int),
        ("n_max_text_ctx", ctypes.c_int),
        ("offset_ms", ctypes.c_int),
        ("duration_ms", ctypes.c_int),
        
        ("translate", ctypes.c_bool),
        ("no_context", ctypes.c_bool),
        ("no_timestamps", ctypes.c_bool),
        ("single_segment", ctypes.c_bool),
        ("print_special", ctypes.c_bool),
        ("print_progress", ctypes.c_bool),
        ("print_realtime", ctypes.c_bool),
        ("print_timestamps", ctypes.c_bool),
        
        ("token_timestamps", ctypes.c_bool),
        ("_pad1", ctypes.c_byte * 3),  # padding
        ("thold_pt", ctypes.c_float),
        ("thold_ptsum", ctypes.c_float),
        ("max_len", ctypes.c_int),
        ("split_on_word", ctypes.c_bool),
        ("_pad2", ctypes.c_byte * 3),
        ("max_tokens", ctypes.c_int),
        
        ("debug_mode", ctypes.c_bool),
        ("_pad3", ctypes.c_byte * 3),
        ("audio_ctx", ctypes.c_int),
        
        ("tdrz_enable", ctypes.c_bool),
        ("_pad4", ctypes.c_byte * 7),
        
        ("suppress_regex", ctypes.c_char_p),
        ("initial_prompt", ctypes.c_char_p),
        ("carry_initial_prompt", ctypes.c_bool),
        ("_pad5", ctypes.c_byte * 7),
        ("prompt_tokens", ctypes.c_void_p),
        ("prompt_n_tokens", ctypes.c_int),
        ("_pad6", ctypes.c_byte * 4),
        
        ("language", ctypes.c_char_p),
        ("detect_language", ctypes.c_bool),
        
        ("suppress_blank", ctypes.c_bool),
        ("suppress_nst", ctypes.c_bool),
        ("_pad7", ctypes.c_byte * 5),
        
        ("temperature", ctypes.c_float),
        ("max_initial_ts", ctypes.c_float),
        ("length_penalty", ctypes.c_float),
        
        ("temperature_inc", ctypes.c_float),
        ("entropy_thold", ctypes.c_float),
        ("logprob_thold", ctypes.c_float),
        ("no_speech_thold", ctypes.c_float),
        
        ("greedy_best_of", ctypes.c_int),
        
        ("beam_size", ctypes.c_int),
        ("patience", ctypes.c_float),
        
        # Callbacks (all void pointers)
        ("new_segment_callback", ctypes.c_void_p),
        ("new_segment_callback_user_data", ctypes.c_void_p),
        ("progress_callback", ctypes.c_void_p),
        ("progress_callback_user_data", ctypes.c_void_p),
        ("encoder_begin_callback", ctypes.c_void_p),
        ("encoder_begin_callback_user_data", ctypes.c_void_p),
        ("abort_callback", ctypes.c_void_p),
        ("abort_callback_user_data", ctypes.c_void_p),
        ("logits_filter_callback", ctypes.c_void_p),
        ("logits_filter_callback_user_data", ctypes.c_void_p),
        
        ("grammar_rules", ctypes.c_void_p),
        ("n_grammar_rules", ctypes.c_size_t),
        ("i_start_rule", ctypes.c_size_t),
        ("grammar_penalty", ctypes.c_float),
        ("_pad8", ctypes.c_byte * 4),
        
        # VAD params - these are what we're testing
        ("vad", ctypes.c_bool),
        ("_pad9", ctypes.c_byte * 7),
        ("vad_model_path", ctypes.c_char_p),
        
        # whisper_vad_params struct
        ("vad_threshold", ctypes.c_float),
        ("vad_min_speech_duration_ms", ctypes.c_int),
        ("vad_min_silence_duration_ms", ctypes.c_int),
        ("vad_max_speech_duration_s", ctypes.c_float),
        ("vad_speech_pad_ms", ctypes.c_int),
        ("vad_samples_overlap", ctypes.c_float),
    ]


class WhisperTest:
    def __init__(self, artifact_dir):
        self.artifact_dir = os.path.abspath(artifact_dir)
        self.lib = None
        self.ctx = None
        
    def load_dependencies(self):
        """Load ggml dependencies first."""
        deps = ["libggml-base.so.0", "libggml-cpu.so.0", "libggml.so.0"]
        for dep in deps:
            dep_path = os.path.join(self.artifact_dir, dep)
            if os.path.exists(dep_path):
                try:
                    ctypes.CDLL(dep_path, mode=ctypes.RTLD_GLOBAL)
                    print(f"  ✓ Loaded dependency: {dep}")
                except Exception as e:
                    print(f"  ✗ Failed to load {dep}: {e}")
                    return False
        return True
    
    def load_library(self):
        """Load libwhisper.so."""
        lib_path = os.path.join(self.artifact_dir, "libwhisper.so")
        if not os.path.exists(lib_path):
            print(f"  ✗ Library not found: {lib_path}")
            return False
        
        try:
            self.lib = ctypes.CDLL(lib_path)
            print(f"  ✓ Loaded libwhisper.so")
            return True
        except Exception as e:
            print(f"  ✗ Failed to load libwhisper.so: {e}")
            return False
    
    def setup_functions(self):
        """Setup ctypes function signatures."""
        # whisper_init_from_file (deprecated but simpler)
        self.lib.whisper_init_from_file.restype = ctypes.c_void_p
        self.lib.whisper_init_from_file.argtypes = [ctypes.c_char_p]
        
        # whisper_full_default_params - returns struct by value
        self.lib.whisper_full_default_params.restype = WhisperFullParams
        self.lib.whisper_full_default_params.argtypes = [ctypes.c_int]
        
        # whisper_full - takes struct by value
        self.lib.whisper_full.restype = ctypes.c_int
        self.lib.whisper_full.argtypes = [
            ctypes.c_void_p,  # ctx
            WhisperFullParams,  # params (by value)
            ctypes.POINTER(ctypes.c_float),  # samples
            ctypes.c_int  # n_samples
        ]
        
        # whisper_full_n_segments
        self.lib.whisper_full_n_segments.restype = ctypes.c_int
        self.lib.whisper_full_n_segments.argtypes = [ctypes.c_void_p]
        
        # whisper_full_get_segment_text
        self.lib.whisper_full_get_segment_text.restype = ctypes.c_char_p
        self.lib.whisper_full_get_segment_text.argtypes = [ctypes.c_void_p, ctypes.c_int]
        
        # whisper_free
        self.lib.whisper_free.restype = None
        self.lib.whisper_free.argtypes = [ctypes.c_void_p]
        
        print("  ✓ Function signatures configured")
        return True
    
    def find_model(self):
        """Find the model file in artifact directory."""
        for f in os.listdir(self.artifact_dir):
            if f.endswith('.bin') and 'ggml' in f:
                return os.path.join(self.artifact_dir, f)
        return None
    
    def load_model(self):
        """Load whisper model."""
        model_path = self.find_model()
        if not model_path:
            print(f"  ✗ No model file found in {self.artifact_dir}")
            return False
        
        print(f"  Loading model: {os.path.basename(model_path)}")
        
        try:
            self.ctx = self.lib.whisper_init_from_file(model_path.encode('utf-8'))
        except Exception as e:
            print(f"  ✗ Exception loading model: {e}")
            return False
        
        if not self.ctx:
            print(f"  ✗ Failed to load model (ctx is NULL)")
            return False
        
        print(f"  ✓ Model loaded successfully")
        return True
    
    def test_transcription_vad_false(self):
        """Test transcription with VAD explicitly set to false."""
        print("\n  Testing whisper_full() with vad=false...")
        
        samples, n_samples = generate_test_audio(duration_sec=1.0)
        print(f"  Generated {n_samples} test samples ({n_samples/WHISPER_SAMPLE_RATE:.1f}s)")
        
        # Get default params
        params = self.lib.whisper_full_default_params(WHISPER_SAMPLING_GREEDY)
        
        # Explicitly set VAD to false
        params.vad = False
        params.vad_model_path = None
        
        print(f"  params.vad = {params.vad}")
        print("  Calling whisper_full()...")
        
        try:
            result = self.lib.whisper_full(self.ctx, params, samples, n_samples)
        except Exception as e:
            print(f"  ✗ Exception in whisper_full: {e}")
            return False
        
        if result != 0:
            print(f"  ✗ whisper_full returned error code: {result}")
            return False
        
        print(f"  ✓ whisper_full() returned success (code: {result})")
        
        n_segments = self.lib.whisper_full_n_segments(self.ctx)
        print(f"  ✓ Got {n_segments} segments")
        
        return True
    
    def test_transcription_vad_true(self):
        """Test transcription with VAD set to true - should work if VAD is disabled at compile time."""
        print("\n  Testing whisper_full() with vad=true (should work if VAD disabled at compile time)...")
        
        samples, n_samples = generate_test_audio(duration_sec=1.0)
        print(f"  Generated {n_samples} test samples ({n_samples/WHISPER_SAMPLE_RATE:.1f}s)")
        
        # Get default params
        params = self.lib.whisper_full_default_params(WHISPER_SAMPLING_GREEDY)
        
        # Set VAD to true - this would fail if VAD is enabled but model not found
        params.vad = True
        params.vad_model_path = None  # No model path
        
        print(f"  params.vad = {params.vad} (intentionally set to true)")
        print("  Calling whisper_full()...")
        
        try:
            result = self.lib.whisper_full(self.ctx, params, samples, n_samples)
        except Exception as e:
            print(f"  ✗ Exception in whisper_full: {e}")
            return False
        
        if result != 0:
            print(f"  ✗ whisper_full returned error code: {result}")
            if result == -1:
                print("    VAD error! This means VAD is NOT disabled at compile time.")
            return False
        
        print(f"  ✓ whisper_full() returned success even with vad=true!")
        print("    This confirms VAD code path is disabled at compile time.")
        
        n_segments = self.lib.whisper_full_n_segments(self.ctx)
        print(f"  ✓ Got {n_segments} segments")
        
        return True
    
    def cleanup(self):
        """Free resources."""
        if self.ctx:
            self.lib.whisper_free(self.ctx)
            self.ctx = None
    
    def run_all_tests(self):
        """Run all VAD disable verification tests."""
        print(f"\n{'='*60}")
        print(f"VAD Disable Verification Test")
        print(f"Artifact directory: {self.artifact_dir}")
        print(f"{'='*60}\n")
        
        tests = [
            ("Loading dependencies", self.load_dependencies),
            ("Loading library", self.load_library),
            ("Setting up functions", self.setup_functions),
            ("Loading model", self.load_model),
            ("Transcription with vad=false", self.test_transcription_vad_false),
            ("Transcription with vad=true (VAD bypass test)", self.test_transcription_vad_true),
        ]
        
        passed = 0
        failed = 0
        
        for test_name, test_func in tests:
            print(f"\n[TEST] {test_name}")
            try:
                if test_func():
                    passed += 1
                    print(f"  → PASSED")
                else:
                    failed += 1
                    print(f"  → FAILED")
                    if test_name in ["Loading library", "Loading model"]:
                        print("  Stopping tests due to critical failure")
                        break
            except Exception as e:
                failed += 1
                print(f"  → FAILED with exception: {e}")
                import traceback
                traceback.print_exc()
        
        self.cleanup()
        
        print(f"\n{'='*60}")
        print(f"Results: {passed} passed, {failed} failed")
        print(f"{'='*60}")
        
        if failed == 0:
            print("\n✓ All tests passed! VAD is properly disabled in this build.")
            return True
        else:
            print("\n✗ Some tests failed. Check output above for details.")
            return False


def main():
    if len(sys.argv) > 1:
        artifact_dir = sys.argv[1]
    else:
        artifact_dir = "artifacts/whisper_base_xeon"
    
    if not os.path.isdir(artifact_dir):
        print(f"Directory not found: {artifact_dir}")
        sys.exit(1)
    
    tester = WhisperTest(artifact_dir)
    success = tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
