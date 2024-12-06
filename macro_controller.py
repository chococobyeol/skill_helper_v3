import time
import win32api
import win32con
from threading import Thread
import keyboard
import ctypes, sys

# 모듈 임포트 시도
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
    from skills.skill_macro_9 import SkillMacro9Controller
except ImportError:
    print("skill_macro 모듈을 찾을 수 없습니다.")
    SkillMacro1Controller = None
    SkillMacro2Controller = None
    SkillMacro3Controller = None
    SkillMacro4Controller = None
    SkillMacro9Controller = None

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
        
        # 컨트롤러 초기화 - 예외 처리 추가
        try:
            self.heal_controller = HealingController()
            self.heal_controller.macro_controller = self
            self.heal_controller.is_running = True  # 힐링은 기본적으로 활성화
        except Exception as e:
            print(f"힐링 컨트롤러 초기화 실패: {e}")
            self.heal_controller = None

        # 스킬 매크로 컨트롤러들 초기화
        self.skill_controllers = {}
        
        # 스킬 매크로 동적 로딩
        skill_numbers = [1, 2, 3, 4, 9]
        for num in skill_numbers:
            try:
                module = __import__(f'skills.skill_macro_{num}', fromlist=[f'SkillMacro{num}Controller'])
                controller_class = getattr(module, f'SkillMacro{num}Controller')
                controller = controller_class()
                if num == 9:  # 스킬9는 매크로 컨트롤러 참조 필요
                    controller.macro_controller = self
                self.skill_controllers[num] = controller
                setattr(self, f'skill_macro_{num}', controller)
            except Exception as e:
                print(f"스킬 매크로 {num} 초기화 실패: {e}")
                self.skill_controllers[num] = None
                setattr(self, f'skill_macro_{num}', None)

        # 퀘스트 컨트롤러 초기화
        try:
            self.quest_action = QuestAction()
            self.quest_action.macro_controller = self
        except Exception as e:
            print(f"퀘스트 액션 초기화 실패: {e}")
            self.quest_action = None

        # 퀘스트 타입 설정
        self.quest_types = {
            'beginner_ghost': False,
            'ghost': False,
            'highclass_ghost': True
        }

        # 단축키 설정
        self.setup_hotkeys()
        
        # 힐링 매크로 토글 단축키
        if self.heal_controller:
            keyboard.add_hotkey('alt+[', lambda: self.toggle_heal_macro())
        
        # 영역 선택 단축키
        keyboard.add_hotkey('alt+\\', self.show_area_selector)
        
        # 퀘스트 매크로 단축키
        if self.quest_action:
            keyboard.add_hotkey('alt+o', lambda: self.toggle_quest_action())

    def setup_hotkeys(self):
        # 스킬 매크로 단축키 설정
        for num in [1, 2, 3, 4, 9]:
            if self.skill_controllers.get(num):
                keyboard.on_press_key(f'F{num}', lambda e, n=num: self.toggle_skill_macro(n))

    def toggle_skill_macro(self, num):
        """스킬 매크로 토글 통합 함수"""
        if num in self.skill_controllers and self.skill_controllers[num]:
            controller = self.skill_controllers[num]
            controller.is_running = not controller.is_running
            status = "실행 중" if controller.is_running else "정지"
            print(f"\n스킬 매크로 {num} 상태: {status}")

    def run_skill_macro(self, num):
        """스킬 매크로 실행 통합 함수"""
        while self.is_active:
            try:
                if not self.skill_controllers.get(num):
                    time.sleep(1)
                    continue

                controller = self.skill_controllers[num]
                
                # 다른 스킬이 실행 중이면 대기
                if self.is_using_skill and self.current_skill != f"skill{num}":
                    time.sleep(0.01)
                    continue

                # 힐/마나 체크
                if (self.heal_controller and 
                    (self.heal_controller.is_healing or 
                     self.heal_controller.mana_controller.is_recovering)):
                    time.sleep(0.01)
                    continue

                # 스킬 사용
                if controller.is_running:
                    self.is_using_skill = True
                    self.current_skill = f"skill{num}"
                    if num == 9:
                        result = controller.try_once()
                        if not result:
                            controller.fail_count += 1
                            if controller.fail_count >= controller.MAX_FAILS:
                                print(f"\n{controller.MAX_FAILS}회 실패로 매크로 중지")
                                controller.is_running = False
                                controller.fail_count = 0
                        else:
                            controller.fail_count = 0
                    else:
                        controller.use_skill()
                    self.is_using_skill = False
                    self.current_skill = None

                time.sleep(0.01)

            except Exception as e:
                print(f"매크로 {num} 실행 중 오류: {str(e)}")
                self.is_using_skill = False
                self.current_skill = None

    def show_area_selector(self):
        skill_area, heal_area = show_area_selector()
        if skill_area and heal_area:
            print(f"스킬/마나 감지 영역: {skill_area}")
            print(f"힐 감지 영역: {heal_area}")
            
            # 힐링 트롤러에 영역 전달
            self.heal_controller.heal_area = heal_area
            
            # 마나 컨트롤러와 스킬 매크로들에 스킬 영역 전달
            self.heal_controller.mana_controller.mana_area = skill_area  # 마나는 스킬 영역 사용
            for num in [1, 2, 3, 4, 9]:
                if self.skill_controllers.get(num):
                    self.skill_controllers[num].skill_area = skill_area
            
            print("모든 매크로의 감지 영역이 업데이트되었습니다.")

    def toggle_quest_action(self):
        if not self.is_using_skill:  # 다른 스킬 사용 중이 아닐 때만 실행
            if hasattr(self.quest_action, 'is_running') and self.quest_action.is_running:
                # 실행 중이면 중지
                self.quest_action.is_running = False
                print("\n퀘스트 매크로를 중지합니다...")
            else:
                # 중지 상태면 시작
                print("\n퀘스트 수락 매크로 시작...")
                Thread(target=self.quest_action.execute_quest_action).start()

    def toggle_heal_macro(self):
        self.heal_controller.is_running = not self.heal_controller.is_running
        status = "활성" if self.heal_controller.is_running else "비활성"
        print(f"\n체력/마력 회복 매크로 상태: {status}")

def main():
    # 관리자 권한 체크 및 요청
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        return

    controller = MacroController()
    
    # 오버레이 창 생성
    overlay = StatusOverlay(controller)
    
    # 스레드 리스트 생성
    threads = []
    
    # 힐링 스레드 추가
    if controller.heal_controller:
        threads.append(Thread(target=controller.heal_controller.check_and_heal))
    
    # 스킬 매크로 스레드 추가
    for num in [1, 2, 3, 4, 9]:
        if controller.skill_controllers.get(num):
            threads.append(Thread(target=controller.run_skill_macro, args=(num,)))
    
    # 스레드 시작
    for thread in threads:
        thread.daemon = True
        thread.start()
    
    print("\n=== 매크로 시작 ===")
    print("F8: 힐링 매크로 시작/정지")
    print("F1~F4, F9: 스킬 매크로 시작/정지")
    print("Alt+O: 퀘스트 매크로 시작/정지")
    print("Alt+[: 체력/마력 회복 시작/정지")
    print("Alt+\\: 영역 선택")
    print("Alt+P: 파티버프 활성화")
    print("Ctrl+Q: 프로그램 종료")
    
    # 오버레이 실행
    try:
        overlay.run()
    except KeyboardInterrupt:
        pass
    finally:
        print("\n프로그램 종료")
        controller.is_active = False
        overlay.stop()

if __name__ == "__main__":
    main() 