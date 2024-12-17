import tkinter as tk
from pynput.keyboard import Listener
import csv
from datetime import date
import os

class TypingCounter:
    def __init__(self, master):
        self.master = master
        master.title("Typing Counter v2.0")
        master.geometry("100x150+100+100")  # 창 크기를 절반으로 줄임

        self.count = 0
        self.is_counting = False
        self.csv_file = "typing_count.csv"

        self.label = tk.Label(master, text="Count: 0", font=("Arial", 16, "bold"))  # 카운트를 더 크게 표시
        self.label.pack(pady=10)

        button_frame = tk.Frame(master)
        button_frame.pack(pady=5)

        self.start_button = tk.Button(button_frame, text="Start", command=self.start_counting)
        self.start_button.pack(side=tk.LEFT, padx=5)  # 버튼을 수평으로 배치하고 간격을 둠

        self.stop_button = tk.Button(button_frame, text="Stop", command=self.stop_counting, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)

        self.save_button = tk.Button(master, text="Save", command=self.save_count)
        self.save_button.pack(pady=5)

        self.quit_button = tk.Button(master, text="Quit", command=master.quit)
        self.quit_button.pack(pady=5)

        self.listener = None

    def start_counting(self):
        self.is_counting = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = Listener(on_press=self.on_press)
        self.listener.start()

    def stop_counting(self):
        self.is_counting = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.listener:
            self.listener.stop()

    def on_press(self, key):
        if self.is_counting:
            self.count += 1
            self.label.config(text=f"Count: {self.count}")

    def save_count(self):
        today = date.today().isoformat()
        data = [today, self.count]
        
        file_exists = os.path.isfile(self.csv_file)
        
        with open(self.csv_file, 'a', newline='') as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Date", "Count"])
            writer.writerow(data)
        
        print(f"Data saved: {data}")

def main():
    root = tk.Tk()
    app = TypingCounter(root)
    root.mainloop()

if __name__ == "__main__":
    main()
