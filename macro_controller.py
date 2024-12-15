# macro_controller.py
import time
import win32api
import win32con
from threading import Thread, RLock
import keyboard
import ctypes, sys

try:
    from healing_recovery import HealingController
except ImportError:
    print("healing_recovery 모듈을 찾을 수 없습니다.")
    HealingController = None

try:
    from skills.skill_macro_1 import SkillMacro1Controller
    from skills.skill_macro_2 import SkillMacro2Controller
    from skills.skill_macro_3 import SkillMacro3Controller
    from skills.skill_macro_4 import SkillMacro4Controller
except ImportError:
    print("skill_macro 모듈을 찾을 수 없습니다.")
    SkillMacro1Controller = None
    SkillMacro2Controller = None
    SkillMacro3Controller = None
    SkillMacro4Controller = None

try:
    from overlay_status import StatusOverlay
except ImportError:
    print("overlay_status 모듈을 찾을 수 없습니다.")
    StatusOverlay = None

try:
    from area_selector import show_area_selector
except ImportError:
    print("area_selector 모듈을 찾을 수 없습니다.")
    show_area_selector = None

try:
    from actions.quest_action import QuestAction
except ImportError:
    print("quest_action 모듈을 찾을 수 없습니다.")
    QuestAction = None

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

class MacroController:
    def __init__(self):
        self.is_active = True
        self.EXIT_KEY = 'ctrl+q'
        self.is_using_skill = False
        self.current_skill = None

        # 글로벌 키 입력 락 추가
        self.key_input_lock = RLock()

        try:
            self.heal_controller = HealingController()
            self.heal_controller.macro_controller = self
            self.heal_controller.is_running = True
            self.heal_controller.mana_controller.is_running = True
        except Exception as e:
            print(f"힐링 컨트롤러 초기화 실패: {e}")
            self.heal_controller = None

        self.skill_controllers = {}
        # 스킬 매크로 번호 리스트에 9 추가
        skill_numbers = [1, 2, 3, 4, 9]
        for num in skill_numbers:
            try:
                module = __import__(f'skills.skill_macro_{num}', fromlist=[f'SkillMacro{num}Controller'])
                controller_class = getattr(module, f'SkillMacro{num}Controller')
                controller = controller_class()
                controller.macro_controller = self
                self.skill_controllers[num] = controller
                setattr(self, f'skill_macro_{num}', controller)
            except Exception as e:
                print(f"스킬 매크로 {num} 초기화 실패: {e}")
                self.skill_controllers[num] = None
                setattr(self, f'skill_macro_{num}', None)

        try:
            self.quest_action = QuestAction()
            self.quest_action.macro_controller = self
        except Exception as e:
            print(f"퀘스트 액션 초기화 실패: {e}")
            self.quest_action = None

        self.quest_types = {
            'beginner_ghost': False,
            'ghost': False,
            'highclass_ghost': True,
            'swift_skeleton': False,
            'skeleton': False,
            'insect': False,
            'virgin_ghost': False,
            'bachelor_ghost': False,
            'broom_ghost': False,
            'egg_ghost': False,
            'fire_ghost': False
        }

        self.setup_hotkeys()
        
        if self.heal_controller:
            keyboard.add_hotkey('`', lambda: self.toggle_heal_macro())
            keyboard.add_hotkey('alt+[', lambda: self.toggle_mana_macro())

        keyboard.add_hotkey('alt+\\', self.show_area_selector)

        if self.quest_action:
            keyboard.add_hotkey('alt+o', lambda: self.toggle_quest_action())

        # 우선순위 관리를 위한 변수 추가
        self.priority_queue = []
        self.previous_macro = None
        self.f4_in_progress = False

        self.threads = []  # 스레드 관리를 위한 리스트 추가

    def setup_hotkeys(self):
        # F1~F4, F9 키 설정
        for num in [1, 2, 3, 4, 9]:
            if self.skill_controllers.get(num):
                keyboard.on_press_key(f'F{num}', lambda e, n=num: self.toggle_skill_macro(n))

    def toggle_skill_macro(self, num):
        if num in self.skill_controllers and self.skill_controllers[num]:
            controller = self.skill_controllers[num]
            
            # F4 매크로가 실행 중일 때는 다른 매크로 토글 무시
            if num != 4 and self.f4_in_progress:
                print(f"\nF4 매크로 실행 중 - F{num} 매크로 토글 무시됨")
                return
                
            was_running = controller.is_running
            
            # 매크로 켜기
            if not was_running:
                # 우선순위에 따라 현재 실행 중인 매크로 중지
                self.handle_priority(num)
                controller.is_running = True
                self.priority_queue.append(num)
            # 매크로 끄기
            else:
                controller.is_running = False
                if num in self.priority_queue:
                    self.priority_queue.remove(num)
                    # ESC 키 전송 (F1, F2, F3, F9 매크로의 경우)
                    if num in [1, 2, 3, 9]:
                        with self.key_input_lock:
                            print("[DEBUG] 스킬 정지 후 ESC 키 전송")
                            win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                            time.sleep(0.02)
                            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                            time.sleep(0.02)
                    # 이전 매크로 재시작
                    self.resume_previous_macro()
            
            status = "실행 중" if controller.is_running else "정지"
            print(f"\n스킬 매크로 {num} 상태: {status}")

    def handle_priority(self, new_macro_num):
        # 우선순위 맵 (숫자가 클수록 높은 우선순위)
        priority_map = {1: 1, 3: 2, 2: 3, 4: 4, 9: 1}  # F9는 F1과 같은 우선순위
        
        # 현재 실행 중인 매크로들 확인
        for num in self.priority_queue[:]:
            if self.skill_controllers[num].is_running:
                # 새로운 매크로가 더 높은 우선순위를 가질 경우
                if priority_map[new_macro_num] > priority_map[num]:
                    self.skill_controllers[num].is_running = False
                    if num in [1, 2, 3, 9]:  # F1, F2, F3, F9 매크로의 경우 ESC 키 전송
                        with self.key_input_lock:
                            win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                            time.sleep(0.02)
                            win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                            time.sleep(0.02)

    def resume_previous_macro(self):
        # 우선순위 큐에서 가장 마지막 매크로 재시작
        if self.priority_queue:
            last_macro = self.priority_queue[-1]
            if self.skill_controllers[last_macro]:
                self.skill_controllers[last_macro].is_running = True

    def run_skill_macro(self, num):
        while self.is_active:
            try:
                if not self.skill_controllers.get(num):
                    time.sleep(1)
                    continue

                controller = self.skill_controllers[num]

                if controller.is_running:
                    if num == 4:  # F4 매크로 실행 시 특별 처리
                        # 전체 F4 매크로 실행을 하나의 락으로 보호
                        with self.key_input_lock:
                            print("[DEBUG] F4 매크로 실행 시작 (키 입력 잠금)")
                            self.f4_in_progress = True
                            
                            # 다른 매크로 중지
                            for other_num in self.priority_queue[:]:
                                if other_num != 4:
                                    self.skill_controllers[other_num].is_running = False
                                    if other_num in [1, 2, 3, 9]:
                                        win32api.keybd_event(win32con.VK_ESCAPE, 0, 0, 0)
                                        time.sleep(0.02)
                                        win32api.keybd_event(win32con.VK_ESCAPE, 0, win32con.KEYEVENTF_KEYUP, 0)
                                        time.sleep(0.02)
                            
                            # F4 스킬 실행
                            controller.use_skill()
                            
                            # F4 매크로 실행 완료 후 정리
                            self.f4_in_progress = False
                            controller.is_running = False
                            if 4 in self.priority_queue:
                                self.priority_queue.remove(4)
                            
                            # 이전 매크로들 재시작
                            self.resume_previous_macro()
                            print("[DEBUG] F4 매크로 실행 완료 (키 입력 잠금 해제)")
                    else:
                        if not self.f4_in_progress:  # F4가 실행 중이 아닐 때만 다른 매크로 실행
                            controller.use_skill()

                time.sleep(0.01)

            except Exception as e:
                print(f"매크로 {num} 실행 중 오류: {str(e)}")
                if num == 4:
                    self.f4_in_progress = False

    def show_area_selector(self):
        skill_area, heal_area, mana_area = show_area_selector()
        if skill_area and heal_area and mana_area:
            print(f"스킬/마나 감지 영역: {skill_area}")
            print(f"힐 감지 영역: {heal_area}")
            print(f"마나 감지 영역: {mana_area}")
            
            self.heal_controller.heal_area = heal_area
            self.heal_controller.mana_controller.mana_area = mana_area
            # F9 매크로도 포함
            for num in [1, 2, 3, 4, 9]:
                if self.skill_controllers.get(num):
                    self.skill_controllers[num].skill_area = skill_area
            
            print("모든 매크로의 감지 영역이 업데이트되었습니다.")

    def toggle_quest_action(self):
        if not self.is_using_skill:
            if hasattr(self.quest_action, 'is_running') and self.quest_action.is_running:
                self.quest_action.is_running = False
                print("\n퀘스트 매크로를 중지합니다...")
            else:
                print("\n퀘스트 수락 매크로 시작...")
                Thread(target=self.quest_action.execute_quest_action).start()

    def toggle_heal_macro(self):
        """체력 회복 매크로 토글"""
        if self.heal_controller:
            self.heal_controller.is_running = not self.heal_controller.is_running
            status = "활성" if self.heal_controller.is_running else "비활성"
            print(f"\n체력 회복 매크로 상태: {status}")

    def toggle_mana_macro(self):
        """마나 회복 매크로 토글"""
        if self.heal_controller:
            self.heal_controller.mana_controller.is_running = not self.heal_controller.mana_controller.is_running
            status = "활성" if self.heal_controller.mana_controller.is_running else "비활성"
            print(f"\n마나 회복 매크로 상태: {status}")

    def cleanup(self):
        """프로그램 종료 시 정리 작업 수행"""
        print("\n프로그램 종료 중...")
        self.is_active = False
        
        # keyboard 핫키 제거
        keyboard.unhook_all()  # 모든 핫키 제거
        
        # 모든 매크로 중지
        if self.heal_controller:
            self.heal_controller.is_active = False
            self.heal_controller.is_running = False
            self.heal_controller.mana_controller.is_active = False
            self.heal_controller.mana_controller.is_running = False
        
        # 모든 스킬 매크로 중지
        for num in [1, 2, 3, 4, 9]:
            if self.skill_controllers.get(num):
                self.skill_controllers[num].is_running = False
        
        # 스레드 종료 대기
        for thread in self.threads:
            if thread.is_alive():
                thread.join(timeout=1.0)
        
        print("프로그램이 안전하게 종료되었습니다.")

def main():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return

    controller = MacroController()
    overlay = StatusOverlay(controller)

    # 스레드 생성 및 저장
    if controller.heal_controller:
        heal_thread = Thread(target=controller.heal_controller.check_and_heal)
        heal_thread.daemon = True
        controller.threads.append(heal_thread)
        heal_thread.start()

    for num in [1, 2, 3, 4, 9]:
        if controller.skill_controllers.get(num):
            skill_thread = Thread(target=controller.run_skill_macro, args=(num,))
            skill_thread.daemon = True
            controller.threads.append(skill_thread)
            skill_thread.start()
    
    print("\n=== 매크로 시작 ===")
    print("F8: 힐링 매크로 시작/정지")
    print("F1~F4, F9: 스킬 매크로 시작/정지")
    print("Alt+O: 퀘스트 매크로 시작/정지")
    print("Alt+[: 체력/마력 회복 시작/정지")
    print("Alt+\\: 영역 선택")
    print("Alt+P: 파티버프 활성화")
    print("Ctrl+Q: 프로그램 종료")
    
    try:
        overlay.run()
    except KeyboardInterrupt:
        pass
    finally:
        overlay.stop()  # 오버레이 먼저 종료
        controller.cleanup()  # 그 다음 컨트롤러 정리

if __name__ == "__main__":
    main()

