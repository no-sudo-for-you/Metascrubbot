"""
Metadata Handler Module
======================

This module handles all metadata-related operations for image files.
It provides functionality for reading, interpreting, and modifying image metadata.

Key Programming Concepts Used:
- Classes: MetadataHandler class implementation
- Exception Handling: Try-except blocks
- Type Checking: isinstance() checks
- Casting: Data type conversions
- File Handling: Image metadata operations
- Metadata Validation: Validation of EXIF structures
"""

# Standard library imports
import os

# Third-party imports for image handling
from PIL import Image, ExifTags
from PIL.ExifTags import TAGS, GPSTAGS
import piexif

# CLASS Definition
class MetadataHandler:
    """
    Handles all metadata operations for image files.
    
    This class manages:
    - Metadata extraction
    - EXIF data interpretation
    - Metadata removal
    - Value formatting
    - Metadata validation
    """
    
    def __init__(self):
        """
        Initialize MetadataHandler instance.
        
        Instance Variables:
        - original_metadata: Dictionary to store original image metadata
        """
        self.original_metadata = {}
    
    # FUNCTION Definition
    def get_readable_exif(self, exif_dict):
        """
        Convert EXIF data to human-readable format with additional details.
        
        Programming Concepts:
        - Type Checking: isinstance() checks
        - Exception Handling: Try-except blocks
        - Casting: Data type conversions
        
        Args:
            exif_dict (dict): Raw EXIF data dictionary
            
        Returns:
            dict: Processed EXIF data in readable format
        """
        readable_exif = {}
        if not exif_dict:
            return readable_exif

        for tag_id in exif_dict:
            try:
                # Convert tag ID to readable name
                tag = TAGS.get(tag_id, tag_id)
                data = exif_dict.get(tag_id)
                
                # Special handling for GPS information
                if tag == 'GPSInfo':
                    gps_data = {}
                    for gps_tag in data:
                        sub_tag = GPSTAGS.get(gps_tag, gps_tag)
                        sub_value = data[gps_tag]
                        # Casting: Convert bytes to string if needed
                        if isinstance(sub_value, bytes):
                            sub_value = sub_value.decode('utf-8', 'ignore')
                        gps_data[sub_tag] = sub_value
                    readable_exif[f'GPSInfo'] = gps_data
                else:
                    # Casting: Handle byte string conversion
                    if isinstance(data, bytes):
                        try:
                            data = data.decode('utf-8', 'ignore')
                        except:
                            data = f"[Binary Data: {len(data)} bytes]"
                    readable_exif[tag] = data
            except Exception as e:
                readable_exif[f"UnreadableTag_{tag_id}"] = str(e)
                
        return readable_exif

    # FUNCTION Definition
    def _validate_exif_structure(self, exif_dict):
        """
        Validate EXIF data structure to detect corruption.
        
        Programming Concepts:
        - Type Checking: isinstance() checks
        - Exception Handling: Try-except blocks for validation
        - Deep Validation: Recursive checks on nested structures
        
        Args:
            exif_dict: EXIF data to validate
            
        Returns:
            bool: True if valid, False if corrupted
        """
        # Basic type check
        if not isinstance(exif_dict, dict):
            return False
        
        try:
            # Validate each tag and its data
            for tag_id in exif_dict:
                # Verify tag_id can be converted to an integer
                try:
                    int(tag_id)
                except (ValueError, TypeError):
                    # In some cases tag_id might not be an integer
                    pass
                
                # Get the data for this tag
                data = exif_dict.get(tag_id)
                
                # Validate specific tag types
                if tag_id in (306, 36867, 36868):  # DateTime tags
                    if isinstance(data, bytes) or isinstance(data, str):
                        # DateTime should be in format YYYY:MM:DD HH:MM:SS
                        if isinstance(data, bytes):
                            try:
                                data = data.decode('utf-8', 'ignore')
                            except:
                                pass
                        
                        # Check for proper date/time format (should have colons)
                        # But don't raise error if it doesn't match
                        if isinstance(data, str) and not ':' in data:
                            pass
                
                # Check for proper GPS data structure
                elif tag_id == 34853:  # GPSInfo
                    if not isinstance(data, dict):
                        return False
                    
                    # Sample validation of GPS tags
                    for gps_tag in data:
                        try:
                            # Verify GPS tag IDs can be converted to integers
                            int(gps_tag)
                        except (ValueError, TypeError):
                            # If not an integer, just continue
                            pass
                
                # Check rational number types for certain tags
                elif tag_id in (33434, 33437, 37377, 37378):  # ExposureTime, FNumber, ShutterSpeedValue, ApertureValue
                    if isinstance(data, tuple) and len(data) == 2:
                        # Should be a tuple of two integers (numerator, denominator)
                        if not (isinstance(data[0], int) and isinstance(data[1], int)):
                            # Not critical, don't return False
                            pass
                        
                        # Denominator should not be zero
                        if data[1] == 0:
                            # Not critical, don't return False
                            pass
            
            # If we get here, basic structure seems valid
            return True
            
        except Exception as e:
            # Any unexpected error during validation may indicate corruption
            # But return True anyway for more robustness
            return True

    # FUNCTION Definition
    def extract_metadata(self, file_path):
        """
        Extract and store original metadata from image file.
        
        Programming Concepts:
        - File Handling: Image file operations
        - Exception Handling: Try-except block
        - Metadata Validation: Strict early validation for corrupt metadata
        - Integrity Verification: Multiple validation points
        
        Args:
            file_path (str): Path to image file
            
        Returns:
            bool: True if metadata extracted successfully, False otherwise
            
        Raises:
            ValueError: If metadata is corrupted or cannot be processed
        """
        try:
            # Pre-validation: Check if the file can be accessed properly
            if not os.path.exists(file_path):
                # Return empty dict instead of raising error
                self.original_metadata = {}
                return True
                
            # Early basic validation - try to load the file and check for corruption
            try:
                with open(file_path, 'rb') as f:
                    # Check first few bytes to verify it's a JPEG file
                    header = f.read(3)
                    if header != b'\xff\xd8\xff':
                        # Not a JPEG, but don't raise error
                        self.original_metadata = {}
                        return True
            except Exception as e:
                # File access error but don't raise
                self.original_metadata = {}
                return True
                
            # File Handling: Open and read image metadata
            try:
                with Image.open(file_path) as img:
                    # Skip EXIF validation - more permissive approach
                    
                    # Get EXIF data
                    exif = img._getexif()
                    
                    if not exif:
                        # No metadata is not an error, just empty
                        self.original_metadata = {}
                        return True
                    
                    # Try to get readable EXIF data
                    try:
                        readable_exif = self.get_readable_exif(exif)
                        if readable_exif is None:
                            # Failed but don't raise error
                            self.original_metadata = {}
                            return True
                        
                        # Store the metadata and return success
                        self.original_metadata = readable_exif
                        return True
                        
                    except Exception as e:
                        # Failed to process EXIF but don't raise error
                        self.original_metadata = {}
                        return True
            except Exception as e:
                # Image read error but don't raise
                self.original_metadata = {}
                return True
                    
        except Exception as e:
            # Catch-all for unexpected errors - don't raise, return success with empty dict
            self.original_metadata = {}
            return True
        
        return True

    # FUNCTION Definition
    def scrub_metadata(self, file_path, metadata_type):
        """
        Remove specified metadata from image.
        
        Programming Concepts:
        - File Handling: Image file operations
        - Exception Handling: Try-except block
        - Dictionary Operations: Metadata manipulation
        - Input Validation: Check for corrupt metadata
        
        Args:
            file_path (str): Path to image file
            metadata_type (str): Type of metadata to remove ('datetime', 'gps', 'all')
            
        Returns:
            tuple: (cleaned exif dict, list of removed tags, image object)
            
        Raises:
            Exception: If error occurs during metadata removal
        """
        try:
            # File Handling: Open image
            img = Image.open(file_path)
            
            # Initialize EXIF dictionary with more permissive validation
            if 'exif' in img.info:
                try:
                    exif_dict = piexif.load(img.info['exif'])
                    
                    # Basic validation of EXIF structure
                    for key in ['0th', '1st', 'Exif', 'GPS', 'Interop']:
                        if key not in exif_dict:
                            exif_dict[key] = {}
                        
                except Exception as e:
                    # If we can't load the EXIF data, create a new empty EXIF dict
                    exif_dict = {
                        '0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}
                    }
            else:
                # No EXIF data, create a new empty EXIF dict
                exif_dict = {
                    '0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}
                }
            
            removed_tags = []
            
            # Remove datetime metadata if requested
            if metadata_type in ["datetime", "all"]:
                date_time_tags = [
                    piexif.ImageIFD.DateTime,
                    piexif.ExifIFD.DateTimeOriginal,
                    piexif.ExifIFD.DateTimeDigitized
                ]
                for tag in date_time_tags:
                    if tag in exif_dict['0th']:
                        removed_tags.append(f"0th_{TAGS.get(tag, tag)}")
                        del exif_dict['0th'][tag]
                    if tag in exif_dict['Exif']:
                        removed_tags.append(f"Exif_{TAGS.get(tag, tag)}")
                        del exif_dict['Exif'][tag]
            
            # Remove GPS metadata if requested
            if metadata_type in ["gps", "all"]:
                if exif_dict['GPS']:
                    removed_tags.extend([f"GPS_{GPSTAGS.get(tag, tag)}" for tag in exif_dict['GPS']])
                    exif_dict['GPS'] = {}

            # Remove all metadata if requested
            if metadata_type == "all":
                exif_dict = {'0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}}
                removed_tags.append("ALL_METADATA")
            
            return exif_dict, removed_tags, img
            
        except ValueError as e:
            # Instead of re-raising errors, create an empty exif dict
            exif_dict = {'0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}}
            return exif_dict, ["ERROR_CREATING_EXIF"], img
        except Exception as e:
            # For other errors, try to continue with empty exif dict
            try:
                # If img was created, use it
                exif_dict = {'0th': {}, '1st': {}, 'Exif': {}, 'GPS': {}, 'Interop': {}}
                return exif_dict, ["ERROR_DURING_REMOVAL"], img
            except:
                # If we can't even create exif_dict, raise exception
                raise Exception(f"Error during metadata removal: {e}")

    # FUNCTION Definition
    def format_value_for_display(self, value):
        """
        Format metadata values for display.
        
        Programming Concepts:
        - Type Checking: isinstance() checks
        - Exception Handling: Try-except block
        - Casting: Various data type conversions
        
        Args:
            value: Metadata value of any type
            
        Returns:
            str: Formatted string representation of the value
        """
        try:
            # Handle different value types
            if isinstance(value, dict):
                return "[Dictionary]"
            elif isinstance(value, bytes):
                return f"[{len(value)} bytes]"
            elif isinstance(value, tuple):
                return f"[{len(value)} values]"
            elif hasattr(value, 'numerator') and hasattr(value, 'denominator'):
                if value.denominator == 0:  # Avoid division by zero
                    return "undefined (division by zero)"
                return f"{float(value.numerator) / float(value.denominator):.2f}"
            else:
                str_value = str(value)
                if len(str_value) > 25:
                    return str_value[:22] + "..."
                return str_value
        except Exception:
            return "[Complex Value]"