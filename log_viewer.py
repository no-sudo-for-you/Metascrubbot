#!/usr/bin/env python3
"""
Log Viewer Script
===============

This standalone script allows users to view encrypted log files.
It provides a simple interface to select and decrypt log files.

Key Programming Concepts Used:
- File Selection: Browse and select encrypted log files
- Password Handling: Secure password entry
- Encrypted File Reading: Decrypt and display encrypted files
- User Interface: Simple command-line interface
"""

# Standard library imports
import os
import sys
import glob
import getpass

# Import secure log handler
try:
    from secure_log_handler import SecureLogHandler
except ImportError:
    print("Error: secure_log_handler.py not found.")
    print("Please make sure it's in the same directory as this script.")
    sys.exit(1)

def clear_screen():
    """Clear the console screen."""
    # Check if Windows or Unix
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def find_log_files(directory):
    """
    Find all encrypted log files in the directory.
    
    Args:
        directory (str): Directory to search
        
    Returns:
        list: List of log file paths
    """
    # Look for .enc files (encrypted logs)
    pattern = os.path.join(directory, "*.enc")
    return glob.glob(pattern)

def show_banner():
    """Display application banner."""
    print("\n" + "="*50)
    print("Metascrubbot: Encrypted Log Viewer")
    print("="*50 + "\n")

def select_log_file(files):
    """
    Display a menu of log files and get user selection.
    
    Args:
        files (list): List of log file paths
        
    Returns:
        str or None: Selected file path or None if exit
    """
    print("\nAvailable Log Files:")
    for i, file_path in enumerate(files, 1):
        file_name = os.path.basename(file_path)
        file_size = os.path.getsize(file_path)
        modified_time = os.path.getmtime(file_path)
        import datetime
        modified_str = datetime.datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
        print(f"{i}. {file_name:<30} ({file_size} bytes) - Modified: {modified_str}")
    
    print("\n0. Exit")
    
    while True:
        try:
            choice = input("\nSelect a file number or enter path: ").strip()
            
            # Check for exit
            if choice == "0" or choice.lower() == "exit":
                return None
            
            # Try to interpret as number
            if choice.isdigit():
                idx = int(choice) - 1
                if 0 <= idx < len(files):
                    return files[idx]
                else:
                    print("Invalid selection. Please try again.")
            else:
                # Interpret as path
                if os.path.exists(choice) and choice.endswith('.enc'):
                    return choice
                else:
                    print("Invalid file path. Please try again.")
        except (ValueError, IndexError):
            print("Invalid input. Please try again.")

def main():
    """Main function to run the log viewer."""
    clear_screen()
    show_banner()
    
    # Create secure log handler
    secure_handler = SecureLogHandler()
    
    # Get current directory
    current_dir = os.getcwd()
    
    # Find log files
    log_files = find_log_files(current_dir)
    
    if not log_files:
        print("\nNo encrypted log files found in the current directory.")
        print("Please make sure log files with .enc extension are present.")
        return
    
    # Select log file
    file_path = select_log_file(log_files)
    if file_path is None:
        print("\nExiting log viewer.")
        return
    
    # Get password
    password = getpass.getpass("\nEnter password to decrypt the log file: ")
    
    try:
        # Decrypt and display log file
        decrypted_content = secure_handler.decrypt_log_file(file_path, password)
        
        # Display decrypted content
        secure_handler.display_decrypted_log(decrypted_content)
        
        # Wait for user to finish
        input("\nPress Enter to exit...")
        
    except Exception as e:
        print(f"\nError: {e}")
        print("This could be due to an incorrect password or corrupted file.")
        
        # Wait before exit
        input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
