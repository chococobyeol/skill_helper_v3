import time
import win32api
import win32con
import pyautogui
import keyboard
import os
from threading import Thread
import numpy as np
import cv2

class ManaRecoveryController:
    def __init__(self):
        self.is_running = False
        self.is_active = True
        self.is_recovering = False
        self.skill_controller = None
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = False
        
        # 이미지 파일 경로 설정
        self.img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
        self.lack_mana1_path = os.path.join(self.img_dir, 'lack_mana1.png')
        self.lack_mana2_path = os.path.join(self.img_dir, 'lack_mana2.png')
        self.fail_recovery_path = os.path.join(self.img_dir, 'fail_mana_recovery.png')
        
        # 키 설정
        self.MANA_RECOVERY_KEY = 0x37  # 7키
        self.MANA_POTION_KEY = 0x55    # U키
        self.TOGGLE_KEY = 'F9'
        self.EXIT_KEY = 'ctrl+q'
        
        self.is_using_skill = False  # 스킬 사용 중 플래그 추가
        
        self.mana_area = None  # 마나 감지 영역 추가
        
        self.check_image_files()

    def check_image_files(self):
        files = [
            self.lack_mana1_path,
            self.lack_mana2_path,
            self.fail_recovery_path
        ]
        missing_files = []
        for file in files:
            if not os.path.exists(file):
                missing_files.append(file)
        
        if missing_files:
            print("\n=== 이미지 파일 확인 필요 ===")
            print("다음 파일들이 없습니다:")
            for file in missing_files:
                print(f"- {file}")
            print("현재 작업 디렉토리:", os.getcwd())
            print("이미지 디렉토리:", self.img_dir)
            print("=========================\n")

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

    def find_image(self, image_path):
        try:
            if self.mana_area is None:  # 영역이 설정되지 않은 경우 기본 영역 사용
                region = (1150, 678, 450, 182)  # 스킬 영역의 기본값
            else:
                region = (self.mana_area.x(), self.mana_area.y(), 
                         self.mana_area.width(), self.mana_area.height())
            
            # pyautogui 대신 OpenCV 직접 사용
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
            
            template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
            if template is None:
                print(f"템플릿 이미지를 불러올 수 없습니다: {image_path}")
                return False
            
            # 템플릿 매칭 수행
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            # 임계값을 0.9로 조정 (90% 이상 일치)
            if max_val >= 0.9:
                location = (max_loc[0], max_loc[1], template.shape[1], template.shape[0])
                print(f"이미지 발견: {os.path.basename(image_path)} 위치: {location}")
                return True
            return False
            
        except Exception as e:
            if not isinstance(e, pyautogui.ImageNotFoundException):
                print(f"오류 발생: {str(e)}")
            return False

    def use_mana_potion(self):
        self.is_using_skill = True  # 스킬 사용 시작
        print("마나 물약 사용")
        self.send_key(self.MANA_POTION_KEY)
        time.sleep(0.05)
        self.send_key(self.MANA_POTION_KEY)
        time.sleep(0.05)
        self.is_using_skill = False  # 스킬 사용 완료

    def try_mana_recovery(self):
        self.is_using_skill = True  # 스킬 사용 시작
        self.send_key(self.MANA_RECOVERY_KEY)
        time.sleep(0.1)
        success = not self.find_image(self.fail_recovery_path)
        self.is_using_skill = False  # 스킬 사용 완료
        return success

    def check_and_recover_mana(self):
        while self.is_active:
            if self.is_running:
                try:
                    # 마나 회복 실패 상태와 일반 마나 부족 상태만 먼저 체크
                    fail_state = self.find_image(self.fail_recovery_path)
                    lack_mana1 = self.find_image(self.lack_mana1_path)

                    # 마나 회복이 필요한 경우
                    if fail_state or lack_mana1:
                        self.is_recovering = True
                        
                        # 일반 마나 부족일 때만 심각한 마나 부족 상태 체크
                        if lack_mana1:
                            lack_mana2 = self.find_image(self.lack_mana2_path)
                            if lack_mana2:
                                print("마나가 너무 부족합니다! 물약 사용")
                                self.use_mana_potion()
                                time.sleep(0.02)

                        # 마나 회복 스킬 사용
                        print("마나 회복 스킬 시도")
                        self.send_key(self.MANA_RECOVERY_KEY)
                        time.sleep(0.05)
                    else:
                        self.is_recovering = False

                except Exception as e:
                    print(f"매크로 실행 중 오류: {str(e)}")
                    self.is_recovering = False
                
                time.sleep(0.01)
            time.sleep(0.01)

    def toggle_macro(self):
        self.is_running = not self.is_running
        status = "실행 중" if self.is_running else "정지"
        print(f"\n매크로 상태: {status}")

def main():
    controller = ManaRecoveryController()
    
    macro_thread = Thread(target=controller.check_and_recover_mana)
    macro_thread.daemon = True
    macro_thread.start()
    
    print("\n=== 마나 회복 컨트롤러 시작 ===")
    print(f"{controller.TOGGLE_KEY}: 마나 회복 매크로 시작/정지")
    print(f"{controller.EXIT_KEY}: 프로그램 종료")
    
    keyboard.add_hotkey(controller.TOGGLE_KEY, controller.toggle_macro)
    
    try:
        keyboard.wait(controller.EXIT_KEY)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n프로그램 종료")
        controller.is_active = False

if __name__ == "__main__":
    main() 