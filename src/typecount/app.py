import tkinter as tk
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
        master.geometry("300x150+100+100")

        self.count = 0
        self.is_counting = False
        self.base_folder = Path(
            __file__
        ).parent  # 현재 스크립트 파일의 부모 폴더 (루트 폴더)
        self.data_folder = self.base_folder / "data"
        self.csv_file_path = self.data_folder / "typing_count.csv"
        self.listener: Optional[Listener] = None

        self._create_data_folder()
        self._create_widgets()

    def _create_data_folder(self) -> None:
        """데이터 폴더가 없으면 생성합니다."""
        self.data_folder.mkdir(parents=True, exist_ok=True)

    def _create_widgets(self) -> None:
        """UI 요소를 생성하고 배치합니다."""
        self.label = tk.Label(self.master, text="Count: 0", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # 버튼 프레임 1 (Start, Stop, Reset)
        button_frame1 = tk.Frame(self.master)
        button_frame1.pack(pady=5)
        self.start_button = tk.Button(
            button_frame1, text="Start", command=self.start_counting
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        self.stop_button = tk.Button(
            button_frame1, text="Stop", command=self.stop_counting, state=tk.DISABLED
        )
        self.stop_button.pack(side=tk.LEFT, padx=5)
        self.reset_button = tk.Button(
            button_frame1, text="Reset", command=self.reset_count
        )
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 버튼 프레임 2 (Save, Quit)
        button_frame2 = tk.Frame(self.master)
        button_frame2.pack(pady=5)
        self.save_button = tk.Button(
            button_frame2, text="Save", command=self.save_count
        )
        self.save_button.pack(side=tk.LEFT, padx=5)
        self.quit_button = tk.Button(
            button_frame2, text="Quit", command=self.master.quit
        )
        self.quit_button.pack(side=tk.LEFT, padx=5)

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
        file_exists = self.csv_file_path.is_file()

        with open(self.csv_file_path, "a", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Count"])
            writer.writerow(data)

        print(f"Data saved to: {self.csv_file_path}")


def main() -> None:
    root = tk.Tk()
    app = TypingCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
