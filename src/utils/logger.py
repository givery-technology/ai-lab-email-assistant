#!/usr/bin/env python
# coding: utf-8

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime

class EmailAssistantLogger:
    """
    Logger class for the Email Assistant application.
    Provides methods for logging at different levels with custom formatting.
    """
    
    def __init__(self, log_level=logging.INFO, log_to_console=True, log_to_file=True,
                 log_dir="logs", log_filename=None):
        """
        Initialize the logger with customizable options.
        
        Args:
            log_level: The logging level (default: INFO)
            log_to_console: Whether to output logs to console (default: True)
            log_to_file: Whether to output logs to file (default: True)
            log_dir: Directory to store log files (default: "logs")
            log_filename: Name of log file (default: email_assistant_YYYY-MM-DD.log)
        """
        self.logger = logging.getLogger("email_assistant")
        self.logger.setLevel(log_level)
        self.logger.propagate = False
        
        # Clear any existing handlers to avoid duplicates
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create formatters
        console_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        
        file_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(name)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler if requested
        if log_to_console:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setFormatter(console_formatter)
            self.logger.addHandler(console_handler)
        
        # Add file handler if requested
        if log_to_file:
            # Create log directory if it doesn't exist
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Set default log filename if none provided
            if log_filename is None:
                current_date = datetime.now().strftime("%Y-%m-%d")
                log_filename = f"email_assistant_{current_date}.log"
            
            log_path = os.path.join(log_dir, log_filename)
            
            # Create a rotating file handler (10MB max size, keep 5 backup files)
            file_handler = RotatingFileHandler(
                log_path, maxBytes=10*1024*1024, backupCount=5
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
    
    def debug(self, message):
        """Log a debug message."""
        self.logger.debug(message)
    
    def info(self, message):
        """Log an info message."""
        self.logger.info(message)
    
    def warning(self, message):
        """Log a warning message."""
        self.logger.warning(message)
    
    def error(self, message):
        """Log an error message."""
        self.logger.error(message)
    
    def critical(self, message):
        """Log a critical message."""
        self.logger.critical(message)
    
    def log_email_processing(self, email_data, classification, reasoning=None):
        """
        Log email processing information.
        
        Args:
            email_data: Dictionary containing email information
            classification: The email classification result
            reasoning: Optional reasoning behind the classification
        """
        email_from = email_data.get("author", "Unknown")
        email_subject = email_data.get("subject", "No Subject")
        
        log_message = f"Processed email from '{email_from}' subject '{email_subject}' - Classification: {classification}"
        self.info(log_message)
        
        if reasoning:
            self.debug(f"Classification reasoning: {reasoning}")
    
    def log_agent_action(self, action_type, details):
        """
        Log agent actions.
        
        Args:
            action_type: Type of action performed (e.g., 'write_email', 'schedule_meeting')
            details: Dictionary with action details
        """
        self.info(f"Agent action: {action_type} - {details}")

# Create default logger instance for easy import
default_logger = EmailAssistantLogger()

# Simple helper functions to use the default logger
def debug(message):
    default_logger.debug(message)

def info(message):
    default_logger.info(message)

def warning(message):
    default_logger.warning(message)

def error(message):
    default_logger.error(message)

def critical(message):
    default_logger.critical(message)

def log_email_processing(email_data, classification, reasoning=None):
    default_logger.log_email_processing(email_data, classification, reasoning)

def log_agent_action(action_type, details):
    default_logger.log_agent_action(action_type, details)