import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pynput.keyboard import Listener, Key
import csv
from datetime import date, datetime
import os
from pathlib import Path
from typing import Optional, Any, Dict
from collections import defaultdict
import time


class TypingCounter:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Typing Counter v0.4 - Enhanced")
        master.geometry("450x300+100+100")  # Adjusted geometry for new features

        self.count = 0
        self.is_counting = False
        self.listener: Optional[Listener] = None
        self.key_counts: Dict[str, int] = defaultdict(int)  # 키별 카운트 저장
        
        # 세션 추적을 위한 새로운 속성들
        self.session_start_time: Optional[datetime] = None
        self.session_end_time: Optional[datetime] = None
        self.total_session_time: float = 0.0  # 초 단위

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

        # 세션 정보 표시 라벨
        self.session_info_label = tk.Label(
            self.master, text="Session: Not started", font=("Arial", 10)
        )
        self.session_info_label.grid(row=4, column=0, pady=5, sticky="ew")

    def start_counting(self) -> None:
        """타이핑 카운트를 시작하고 UI를 업데이트합니다."""
        self.is_counting = True
        self.session_start_time = datetime.now()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = Listener(on_press=self._on_press)
        self.listener.start()
        self._update_session_info()

    def stop_counting(self) -> None:
        """타이핑 카운트를 중지하고 UI를 업데이트합니다."""
        self.is_counting = False
        self.session_end_time = datetime.now()
        if self.session_start_time:
            session_duration = (self.session_end_time - self.session_start_time).total_seconds()
            self.total_session_time += session_duration
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.listener:
            self.listener.stop()
        self._update_session_info()

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
        self.key_counts.clear()
        self.total_session_time = 0.0
        self.session_start_time = None
        self.session_end_time = None
        self.label.config(text=f"Count: {self.count}")
        self._update_session_info()

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

    def _update_session_info(self) -> None:
        """세션 정보를 업데이트합니다."""
        if self.is_counting and self.session_start_time:
            current_time = datetime.now()
            current_session_time = (current_time - self.session_start_time).total_seconds()
            total_time = self.total_session_time + current_session_time
            wpm = self._calculate_wpm(total_time)
            self.session_info_label.config(
                text=f"Session: {total_time:.1f}s | WPM: {wpm:.1f}"
            )
            # 1초마다 업데이트
            self.master.after(1000, self._update_session_info)
        elif self.total_session_time > 0:
            wpm = self._calculate_wpm(self.total_session_time)
            self.session_info_label.config(
                text=f"Session: {self.total_session_time:.1f}s | WPM: {wpm:.1f}"
            )
        else:
            self.session_info_label.config(text="Session: Not started")

    def _calculate_wpm(self, session_time_seconds: float) -> float:
        """WPM (Words Per Minute)을 계산합니다. 평균 5글자를 1단어로 계산."""
        if session_time_seconds <= 0:
            return 0.0
        words = self.count / 5  # 평균 5글자를 1단어로 계산
        minutes = session_time_seconds / 60
        return words / minutes if minutes > 0 else 0.0

    def view_key_stats(self) -> None:
        """키별 통계를 새 창에 표시합니다."""
        if not self.key_counts:
            messagebox.showinfo("통계", "아직 타이핑 데이터가 없습니다.")
            return

        # 새 창 생성
        stats_window = tk.Toplevel(self.master)
        stats_window.title("키별 통계")
        stats_window.geometry("400x300")

        # 스크롤 가능한 텍스트 위젯
        text_widget = scrolledtext.ScrolledText(stats_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 키 통계를 빈도순으로 정렬
        sorted_keys = sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)
        
        stats_text = f"총 키 입력 수: {self.count}\n"
        stats_text += f"고유 키 수: {len(self.key_counts)}\n"
        stats_text += f"세션 시간: {self.total_session_time:.1f}초\n"
        stats_text += f"WPM: {self._calculate_wpm(self.total_session_time):.1f}\n\n"
        stats_text += "키별 입력 횟수 (빈도순):\n"
        stats_text += "-" * 30 + "\n"

        for key, count in sorted_keys:
            percentage = (count / self.count) * 100 if self.count > 0 else 0
            stats_text += f"{key}: {count}회 ({percentage:.1f}%)\n"

        text_widget.insert(tk.END, stats_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용으로 설정

    def visualize_data(self) -> None:
        """키 입력 데이터를 텍스트 형태로 시각화합니다."""
        if not self.key_counts:
            messagebox.showinfo("시각화", "아직 타이핑 데이터가 없습니다.")
            return

        # 새 창 생성
        viz_window = tk.Toplevel(self.master)
        viz_window.title("키 입력 시각화")
        viz_window.geometry("500x400")

        # 스크롤 가능한 텍스트 위젯
        text_widget = scrolledtext.ScrolledText(viz_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 상위 15개 키만 표시
        sorted_keys = sorted(self.key_counts.items(), key=lambda x: x[1], reverse=True)
        top_keys = sorted_keys[:15]
        
        if not top_keys:
            text_widget.insert(tk.END, "표시할 데이터가 없습니다.")
            return

        # 텍스트 기반 막대 그래프 생성
        viz_text = f"키 입력 빈도 시각화 (상위 15개)\n"
        viz_text += "=" * 50 + "\n\n"
        
        max_count = max(count for _, count in top_keys)
        bar_width = 30  # 막대 그래프의 최대 너비
        
        for key, count in top_keys:
            # 키 이름을 적절한 길이로 맞춤
            key_display = key if len(key) <= 8 else key[:8]
            key_display = f"{key_display:>8}"
            
            # 막대 그래프 생성 (■ 문자 사용)
            bar_length = int((count / max_count) * bar_width)
            bar = "■" * bar_length
            
            # 백분율 계산
            percentage = (count / self.count) * 100 if self.count > 0 else 0
            
            viz_text += f"{key_display} |{bar:<30} {count:>4} ({percentage:>5.1f}%)\n"
        
        viz_text += "\n" + "=" * 50 + "\n"
        viz_text += f"총 키 입력: {self.count}\n"
        viz_text += f"고유 키 수: {len(self.key_counts)}\n"
        viz_text += f"세션 시간: {self.total_session_time:.1f}초\n"
        viz_text += f"WPM: {self._calculate_wpm(self.total_session_time):.1f}"

        text_widget.insert(tk.END, viz_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용으로 설정


def main() -> None:
    root = tk.Tk()
    app = TypingCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
