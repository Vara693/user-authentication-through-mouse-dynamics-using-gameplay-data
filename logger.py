import csv
import time
import os
from datetime import datetime
from typing import Dict, Any

class MouseLogger:
    def __init__(self):
        self.current_file = None
        self.csv_writer = None
        self.file_handle = None
        self.start_time = None

    def start_logging(self, username: str, session_id: int):
        """Start logging mouse data for a session"""
        # Create user directory if it doesn't exist
        user_dir = f"data/{username}"
        if not os.path.exists(user_dir):
            os.makedirs(user_dir)

        # Create CSV file for this session
        self.current_file = f"{user_dir}/session_{session_id}.csv"
        self.file_handle = open(self.current_file, 'w', newline='')
        self.csv_writer = csv.writer(self.file_handle)

        # Write header
        self.csv_writer.writerow([
            'timestamp', 'event_type', 'x', 'y', 
            'button', 'pressed', 'drag_data'
        ])

        self.start_time = time.time()
        print(f"Started logging to {self.current_file}")

    def log_event(self, event_type: str, x: int, y: int, 
                 button: str = None, pressed: bool = None, 
                 drag_data: str = None):
        """Log a mouse event"""
        if not self.csv_writer:
            return

        timestamp = time.time() - self.start_time
        self.csv_writer.writerow([
            f"{timestamp:.6f}",
            event_type,
            x, y,
            button or '',
            pressed if pressed is not None else '',
            drag_data or ''
        ])
        self.file_handle.flush()

    def stop_logging(self):
        """Stop logging and close file"""
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None
            self.csv_writer = None
            self.current_file = None
            print("Stopped logging")