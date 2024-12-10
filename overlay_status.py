import tkinter as tk
from tkinter import ttk
import win32gui
import win32con
import threading
import keyboard

class StatusOverlay:
    def __init__(self, macro_controller):
        self.macro_controller = macro_controller
        self.is_active = True
        
        # tkinter 초기화는 메인 스레드에서
        self.root = None
        self.labels = {}
        
        # 초기화 완료 이벤트
        self.init_done = threading.Event()
        
    def initialize_gui(self):
        # 메인 윈도우 생성
        self.root = tk.Tk()
        self.root.title("매크로 상태")
        
        # 윈도우 설정
        self.root.attributes('-topmost', True)
        self.root.attributes('-alpha', 0.85)
        self.root.overrideredirect(True)
        
        # 윈도우 크기 증가 (너비를 220으로, 높이를 290으로)
        self.root.geometry('220x290+10+50')  # 너비를 180에서 220으로 수정
        
        # 메인 프레임 생성
        main_frame = ttk.Frame(self.root, padding="5")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 상단 프레임 (크로 상 표시용)
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill='x', expand=True)
        
        # 스타일 설정
        style = ttk.Style()
        style.configure('Title.TLabel', font=('맑은 고딕', 10, 'bold'))
        style.configure('Status.TLabel', font=('맑은 고딕', 9))
        
        # 레이블들 사이의 간격 조정
        pady_value = 1  # 레이블 사이 간격을 줄임
        
        # 타이틀
        title = ttk.Label(status_frame, text="매크로 상태", style='Title.TLabel')
        title.pack(pady=(0, 5))
        
        # 구분선
        separator = ttk.Separator(status_frame, orient='horizontal')
        separator.pack(fill='x', pady=3)
        
        # 상태 표시 레이블들
        self.labels = {
            'skill1': ttk.Label(status_frame, text="F1: 비활성", style='Status.TLabel'),
            'skill2': ttk.Label(status_frame, text="F2: 비활성", style='Status.TLabel'),
            'skill3': ttk.Label(status_frame, text="F3: 비활성", style='Status.TLabel'),
            'skill4': ttk.Label(status_frame, text="버프(F4): 비활성", style='Status.TLabel'),
            'skill4_party': ttk.Label(status_frame, text="파티버프(F4:a+P): 비활성", style='Status.TLabel'),
            'skill9': ttk.Label(status_frame, text="자동(F9): 비활성", style='Status.TLabel'),
            'heal': ttk.Label(status_frame, text="체력/마력: 활성", style='Status.TLabel'),
            'quest': ttk.Label(status_frame, text="퀘스트(a+O): 비활성", style='Status.TLabel'),
            'quest_status': ttk.Label(status_frame, text="", style='Status.TLabel', foreground='gray')
        }
        
        # 레이블 배치
        for label in self.labels.values():
            label.pack(anchor='w', padx=10, pady=pady_value)
        
        # 하단 프레임 (종료 안내용)
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill='x', side='bottom')
        
        # 구분선
        separator2 = ttk.Separator(bottom_frame, orient='horizontal')
        separator2.pack(fill='x')
        
        # 종료 안내 (항상 하단 고정)
        exit_label = ttk.Label(bottom_frame, text="Ctrl+Q: 종료", style='Status.TLabel', foreground='gray')
        exit_label.pack(anchor='e', padx=5, pady=3)
        
        # 클릭해서 드래그 가능하도록
        self.root.bind('<Button-1>', self.start_move)
        self.root.bind('<B1-Motion>', self.on_move)
        
        # Ctrl+Q 종료 이벤트 바인딩
        self.root.bind('<Control-q>', self.on_exit)
        
        # 초기화 완료
        self.init_done.set()
        
        # 상태 업데이트 시작
        self.update_status()
        
        # 메인루프 시작
        while self.is_active:
            try:
                self.root.update()
                self.root.update_idletasks()
                # Ctrl+Q 체크
                if keyboard.is_pressed('ctrl+q'):
                    self.on_exit()
                    break
            except:
                break

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.root.winfo_x() + deltax
        y = self.root.winfo_y() + deltay
        self.root.geometry(f"+{x}+{y}")

    def update_status(self):
        try:
            if not self.is_active:
                return
            
            # 매크로 상태 업데이트
            for key, label in self.labels.items():
                try:
                    if key == 'heal':  # 체력/마력 상태 업데이트 추가
                        is_active = self.macro_controller.heal_controller.is_running
                        status = "활성" if is_active else "비활성"
                        label.config(text=f"체력/마력: {status}", foreground='#007ACC' if is_active else 'black')
                    elif key == 'skill4_party':  # 파티버프 상태 업데이트
                        is_active = self.macro_controller.skill_macro_4.use_party_skill
                        status = "활성" if is_active else "비활성"
                        label.config(text=f"파티버프(F4:a+P): {status}", foreground='#007ACC' if is_active else 'black')
                    elif key == 'quest':
                        is_active = hasattr(self.macro_controller.quest_action, 'is_running') and self.macro_controller.quest_action.is_running
                        status = "활성" if is_active else "비활성"
                        label.config(text=f"퀘스트(a+O): {status}", foreground='#007ACC' if is_active else 'black')
                        
                        # 퀘스트 상태 업데이트 (활성 상태가 아니어도 마지막 정보 표시)
                        attempt = getattr(self.macro_controller.quest_action, 'current_attempt', 0)
                        quest_type = getattr(self.macro_controller.quest_action, 'found_quest_type', None)
                        
                        if is_active or quest_type:  # 실행 중이거나 퀘스트가 있을 때
                            quest_name = {
                                'beginner_ghost': '초급유령',
                                'ghost': '유령',
                                'highclass_ghost': '고급유령',
                                'swift_skeleton': '날쌘해골',
                                'skeleton': '해골',
                                None: '검색중'
                            }.get(quest_type, '검색중')
                            
                            if is_active:
                                status_text = f"시도: {attempt}/50  {quest_name}"
                            else:
                                status_text = f"현재 퀘스트: {quest_name}"
                                
                            if 'quest_status' in self.labels:
                                self.labels['quest_status'].config(
                                    text=status_text,
                                    foreground='#007ACC'
                                )
                        else:
                            if 'quest_status' in self.labels:
                                self.labels['quest_status'].config(text="", foreground='gray')
                    else:
                        # skill1~9 매크로 상태 업데이트
                        skill_number = key[-1]
                        macro_attr = f'skill_macro_{skill_number}'
                        if hasattr(self.macro_controller, macro_attr):
                            macro = getattr(self.macro_controller, macro_attr)
                            is_active = macro.is_running
                            status = "활성" if is_active else "비활성"
                            label.config(text=f"F{skill_number}: {status}", foreground='#007ACC' if is_active else 'black')
                except Exception as e:
                    with open('overlay_error.log', 'a') as f:
                        f.write(f"Label update error for {key}: {str(e)}\n")
            
            # 100ms마다 업데이트
            if self.is_active:
                self.root.after(100, self.update_status)
            
        except Exception as e:
            with open('overlay_error.log', 'a') as f:
                f.write(f"Update status error: {str(e)}\n")

    def run(self):
        self.initialize_gui()

    def stop(self):
        self.is_active = False
        if self.root:
            self.root.quit()

    def on_exit(self, event=None):
        self.is_active = False
        self.macro_controller.is_active = False
        if self.root:
            self.root.quit() 