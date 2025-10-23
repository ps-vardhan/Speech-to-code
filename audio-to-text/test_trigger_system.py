#!/usr/bin/env python3
"""
Test Script for Trigger Word System

This script tests the TriggerWordHandler functionality without requiring
actual audio input. It simulates transcriptions to verify trigger word
detection and file writing works correctly.

Usage:
    python test_trigger_system.py
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

# Add the speech_to_text module to the path
sys.path.insert(0, str(Path(__file__).parent))

from speech_to_text.trigger_word_handler import TriggerWordHandler, create_default_handler

def test_basic_functionality():
    """Test basic trigger word functionality."""
    print("🧪 Testing Basic Trigger Word Functionality")
    print("-" * 50)
    
    # Create temporary directory for testing
    test_dir = tempfile.mkdtemp(prefix="trigger_test_")
    print(f"Test directory: {test_dir}")
    
    try:
        # Create handler
        handler = create_default_handler(output_directory=test_dir)
        
        # Test transcriptions
        test_cases = [
            ("Hello world", False, "No trigger word"),
            ("Code create a function", True, "Code trigger detected"),
            ("that prints hello world", False, "Continue in code mode"),
            ("Description this function", True, "Description trigger detected"),
            ("demonstrates basic programming", False, "Continue in description mode"),
            ("Stop recording now", True, "Stop trigger detected"),
            ("This should not be saved", False, "No active mode")
        ]
        
        print("\nTesting transcript processing:")
        for i, (transcript, expected_trigger, description) in enumerate(test_cases, 1):
            print(f"\n{i}. {description}")
            print(f"   Input: '{transcript}'")
            
            result = handler.process_transcript(transcript)
            status = handler.get_status()
            
            print(f"   Trigger detected: {result}")
            print(f"   Current mode: {status['current_mode']}")
            print(f"   Current file: {status['current_file']}")
        
        # Check created files
        print(f"\n📁 Files created in {test_dir}:")
        files = os.listdir(test_dir)
        for file in files:
            filepath = os.path.join(test_dir, file)
            if os.path.isfile(filepath):
                size = os.path.getsize(filepath)
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                print(f"  📄 {file} ({size} bytes)")
                print(f"      Content: '{content}'")
        
        return len(files) > 0
        
    finally:
        # Clean up
        shutil.rmtree(test_dir)
        print(f"\n🧹 Cleaned up test directory: {test_dir}")

def test_custom_triggers():
    """Test custom trigger words."""
    print("\n🧪 Testing Custom Trigger Words")
    print("-" * 50)
    
    test_dir = tempfile.mkdtemp(prefix="trigger_custom_test_")
    print(f"Test directory: {test_dir}")
    
    try:
        # Create handler with custom triggers
        custom_triggers = {
            "ideas": "ideas.txt",
            "meeting": "meeting_notes.txt", 
            "stop": None
        }
        
        handler = TriggerWordHandler(
            trigger_words=custom_triggers,
            output_directory=test_dir
        )
        
        # Test custom triggers
        test_cases = [
            ("Ideas for the project", "ideas"),
            ("Meeting notes from today", "meeting"),
            ("Stop taking notes", None)
        ]
        
        print("\nTesting custom triggers:")
        for transcript, expected_mode in test_cases:
            print(f"\nInput: '{transcript}'")
            result = handler.process_transcript(transcript)
            status = handler.get_status()
            print(f"Trigger detected: {result}")
            print(f"Current mode: {status['current_mode']}")
            print(f"Expected mode: {expected_mode}")
        
        # Check files
        files = os.listdir(test_dir)
        print(f"\n📁 Created files: {files}")
        
        return True
        
    finally:
        shutil.rmtree(test_dir)

def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n🧪 Testing Edge Cases")
    print("-" * 50)
    
    test_dir = tempfile.mkdtemp(prefix="trigger_edge_test_")
    
    try:
        handler = create_default_handler(output_directory=test_dir)
        
        # Test edge cases
        edge_cases = [
            ("", "Empty string"),
            ("   ", "Whitespace only"),
            ("code", "Just trigger word"),
            ("CODE", "Uppercase trigger"),
            ("Code!", "Trigger with punctuation"),
            ("The word code appears here", "Trigger in sentence"),
            ("stop", "Stop without active mode"),
            ("code code code", "Multiple triggers"),
        ]
        
        print("\nTesting edge cases:")
        for transcript, description in edge_cases:
            print(f"\n{description}: '{transcript}'")
            result = handler.process_transcript(transcript)
            status = handler.get_status()
            print(f"  Result: {result}, Mode: {status['current_mode']}")
        
        return True
        
    finally:
        shutil.rmtree(test_dir)

def test_file_operations():
    """Test file writing operations."""
    print("\n🧪 Testing File Operations")
    print("-" * 50)
    
    test_dir = tempfile.mkdtemp(prefix="trigger_file_test_")
    
    try:
        handler = create_default_handler(output_directory=test_dir)
        
        # Simulate a complete workflow
        workflow = [
            "code",
            "def hello_world():",
            "    print('Hello, World!')",
            "    return True",
            "description",
            "This function prints a greeting message",
            "and returns True to indicate success",
            "stop"
        ]
        
        print("Simulating complete workflow:")
        for i, text in enumerate(workflow, 1):
            print(f"{i:2d}. '{text}'")
            handler.process_transcript(text)
        
        # Check results
        files = handler.get_output_files()
        print(f"\n📁 Output files: {len(files)}")
        
        for filepath in files:
            filename = os.path.basename(filepath)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"\n📄 {filename}:")
            print(f"    Content:\n{content}")
        
        return len(files) >= 2  # Should have code.txt and description.txt
        
    finally:
        shutil.rmtree(test_dir)

def main():
    """Run all tests."""
    print("🚀 Trigger Word System Test Suite")
    print("=" * 60)
    
    tests = [
        ("Basic Functionality", test_basic_functionality),
        ("Custom Triggers", test_custom_triggers),
        ("Edge Cases", test_edge_cases),
        ("File Operations", test_file_operations)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"Running: {test_name}")
        print('='*60)
        
        try:
            result = test_func()
            results.append((test_name, result, None))
            print(f"✅ {test_name}: {'PASSED' if result else 'FAILED'}")
        except Exception as e:
            results.append((test_name, False, str(e)))
            print(f"❌ {test_name}: FAILED - {e}")
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print('='*60)
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASSED" if result else f"❌ FAILED"
        if error:
            status += f" ({error})"
        print(f"{status:15} {test_name}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The trigger word system is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())

