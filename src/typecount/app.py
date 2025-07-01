import tkinter as tk
from tkinter import filedialog
from pynput.keyboard import Listener
import csv
from datetime import date
import os
from pathlib import Path
from typing import Optional, Any


class TypingCounter:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Typing Counter v0.2")
        master.geometry("350x200+100+100")  # Adjusted geometry

        self.count = 0
        self.is_counting = False
        self.listener: Optional[Listener] = None

        self._create_widgets()

    def _create_widgets(self) -> None:
        """UI 요소를 생성하고 배치합니다."""
        # Configure master column for centering frames
        self.master.columnconfigure(0, weight=1)

        self.label = tk.Label(self.master, text="Count: 0", font=("Arial", 16, "bold"))
        self.label.grid(row=0, column=0, pady=10, sticky="ew")

        # 버튼 프레임 1 (Start, Stop, Reset)
        button_frame1 = tk.Frame(self.master)
        button_frame1.grid(row=1, column=0, pady=5)
        # Configure columns in button_frame1 to be of equal weight for centering/distribution
        button_frame1.columnconfigure(0, weight=1)
        button_frame1.columnconfigure(1, weight=1)
        button_frame1.columnconfigure(2, weight=1)

        self.start_button = tk.Button(
            button_frame1, text="Start", command=self.start_counting
        )
        self.start_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.stop_button = tk.Button(
            button_frame1, text="Stop", command=self.stop_counting, state=tk.DISABLED
        )
        self.stop_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.reset_button = tk.Button(
            button_frame1, text="Reset", command=self.reset_count
        )
        self.reset_button.grid(row=0, column=2, padx=5, pady=5, sticky="ew")

        # 버튼 프레임 2 (Save, Quit)
        button_frame2 = tk.Frame(self.master)
        button_frame2.grid(row=2, column=0, pady=5)
        # Configure columns in button_frame2 for centering/distribution
        button_frame2.columnconfigure(0, weight=1)
        button_frame2.columnconfigure(1, weight=1)

        self.save_button = tk.Button(
            button_frame2, text="Save", command=self.save_count
        )
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.quit_button = tk.Button(
            button_frame2, text="Quit", command=self.master.quit
        )
        self.quit_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

    def start_counting(self) -> None:
        """타이핑 카운트를 시작하고 UI를 업데이트합니다."""
        self.is_counting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = Listener(on_press=self._on_press)
        self.listener.start()

    def stop_counting(self) -> None:
        """타이핑 카운트를 중지하고 UI를 업데이트합니다."""
        self.is_counting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.listener:
            self.listener.stop()

    def _on_press(self, key: Any) -> None:
        """키가 눌릴 때마다 카운트를 증가시키고 UI를 업데이트합니다."""
        if self.is_counting:
            self.count += 1
            self.label.config(text=f"Count: {self.count}")

    def reset_count(self) -> None:
        """카운트를 0으로 초기화하고 UI를 업데이트합니다."""
        self.count = 0
        self.label.config(text=f"Count: {self.count}")

    def save_count(self) -> None:
        """현재 카운트를 CSV 파일에 저장합니다."""
        today = date.today().isoformat()
        data = [today, self.count]

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="typing_count.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filepath:  # User cancelled the dialog
            return

        file_path_obj = Path(filepath)
        file_exists = file_path_obj.is_file()

        with open(file_path_obj, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Count"])
            writer.writerow(data)

        print(f"Data saved to: {file_path_obj}")


def main() -> None:
    root = tk.Tk()
    app = TypingCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
