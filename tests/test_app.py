import unittest
import tkinter as tk
import csv
import tempfile
import os
from datetime import date
from unittest.mock import (
    patch,
    mock_open,
)
from pathlib import Path

# Adjust the import path if your project structure requires it
from src.typecount.app import TypingCounter


class TestTypingCounterSaveCount(unittest.TestCase):
    def setUp(self):
        """Set up for each test."""
        self.master = tk.Tk()
        # Prevent the Tkinter window from appearing during tests
        self.master.withdraw()
        self.app = TypingCounter(self.master)
        # Create a temporary directory for test files
        self.temp_dir_context = tempfile.TemporaryDirectory()
        self.temp_dir_name = self.temp_dir_context.name

    def tearDown(self):
        """Clean up after each test."""
        # Destroy the temporary directory and its contents
        self.temp_dir_context.cleanup()
        # Destroy the Tkinter master window
        self.master.destroy()

    @patch("src.typecount.app.filedialog.asksaveasfilename")
    @patch("src.typecount.app.messagebox.showinfo")
    def test_save_to_new_file(self, mock_showinfo, mock_asksaveasfilename):
        """Test saving data to a new CSV file."""
        test_filename = Path(self.temp_dir_name) / "new_test_data.csv"
        mock_asksaveasfilename.return_value = str(test_filename)

        self.app.count = 123
        self.app.save_count()

        mock_asksaveasfilename.assert_called_once()
        self.assertTrue(test_filename.is_file())

        with open(test_filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader)
            self.assertEqual(header, ["Date", "Count"])
            data_row = next(reader)
            self.assertEqual(data_row, [date.today().isoformat(), "123"])
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    @patch("src.typecount.app.filedialog.asksaveasfilename")
    @patch("src.typecount.app.messagebox.showinfo")
    def test_append_to_existing_file(self, mock_showinfo, mock_asksaveasfilename):
        """Test appending data to an existing CSV file."""
        test_filename = Path(self.temp_dir_name) / "existing_test_data.csv"

        # Pre-populate the file
        initial_data = [["Date", "Count"], ["2023-01-01", "100"]]
        with open(test_filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerows(initial_data)

        mock_asksaveasfilename.return_value = str(test_filename)

        self.app.count = 456
        self.app.save_count()

        mock_asksaveasfilename.assert_called_once()

        with open(test_filename, "r", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            # Check header
            header = next(reader)
            self.assertEqual(header, ["Date", "Count"])
            # Check original data
            data_row1 = next(reader)
            self.assertEqual(data_row1, ["2023-01-01", "100"])
            # Check appended data
            data_row2 = next(reader)
            self.assertEqual(data_row2, [date.today().isoformat(), "456"])
            with self.assertRaises(StopIteration):  # Ensure no more rows
                next(reader)

    @patch("src.typecount.app.filedialog.asksaveasfilename")
    @patch(
        "src.typecount.app.open", new_callable=mock_open
    )
    def test_save_cancel_dialog(self, mock_file_open, mock_asksaveasfilename):
        """Test user cancelling the save dialog."""
        mock_asksaveasfilename.return_value = None  # Simulate user cancelling

        self.app.count = 789
        self.app.save_count()

        mock_asksaveasfilename.assert_called_once()
        mock_file_open.assert_not_called()

        files_in_temp_dir = os.listdir(self.temp_dir_name)
        self.assertEqual(
            len(files_in_temp_dir),
            0,
            "No files should be created if save is cancelled.",
        )


if __name__ == "__main__":
    unittest.main()
