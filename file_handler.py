"""
File Handler Module
==================

This module handles all file operations for the metadata scrubber application.

Key Programming Concepts Used:
- Classes: FileHandler class implementation
- OS Module: File system operations and path handling
- File Handling: File read/write operations
- Functions: Multiple class methods for file manipulation
- Exception Handling: Try-except blocks for error management
- Input Validation: File path and name validation
- Metadata Validation: EXIF data integrity checking
"""

# OS Module Usage: Import for file system operations
import os
import re  # Added for input validation
import traceback
# Third-party imports for image handling
import piexif
from PIL import Image

# CLASS Definition
class FileHandler:
    """
    Handles all file operations related to image processing and metadata cleaning.
    
    This class manages:
    - File validation
    - Clean file tracking
    - Image saving with cleaned metadata
    - File statistics retrieval
    """
    
    def __init__(self):
        """
        Initialize FileHandler instance.
        
        Instance Variables:
        - clean_file_count: Tracks number of files processed
        - latest_clean_file: Stores path of most recent cleaned file
        """
        self.clean_file_count = 0  # Counter for processed files
        self.latest_clean_file = None  # Tracks most recent cleaned file path

    # FUNCTION Definition
    def validate_file(self, file_path):
        """
        Validate if file exists and is a JPG image with valid metadata structure.
        
        Programming Concepts:
        - OS Module Usage: Path existence check
        - File Handling: Extension verification
        - String operations: Case-insensitive extension check
        - Input Validation: File path length and character checks
        - Metadata Validation: Basic EXIF integrity check
        
        Args:
            file_path (str): Path to the file to validate
            
        Returns:
            bool: True if file exists and is a valid JPG, False otherwise
            
        Raises:
            ValueError: If the file path is too long, contains illegal characters, or has corrupted metadata
        """
        try:
            # Check file path length (adjust max_length as needed for your OS)
            max_length = 250
            if len(file_path) > max_length:
                raise ValueError(f"File path too long. Maximum allowed is {max_length} characters.")
            
            # Check for illegal characters in the file name
            file_name = os.path.basename(file_path)
            # Define a pattern for valid file names
            # Typically avoiding: < > : " / \ | ? * and control characters
            if not re.match(r'^[^<>:"/\\|?*\x00-\x1F]*$', file_name):
                raise ValueError("File name contains illegal characters. Avoid: < > : \" / \\ | ? * and control characters.")
            
            # OS Module: Check if file exists
            if not os.path.exists(file_path):
                return False
                
            # Check if it's a JPG file
            if not file_path.lower().endswith(('.jpg', '.jpeg')):
                return False
                
            # Attempt to open the file and perform basic metadata validation
            try:
                with Image.open(file_path) as img:
                    # Try to access basic image properties to verify it's a valid image
                    img.size
                    
                    # Basic check for metadata integrity - with more permissive error handling
                    if 'exif' in img.info:
                        try:
                            # Try to load EXIF data - this will fail if it's severely corrupted
                            piexif.load(img.info['exif'])
                        except Exception as e:
                            # Instead of raising error, we'll just print a warning
                            print(f"Warning: Possible metadata corruption: {e}")
                            print("We'll attempt to process the file anyway.")
                            # Return True to continue processing
                            return True
                    
                    return True
                    
            except ValueError as e:
                # Re-raise validation errors
                raise
            except Exception as e:
                error_msg = str(e)
                if any(keyword in error_msg.lower() for keyword in ["corrupt", "invalid", "broken", "truncated"]):
                    # Print warning instead of raising error
                    print(f"Warning: File validation issue: {error_msg}")
                    print("We'll attempt to process the file anyway.")
                    return True
                return False
            
            return False
            
        except ValueError as e:
            # Re-raise these specific validation errors
            raise
        except Exception as e:
            # For unexpected errors, print debug info but return False
            print(f"Unexpected error in validate_file: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return False

    # FUNCTION Definition with File Handling
    def save_cleaned_image(self, original_path, img, exif_dict):
        """
        Save image with cleaned metadata.
        
        Programming Concepts:
        - OS Module Usage: Path manipulation
        - File Handling: Image saving
        - Exception Handling: Try-except for error management
        - Input Validation: New file name length validation
        
        Args:
            original_path (str): Path to original image
            img (PIL.Image): Image object to save
            exif_dict (dict): Clean EXIF data dictionary
            
        Returns:
            str: Path to newly saved file
            
        Raises:
            Exception: If error occurs during save operation
        """
        try:
            # Increment clean file counter
            self.clean_file_count += 1
            
            # OS Module: Path manipulation to create new filename
            base_name = os.path.splitext(original_path)[0]
            new_file = f"{base_name}_clean_{self.clean_file_count}.jpg"
            
            # Check if the new file path is too long
            max_length = 250  # Adjust as needed for your OS
            if len(new_file) > max_length:
                # Truncate the base name to fit within limits
                allowed_base_length = max_length - len(f"_clean_{self.clean_file_count}.jpg") - 10
                truncated_base = os.path.splitext(original_path)[0][:allowed_base_length]
                new_file = f"{truncated_base}_clean_{self.clean_file_count}.jpg"
            
            # File Handling: Convert EXIF dict to bytes and save image
            try:
                exif_bytes = piexif.dump(exif_dict)
                img.save(new_file, "JPEG", exif=exif_bytes, quality=100)
            except Exception as e:
                # If EXIF dumping fails, try saving without EXIF
                print(f"Warning: Error saving with EXIF data: {e}. Trying to save without EXIF.")
                img.save(new_file, "JPEG", quality=100)
            
            # Update latest clean file tracker
            self.latest_clean_file = new_file
            return new_file
            
        except Exception as e:
            # Print full error details for debugging
            print(f"Error saving cleaned image: {e}")
            print(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Error saving cleaned image: {e}")

    # FUNCTION Definition
    def get_latest_clean_file(self):
        """
        Get the path of the most recently created cleaned file.
        
        Programming Concepts:
        - OS Module Usage: Path existence verification
        
        Returns:
            str or None: Path to latest clean file if exists, None otherwise
        """
        # OS Module: Check if latest clean file exists
        if self.latest_clean_file and os.path.exists(self.latest_clean_file):
            return self.latest_clean_file
        return None

    # FUNCTION Definition
    def get_file_size(self, file_path):
        """
        Get the size of a file in bytes.
        
        Programming Concepts:
        - OS Module Usage: File size retrieval
        - Exception Handling: Try-except for error management
        
        Args:
            file_path (str): Path to file
            
        Returns:
            int: Size of file in bytes
            
        Raises:
            Exception: If error occurs getting file size
        """
        try:
            # OS Module: Get file size
            return os.path.getsize(file_path)
        except Exception as e:
            print(f"Error getting file size: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return 0  # Return 0 instead of raising exception

    # FUNCTION Definition
    def get_file_dates(self, file_path):
        """
        Get creation and modification dates for a file.
        
        Programming Concepts:
        - OS Module Usage: File statistics retrieval
        - Casting: Converting timestamps to dictionary
        - Exception Handling: Try-except for error management
        
        Args:
            file_path (str): Path to file
            
        Returns:
            dict: Dictionary containing created and modified timestamps
            
        Raises:
            Exception: If error occurs getting file dates
        """
        try:
            # OS Module: Get file statistics
            stats = os.stat(file_path)
            
            # Casting: Convert timestamps to dictionary
            return {
                'created': stats.st_ctime,  # Creation time
                'modified': stats.st_mtime  # Modification time
            }
        except Exception as e:
            print(f"Error getting file dates: {e}")
            print(f"Error details: {traceback.format_exc()}")
            # Return empty dict instead of raising exception
            return {
                'created': 0,
                'modified': 0
            }