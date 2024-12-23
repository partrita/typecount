import tkinter as tk
from pynput.keyboard import Listener
import csv
from datetime import date
import os
from typing import Optional, Any

class TypingCounter:
    def __init__(self, master: tk.Tk) -> None:
        self.master: tk.Tk = master
        master.title("Typing Counter v2.2")
        master.geometry("300x150+100+100")

        self.count: int = 0
        self.is_counting: bool = False
        self.csv_file: str = "typing_count.csv"

        self.label: tk.Label = tk.Label(master, text="Count: 0", font=("Arial", 16, "bold"))
        self.label.pack(pady=10)

        # 첫 번째 버튼 프레임 (Start, Stop, Reset)
        button_frame1: tk.Frame = tk.Frame(master)
        button_frame1.pack(pady=5)

        self.start_button: tk.Button = tk.Button(button_frame1, text="Start", command=self.start_counting)
        self.start_button.pack(side=tk.LEFT, padx=5)

        self.stop_button: tk.Button = tk.Button(button_frame1, text="Stop", command=self.stop_counting, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.reset_button: tk.Button = tk.Button(button_frame1, text="Reset", command=self.reset_count)
        self.reset_button.pack(side=tk.LEFT, padx=5)

        # 두 번째 버튼 프레임 (Save, Quit)
        button_frame2: tk.Frame = tk.Frame(master)
        button_frame2.pack(pady=5)

        self.save_button: tk.Button = tk.Button(button_frame2, text="Save", command=self.save_count)
        self.save_button.pack(side=tk.LEFT, padx=5)

        self.quit_button: tk.Button = tk.Button(button_frame2, text="Quit", command=master.quit)
        self.quit_button.pack(side=tk.LEFT, padx=5)

        self.listener: Optional[Listener] = None

    def start_counting(self) -> None:
        self.is_counting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_counting(self) -> None:
        self.is_counting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.listener:
            self.listener.stop()

    def on_press(self, key: Any) -> None:
        if self.is_counting:
            self.count += 1
            self.label.config(text=f"Count: {self.count}")

    def reset_count(self) -> None:
        self.count = 0
        self.label.config(text=f"Count: {self.count}")

    def save_count(self) -> None:
        today: str = date.today().isoformat()
        data: list[str | int] = [today, self.count]
        
        file_exists: bool = os.path.isfile(self.csv_file)
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Count"])
            writer.writerow(data)
        
        print(f"Data saved: {data}")

def main() -> None:
    root: tk.Tk = tk.Tk()
    app: TypingCounter = TypingCounter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
