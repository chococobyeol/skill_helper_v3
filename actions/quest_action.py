import time
import pyautogui
import win32api
import win32con
from PIL import Image
import os
import cv2
import numpy as np
from random_delay import add_delay

class QuestAction:
    def __init__(self):
        # 현재 스크립트의 디렉토리 경로 가져오기
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        # 절대 경로로 이미지 경로 설정
        self.quest_image_paths = {
            'beginner_ghost': os.path.join(self.base_path, 'img', 'quest', 'beginner_ghost.png'),
            'ghost': os.path.join(self.base_path, 'img', 'quest', 'ghost.png'),
            'highclass_ghost': os.path.join(self.base_path, 'img', 'quest', 'highclass_ghost.png'),
            'swift_skeleton': os.path.join(self.base_path, 'img', 'quest', 'swift_skeleton.png'),
            'skeleton': os.path.join(self.base_path, 'img', 'quest', 'skeleton.png'),
            'insect': os.path.join(self.base_path, 'img', 'quest', 'insect.png'),
            'virgin_ghost': os.path.join(self.base_path, 'img', 'quest', 'virgin_ghost.png'),
            'bachelor_ghost': os.path.join(self.base_path, 'img', 'quest', 'bachelor_ghost.png'),
            'broom_ghost': os.path.join(self.base_path, 'img', 'quest', 'broom_ghost.png'),
            'egg_ghost': os.path.join(self.base_path, 'img', 'quest', 'egg_ghost.png'),
            'fire_ghost': os.path.join(self.base_path, 'img', 'quest', 'fire_ghost.png')
        }
        
        # NPC 이미지 경로들 추가
        self.npc_image_paths = [
            os.path.join(self.base_path, 'img', 'quest', 'king1.png'),
            os.path.join(self.base_path, 'img', 'quest', 'king2.png'),
            os.path.join(self.base_path, 'img', 'quest', 'king3.png')
        ]
        
        # 수락/취소 버튼 이미지 경로
        self.accept_image_path = os.path.join(self.base_path, 'img', 'quest', 'accept.png')
        self.cancel_image_path = os.path.join(self.base_path, 'img', 'quest', 'cancel.png')
        self.macro_controller = None
        
        # 이미지 파일 존재 여부 확인
        if not self._check_image_files():
            raise FileNotFoundError("필요한 이미지 파일이 없습니다. 이미지 파일을 확인해주세요.")
        
        self.current_attempt = 0  # 현재 시도 횟수
        self.found_quest_type = None  # 찾은 퀘스트 종류
    
    def _check_image_files(self):
        all_files_exist = True
        
        # 퀘스트 타입 이미지 확인
        for quest_type, image_path in self.quest_image_paths.items():
            if not os.path.exists(image_path):
                print(f"경고: {quest_type} 이미지 파일이 없습니다: {image_path}")
                all_files_exist = False
        
        # NPC 이미지 확인
        for npc_image in self.npc_image_paths:
            if not os.path.exists(npc_image):
                print(f"경고: NPC 이미지 파일이 없습니다: {npc_image}")
                all_files_exist = False
        
        # 수락 버튼 이미지 확인
        if not os.path.exists(self.accept_image_path):
            print(f"경고: 수락 버튼 이미지 파일이 없습니다: {self.accept_image_path}")
            all_files_exist = False
            
        return all_files_exist

    def find_quest_type(self):
        try:
            screen = pyautogui.screenshot()
            # screen.save('debug_screenshot.png')
            
            print("퀘스트 종류 확인 중...")
            region = (1208, 127, 1550-1208, 604-127)
            print(f"검색 영역: {region}")
            
            # 전체 스크린샷에서 region 부분만 잘라내기
            screen = pyautogui.screenshot(region=region)
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
            
            for quest_type, image_path in self.quest_image_paths.items():
                if not self.macro_controller.quest_types[quest_type]:
                    continue
                    
                try:
                    print(f"{quest_type} 퀘스트 찾는 중...")
                    print(f"이미지 경로: {image_path}")
                    print(f"이미지 존재 여부: {os.path.exists(image_path)}")
                    
                    template = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
                    if template is None:
                        print(f"템플릿 이미지를 불러올 수 없습니다: {image_path}")
                        continue
                    
                    # 템플릿 매칭 수행
                    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    # 퀘스트 발견은 94% 이상 매칭 
                    if max_val >= 0.94:
                        print(f"{quest_type} 퀘스트 발견! 매칭 점수: {max_val:.4f}")
                        self.found_quest_type = quest_type  # 찾은 퀘스트 종류 저장
                        return True
                    else:
                        print(f"{quest_type} 퀘스트 없음")
                        
                except Exception as e:
                    print(f"{quest_type} 확인 중 오류: {str(e)}")
                    continue
            
            self.found_quest_type = None  # 퀘스트를 찾지 못한 경우
            return False
            
        except Exception as e:
            print(f"퀘스트 확인 오류: {str(e)}")
            pyautogui.press('esc')
            return None

    def check_and_cancel_quest(self):
        print("\n=== 퀘스트 내용 확인 시작 ===")
        pyautogui.press('enter')
        time.sleep(0.2)
        
        print("스크롤 시작...")
        pyautogui.press('s')
        time.sleep(0.2)
        pyautogui.press('pagedown')
        time.sleep(0.2)
        pyautogui.press('pagedown')
        time.sleep(0.5)
        
        result = self.find_quest_type()
        if result is None:  # 오류 발생
            return None
        elif result:  # 원하는 퀘스트 발견
            return True
        else:
            print("\n=== 일반 퀘스트 취소 진행 ===")
            # NPC 찾기
            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
            
            for npc_image in self.npc_image_paths:
                try:
                    template = cv2.imread(npc_image, cv2.IMREAD_GRAYSCALE)
                    if template is None:
                        continue
                    
                    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    if max_val >= 0.9:
                        center = (max_loc[0] + template.shape[1] // 2, 
                                max_loc[1] + template.shape[0] // 2)
                        print(f"NPC 위치 발견: {center}")
                        
                        # 취소 작업 시작
                        pyautogui.doubleClick(center)  # NPC 더블클릭
                        time.sleep(0.5)
                        pyautogui.press('enter')  # 첫 째 엔터
                        time.sleep(0.2)
                        pyautogui.press('down')   # 아래 방향키
                        time.sleep(0.2)
                        pyautogui.press('enter')  # 두 번째 엔터
                        time.sleep(0.2)
                        pyautogui.press('enter')  # 세 번째 엔터
                        time.sleep(0.2)
                        pyautogui.press('enter')  # 네 번째 엔터
                        time.sleep(0.5)
                        
                        return False
                        
                except Exception as e:
                    print(f"이미지 {npc_image} 검색 중 오류: {str(e)}")
                    continue
            
            print("취소를 위한 NPC를 찾을 수 없습니다.")
            return None

    def execute_quest_action(self):
        """퀘스트 매크로 메인 실행 함수"""
        self.current_attempt = 0  # 시도 횟수 초기화
        max_attempts = 50
        self.is_running = True
        
        while self.current_attempt < max_attempts and self.is_running:
            print(f"\n=== 퀘스트 시도 {self.current_attempt + 1}/{max_attempts} ===")
            
            # NPC 찾기
            npc_location = self.find_npc()
            if not npc_location:
                print("NPC를 찾을 수 없습니다.")
                time.sleep(1.0)
                pyautogui.press('esc')
                self.current_attempt += 1  # 시도 횟수 증가 위치 수정
                continue
                
            # NPC 더블클릭
            pyautogui.doubleClick(npc_location)
            time.sleep(0.5)
            
            # 대화창 상태 확인
            dialog_state = self.check_dialog_state()
            
            if dialog_state == "accept":
                print("수락 단계 감지")
                if self.process_accept():
                    # 퀘스트 내용 확인
                    if self.check_quest_content():
                        print("원하는 퀘스트 발견! 수락 완료")
                        self.is_running = False
                        return True
                    else:
                        print("원하지 않는 퀘스트, 취소 진행")
                        # NPC 다시 찾아서 취소
                        npc_location = self.find_npc()
                        if npc_location:
                            pyautogui.doubleClick(npc_location)
                            time.sleep(0.5)
                            self.process_cancel()
                
            elif dialog_state == "cancel":
                print("취소 단계 감지")
                self.process_cancel()
                
            else:
                print("알 수 없는 대화창 상태")
                pyautogui.press('enter')
                time.sleep(0.2)
                pyautogui.press('esc')
            
            self.current_attempt += 1
            time.sleep(0.5)
            
        print(f"\n{max_attempts}회 시도했지만 원하는 퀘스트를 찾지 못했습니다.")
        return False

    def find_npc(self):
        """NPC를 찾아서 위치를 반환"""
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
        
        for npc_image in self.npc_image_paths:
            if not os.path.exists(npc_image):
                continue
                
            template = cv2.imread(npc_image, cv2.IMREAD_GRAYSCALE)
            if template is None:
                continue
            
            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= 0.9:
                center = (max_loc[0] + template.shape[1] // 2, 
                         max_loc[1] + template.shape[0] // 2)
                print(f"NPC 위치 발견: {center}")
                return center
        return None

    def check_dialog_state(self):
        """대화창 상태 확인 (수락/취소)"""
        screen = pyautogui.screenshot()
        screen_np = np.array(screen)
        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
        screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
        
        # 수락 버튼 확인
        accept_template = cv2.imread(self.accept_image_path, cv2.IMREAD_GRAYSCALE)
        if accept_template is not None:
            result = cv2.matchTemplate(screen_gray, accept_template, cv2.TM_CCOEFF_NORMED)
            if np.max(result) >= 0.9:
                return "accept"
        
        # 취소 버튼 확인
        cancel_template = cv2.imread(self.cancel_image_path, cv2.IMREAD_GRAYSCALE)
        if cancel_template is not None:
            result = cv2.matchTemplate(screen_gray, cancel_template, cv2.TM_CCOEFF_NORMED)
            if np.max(result) >= 0.9:
                return "cancel"
        
        return "unknown"

    def process_accept(self):
        """수락 단계 처리"""
        pyautogui.press('enter')  # 첫 번째 엔터
        time.sleep(0.5)
        pyautogui.press('enter')  # 두 번째 엔터
        time.sleep(0.2)
        pyautogui.press('down')   # 아래 방향키
        time.sleep(0.2)
        pyautogui.press('enter')  # 세 번째 엔터
        time.sleep(0.2)
        pyautogui.press('enter')  # 네 번째 엔터
        time.sleep(0.5)
        return True

    def process_cancel(self):
        """취소 단계 처리"""
        time.sleep(0.5)
        pyautogui.press('enter')  # 첫 째 엔터
        time.sleep(0.2)
        pyautogui.press('down')   # 아래 방향키
        time.sleep(0.2)
        pyautogui.press('enter')  # 두 번째 엔터
        time.sleep(0.2)
        pyautogui.press('enter')  # 세 번째 엔터
        time.sleep(0.2)
        pyautogui.press('enter')  # 네 번째 엔터
        time.sleep(0.5)

    def check_quest_content(self):
        """퀘스트 내용을 확인하여 원하는 퀘스트인지 체크"""
        print("\n=== 퀘스트 내용 확인 시작 ===")
        pyautogui.press('enter')
        time.sleep(0.2)
        
        print("스크롤 시작...")
        pyautogui.press('s')
        time.sleep(0.2)
        pyautogui.press('pagedown')
        time.sleep(0.2)
        pyautogui.press('pagedown')
        time.sleep(0.5)
        
        return self.find_quest_type()

    def send_key(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(add_delay(0.02))
        win32api.keybd_event(key, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(add_delay(0.02))