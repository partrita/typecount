import tkinter as tk
from tkinter import filedialog, messagebox
from pynput.keyboard import Listener, Key
import csv
from datetime import date
import os
from pathlib import Path
from typing import Optional, Any, Dict
from collections import defaultdict
import matplotlib.pyplot as plt
import pandas as pd


class TypingCounter:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Typing Counter v0.3")
        master.geometry("400x250+100+100")  # Adjusted geometry for new buttons

        self.count = 0
        self.is_counting = False
        self.listener: Optional[Listener] = None
        self.key_counts: Dict[str, int] = defaultdict(int)  # 키별 카운트 저장

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

        # 버튼 프레임 2 (Save, View Stats)
        button_frame2 = tk.Frame(self.master)
        button_frame2.grid(row=2, column=0, pady=5)
        # Configure columns in button_frame2 for centering/distribution
        button_frame2.columnconfigure(0, weight=1)
        button_frame2.columnconfigure(1, weight=1)

        self.save_button = tk.Button(
            button_frame2, text="Save", command=self.save_count
        )
        self.save_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.stats_button = tk.Button(
            button_frame2, text="View Stats", command=self.view_key_stats
        )
        self.stats_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 버튼 프레임 3 (Visualize, Quit)
        button_frame3 = tk.Frame(self.master)
        button_frame3.grid(row=3, column=0, pady=5)
        # Configure columns in button_frame3 for centering/distribution
        button_frame3.columnconfigure(0, weight=1)
        button_frame3.columnconfigure(1, weight=1)

        self.visualize_button = tk.Button(
            button_frame3, text="Visualize Data", command=self.visualize_data
        )
        self.visualize_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.quit_button = tk.Button(
            button_frame3, text="Quit", command=self.master.quit
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
            
            # 키 이름을 문자열로 변환하여 저장
            key_name = self._get_key_name(key)
            self.key_counts[key_name] += 1
            
            self.label.config(text=f"Count: {self.count}")

    def _get_key_name(self, key: Any) -> str:
        """키 객체를 읽기 쉬운 문자열로 변환합니다."""
        try:
            # 일반 문자 키의 경우
            if hasattr(key, 'char') and key.char is not None:
                return key.char
            # 특수 키의 경우
            elif hasattr(key, 'name'):
                return key.name
            # Key 열거형의 경우
            else:
                return str(key).replace('Key.', '')
        except AttributeError:
            return str(key)

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
