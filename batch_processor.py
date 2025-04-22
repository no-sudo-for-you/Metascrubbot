"""
Batch Processor Module
====================

This module handles batch processing of files using multithreading.
It provides functionality to process multiple files concurrently.

Key Programming Concepts Used:
- Classes: BatchProcessor class implementation
- Multithreading: Concurrent file processing
- Directory Iteration: Finding files by extension
- Thread Pool: Managing concurrent processing
- Progress Tracking: Tracking batch progress
- File Filtering: Filter files by type
"""

# Standard library imports
import os
import glob
import time
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from queue import Queue, Empty

# CLASS Definition
class BatchProcessor:
    """
    Handles batch processing of files using multithreading.
    
    This class manages:
    - File discovery by type
    - Concurrent processing
    - Progress tracking
    - Thread management
    """
    
    def __init__(self, ui_handler):
        """
        Initialize BatchProcessor instance.
        
        Args:
            ui_handler: UserInterface instance for progress updates
        """
        self.ui_handler = ui_handler
        self.results = []
        self.results_lock = threading.Lock()
        self.files_processed = 0
        self.files_processed_lock = threading.Lock()
        # Limit max threads to balance performance and stability
        self.max_threads = min(os.cpu_count() or 2, 4)  # Limit max threads to 4 or CPU count
    
    def find_files_by_extension(self, directory, extensions, recursive=False):
        """
        Find all files with specified extensions in a directory.
        
        Args:
            directory (str): Directory to search
            extensions (list): List of file extensions to find
            recursive (bool): Whether to search recursively
            
        Returns:
            list: List of file paths
        """
        if not os.path.isdir(directory):
            return []
        
        found_files = []
        
        # Convert extensions to lowercase for case-insensitive matching
        extensions = [ext.lower() for ext in extensions]
        
        if recursive:
            # For recursive search, use os.walk
            for root, _, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.splitext(file_path)[1].lower() in extensions:
                        found_files.append(file_path)
        else:
            # For non-recursive search, use glob pattern matching
            for ext in extensions:
                # Ensure the extension starts with a dot
                if not ext.startswith('.'):
                    ext = '.' + ext
                pattern = os.path.join(directory, f"*{ext}")
                found_files.extend(glob.glob(pattern))
        
        return found_files
    
    def process_file_worker(self, file_path, metadata_type, process_func, total_files, result_queue):
        """
        Worker function to process a single file in a thread.
        
        Args:
            file_path (str): Path to file
            metadata_type (str): Type of metadata operation
            process_func: Function to process the file
            total_files (int): Total number of files for progress
            result_queue: Queue to store results
        """
        try:
            # Process the file
            success = process_func(metadata_type, file_path)
            
            # Add result to queue
            result_queue.put((file_path, success))
            
            # Update progress
            with self.files_processed_lock:
                self.files_processed += 1
                progress = int((self.files_processed / total_files) * 100)
                
                # Print progress message rather than updating a progress bar
                print(f"Processed {self.files_processed}/{total_files} files ({progress}%)")
        
        except Exception as e:
            # Log the full error with traceback for debugging
            print(f"Error processing file {file_path}: {e}")
            print(f"Error details: {traceback.format_exc()}")
            
            # Add failure result to queue
            result_queue.put((file_path, False))
    
    def process_files_batch(self, file_paths, metadata_type, process_func, add_metadata_func=None, metadata_dict=None):
        """
        Process multiple files concurrently with multiple threads.
        
        Args:
            file_paths (list): List of file paths to process
            metadata_type (str): Type of metadata operation
            process_func: Function to process a file
            add_metadata_func: Function to add metadata (optional)
            metadata_dict: Metadata to add (optional)
            
        Returns:
            tuple: (success_count, failure_count, list of results)
        """
        total_files = len(file_paths)
        if total_files == 0:
            return 0, 0, []
        
        # Reset counters
        self.files_processed = 0
        self.results = []
        
        # Create a queue for results
        result_queue = Queue()
        
        # Limit number of threads based on file count and system capability
        num_threads = min(self.max_threads, total_files)
        
        print(f"Starting batch processing with {num_threads} threads...")
        
        # Start timer
        start_time = time.time()
        
        # Use ThreadPoolExecutor to manage threads
        with ThreadPoolExecutor(max_workers=num_threads) as executor:
            # Submit all tasks
            for file_path in file_paths:
                if metadata_type.startswith("mod_") and add_metadata_func and metadata_dict:
                    # For add/modify metadata operations
                    executor.submit(
                        self.process_add_metadata_worker, 
                        file_path, 
                        metadata_type,
                        add_metadata_func,
                        metadata_dict,
                        total_files,
                        result_queue
                    )
                else:
                    # For remove metadata operations
                    executor.submit(
                        self.process_file_worker, 
                        file_path, 
                        metadata_type, 
                        process_func, 
                        total_files, 
                        result_queue
                    )
        
        # Collect results from queue
        results = []
        while not result_queue.empty():
            try:
                result = result_queue.get(block=False)
                results.append(result)
            except Empty:
                break
        
        # Count successes and failures
        success_count = sum(1 for _, success in results if success)
        failure_count = len(results) - success_count
        
        # End timer
        end_time = time.time()
        total_time = end_time - start_time
        
        print(f"Batch processing completed in {total_time:.2f} seconds")
        print(f"Successes: {success_count}, Failures: {failure_count}")
        
        return success_count, failure_count, results
    
    def process_add_metadata_worker(self, file_path, metadata_type, add_metadata_func, metadata_dict, total_files, result_queue):
        """
        Worker function to add metadata to a single file in a thread.
        
        Args:
            file_path (str): Path to file
            metadata_type (str): Type of metadata operation
            add_metadata_func: Function to add metadata
            metadata_dict: Metadata dictionary to add
            total_files (int): Total number of files for progress
            result_queue: Queue to store results
        """
        try:
            # Process the file
            success = add_metadata_func(metadata_type, file_path, metadata_dict)
            
            # Add result to queue
            result_queue.put((file_path, success))
            
            # Update progress
            with self.files_processed_lock:
                self.files_processed += 1
                progress = int((self.files_processed / total_files) * 100)
                
                # Print progress message rather than updating a progress bar
                print(f"Processed {self.files_processed}/{total_files} files ({progress}%)")
        
        except Exception as e:
            # Log the full error with traceback for debugging
            print(f"Error processing file {file_path}: {e}")
            print(f"Error details: {traceback.format_exc()}")
            
            # Add failure result to queue
            result_queue.put((file_path, False))
            
    def get_batch_summary(self, results):
        """
        Generate a summary of batch processing results.
        
        Args:
            results (list): List of (file_path, success) tuples
            
        Returns:
            str: Summary text
        """
        if not results:
            return "No files were processed."
        
        success_count = sum(1 for _, success in results if success)
        failure_count = len(results) - success_count
        
        summary = f"\nBatch Processing Summary:\n"
        summary += f"=====================\n"
        summary += f"Total files processed: {len(results)}\n"
        summary += f"Successful: {success_count}\n"
        summary += f"Failed: {failure_count}\n"
        
        if failure_count > 0:
            summary += f"\nFailed files:\n"
            for file_path, success in results:
                if not success:
                    summary += f"- {os.path.basename(file_path)}\n"
        
        return summary