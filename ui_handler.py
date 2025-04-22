"""
UI Handler Module
===============

This module handles all user interface operations for the metadata scrubber.
It provides a command-line interface for user interaction.

Key Programming Concepts Used:
- Classes: UserInterface class implementation
- String Formatting: f-strings and alignment
- Input/Output: User interaction handling
- File Type Selection: Menu for file type selection
- Batch Processing: Interface for batch operations
"""

# Standard library imports
import os
import getpass
import traceback

# CLASS Definition
class UserInterface:
    """
    Handles all user interface operations.
    
    This class manages:
    - User input/output
    - Menu display
    - Result presentation
    - File type selection
    - Batch processing input
    """
    
    def __init__(self):
        """
        Initialize UserInterface instance.
        """
        pass  # No progress bar initialization

    # FUNCTION Definition
    def show_welcome_screen(self):
        """
        Display welcome message to user.
        
        Programming Concepts:
        - String Formatting: Multi-line output
        """
        
        print("\n" + "="*60)
        print("Welcome to Metascrubbot: Enhanced Metadata Management Tool!")
        print("Supporting: JPG, PDF, Word (.docx), and Excel (.xlsx) files")
        print("="*60 + "\n")

    # FUNCTION Definition
    def setup_log_file(self):
        """
        Get log file settings from user.
        
        Returns:
            tuple: (log_file_path, encrypt_log, password)
        """
        print("\nLog File Setup:")
        print("-" * 30)
        
        while True:
            custom_name = input("Use custom log file name? (y/n): ").strip().lower()
            
            if custom_name == 'y':
                custom_filename = input("Enter log file name (without extension): ").strip()
                if not custom_filename:
                    print("Invalid filename. Using default.")
                    log_file_path = self._get_default_logfile()
                else:
                    log_file_path = os.path.join(os.getcwd(), f"{custom_filename}.csv")
            else:
                log_file_path = self._get_default_logfile()
            
            encrypt_log = input("Encrypt log file? (y/n): ").strip().lower() == 'y'
            
            password = None
            if encrypt_log:
                # Change extension for encrypted logs
                log_file_path = log_file_path.replace(".csv", ".enc")
                
                # Get password with confirmation
                while True:
                    password = getpass.getpass("Enter encryption password: ")
                    confirm = getpass.getpass("Confirm password: ")
                    
                    if password == confirm:
                        break
                    else:
                        print("Passwords do not match. Please try again.")
            
            # Check if everything is valid
            try:
                # Validate log file path
                if os.path.exists(log_file_path):
                    overwrite = input(f"Log file '{log_file_path}' already exists. Overwrite? (y/n): ").strip().lower()
                    if overwrite != 'y':
                        continue
                
                return log_file_path, encrypt_log, password
            
            except Exception as e:
                print(f"Error with log file setup: {e}")
                print(f"Error details: {traceback.format_exc()}")
                # Use default settings if there's an error
                return os.path.join(os.getcwd(), "metadata_log.csv"), False, None
    
    def _get_default_logfile(self):
        """
        Generate a default log file name based on date and existing files.
        
        Returns:
            str: Default log file path
        """
        import datetime
        import glob
        
        today = datetime.datetime.now().strftime("%Y%m%d")
        base_name = f"metadata_changes_{today}"
        
        # Find existing log files with similar names
        pattern = os.path.join(os.getcwd(), f"{base_name}*.csv")
        existing_files = glob.glob(pattern)
        
        if not existing_files:
            return os.path.join(os.getcwd(), f"{base_name}.csv")
        else:
            # Find the highest number
            max_num = 0
            for file in existing_files:
                filename = os.path.basename(file)
                if filename == f"{base_name}.csv":
                    max_num = max(max_num, 1)
                else:
                    # Try to extract the number
                    try:
                        num_part = filename.replace(f"{base_name}_", "").replace(".csv", "")
                        num = int(num_part)
                        max_num = max(max_num, num + 1)
                    except (ValueError, IndexError):
                        pass
            
            # Use the next number
            if max_num == 0:
                return os.path.join(os.getcwd(), f"{base_name}.csv")
            else:
                return os.path.join(os.getcwd(), f"{base_name}_{max_num}.csv")

    # FUNCTION Definition
    def select_file_type(self, file_type_handlers):
        """
        Display a menu for selecting file type.
        
        Args:
            file_type_handlers (dict): Dictionary of file type handlers
            
        Returns:
            str or None: Selected file type key or None if exit
        """
        print("\nSelect File Type:")
        print("-" * 30)
        
        # Display file type options
        for i, (key, handler) in enumerate(file_type_handlers.items(), start=1):
            print(f"{i}. {handler.display_name}")
        
        print("\n0. Exit")
        
        # Get user choice
        while True:
            choice = input("\nEnter your choice (0-{}): ".format(len(file_type_handlers))).strip()
            
            if choice == "0" or choice.lower() == "exit":
                return None
            
            try:
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(file_type_handlers):
                    return list(file_type_handlers.keys())[choice_idx]
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a number.")

    # FUNCTION Definition
    def select_processing_mode(self):
        """
        Select between single file or batch processing mode.
        
        Returns:
            str: "single" or "batch"
        """
        print("\nSelect Processing Mode:")
        print("-" * 30)
        print("1. Process Single File")
        print("2. Process Multiple Files (Batch Mode)")
        print("\n0. Back")
        
        while True:
            choice = input("\nEnter your choice (0-2): ").strip()
            
            if choice == "0" or choice.lower() == "back":
                return None
            elif choice == "1":
                return "single"
            elif choice == "2":
                return "batch"
            else:
                print("Invalid choice. Please try again.")

    # FUNCTION Definition
    def get_file_path(self, file_type_handler=None):
        """
        Get file path from user input.
        
        Programming Concepts:
        - Input Handling: User input processing
        - String Methods: strip()
        - File Validation: Check for supported file types
        
        Args:
            file_type_handler: Handler for validating file type
            
        Returns:
            str or None: File path if provided, None if exit requested
        """
        extensions = ""
        if file_type_handler:
            extensions = ", ".join(file_type_handler.file_extension)
            extensions = f" ({extensions})"
        
        while True:
            file_path = input(f"\nPlease enter the path to your file{extensions} (or 'exit' to quit): ").strip()
            if file_path.lower() == 'exit':
                return None
            
            # Check if file exists
            if not os.path.exists(file_path):
                print(f"File not found: {file_path}")
                continue
                
            # Validate file type if handler provided
            if file_type_handler:
                try:
                    if file_type_handler.validate_file(file_path):
                        return file_path
                    else:
                        print(f"Invalid or unsupported file. Please select a {file_type_handler.display_name} file.")
                except ValueError as e:
                    print(f"Error: {e}")
                    print("Please select another file.")
            else:
                return file_path

    # FUNCTION Definition
    def get_batch_files(self, file_type_handler):
        """
        Get batch file processing settings.
        
        Args:
            file_type_handler: Handler for file type
            
        Returns:
            tuple: (file_paths, use_directory, recursive)
        """
        print("\nBatch Processing Setup:")
        print("-" * 30)
        
        # Choose between directory or file list
        print("1. Process all files in a directory")
        print("2. Enter file paths manually")
        print("\n0. Back")
        
        batch_choice = input("\nEnter your choice (0-2): ").strip()
        
        if batch_choice == "0" or batch_choice.lower() == "back":
            return None, False, False
        
        file_paths = []
        
        if batch_choice == "1":
            # Process directory
            directory = input("\nEnter directory path: ").strip()
            
            if not os.path.isdir(directory):
                print("Invalid directory path.")
                return None, False, False
            
            recursive = input("Search subdirectories too? (y/n): ").strip().lower() == 'y'
            
            # Return directory path and recursive flag
            return directory, True, recursive
        
        elif batch_choice == "2":
            # Manual file entry
            print("\nEnter file paths one per line. Enter an empty line when done.")
            
            while True:
                file_path = input("> ").strip()
                
                if not file_path:
                    break
                
                # Check if file exists
                if not os.path.exists(file_path):
                    print(f"File not found: {file_path}")
                    continue
                
                try:
                    if file_type_handler.validate_file(file_path):
                        file_paths.append(file_path)
                    else:
                        print(f"Skipping invalid or unsupported file: {file_path}")
                except ValueError as e:
                    print(f"Error with file {file_path}: {e}")
                    print("Skipping this file.")
            
            if not file_paths:
                print("No valid files entered.")
                return None, False, False
            
            return file_paths, False, False
        
        else:
            print("Invalid choice.")
            return None, False, False

    # FUNCTION Definition
    def show_file_metadata_menu(self, file_type_handler):
        """
        Display metadata operations menu specific to file type.
        
        Args:
            file_type_handler: Handler for file type
            
        Returns:
            tuple: (option_name, metadata_type)
        """
        options = file_type_handler.get_metadata_menu_options()
        
        print("\nMetadata Operations:")
        print("-" * 30)
        
        # Display metadata operations
        for i, (option_name, _) in enumerate(options, start=1):
            print(f"{i}. {option_name}")
        
        # Additional options
        print(f"{len(options) + 1}. View Current Metadata")
        print(f"{len(options) + 2}. Compare Original vs Current Metadata")
        print(f"{len(options) + 3}. Select New File")
        print(f"{len(options) + 4}. Back to Main Menu")
        
        # Get user choice
        while True:
            choice = input(f"\nEnter your choice (1-{len(options) + 4}): ").strip()
            
            try:
                choice_idx = int(choice) - 1
                
                # Handle metadata operations
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                
                # Handle additional options
                elif choice_idx == len(options):
                    return ("view_metadata", None)
                elif choice_idx == len(options) + 1:
                    return ("compare_metadata", None)
                elif choice_idx == len(options) + 2:
                    return ("new_file", None)
                elif choice_idx == len(options) + 3:
                    return ("main_menu", None)
                else:
                    print("Invalid choice. Please try again.")
            
            except ValueError:
                if choice.lower() == "exit":
                    return ("exit", None)
                else:
                    print("Please enter a number.")

    # FUNCTION Definition
    def get_metadata_values(self, metadata_type):
        """
        Get metadata values from user for add/modify operations.
        
        Args:
            metadata_type (str): Type of metadata to add/modify
            
        Returns:
            dict: Dictionary of metadata values
        """
        metadata_dict = {}
        
        # Handle different metadata types for different file formats
        if metadata_type == "mod_datetime":
            # For JPEG date/time
            print("\nEnter Date/Time Information:")
            print("-" * 30)
            
            date_time = input("Enter date and time (YYYY:MM:DD HH:MM:SS): ").strip()
            
            if date_time:
                metadata_dict["image"] = {"DateTime": date_time}
                metadata_dict["exif"] = {"DateTimeOriginal": date_time, "DateTimeDigitized": date_time}
        
        elif metadata_type == "mod_gps":
            # For JPEG GPS
            print("\nEnter GPS Information:")
            print("-" * 30)
            
            lat = input("Enter latitude (decimal degrees, e.g., 40.7128): ").strip()
            lon = input("Enter longitude (decimal degrees, e.g., -74.0060): ").strip()
            
            if lat and lon:
                try:
                    lat_float = float(lat)
                    lon_float = float(lon)
                    
                    # Convert to GPS format
                    metadata_dict["gps"] = {
                        "GPSLatitudeRef": "N" if lat_float >= 0 else "S",
                        "GPSLatitude": abs(lat_float),
                        "GPSLongitudeRef": "E" if lon_float >= 0 else "W",
                        "GPSLongitude": abs(lon_float)
                    }
                except ValueError:
                    print("Invalid coordinates. Using empty values.")
        
        elif metadata_type == "mod_camera":
            # For JPEG camera info
            print("\nEnter Camera Information:")
            print("-" * 30)
            
            make = input("Camera Make: ").strip()
            model = input("Camera Model: ").strip()
            
            if make or model:
                metadata_dict["image"] = {}
                if make:
                    metadata_dict["image"]["Make"] = make
                if model:
                    metadata_dict["image"]["Model"] = model
        
        elif metadata_type in ["mod_author", "mod_creator"]:
            # For document author
            print("\nEnter Author Information:")
            print("-" * 30)
            
            author = input("Author Name: ").strip()
            
            if author:
                if metadata_type == "mod_author":
                    metadata_dict["author"] = author
                    metadata_dict["creator"] = author
                else:
                    metadata_dict["creator"] = author
        
        elif metadata_type == "mod_title":
            # For document title
            print("\nEnter Title Information:")
            print("-" * 30)
            
            title = input("Document Title: ").strip()
            
            if title:
                metadata_dict["title"] = title
        
        elif metadata_type == "mod_subject":
            # For document subject
            print("\nEnter Subject Information:")
            print("-" * 30)
            
            subject = input("Document Subject: ").strip()
            
            if subject:
                metadata_dict["subject"] = subject
        
        elif metadata_type == "mod_keywords":
            # For document keywords
            print("\nEnter Keyword Information:")
            print("-" * 30)
            
            keywords = input("Keywords (comma-separated): ").strip()
            
            if keywords:
                metadata_dict["keywords"] = keywords
        
        elif metadata_type == "mod_category":
            # For document category
            print("\nEnter Category Information:")
            print("-" * 30)
            
            category = input("Document Category: ").strip()
            
            if category:
                metadata_dict["category"] = category
        
        elif metadata_type == "mod_comments":
            # For document comments
            print("\nEnter Comment Information:")
            print("-" * 30)
            
            comments = input("Comments: ").strip()
            
            if comments:
                metadata_dict["comments"] = comments
        
        elif metadata_type == "mod_description":
            # For document description
            print("\nEnter Description Information:")
            print("-" * 30)
            
            description = input("Description: ").strip()
            
            if description:
                metadata_dict["description"] = description
        
        return metadata_dict

    # FUNCTION Definition
    def show_menu(self):
        """
        Display main menu and get user choice.
        
        Programming Concepts:
        - String Formatting: Menu layout
        - Input Handling: User choice
        
        Returns:
            str: User's menu choice
        """
        print("\nMain Menu:")
        print("-" * 30)
        print("1. Process Files (Remove/Add Metadata)")
        print("2. View Encrypted Log File")
        print("3. Quit")
        print("\nType 'exit' at any time to quit the program")
        
        return input("\nEnter your choice (1-3): ").strip()

    # FUNCTION Definition
    def show_exit_message(self):
        """
        Display exit message to user.
        """
        print("\nThank you for using Metascrubbot!!")

    # FUNCTION Definition
    def start_progress(self):
        """
        Initialize progress for operations.
        No progress bar - just print the message.
        """
        print("Processing - please wait...")

    # FUNCTION Definition
    def update_progress(self, amount):
        """
        Update progress with simple percentage updates at key milestones.
        
        Args:
            amount (int): Amount to increment progress
        """
        # Only print at key milestones to avoid spamming the console
        if amount == 50:
            print("Processing: 50% complete...")
        elif amount == 90:
            print("Processing: 90% complete...")

    # FUNCTION Definition
    def finish_progress(self):
        """
        Close progress indication.
        """
        print("Processing: Complete!")

    # FUNCTION Definition
    def show_operation_results(self, new_file, stats):
        """
        Display results of metadata operation.
        
        Programming Concepts:
        - String Formatting: f-strings with number formatting
        
        Args:
            new_file (str): Path to processed file
            stats (dict): Operation statistics
        """
        print(f"\nMetadata operation completed successfully.")
        print(f"New file saved as: {new_file}")
        
        #if 'size_reduction' in stats:
            #print(f"Size reduction: {stats['size_reduction']:,} bytes "
                #f"({stats['size_reduction_percentage']:.2f}%)")

    # FUNCTION Definition
    def show_error(self, error_message):
        """
        Display error message to user.
        
        Args:
            error_message (str): Error message to display
        """
        print(f"\nError: {error_message}")

    # FUNCTION Definition
    def display_metadata(self, metadata):
        """
        Display metadata to user.
        
        Args:
            metadata (dict): Metadata dictionary
        """
        if not metadata:
            print("\nNo metadata found.")
            return
        
        print("\nMetadata:")
        print("-" * 50)
        
        for tag, value in sorted(metadata.items()):
            formatted_value = str(value)
            if len(formatted_value) > 50:
                formatted_value = formatted_value[:47] + "..."
            print(f"{tag:<30}: {formatted_value}")
        
        print("-" * 50)

    # FUNCTION Definition
    def display_metadata_comparison(self, original_metadata, current_metadata):
        """
        Display comparison between original and current metadata.
        
        Programming Concepts:
        - String Formatting: Table layout
        - Set Operations: Combining keys
        - Sort Operations: Sorted display
        
        Args:
            original_metadata (dict): Original metadata
            current_metadata (dict): Current metadata
        """
        # Handle error case where either metadata dict isn't valid
        if not isinstance(original_metadata, dict) or not isinstance(current_metadata, dict):
            print("\nError: Cannot compare metadata - invalid format.")
            if not isinstance(original_metadata, dict):
                print(f"Original metadata error: {original_metadata}")
            if not isinstance(current_metadata, dict):
                print(f"Current metadata error: {current_metadata}")
            return
            
        print("\nMetadata Comparison Analysis:")
        print("=" * 100)
        
        # Display summary counts
        print(f"Original metadata tags: {len(original_metadata)}")
        print(f"Current metadata tags: {len(current_metadata)}")
        print(f"Tags removed: {len(original_metadata) - len(current_metadata)}")
        print("=" * 100)
        
        # Display table header
        print(f"{'Tag':<30} | {'Status':<15} | {'Original Value':<25} | {'Current Value':<25}")
        print("=" * 100)
        
        # Get all unique tags
        all_tags = sorted(set(list(original_metadata.keys()) + list(current_metadata.keys())))
        
        # Display comparison for each tag
        for tag in all_tags:
            orig_value = original_metadata.get(tag, "Not present")
            curr_value = current_metadata.get(tag, "Removed")
            
            # Determine tag status
            if tag not in original_metadata:
                status = "Added"
            elif tag not in current_metadata:
                status = "Removed"
            elif orig_value != curr_value:
                status = "Modified"
            else:
                status = "Unchanged"
            
            # Format values for display (truncate if too long)
            if isinstance(orig_value, str) and len(orig_value) > 25:
                orig_value_display = orig_value[:22] + "..."
            else:
                orig_value_display = str(orig_value)[:25]
                
            if isinstance(curr_value, str) and len(curr_value) > 25:
                curr_value_display = curr_value[:22] + "..."
            else:
                curr_value_display = str(curr_value)[:25]
            
            # Display formatted comparison row
            print(f"{tag:<30} | {status:<15} | {orig_value_display:<25} | {curr_value_display:<25}")
                
        print("=" * 100)