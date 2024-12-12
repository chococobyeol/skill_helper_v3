# mana_recovery.py
import time
import win32api
import win32con
import pyautogui
import keyboard
import os
from threading import Thread
import numpy as np
import cv2
import re
import torch
import easyocr

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
        self.CTRL_KEY = win32con.VK_CONTROL  # Ctrl 키
        self.TOGGLE_KEY = 'F9'
        self.EXIT_KEY = 'ctrl+q'
        
        self.is_using_skill = False  # 스킬 사용 중 플래그 추가
        
        self.mana_area = None  # 마나 감지 가
        
        # OCR 초기화
        try:
            if torch.cuda.is_available():
                device = torch.device('cuda:0')
                torch.cuda.set_device(device)
                print(f"GPU 사용: {torch.cuda.get_device_name(0)}")
                print(f"CUDA 버전: {torch.version.cuda}")
                
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
            
        except Exception as e:
            print(f"GPU 초기화 실패: {str(e)}")
            print("CPU 모드로 대체합니다.")
            self.reader = easyocr.Reader(['en'], gpu=False)

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

    def extract_mana_value(self, image):
        """이미지에서 마나 수치를 추출"""
        try:
            # BGR로 변환
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            # HSV 변환
            hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
            
            # 기존 녹색 범위
            lower_green1 = np.array([40, 50, 50])
            upper_green1 = np.array([80, 255, 255])
            
            # BBD3AB ±2 범위 추가 (HSV로 변환)
            lower_green2 = np.array([82, 40, 160])  # BBD3AB - 2
            upper_green2 = np.array([86, 50, 180])  # BBD3AB + 2
            
            # 두 마스크 생성
            mask1 = cv2.inRange(hsv, lower_green1, upper_green1)
            mask2 = cv2.inRange(hsv, lower_green2, upper_green2)
            
            # 마스크 합치기
            green_mask = cv2.bitwise_or(mask1, mask2)
            
            # 노이즈 제거 및 텍스트 선명화
            kernel = np.ones((2,2), np.uint8)
            processed = cv2.morphologyEx(green_mask, cv2.MORPH_CLOSE, kernel)
            
            # OCR 실행 (숫자만 인식)
            results = self.reader.readtext(processed, allowlist='0123456789')
            
            for (bbox, text, prob) in results:
                numbers = re.findall(r'\d+', text.replace(" ", ""))
                if numbers:
                    value = int(numbers[0])
                    if 0 <= value <= 999999:  # 유효한 마나값 범위
                        return value
            
            # OCR 실패시 템플릿 매칭으로 확인
            screen_gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)
            
            # 템플릿별 반환값 설정
            template_values = {
                1: 0,    # zero_mana1.png -> 0
                2: 30,   # zero_mana2.png -> 30
                3: 60,   # zero_mana3.png -> 60
                4: 90    # zero_mana4.png -> 90
            }
            
            # 템플릿 매칭 확인
            for i in range(1, 5):
                template_path = os.path.join(self.img_dir, f'zero_mana{i}.png')
                if os.path.exists(template_path):
                    zero_template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
                    if zero_template is not None:
                        result = cv2.matchTemplate(screen_gray, zero_template, cv2.TM_CCOEFF_NORMED)
                        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                        
                        if max_val >= 0.9:  # 90% 이상 일치하면 해당 값 반환
                            return template_values[i]
            
            return None
            
        except Exception as e:
            return None

    def check_mana(self):
        """현재 마나 수치 확인"""
        try:
            if self.mana_area is None:
                # 체력바 바로 아래 위치 (체력바와 같은 크기)
                region = (1285, 933, 314, 33)  # y값을 900 + 33 = 933으로 설정
            else:
                region = (self.mana_area.x(), self.mana_area.y(), 
                         self.mana_area.width(), self.mana_area.height())
            
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            
            return self.extract_mana_value(screen_np)
            
        except Exception:
            return None

    def use_mana_potion(self):
        self.is_using_skill = True  # 스킬 사용 시작
        print("마나 물약 사용")
        # U 키만 누르고 떼기
        self.send_key(self.MANA_POTION_KEY)
        time.sleep(0.02)
        self.send_key(self.MANA_POTION_KEY)
        time.sleep(0.02)
        self.is_using_skill = False  # 스킬 사용 완료

    def try_mana_recovery(self):
        """마나 회복 스킬 사용"""
        self.is_using_skill = True
        print("마나 회복 스킬 시도")
        self.send_key(self.MANA_RECOVERY_KEY)
        time.sleep(0.05)
        self.is_using_skill = False

    def check_and_recover_mana(self):
        while self.is_active:
            if self.is_running:
                try:
                    current_mana = self.check_mana()
                    
                    if current_mana is not None:
                        if current_mana <= 30:  # 마나가 매우 부족할 때
                            self.is_recovering = True
                            print(f"현재 마나: {current_mana}")  # 마나가 매우 부족할 때만 출력
                            print("마나가 너무 부족합니다! 물약 사용")
                            self.use_mana_potion()
                            time.sleep(0.05)
                        elif current_mana <= 1000:  # 마나가 부족할 때
                            self.is_recovering = True
                            print(f"현재 마나: {current_mana}")  # 마나가 부족할 때만 출력
                            self.try_mana_recovery()
                            time.sleep(0.05)
                        else:
                            self.is_recovering = False

                except Exception as e:
                    print(f"마나 체크 오류: {str(e)}")
                    self.is_recovering = False
                
                time.sleep(0.05)
            time.sleep(0.05)

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