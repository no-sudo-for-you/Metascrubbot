"""
Main Script Module (Enhanced Version)
====================================

This is the main coordinator script for the Enhanced Metadata Scrubber application.
It orchestrates the interaction between different components of the system.

Key Programming Concepts Used:
- Functions: Multiple function definitions for program flow
- Module Imports: Component handlers import
- Exception Handling: Try-except blocks for error management
- File Handling: Multiple file type operations
- Input Validation: Handling validation errors
- Metadata Validation: Early validation of file integrity
- Multiple File Types: Support for different file formats
- Batch Processing: Support for processing multiple files
- Encrypted Logging: Support for secure logging
"""

# Standard library imports
import os
import sys
import getpass
import traceback

# Local module imports for component handlers
from metadata_handler import MetadataHandler
from file_handler import FileHandler
from metadata_logger import MetadataLogger
from ui_handler import UserInterface
from file_type_handler import JPGHandler, PDFHandler, WordHandler, ExcelHandler
from batch_processor import BatchProcessor
from secure_log_handler import SecureLogHandler

# FUNCTION Definition
def process_metadata_removal(metadata_type, file_path, handlers, file_type_handler):
    """
    Process metadata removal operation for a given file.
    
    Programming Concepts:
    - Tuple Unpacking: Handlers tuple
    - Exception Handling: Try-except block
    - Function Parameters: Multiple parameter handling
    - Metadata Validation: Additional validation before processing
    - Type-Specific Handling: Using appropriate file type handler
    
    Args:
        metadata_type (str): Type of metadata to remove
        file_path (str): Path to file
        handlers (tuple): Tuple containing UI, metadata, file, and logger handlers
        file_type_handler: Handler for the specific file type
        
    Returns:
        bool: True if operation successful, False otherwise
    """
    # Unpack handler components from tuple
    ui, metadata_handler, file_handler, logger = handlers
    
    try:
        # Start progress tracking
        ui.start_progress()
        ui.update_progress(10)
        
        # Extract original metadata for logging
        try:
            original_metadata = file_type_handler.extract_metadata(file_path)
            ui.update_progress(20)
        except Exception as e:
            # If metadata extraction fails, log the error but continue
            print(f"Warning: Error extracting metadata: {e}")
            original_metadata = {"Error": str(e)}
            ui.update_progress(20)
        
        # Remove specified metadata using type-specific handler
        try:
            file_obj, removed_tags, exif_dict = file_type_handler.remove_metadata(file_path, metadata_type)
            ui.update_progress(40)
        except Exception as e:
            ui.finish_progress()
            ui.show_error(f"Error removing metadata: {str(e)}")
            return False
        
        # File Handling: Save new file with cleaned metadata
        try:
            counter = file_handler.clean_file_count + 1
            new_file = file_type_handler.save_modified_file(file_path, file_obj, exif_dict, counter)
            file_handler.clean_file_count = counter
            file_handler.latest_clean_file = new_file
            ui.update_progress(70)
        except Exception as e:
            ui.finish_progress()
            ui.show_error(f"Error saving modified file: {str(e)}")
            return False
        
        # File Handling: Read current metadata for logging
        try:
            current_metadata = file_type_handler.extract_metadata(new_file)
            ui.update_progress(80)
        except Exception as e:
            # If metadata extraction fails, log the error but continue
            print(f"Warning: Error extracting metadata from new file: {e}")
            current_metadata = {"Error": str(e)}
            ui.update_progress(80)
        
        # Log the operation details
        try:
            stats = logger.log_operation(
                file_path, new_file, metadata_type, removed_tags,
                original_metadata, current_metadata
            )
        except Exception as e:
            # If logging fails, print warning but consider operation successful
            print(f"Warning: Error logging operation: {e}")
            # Create minimal stats dictionary
            stats = {
                'original_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'new_size': os.path.getsize(new_file) if os.path.exists(new_file) else 0,
                'size_reduction': 0,
                'size_reduction_percentage': 0
            }
        
        # Complete progress tracking
        ui.update_progress(20)
        ui.finish_progress()
        
        # Display results to user
        ui.show_operation_results(new_file, stats)
        
        return True
        
    except ValueError as e:
        # Specifically catch validation errors
        ui.finish_progress()
        ui.show_error(f"Validation error: {str(e)}")
        return False
    except Exception as e:
        ui.finish_progress()
        # Print full traceback for debugging
        print(f"Full error details: {traceback.format_exc()}")
        ui.show_error(f"Error during metadata operation: {str(e)}")
        return False

# FUNCTION Definition
def process_add_metadata(metadata_type, file_path, handlers, file_type_handler, metadata_dict):
    """
    Process add/modify metadata operation for a given file.
    
    Args:
        metadata_type (str): Type of metadata to add/modify
        file_path (str): Path to file
        handlers (tuple): Tuple containing UI, metadata, file, and logger handlers
        file_type_handler: Handler for the specific file type
        metadata_dict (dict): Metadata values to add/modify
        
    Returns:
        bool: True if operation successful, False otherwise
    """
    # Unpack handler components from tuple
    ui, metadata_handler, file_handler, logger = handlers
    
    try:
        # Start progress tracking
        ui.start_progress()
        ui.update_progress(10)
        
        # Extract original metadata for logging
        try:
            original_metadata = file_type_handler.extract_metadata(file_path)
            ui.update_progress(20)
        except Exception as e:
            # If metadata extraction fails, log the error but continue
            print(f"Warning: Error extracting metadata: {e}")
            original_metadata = {"Error": str(e)}
            ui.update_progress(20)
        
        # Add/modify metadata using type-specific handler
        try:
            file_obj, modified_tags, exif_dict = file_type_handler.add_metadata(file_path, metadata_dict)
            ui.update_progress(40)
        except Exception as e:
            ui.finish_progress()
            ui.show_error(f"Error modifying metadata: {str(e)}")
            return False
        
        # File Handling: Save new file with modified metadata
        try:
            counter = file_handler.clean_file_count + 1
            new_file = file_type_handler.save_modified_file(file_path, file_obj, exif_dict, counter)
            file_handler.clean_file_count = counter
            file_handler.latest_clean_file = new_file
            ui.update_progress(70)
        except Exception as e:
            ui.finish_progress()
            ui.show_error(f"Error saving modified file: {str(e)}")
            return False
        
        # File Handling: Read current metadata for logging
        try:
            current_metadata = file_type_handler.extract_metadata(new_file)
            ui.update_progress(80)
        except Exception as e:
            # If metadata extraction fails, log the error but continue
            print(f"Warning: Error extracting metadata from new file: {e}")
            current_metadata = {"Error": str(e)}
            ui.update_progress(80)
        
        # Log the operation details
        try:
            stats = logger.log_operation(
                file_path, new_file, f"Metadata Modification - {metadata_type}", modified_tags,
                original_metadata, current_metadata
            )
        except Exception as e:
            # If logging fails, print warning but consider operation successful
            print(f"Warning: Error logging operation: {e}")
            # Create minimal stats dictionary
            stats = {
                'original_size': os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                'new_size': os.path.getsize(new_file) if os.path.exists(new_file) else 0,
                'size_reduction': 0,
                'size_reduction_percentage': 0
            }
        
        # Complete progress tracking
        ui.update_progress(20)
        ui.finish_progress()
        
        # Display results to user
        ui.show_operation_results(new_file, stats)
        
        return True
        
    except ValueError as e:
        # Specifically catch validation errors
        ui.finish_progress()
        ui.show_error(f"Validation error: {str(e)}")
        return False
    except Exception as e:
        ui.finish_progress()
        # Print full traceback for debugging
        print(f"Full error details: {traceback.format_exc()}")
        ui.show_error(f"Error during metadata operation: {str(e)}")
        return False

# FUNCTION Definition
def view_current_metadata(handlers, file_type_handler):
    """
    View metadata of the most recently processed file.
    
    Programming Concepts:
    - Tuple Unpacking: Handlers tuple
    - File Handling: File operations
    - Exception Handling: Try-except block
    - Type-Specific Handling: Using appropriate file type handler
    
    Args:
        handlers (tuple): Tuple containing UI, metadata, file, and logger handlers
        file_type_handler: Handler for the specific file type
    """
    # Unpack needed handlers
    ui, _, file_handler, _ = handlers
    
    # Get latest processed file
    latest_file = file_handler.get_latest_clean_file()
    if not latest_file:
        ui.show_error("No processed files found")
        return
        
    try:
        # Extract and display metadata using type-specific handler
        metadata = file_type_handler.extract_metadata(latest_file)
        ui.display_metadata(metadata)
    except Exception as e:
        ui.show_error(f"Error reading current metadata: {e}")

# FUNCTION Definition
def compare_metadata(file_path, handlers, file_type_handler):
    """
    Compare original and current metadata of processed file.
    
    Programming Concepts:
    - Tuple Unpacking: Handlers tuple
    - File Handling: File operations
    - Exception Handling: Try-except block
    - Type-Specific Handling: Using appropriate file type handler
    
    Args:
        file_path (str): Path to original file
        handlers (tuple): Tuple containing UI, metadata, file, and logger handlers
        file_type_handler: Handler for the specific file type
    """
    # Unpack needed handlers
    ui, _, file_handler, _ = handlers
    
    # Get latest processed file
    latest_file = file_handler.get_latest_clean_file()
    if not latest_file:
        ui.show_error("No processed files found to compare")
        return
        
    try:
        # Extract original metadata
        original_metadata = file_type_handler.extract_metadata(file_path)
        
        # Extract current metadata
        current_metadata = file_type_handler.extract_metadata(latest_file)
        
        # Display comparison
        ui.display_metadata_comparison(original_metadata, current_metadata)
    except Exception as e:
        ui.show_error(f"Error comparing metadata: {e}")

# FUNCTION Definition
def process_batch_files(metadata_type, handlers, file_type_handler, batch_files, add_metadata_func=None, metadata_dict=None):
    """
    Process multiple files in batch mode.
    
    Args:
        metadata_type (str): Type of metadata operation
        handlers (tuple): Tuple containing UI, metadata, file, and logger handlers
        file_type_handler: Handler for the specific file type
        batch_files (list): List of file paths to process
        add_metadata_func: Function to add metadata (optional)
        metadata_dict: Metadata values to add/modify (optional)
        
    Returns:
        bool: True if operation successful, False otherwise
    """
    # Unpack needed handlers
    ui, _, _, _ = handlers
    
    # Initialize batch processor
    batch_processor = BatchProcessor(ui)
    
    print(f"\nStarting batch processing of {len(batch_files)} files...")
    
    if metadata_type.startswith("mod_") and add_metadata_func and metadata_dict:
        # For add/modify metadata operations, wrap the function
        def add_metadata_wrapper(metadata_type, file_path, metadata_dict):
            return process_add_metadata(metadata_type, file_path, handlers, file_type_handler, metadata_dict)
        
        # Process files in batch
        success_count, failure_count, results = batch_processor.process_files_batch(
            batch_files, metadata_type, None, add_metadata_wrapper, metadata_dict
        )
    else:
        # For remove metadata operations
        def remove_metadata_wrapper(metadata_type, file_path):
            return process_metadata_removal(metadata_type, file_path, handlers, file_type_handler)
        
        # Process files in batch
        success_count, failure_count, results = batch_processor.process_files_batch(
            batch_files, metadata_type, remove_metadata_wrapper
        )
    
    # Display summary
    summary = batch_processor.get_batch_summary(results)
    print(summary)
    
    return success_count > 0

# FUNCTION Definition
def view_log_file(ui):
    """
    View an encrypted log file.
    
    Args:
        ui (UserInterface): UI handler
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Initialize secure log handler
        secure_handler = SecureLogHandler()
        
        # Get log file path
        log_file = input("\nEnter path to encrypted log file: ").strip()
        
        if not os.path.exists(log_file):
            ui.show_error(f"Log file not found: {log_file}")
            return False
        
        if not log_file.endswith('.enc'):
            ui.show_error("Not an encrypted log file (.enc extension required)")
            return False
        
        # Get password
        password = secure_handler.get_password()
        if not password:
            return False
        
        # Decrypt and display log file
        try:
            decrypted_content = secure_handler.decrypt_log_file(log_file, password)
            secure_handler.display_decrypted_log(decrypted_content)
            return True
        except Exception as e:
            ui.show_error(f"Error decrypting log file: {e}")
            return False
        
    except Exception as e:
        ui.show_error(f"Error viewing log file: {e}")
        return False

# FUNCTION Definition
def process_file(file_path, file_type_handler, handlers):
    """
    Process a single file with metadata operations.
    
    Args:
        file_path (str): Path to file
        file_type_handler: Handler for file type
        handlers (tuple): Handler components
        
    Returns:
        bool: True to continue with this file, False to select a new file
    """
    # Unpack UI handler
    ui, _, _, _ = handlers
    
    # Extract and display current metadata
    try:
        current_metadata = file_type_handler.extract_metadata(file_path)
        print(f"\nCurrent metadata for {os.path.basename(file_path)}:")
        ui.display_metadata(current_metadata)
    except Exception as e:
        ui.show_error(f"Error reading file metadata: {e}")
        # Continue anyway - don't return False
    
    # File processing loop
    while True:
        # Show file-specific metadata menu
        option, metadata_type = ui.show_file_metadata_menu(file_type_handler)
        
        # Handle menu options
        if option == "exit":
            return False
        elif option == "main_menu":
            return False
        elif option == "new_file":
            return False
        elif option == "view_metadata":
            view_current_metadata(handlers, file_type_handler)
        elif option == "compare_metadata":
            compare_metadata(file_path, handlers, file_type_handler)
        elif option.startswith("Add/Modify"):
            # Get metadata values from user
            metadata_dict = ui.get_metadata_values(metadata_type)
            
            if metadata_dict:
                # Process add/modify metadata operation
                process_add_metadata(metadata_type, file_path, handlers, file_type_handler, metadata_dict)
            else:
                print("No metadata values provided. Operation cancelled.")
        else:
            # Process remove metadata operation
            process_metadata_removal(metadata_type, file_path, handlers, file_type_handler)
    
    return True

# FUNCTION Definition
def main():
    """
    Main program entry point and control loop.
    
    Programming Concepts:
    - Object Instantiation: Handler class instances
    - OS Module Usage: Current working directory
    - Loop Control: While loops for program flow
    - Exception Handling: Validation errors handling
    - File Validation: Multiple layers of validation
    - File Type Handling: Support for different file formats
    - Batch Processing: Support for processing multiple files
    """
    # Initialize UI handler
    ui = UserInterface()
    
    # Display welcome screen
    ui.show_welcome_screen()
    
    # Setup log file with encryption option
    try:
        log_file_path, encrypt_log, password = ui.setup_log_file()
    except Exception as e:
        print(f"Error setting up log file: {e}")
        print("Please restart the application.")
        return
    
    # Initialize logger with encryption settings
    try:
        logger = MetadataLogger(log_file_path, encrypt_log, password)
    except ValueError as e:
        print(f"Error initializing logger: {e}")
        print("Please restart the application with a valid log file path.")
        return
    
    # Initialize other handlers
    metadata_handler = MetadataHandler()
    file_handler = FileHandler()
    
    # Package handlers for easier passing
    handlers = (ui, metadata_handler, file_handler, logger)
    
    # Initialize file type handlers
    file_type_handlers = {
        'jpg': JPGHandler(),
        'pdf': PDFHandler(),
        'word': WordHandler(),
        'excel': ExcelHandler()
    }
    
    # Main program loop
    while True:
        # Show main menu
        choice = ui.show_menu()
        
        # Process main menu choice
        if choice == '1':
            # Process files - first select file type
            file_type_key = ui.select_file_type(file_type_handlers)
            if not file_type_key:
                continue
            
            # Get file type handler
            file_type_handler = file_type_handlers[file_type_key]
            
            # Select processing mode (single or batch)
            mode = ui.select_processing_mode()
            if not mode:
                continue
            
            if mode == "single":
                # Single file processing
                # Get file path from user
                file_path = ui.get_file_path(file_type_handler)
                if not file_path:
                    continue
                
                # Process file with metadata operations
                process_file(file_path, file_type_handler, handlers)
                
            elif mode == "batch":
                # Batch processing
                # Get batch files
                batch_data, use_directory, recursive = ui.get_batch_files(file_type_handler)
                if not batch_data:
                    continue
                
                if use_directory:
                    # Find all matching files in directory
                    batch_processor = BatchProcessor(ui)
                    batch_files = batch_processor.find_files_by_extension(
                        batch_data, file_type_handler.file_extension, recursive
                    )
                    
                    if not batch_files:
                        ui.show_error(f"No {file_type_handler.display_name} files found in the directory.")
                        continue
                    
                    print(f"Found {len(batch_files)} {file_type_handler.display_name} files.")
                else:
                    # Use explicitly provided file list
                    batch_files = batch_data
                
                # Get metadata operation to perform on all files
                option, metadata_type = ui.show_file_metadata_menu(file_type_handler)
                
                # Handle menu options
                if option in ["exit", "main_menu", "new_file", "view_metadata", "compare_metadata"]:
                    continue
                
                if option.startswith("Add/Modify"):
                    # Get metadata values from user
                    metadata_dict = ui.get_metadata_values(metadata_type)
                    
                    if metadata_dict:
                        # Process batch with add/modify metadata
                        process_batch_files(
                            metadata_type, handlers, file_type_handler, batch_files,
                            process_add_metadata, metadata_dict
                        )
                    else:
                        print("No metadata values provided. Operation cancelled.")
                else:
                    # Process batch with remove metadata
                    process_batch_files(metadata_type, handlers, file_type_handler, batch_files)
        
        elif choice == '2':
            # View encrypted log file
            view_log_file(ui)
            
        elif choice == '3' or choice.lower() == 'exit':
            # Exit program
            ui.show_exit_message()
            break
            
        else:
            ui.show_error("Invalid choice. Please try again.")
                
# Script entry point
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
        print("Exiting program.")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        # Print full traceback for debugging
        print(f"Error details: {traceback.format_exc()}")
        print("Please restart the application.")