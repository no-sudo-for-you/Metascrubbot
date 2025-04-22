"""
Metadata Logger Module
=====================

This module handles logging operations for metadata changes.
It maintains a CSV log of all metadata operations performed.

Key Programming Concepts Used:
- Classes: MetadataLogger class implementation
- OS Module: File path operations
- File Handling: CSV file operations
- DateTime Handling: Timestamp operations
- Exception Handling: Try-except blocks
- Input Validation: File name validation
- Encryption: Log file encryption support
"""

# Standard library imports
import os
import csv
import time
from datetime import datetime
import getpass
import traceback
import threading

# Import secure log handler
try:
    from secure_log_handler import SecureLogHandler
except ImportError:
    # For backwards compatibility, define a minimal stub if not available
    class SecureLogHandler:
        def get_password(self, confirm=False):
            return getpass.getpass("Enter password: ") if confirm else None

# CLASS Definition
class MetadataLogger:
    """
    Handles logging of metadata operations to CSV file.
    
    This class manages:
    - Log file initialization
    - Operation logging
    - Statistics tracking
    - Log file validation
    - Log file encryption
    """
    
    def __init__(self, log_file_path, encrypt_log=False, password=None):
        """
        Initialize MetadataLogger instance.
        
        Programming Concepts:
        - File Path Handling: Log file path setup
        - List Definition: CSV headers
        - Input Validation: Validate log file name
        - Encryption: Initialize encryption
        
        Args:
            log_file_path (str): Path where log file should be created/accessed
            encrypt_log (bool): Whether to encrypt the log file
            password (str): Password for encryption (if None, will prompt)
            
        Raises:
            ValueError: If the log file name is invalid
        """
        # Validate the log file name
        try:
            self._validate_log_filename(log_file_path)
        except ValueError as e:
            raise ValueError(f"Error initializing log file: {e}")
            
        self.log_file = log_file_path
        self.encrypt_log = encrypt_log
        self.password = password
        self.secure_handler = None
        self.log_lock = threading.Lock()  # Add a lock for thread safety
        
        # Setup secure handler if encryption is enabled
        if self.encrypt_log:
            try:
                self.secure_handler = SecureLogHandler()
            except Exception as e:
                print(f"Warning: Cannot initialize secure logging: {e}")
                print("Continuing with unencrypted logging.")
                self.encrypt_log = False
        
        # Define CSV headers
        self.headers = [
            'Timestamp', 'Original File', 'New File', 'Operation Type',
            'Metadata Type Removed', 'Specific Tags Removed', 'Original File Size (bytes)',
            'New File Size (bytes)', 'Original Metadata Count', 'Remaining Metadata Count',
            'Size Reduction (bytes)', 'Size Reduction Percentage', 'Original Creation Date',
            'Original Modified Date', 'Processing Date', 'Original File Path',
            'New File Path', 'Original EXIF Tags', 'Remaining EXIF Tags',
            'Operation Success Status'
        ]
        self._initialize_log_file()

    def _validate_log_filename(self, filename):
        """
        Validate the log filename to prevent null bytes and other problematic characters.
        
        Args:
            filename (str): The filename to validate
            
        Returns:
            bool: True if valid, False otherwise
            
        Raises:
            ValueError: If the filename contains null bytes or other invalid characters
        """
        # Check for null bytes
        if '\0' in filename:
            raise ValueError("Invalid log file name: Contains null bytes")
        
        # Check file path length
        max_length = 250  # Adjust as needed for your OS
        if len(filename) > max_length:
            raise ValueError(f"File path too long. Maximum allowed is {max_length} characters.")
        
        # Add more validation as needed
        return True

    # FUNCTION Definition
    def _initialize_log_file(self):
        """
        Initialize log file with headers if it doesn't exist.
        
        Programming Concepts:
        - OS Module Usage: File existence check
        - File Handling: CSV file creation
        - Exception Handling: Try-except block
        - Encryption: Handle encrypted log initialization
        
        Raises:
            Exception: If error occurs during file initialization
        """
        try:
            # For encrypted logs, we don't need to check if file exists
            # We'll create or append when writing
            if not self.encrypt_log:
                # Create log file if it doesn't exist
                if not os.path.exists(self.log_file):
                    with open(self.log_file, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(self.headers)
            else:
                # For encrypted logs, create initial file if it doesn't exist
                if not os.path.exists(self.log_file):
                    # Create a temporary file with headers
                    import tempfile
                    temp_fd, temp_file = tempfile.mkstemp(suffix='.csv')
                    with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(self.headers)
                    
                    # If we have a password, encrypt the empty log file
                    if self.password and self.secure_handler:
                        try:
                            self.secure_handler.encrypt_log_file(temp_file, self.log_file, self.password)
                        except Exception as e:
                            print(f"Warning: Could not create encrypted log file: {e}")
                        finally:
                            # Delete the temp file
                            try:
                                os.unlink(temp_file)
                            except:
                                pass
        except Exception as e:
            print(f"Error initializing log file: {e}")
            print(f"Error details: {traceback.format_exc()}")
            # Don't raise exception, just print warning
            print("Logging may not work correctly.")

    # FUNCTION Definition
    def log_operation(self, original_file, new_file, metadata_type, removed_tags,
                     original_metadata, current_metadata):
        """
        Log metadata operation details to CSV file.
        
        Programming Concepts:
        - OS Module Usage: File size and stats
        - DateTime Handling: Timestamp formatting
        - File Handling: CSV writing
        - Casting: Numeric calculations
        - Exception Handling: Try-except block
        - Encryption: Handle encrypted log writing
        
        Args:
            original_file (str): Path to original image
            new_file (str): Path to processed image
            metadata_type (str): Type of metadata operation
            removed_tags (list): List of removed metadata tags
            original_metadata (dict): Original metadata
            current_metadata (dict): Current metadata
            
        Returns:
            dict: Statistics about the operation
            
        Raises:
            Exception: If error occurs during logging
        """
        # Acquire lock to prevent multiple threads from writing simultaneously
        with self.log_lock:
            try:
                # Calculate file sizes and reduction - with error handling
                try:
                    original_size = os.path.getsize(original_file) if os.path.exists(original_file) else 0
                except Exception:
                    original_size = 0
                    
                try:
                    new_size = os.path.getsize(new_file) if os.path.exists(new_file) else 0
                except Exception:
                    new_size = 0
                    
                size_reduction = original_size - new_size if original_size > new_size else 0
                size_reduction_percentage = (size_reduction / original_size) * 100 if original_size > 0 else 0
                
                # Get file timestamps - with error handling
                try:
                    orig_stats = os.stat(original_file)
                    orig_creation = datetime.fromtimestamp(orig_stats.st_ctime).strftime("%Y-%m-%d %H:%M:%S")
                    orig_modified = datetime.fromtimestamp(orig_stats.st_mtime).strftime("%Y-%m-%d %H:%M:%S")
                except Exception:
                    orig_creation = "Unknown"
                    orig_modified = "Unknown"
                
                # Prepare log entry
                log_entry = [
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Current timestamp
                    os.path.basename(original_file),  # Original filename
                    os.path.basename(new_file),  # New filename
                    f"Metadata Removal - {metadata_type}",  # Operation description
                    metadata_type,  # Type of metadata removed
                    '; '.join(removed_tags) if removed_tags else "None",  # List of removed tags
                    original_size,  # Original file size
                    new_size,  # New file size
                    len(original_metadata) if isinstance(original_metadata, dict) else 0,  # Original metadata count
                    len(current_metadata) if isinstance(current_metadata, dict) else 0,  # Current metadata count
                    size_reduction,  # Size reduction in bytes
                    f"{size_reduction_percentage:.2f}%",  # Size reduction percentage
                    orig_creation,  # Original creation date
                    orig_modified,  # Original modification date
                    datetime.now().strftime("%Y-%m-%d %H:%M:%S"),  # Processing timestamp
                    os.path.abspath(original_file),  # Full original file path
                    os.path.abspath(new_file),  # Full new file path
                    '; '.join(sorted(original_metadata.keys())) if isinstance(original_metadata, dict) else "Error",  # Original metadata tags
                    '; '.join(sorted(current_metadata.keys())) if isinstance(current_metadata, dict) else "Error",  # Remaining metadata tags
                    "Success"  # Operation status
                ]
                
                # Add random delay to avoid multiple threads trying to decrypt/write simultaneously
                time.sleep(0.1)  
                
                if self.encrypt_log and self.secure_handler:
                    # For encrypted logs, we need to read existing content, append, and encrypt
                    try:
                        self._append_to_encrypted_log(log_entry)
                    except Exception as e:
                        print(f"Warning: Error writing to encrypted log: {e}")
                        print(f"Error details: {traceback.format_exc()}")
                        print("Operation will continue but logging may be incomplete.")
                else:
                    # For unencrypted logs, simply append to the CSV file
                    try:
                        with open(self.log_file, 'a', newline='', encoding='utf-8') as f:
                            writer = csv.writer(f)
                            writer.writerow(log_entry)
                    except Exception as e:
                        print(f"Warning: Error writing to log file: {e}")
                        print(f"Error details: {traceback.format_exc()}")
                        print("Operation will continue but logging may be incomplete.")
                
                # Return statistics
                return {
                    'original_size': original_size,
                    'new_size': new_size,
                    'size_reduction': size_reduction,
                    'size_reduction_percentage': size_reduction_percentage
                }
                
            except Exception as e:
                print(f"Error logging operation: {e}")
                print(f"Error details: {traceback.format_exc()}")
                print("Operation will continue but logging may be incomplete.")
                
                # Return default statistics
                return {
                    'original_size': 0,
                    'new_size': 0,
                    'size_reduction': 0,
                    'size_reduction_percentage': 0
                }

    # FUNCTION Definition
    def _append_to_encrypted_log(self, log_entry):
        """
        Append to encrypted log file. If file doesn't exist, create it.
        
        Args:
            log_entry (list): List of log entry values
            
        Raises:
            Exception: If error occurs during encrypted logging
        """
        import io
        import tempfile
        
        try:
            # Check if we need to get a password
            if self.password is None:
                # Get password from user
                self.password = self.secure_handler.get_password(confirm=True)
                if not self.password:
                    print("Warning: No password provided for encrypted logging.")
                    print("Skipping log entry.")
                    return
            
            # Create a temporary file for intermediate storage
            temp_file = None
            
            # If log file exists, decrypt it first
            if os.path.exists(self.log_file):
                try:
                    # Decrypt existing content
                    decrypted_content = self.secure_handler.decrypt_log_file(self.log_file, self.password)
                    
                    # Create a temp file with the decrypted content
                    temp_fd, temp_file = tempfile.mkstemp(suffix='.csv')
                    with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as f:
                        f.write(decrypted_content)
                    
                    # Append new log entry
                    with open(temp_file, 'a', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(log_entry)
                
                except Exception as e:
                    # If decryption fails, assume the file is corrupted or wrong password
                    # Start a new file
                    print(f"Warning: Could not decrypt existing log file: {e}")
                    print(f"Error details: {traceback.format_exc()}")
                    print("Creating a new encrypted log file.")
                    
                    # Create a new temp file
                    temp_fd, temp_file = tempfile.mkstemp(suffix='.csv')
                    with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f)
                        writer.writerow(self.headers)
                        writer.writerow(log_entry)
            else:
                # Create a new temp file
                temp_fd, temp_file = tempfile.mkstemp(suffix='.csv')
                with os.fdopen(temp_fd, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(self.headers)
                    writer.writerow(log_entry)
            
            # Encrypt the temp file and save to log file
            if temp_file:
                self.secure_handler.encrypt_log_file(temp_file, self.log_file, self.password)
                
                # Delete the temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
        
        except Exception as e:
            # Clean up temp file if it exists
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except:
                    pass
            
            raise Exception(f"Error with encrypted logging: {e}")
    
    # FUNCTION Definition
    def get_log_file_path(self):
        """
        Return the full path to the log file.
        
        Programming Concepts:
        - OS Module Usage: Path resolution
        
        Returns:
            str: Absolute path to log file
        """
        return os.path.abspath(self.log_file)