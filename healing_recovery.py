import time
import win32api
import win32con
import pyautogui
import keyboard
import os
from threading import Thread
from mana_recovery import ManaRecoveryController
import numpy as np
import cv2
from datetime import datetime
import easyocr
import torch
import re

class HealingController:
    def __init__(self):
        self.is_running = True
        self.is_active = True
        self.is_healing = False
        pyautogui.PAUSE = 0.1
        pyautogui.FAILSAFE = False
        
        # 마나 회복 컨트롤러 초기화
        self.mana_controller = ManaRecoveryController()
        self.mana_controller.is_running = True  # 마나 회복은 항상 활성화
        
        # 이미지 파일 경로 설정
        self.img_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'img')
        self.lack_health_path = os.path.join(self.img_dir, 'lack_health.png')
        
        # 키 설정
        self.HEAL_KEY = 0x35  # 5키
        self.HOME_KEY = win32con.VK_HOME  # Home키
        self.ESC_KEY = win32con.VK_ESCAPE  # ESC키
        self.ENTER_KEY = win32con.VK_RETURN  # Enter키
        self.TOGGLE_KEY = 'F8'  # 매크로 토글 키
        self.EXIT_KEY = 'ctrl+q'  # 종료 키
        
        self.is_using_skill = False  # 스킬 사용 중 플래그 추가
        
        self.heal_area = None  # 힐 감지 영역 추가
        
        self.check_image_files()
        
        # 스크린샷 단축키 등록
        keyboard.add_hotkey('alt+]', self.take_debug_screenshot)
        
        # CUDA 및 GPU 설정
        try:
            # CUDA 설정 강제
            os.environ['CUDA_VISIBLE_DEVICES'] = '0'
            torch.cuda.empty_cache()
            
            if torch.cuda.is_available():
                device = torch.device('cuda:0')
                torch.cuda.set_device(device)
                print(f"GPU 사용: {torch.cuda.get_device_name(0)}")
                print(f"CUDA 버전: {torch.version.cuda}")
                
                # OCR 리더 초기화 (GPU 강제 설정)
                self.reader = easyocr.Reader(
                    ['en'],
                    gpu=True,
                    detector=True,
                    recognizer=True,
                    verbose=False,
                    model_storage_directory='./easyocr_models',
                    download_enabled=True,
                    cudnn_benchmark=True
                )
                print("EasyOCR GPU 모드로 초기화됨")
                
            else:
                raise RuntimeError("CUDA를 찾을 수 없습니다.")
                
        except Exception as e:
            print(f"GPU 초기화 실패: {str(e)}")
            print("CPU 모드로 대체합니다.")
            self.reader = easyocr.Reader(['en'], gpu=False)
        
        self.health_threshold = 3500

    def check_image_files(self):
        if not os.path.exists(self.lack_health_path):
            print("\n=== 이미지 파일 확인 필요 ===")
            print(f"파일이 없습니다: {self.lack_health_path}")
            print("현재 작업 디렉토리:", os.getcwd())
            print("이미지 디렉토리:", self.img_dir)
            print("=========================\n")

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.02)
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(0.02)

    def extract_health_value(self, image):
        """이미지에서 체력 수치를 추출"""
        try:
            # BGR로 변환
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # HSV 변환
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # 녹색 범위 설정 (게임의 체력 ���색)
            lower_green = np.array([40, 50, 50])  # 밝은 녹색
            upper_green = np.array([80, 255, 255])
            
            # 녹색 마스크 생성
            green_mask = cv2.inRange(hsv, lower_green, upper_green)
            
            # 노이즈 제거 및 텍스트 선명화
            kernel = np.ones((2,2), np.uint8)
            processed = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
            
            # OCR 실행 (숫자만 인식)
            results = self.reader.readtext(processed, allowlist='0123456789')
            
            for (bbox, text, prob) in results:
                # 숫자만 추출
                numbers = re.findall(r'\d+', text.replace(" ", ""))
                if numbers:
                    value = int(numbers[0])
                    if 0 <= value <= 9999999:  # 유효한 체력값 범위
                        return value
            
            return None
            
        except Exception as e:
            return None

    def find_image(self, image_path):
        try:
            if self.heal_area is None:
                region = (1285, 900, 314, 33)
            else:
                region = (self.heal_area.x(), self.heal_area.y(), 
                         self.heal_area.width(), self.heal_area.height())
            
            # 스크린샷 캡처
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            
            # 체력 수치 추출
            health = self.extract_health_value(screen_np)
            
            if health is not None:
                # 체력이 임계값 이하일 때만 출력
                if health <= self.health_threshold:
                    print(f"현재 체력: {health}")
                return health <= self.health_threshold
            
            return False
            
        except Exception as e:
            print(f"체력 확인 중 오류: {str(e)}")
            return False

    def use_heal_skill(self):
        if self.macro_controller.is_using_skill and self.macro_controller.current_skill != "heal":
            return

        self.is_using_skill = True
        self.macro_controller.is_using_skill = True
        self.macro_controller.current_skill = "heal"
        print("힐링 스킬 시도")
        
        try:
            keyboard.block_key('up')
            keyboard.block_key('down')
            keyboard.block_key('left')
            keyboard.block_key('right')
            keyboard.block_key('enter')
            
            self.send_key(self.ESC_KEY)
            time.sleep(0.01)
            self.send_key(self.HEAL_KEY)
            time.sleep(0.01)
            self.send_key(self.HOME_KEY)
            time.sleep(0.01)
            self.send_key(self.ENTER_KEY)
            time.sleep(0.01)
        
        finally:
            keyboard.unblock_key('up')
            keyboard.unblock_key('down')
            keyboard.unblock_key('left')
            keyboard.unblock_key('right')
            keyboard.unblock_key('enter')
            
            self.is_using_skill = False
            self.macro_controller.is_using_skill = False
            self.macro_controller.current_skill = None

    def check_and_heal(self):
        # 마나 회복 스레드 시작 
        mana_thread = Thread(target=self.mana_controller.check_and_recover_mana)
        mana_thread.daemon = True
        mana_thread.start()

        while self.is_active:
            if self.is_running:
                try:
                    # 마나 회복 중이면 힐링 시도하지 않음
                    if self.mana_controller.is_recovering:
                        time.sleep(0.01)
                        continue

                    # 체력 부족 상태 체크 (이제 OCR로 확인)
                    if self.find_image(self.lack_health_path):
                        self.is_healing = True
                        print("체력 부족: 힐링 스킬 시도")
                        self.use_heal_skill()
                        time.sleep(0.05)
                    else:
                        self.is_healing = False

                except Exception as e:
                    print(f"매크로 실행 중 오류: {str(e)}")
                    self.is_healing = False
                
                time.sleep(0.01)
            time.sleep(0.01)

    def toggle_macro(self):
        self.is_running = not self.is_running
        status = "실행 중" if self.is_running else "정지"
        print(f"\n힐링 매크로 상태: {status}")

    # is_running 속성의 setter 추가
    @property
    def is_running(self):
        return self._is_running

    @is_running.setter
    def is_running(self, value):
        self._is_running = value
        # 마나 회복도 같이 토글
        if hasattr(self, 'mana_controller'):
            self.mana_controller.is_running = value

    def take_debug_screenshot(self):
        """디버그용 스크린샷 기능 비활성화"""
        pass

def main():
    controller = HealingController()
    
    macro_thread = Thread(target=controller.check_and_heal)
    macro_thread.daemon = True
    macro_thread.start()
    
    print("\n=== 힐링 매크로 시작 ===")
    print(f"{controller.TOGGLE_KEY}: 힐링 매크로 시작/정지")
    print(f"{controller.EXIT_KEY}: 프로그램 종료")
    
    keyboard.add_hotkey(controller.TOGGLE_KEY, controller.toggle_macro)
    keyboard.add_hotkey('alt+]', controller.take_debug_screenshot)
    
    try:
        keyboard.wait(controller.EXIT_KEY)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n프로그램 종료")
        controller.is_active = False

if __name__ == "__main__":
    main() 