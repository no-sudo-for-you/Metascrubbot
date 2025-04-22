"""
Secure Log Handler Module
========================

This module handles secure logging operations with encryption/decryption.
It provides functionality to encrypt and decrypt log files.

Key Programming Concepts Used:
- Classes: SecureLogHandler class implementation
- Encryption: Fernet symmetric encryption
- Password Handling: Password hashing
- File Handling: Binary file operations
- Exception Handling: Try-except blocks
"""

# Standard library imports
import os
import csv
from io import StringIO
import base64
import getpass
import traceback

# Check if cryptography library is available
try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    print("Warning: cryptography module not available. Secure logging will be disabled.")
    CRYPTO_AVAILABLE = False

# CLASS Definition
class SecureLogHandler:
    """
    Handles secure log file operations with encryption/decryption.
    
    This class manages:
    - Log file encryption
    - Log file decryption
    - Password handling
    - Secure file operations
    """
    
    def __init__(self):
        """Initialize SecureLogHandler instance."""
        if not CRYPTO_AVAILABLE:
            print("Warning: Secure operations will not be available without the cryptography module.")
            print("Please install it with: pip install cryptography")
            
        # Salt for password hashing
        self.salt = b'metascrubbotsalt123456'  # Should ideally be randomized and stored
    
    def _get_key_from_password(self, password):
        """
        Derive an encryption key from a password.
        
        Args:
            password (str): User password
            
        Returns:
            bytes: Encryption key
        """
        if not CRYPTO_AVAILABLE:
            raise Exception("Cryptography module not available")
            
        # Convert password to bytes
        password_bytes = password.encode()
        
        # Use PBKDF2HMAC to derive a key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=self.salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password_bytes))
        
        return key
    
    def encrypt_log_file(self, input_file, output_file, password):
        """
        Encrypt a log file with a password.
        
        Args:
            input_file (str): Path to input file
            output_file (str): Path to output encrypted file
            password (str): Encryption password
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            Exception: If encryption fails
        """
        if not CRYPTO_AVAILABLE:
            raise Exception("Cryptography module not available for encryption")
            
        try:
            # Get encryption key from password
            key = self._get_key_from_password(password)
            fernet = Fernet(key)
            
            # Read input file
            with open(input_file, 'rb') as f:
                data = f.read()
            
            # Encrypt data
            encrypted_data = fernet.encrypt(data)
            
            # Write encrypted data to output file
            with open(output_file, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error encrypting log file: {e}")
            print(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Error encrypting log file: {e}")
    
    def decrypt_log_file(self, input_file, password):
        """
        Decrypt a log file with a password.
        
        Args:
            input_file (str): Path to encrypted file
            password (str): Decryption password
            
        Returns:
            str: Decrypted data as string
            
        Raises:
            Exception: If decryption fails
        """
        if not CRYPTO_AVAILABLE:
            raise Exception("Cryptography module not available for decryption")
            
        try:
            # Get encryption key from password
            key = self._get_key_from_password(password)
            fernet = Fernet(key)
            
            # Read encrypted file
            with open(input_file, 'rb') as f:
                encrypted_data = f.read()
            
            # Decrypt data
            try:
                decrypted_data = fernet.decrypt(encrypted_data)
            except Exception as e:
                # More specific error for incorrect password
                if "Invalid token" in str(e):
                    raise Exception("Incorrect password or corrupted file")
                else:
                    raise
            
            # Return as string
            return decrypted_data.decode('utf-8')
        except Exception as e:
            print(f"Error decrypting log file: {e}")
            print(f"Error details: {traceback.format_exc()}")
            raise Exception(f"Error decrypting log file: {e}")
    
    def display_decrypted_log(self, log_content):
        """
        Display decrypted log content in a tabular format with row numbers.
        
        Args:
            log_content (str): Decrypted log content
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Parse CSV content
            csv_reader = csv.reader(StringIO(log_content))
            rows = list(csv_reader)
            
            if not rows:
                print("Log file is empty.")
                return True
            
            # Get headers
            headers = rows[0]
            data_rows = rows[1:]
            
            # Display table
            print("\nLog File Contents:")
            print("=" * 124)
            
            # Print headers with row number column
            header_cols = min(5, len(headers))
            header_row = f"{'Row #':<6} | "
            for i in range(header_cols):
                header_row += f"{headers[i]:<20} | "
            print(header_row)
            print("-" * 124)
            
            # Print data rows with row numbers
            for row_num, row in enumerate(data_rows, 1):
                data_row = f"{row_num:<6} | "
                for i in range(min(header_cols, len(row))):
                    # Truncate long cell values
                    cell_val = row[i][:18] if len(row[i]) > 18 else row[i]
                    data_row += f"{cell_val:<20} | "
                print(data_row)
            
            print("=" * 124)
            
            # Ask if user wants to see all details for a specific row
            while True:
                choice = input("\nView details for a specific row? (row number/n): ").strip().lower()
                if choice == 'n':
                    break
                
                try:
                    row_num = int(choice)
                    if 1 <= row_num <= len(data_rows):
                        print("\nDetailed View:")
                        print("=" * 100)
                        row = data_rows[row_num-1]
                        for i, header in enumerate(headers):
                            if i < len(row):
                                print(f"{header:<30}: {row[i]}")
                            else:
                                print(f"{header:<30}: <empty>")
                        print("=" * 100)
                    else:
                        print(f"Invalid row number. Please enter a number between 1 and {len(data_rows)}.")
                except ValueError:
                    print("Please enter a valid row number or 'n'.")
            
            return True
        except Exception as e:
            print(f"Error displaying log: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return False
    
    def get_password(self, confirm=False):
        """
        Get password from user input (masked).
        
        Args:
            confirm (bool): Whether to confirm password entry
            
        Returns:
            str: Password entered
        """
        try:
            password = getpass.getpass("Enter password: ")
            
            if confirm:
                confirm_password = getpass.getpass("Confirm password: ")
                if password != confirm_password:
                    print("Passwords do not match!")
                    return None
            
            return password
        except Exception as e:
            print(f"Error getting password: {e}")
            print(f"Error details: {traceback.format_exc()}")
            return None