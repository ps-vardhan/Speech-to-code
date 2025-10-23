"""
Trigger Word Handler for Speech-to-Text Pipeline

This module provides functionality to detect trigger words in transcribed text
and automatically save subsequent speech to designated files based on the detected
trigger word.

Features:
- Keyword detection for "code", "description", and "stop" commands
- Automatic file writing to code.txt and description.txt
- Context-aware buffering to handle partial transcriptions
- Integration with existing STT pipeline
- Configurable trigger words and file paths
"""

import os
import re
import logging
from typing import Optional, Dict, List, Callable
from datetime import datetime

logger = logging.getLogger(__name__)

class TriggerWordHandler:
    """
    Handles trigger word detection and file writing for the STT pipeline.
    
    This class monitors transcribed text for specific trigger words and manages
    the writing of subsequent text to appropriate files based on the detected trigger.
    """
    
    def __init__(self, 
                 trigger_words: Dict[str, str] = None,
                 output_directory: str = ".",
                 enable_timestamps: bool = False,
                 auto_cleanup_trigger_words: bool = True,
                 on_mode_change: Callable[[str], None] = None):
        """
        Initialize the TriggerWordHandler.
        
        Args:
            trigger_words: Dictionary mapping trigger words to file names
                          Default: {"code": "code.txt", "description": "description.txt", "stop": None}
            output_directory: Directory where output files will be saved
            enable_timestamps: Whether to add timestamps to filenames
            auto_cleanup_trigger_words: Whether to remove trigger words from saved text
            on_mode_change: Callback function called when mode changes
        """
        self.trigger_words = trigger_words or {
            "code": "code.txt",
            "description": "description.txt", 
            "stop": None
        }
        
        self.output_directory = output_directory
        self.enable_timestamps = enable_timestamps
        self.auto_cleanup_trigger_words = auto_cleanup_trigger_words
        self.on_mode_change = on_mode_change
        
        # Current state
        self.current_mode = None
        self.current_file = None
        self.buffer = []
        self.last_trigger_time = None
        
        # Create output directory if it doesn't exist
        os.makedirs(self.output_directory, exist_ok=True)
        
        # Compile trigger word patterns for efficient matching
        self.trigger_patterns = {}
        for trigger, filename in self.trigger_words.items():
            if filename:  # Skip 'stop' trigger
                pattern = re.compile(r'\b' + re.escape(trigger.lower()) + r'\b', re.IGNORECASE)
                self.trigger_patterns[trigger] = pattern
        
        # Stop pattern (matches "stop" anywhere in text)
        self.stop_pattern = re.compile(r'\b' + re.escape("stop") + r'\b', re.IGNORECASE)
        
        logger.info(f"TriggerWordHandler initialized with triggers: {list(self.trigger_words.keys())}")
    
    def _get_filename(self, base_filename: str) -> str:
        """Generate filename with optional timestamp."""
        if self.enable_timestamps:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            name, ext = os.path.splitext(base_filename)
            return f"{name}_{timestamp}{ext}"
        return base_filename
    
    def _cleanup_trigger_word(self, text: str, trigger_word: str) -> str:
        """Remove trigger word from text if auto_cleanup is enabled."""
        if not self.auto_cleanup_trigger_words:
            return text
        
        # Remove the trigger word and any leading/trailing whitespace
        pattern = re.compile(r'\b' + re.escape(trigger_word.lower()) + r'\b', re.IGNORECASE)
        cleaned = pattern.sub('', text).strip()
        
        # Remove any leading punctuation or extra spaces
        cleaned = re.sub(r'^[^\w\s]+', '', cleaned).strip()
        
        return cleaned
    
    def _write_to_file(self, text: str):
        """Write text to the current active file."""
        if not self.current_file or not text.strip():
            return
        
        try:
            filepath = os.path.join(self.output_directory, self.current_file)
            with open(filepath, 'a', encoding='utf-8') as f:
                f.write(text + "\n")
            logger.debug(f"Wrote to {filepath}: {text[:50]}...")
        except Exception as e:
            logger.error(f"Error writing to file {self.current_file}: {e}")
    
    def _switch_mode(self, new_mode: str, trigger_word: str = None):
        """Switch to a new mode and update file handling."""
        if new_mode == self.current_mode:
            return
        
        old_mode = self.current_mode
        self.current_mode = new_mode
        
        # Update current file
        if new_mode and new_mode in self.trigger_words:
            self.current_file = self._get_filename(self.trigger_words[new_mode])
        else:
            self.current_file = None
        
        # Call mode change callback
        if self.on_mode_change:
            try:
                self.on_mode_change(new_mode, old_mode, trigger_word)
            except Exception as e:
                logger.error(f"Error in mode change callback: {e}")
        
        logger.info(f"Mode switched from '{old_mode}' to '{new_mode}'")
    
    def process_transcript(self, transcript: str) -> bool:
        """
        Process a transcript for trigger words and handle mode switching.
        
        Args:
            transcript: The transcribed text to process
            
        Returns:
            bool: True if a trigger word was detected, False otherwise
        """
        if not transcript or not transcript.strip():
            return False
        
        transcript_lower = transcript.lower().strip()
        trigger_detected = False
        
        # Check for stop trigger first
        if self.stop_pattern.search(transcript_lower):
            if self.current_mode:
                logger.info("🛑 Stop trigger detected - ending recording")
                self._switch_mode(None, "stop")
                trigger_detected = True
            return trigger_detected
        
        # Check for other trigger words
        for trigger_word, filename in self.trigger_words.items():
            if trigger_word == "stop" or not filename:
                continue
                
            if self.trigger_patterns[trigger_word].search(transcript_lower):
                logger.info(f"🧩 {trigger_word.title()} trigger detected - switching mode")
                self._switch_mode(trigger_word, trigger_word)
                trigger_detected = True
                break
        
        # If no trigger detected and we're in a mode, write to current file
        if not trigger_detected and self.current_mode and self.current_file:
            # Clean up trigger word if it's at the beginning
            cleaned_text = self._cleanup_trigger_word(transcript, self.current_mode)
            if cleaned_text:
                self._write_to_file(cleaned_text)
        
        return trigger_detected
    
    def get_status(self) -> Dict:
        """Get current handler status."""
        return {
            "current_mode": self.current_mode,
            "current_file": self.current_file,
            "trigger_words": self.trigger_words,
            "output_directory": self.output_directory
        }
    
    def reset(self):
        """Reset the handler to initial state."""
        self.current_mode = None
        self.current_file = None
        self.buffer = []
        self.last_trigger_time = None
        logger.info("TriggerWordHandler reset")
    
    def add_trigger_word(self, trigger: str, filename: str):
        """Add a new trigger word and associated filename."""
        self.trigger_words[trigger] = filename
        if filename:
            pattern = re.compile(r'\b' + re.escape(trigger.lower()) + r'\b', re.IGNORECASE)
            self.trigger_patterns[trigger] = pattern
        logger.info(f"Added trigger word '{trigger}' -> '{filename}'")
    
    def remove_trigger_word(self, trigger: str):
        """Remove a trigger word."""
        if trigger in self.trigger_words:
            del self.trigger_words[trigger]
            if trigger in self.trigger_patterns:
                del self.trigger_patterns[trigger]
            logger.info(f"Removed trigger word '{trigger}'")
    
    def get_output_files(self) -> List[str]:
        """Get list of output files that have been created."""
        files = []
        for filename in self.trigger_words.values():
            if filename:
                filepath = os.path.join(self.output_directory, filename)
                if os.path.exists(filepath):
                    files.append(filepath)
        return files


def create_default_handler(output_directory: str = ".", 
                          enable_timestamps: bool = False) -> TriggerWordHandler:
    """
    Create a TriggerWordHandler with default settings.
    
    Args:
        output_directory: Directory for output files
        enable_timestamps: Whether to add timestamps to filenames
        
    Returns:
        TriggerWordHandler: Configured handler instance
    """
    def mode_change_callback(new_mode, old_mode, trigger_word):
        """Default callback for mode changes."""
        if new_mode:
            print(f"🎤 {new_mode.title()} mode activated")
        elif old_mode:
            print(f"🛑 Stopped recording to {old_mode}")
    
    return TriggerWordHandler(
        output_directory=output_directory,
        enable_timestamps=enable_timestamps,
        on_mode_change=mode_change_callback
    )

