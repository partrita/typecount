import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pynput.keyboard import Listener, Key
import csv
from datetime import date, datetime, timedelta
import os
from pathlib import Path
from typing import Optional, Any, Dict
from collections import defaultdict
import time
import json


class TypingCounter:
    def __init__(self, master: tk.Tk) -> None:
        self.master = master
        master.title("Typing Counter v0.4 - Enhanced")
        master.geometry("450x350+100+100")  # Adjusted geometry for new features

        self.count = 0
        self.is_counting = False
        self.listener: Optional[Listener] = None
        self.key_counts: Dict[str, int] = defaultdict(int)  # 키별 카운트 저장
        
        # 세션 추적을 위한 새로운 속성들
        self.session_start_time: Optional[datetime] = None
        self.session_end_time: Optional[datetime] = None
        self.total_session_time: float = 0.0  # 초 단위
        
        # 15초 비활성 감지를 위한 속성들
        self.last_key_time: Optional[datetime] = None
        self.inactive_threshold: float = 15.0  # 15초
        self.is_session_paused: bool = False
        self.pause_start_time: Optional[datetime] = None

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

        # 버튼 프레임 3 (Visualize, Load Data)
        button_frame3 = tk.Frame(self.master)
        button_frame3.grid(row=3, column=0, pady=5)
        # Configure columns in button_frame3 for centering/distribution
        button_frame3.columnconfigure(0, weight=1)
        button_frame3.columnconfigure(1, weight=1)

        self.visualize_button = tk.Button(
            button_frame3, text="Visualize Data", command=self.visualize_data
        )
        self.visualize_button.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.load_button = tk.Button(
            button_frame3, text="Load & Analyze", command=self.load_and_analyze_data
        )
        self.load_button.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # 버튼 프레임 4 (Quit)
        button_frame4 = tk.Frame(self.master)
        button_frame4.grid(row=4, column=0, pady=5)
        
        self.quit_button = tk.Button(
            button_frame4, text="Quit", command=self.master.quit
        )
        self.quit_button.pack()

        # 세션 정보 표시 라벨
        self.session_info_label = tk.Label(
            self.master, text="Session: Not started", font=("Arial", 10)
        )
        self.session_info_label.grid(row=5, column=0, pady=5, sticky="ew")

    def start_counting(self) -> None:
        """타이핑 카운트를 시작하고 UI를 업데이트합니다."""
        self.is_counting = True
        self.session_start_time = datetime.now()
        self.last_key_time = None
        self.is_session_paused = False
        self.pause_start_time = None
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.listener = Listener(on_press=self._on_press)
        self.listener.start()
        self._update_session_info()

    def stop_counting(self) -> None:
        """타이핑 카운트를 중지하고 UI를 업데이트합니다."""
        self.is_counting = False
        self.session_end_time = datetime.now()
        
        # 세션이 일시 중단되지 않은 상태라면 현재까지의 시간을 누적
        if self.session_start_time and not self.is_session_paused:
            session_duration = (self.session_end_time - self.session_start_time).total_seconds()
            self.total_session_time += session_duration
        
        # 상태 초기화
        self.is_session_paused = False
        self.pause_start_time = None
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        if self.listener:
            self.listener.stop()
        self._update_session_info()

    def _on_press(self, key: Any) -> None:
        """키가 눌릴 때마다 카운트를 증가시키고 UI를 업데이트합니다."""
        if self.is_counting:
            current_time = datetime.now()
            
            # 세션이 일시 중단된 상태에서 키 입력이 있으면 재개
            if self.is_session_paused:
                self._resume_session(current_time)
            
            self.count += 1
            self.last_key_time = current_time
            
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

    def _pause_session(self, current_time: datetime) -> None:
        """세션을 일시 중단합니다."""
        if not self.is_session_paused and self.session_start_time:
            self.is_session_paused = True
            self.pause_start_time = current_time
            # 현재까지의 세션 시간을 누적
            session_duration = (current_time - self.session_start_time).total_seconds()
            self.total_session_time += session_duration

    def _resume_session(self, current_time: datetime) -> None:
        """세션을 재개합니다."""
        if self.is_session_paused:
            self.is_session_paused = False
            self.session_start_time = current_time
            self.pause_start_time = None

    def reset_count(self) -> None:
        """카운트를 0으로 초기화하고 UI를 업데이트합니다."""
        self.count = 0
        self.key_counts.clear()
        self.total_session_time = 0.0
        self.session_start_time = None
        self.session_end_time = None
        self.last_key_time = None
        self.is_session_paused = False
        self.pause_start_time = None
        self.label.config(text=f"Count: {self.count}")
        self._update_session_info()

    def save_count(self) -> None:
        """현재 카운트와 키별 통계를 CSV 파일에 저장합니다."""
        if self.count == 0:
            messagebox.showwarning("저장", "저장할 데이터가 없습니다.")
            return

        today = date.today().isoformat()
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile="typing_count_enhanced.csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filepath:  # User cancelled the dialog
            return

        file_path_obj = Path(filepath)
        
        # 기존 데이터 읽기
        existing_data = {}
        if file_path_obj.is_file():
            try:
                with open(file_path_obj, "r", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        date_key = row["Date"]
                        existing_data[date_key] = {
                            "Count": int(row["Count"]),
                            "SessionTime": float(row.get("SessionTime", 0)),
                            "WPM": float(row.get("WPM", 0)),
                            "UniqueKeys": int(row.get("UniqueKeys", 0)),
                            "KeyStats": json.loads(row.get("KeyStats", "{}"))
                        }
            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
                # 파일이 없거나 형식이 다른 경우 새로 시작
                existing_data = {}

        # 현재 데이터와 기존 데이터 합치기
        if today in existing_data:
            # 같은 날짜 데이터가 있으면 합치기
            existing_data[today]["Count"] += self.count
            existing_data[today]["SessionTime"] += self.total_session_time
            
            # 키 통계 합치기
            for key, count in self.key_counts.items():
                if key in existing_data[today]["KeyStats"]:
                    existing_data[today]["KeyStats"][key] += count
                else:
                    existing_data[today]["KeyStats"][key] = count
            
            # WPM 재계산 (총 카운트와 총 세션 시간 기준)
            total_session_time = existing_data[today]["SessionTime"]
            existing_data[today]["WPM"] = self._calculate_wpm_from_count_and_time(
                existing_data[today]["Count"], total_session_time
            )
            existing_data[today]["UniqueKeys"] = len(existing_data[today]["KeyStats"])
        else:
            # 새로운 날짜 데이터 추가
            existing_data[today] = {
                "Count": self.count,
                "SessionTime": self.total_session_time,
                "WPM": self._calculate_wpm(self.total_session_time),
                "UniqueKeys": len(self.key_counts),
                "KeyStats": dict(self.key_counts)
            }

        # 데이터를 날짜순으로 정렬하여 저장
        sorted_dates = sorted(existing_data.keys())
        
        with open(file_path_obj, "w", newline="", encoding="utf-8") as f:
            fieldnames = ["Date", "Count", "SessionTime", "WPM", "UniqueKeys", "KeyStats"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for date_key in sorted_dates:
                data = existing_data[date_key]
                writer.writerow({
                    "Date": date_key,
                    "Count": data["Count"],
                    "SessionTime": round(data["SessionTime"], 2),
                    "WPM": round(data["WPM"], 2),
                    "UniqueKeys": data["UniqueKeys"],
                    "KeyStats": json.dumps(data["KeyStats"], ensure_ascii=False)
                })

        messagebox.showinfo("저장 완료", f"데이터가 성공적으로 저장되었습니다.\n파일: {file_path_obj}")
        print(f"Enhanced data saved to: {file_path_obj}")

    def _calculate_wpm_from_count_and_time(self, total_count: int, total_time_seconds: float) -> float:
        """총 카운트와 총 시간으로 WPM을 계산합니다."""
        if total_time_seconds <= 0:
            return 0.0
        words = total_count / 5  # 평균 5글자를 1단어로 계산
        minutes = total_time_seconds / 60
        return words / minutes if minutes > 0 else 0.0

    def _update_session_info(self) -> None:
        """세션 정보를 업데이트합니다."""
        if self.is_counting and self.session_start_time:
            current_time = datetime.now()
            
            # 15초 비활성 감지
            if self.last_key_time and not self.is_session_paused:
                time_since_last_key = (current_time - self.last_key_time).total_seconds()
                if time_since_last_key >= self.inactive_threshold:
                    self._pause_session(self.last_key_time + timedelta(seconds=self.inactive_threshold))
            
            # 현재 세션 시간 계산
            if self.is_session_paused:
                # 일시 중단된 상태: 누적된 시간만 표시
                total_time = self.total_session_time
                status = "PAUSED"
            else:
                # 활성 상태: 현재 세션 시간 + 누적 시간
                current_session_time = (current_time - self.session_start_time).total_seconds()
                total_time = self.total_session_time + current_session_time
                status = "ACTIVE"
            
            wpm = self._calculate_wpm(total_time)
            self.session_info_label.config(
                text=f"Session: {total_time:.1f}s | WPM: {wpm:.1f} | {status}"
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

    def load_and_analyze_data(self) -> None:
        """저장된 데이터를 불러와서 분석합니다."""
        filepath = filedialog.askopenfilename(
            title="분석할 데이터 파일 선택",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
        )

        if not filepath:
            return

        try:
            # 데이터 로드
            data = {}
            with open(filepath, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    date_key = row["Date"]
                    data[date_key] = {
                        "Count": int(row["Count"]),
                        "SessionTime": float(row.get("SessionTime", 0)),
                        "WPM": float(row.get("WPM", 0)),
                        "UniqueKeys": int(row.get("UniqueKeys", 0)),
                        "KeyStats": json.loads(row.get("KeyStats", "{}"))
                    }

            if not data:
                messagebox.showinfo("분석", "분석할 데이터가 없습니다.")
                return

            self._show_data_analysis(data, filepath)

        except Exception as e:
            messagebox.showerror("오류", f"데이터를 불러오는 중 오류가 발생했습니다:\n{str(e)}")

    def _show_data_analysis(self, data: Dict, filepath: str) -> None:
        """데이터 분석 결과를 새 창에 표시합니다."""
        # 새 창 생성
        analysis_window = tk.Toplevel(self.master)
        analysis_window.title("데이터 분석 결과")
        analysis_window.geometry("600x500")

        # 스크롤 가능한 텍스트 위젯
        text_widget = scrolledtext.ScrolledText(analysis_window, wrap=tk.WORD, font=("Courier", 10))
        text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 분석 수행
        total_count = sum(day_data["Count"] for day_data in data.values())
        total_session_time = sum(day_data["SessionTime"] for day_data in data.values())
        avg_wpm = sum(day_data["WPM"] for day_data in data.values()) / len(data)
        
        # 전체 키 통계 합계
        all_key_stats = defaultdict(int)
        for day_data in data.values():
            for key, count in day_data["KeyStats"].items():
                all_key_stats[key] += count

        # 가장 활발한 날과 가장 조용한 날
        most_active_day = max(data.items(), key=lambda x: x[1]["Count"])
        least_active_day = min(data.items(), key=lambda x: x[1]["Count"])

        # 상위 키 통계
        top_keys = sorted(all_key_stats.items(), key=lambda x: x[1], reverse=True)[:10]

        # 분석 결과 텍스트 생성
        analysis_text = f"타이핑 데이터 분석 결과\n"
        analysis_text += f"파일: {Path(filepath).name}\n"
        analysis_text += "=" * 60 + "\n\n"
        
        analysis_text += "📊 전체 통계\n"
        analysis_text += "-" * 30 + "\n"
        analysis_text += f"분석 기간: {len(data)}일\n"
        analysis_text += f"총 키 입력: {total_count:,}회\n"
        analysis_text += f"총 세션 시간: {total_session_time/3600:.1f}시간\n"
        analysis_text += f"평균 WPM: {avg_wpm:.1f}\n"
        analysis_text += f"일평균 키 입력: {total_count/len(data):.0f}회\n"
        analysis_text += f"고유 키 수: {len(all_key_stats)}개\n\n"

        analysis_text += "📈 일별 통계\n"
        analysis_text += "-" * 30 + "\n"
        analysis_text += f"가장 활발한 날: {most_active_day[0]} ({most_active_day[1]['Count']:,}회)\n"
        analysis_text += f"가장 조용한 날: {least_active_day[0]} ({least_active_day[1]['Count']:,}회)\n\n"

        analysis_text += "⌨️  상위 10개 키 (전체 기간)\n"
        analysis_text += "-" * 30 + "\n"
        for i, (key, count) in enumerate(top_keys, 1):
            percentage = (count / total_count) * 100
            key_display = key if len(key) <= 10 else key[:10]
            analysis_text += f"{i:2d}. {key_display:>10}: {count:>6,}회 ({percentage:>5.1f}%)\n"

        analysis_text += "\n📅 일별 상세 데이터\n"
        analysis_text += "-" * 30 + "\n"
        analysis_text += f"{'날짜':>10} {'키입력':>8} {'시간(분)':>8} {'WPM':>6} {'고유키':>6}\n"
        analysis_text += "-" * 50 + "\n"
        
        for date_key in sorted(data.keys()):
            day_data = data[date_key]
            session_minutes = day_data["SessionTime"] / 60
            analysis_text += f"{date_key:>10} {day_data['Count']:>8,} {session_minutes:>8.1f} {day_data['WPM']:>6.1f} {day_data['UniqueKeys']:>6}\n"

        text_widget.insert(tk.END, analysis_text)
        text_widget.config(state=tk.DISABLED)  # 읽기 전용으로 설정


def main() -> None:
    root = tk.Tk()
    app = TypingCounter(root)
    root.mainloop()


if __name__ == "__main__":
    main()
