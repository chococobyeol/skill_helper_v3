import time
import pyautogui
import win32api
import win32con
from PIL import Image
import os
import cv2
import numpy as np

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
            'skeleton': os.path.join(self.base_path, 'img', 'quest', 'skeleton.png')
        }
        
        # NPC 이미지 경로들 추가
        self.npc_image_paths = [
            os.path.join(self.base_path, 'img', 'quest', 'king1.png'),
            os.path.join(self.base_path, 'img', 'quest', 'king2.png'),
            os.path.join(self.base_path, 'img', 'quest', 'king3.png')
        ]
        
        self.accept_image_path = os.path.join(self.base_path, 'img', 'quest', 'accept1.png')
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
        self.current_attempt = 0  # 시도 횟수 초기화
        max_attempts = 50
        attempt_count = 0
        
        # 실행 상태 플래그 추가
        self.is_running = True
        
        while attempt_count < max_attempts and self.is_running:
            self.current_attempt = attempt_count  # 현재 시도 횟수 업데이트
            attempt_count += 1
            print(f"\n=== 퀘스트 시도 {attempt_count}/{max_attempts} ===")
            
            time.sleep(1.0)
            
            # 퀘스트 수락 시도
            accept_result = self.try_accept_quest()
            if accept_result is None:  # 오류 발생
                continue
            elif not accept_result:  # 수락 실패
                continue
                
            # 퀘스트 확인 및 취소
            check_result = self.check_and_cancel_quest()
            if check_result is None:  # 오류 발생
                continue
            elif check_result:  # 원하는 퀘스트
                print("원하는 퀘스트 발견! 수락 완료")
                self.is_running = False  # 매크로 종료
                return True
            else:
                print("원하지 않는 퀘스트, 다시 시도합니다...")
                time.sleep(0.5)
                continue
        
        if not self.is_running:
            print("\n퀘스트 매크로가 중지되었습니다.")
        else:
            print(f"\n{max_attempts}회 시도했지만 원하는 퀘스트를 찾지 못했습니다.")
        return False

    def try_accept_quest(self):
        try:
            print("퀘스트 NPC 찾는 중...")
            
            # 스크린샷을 OpenCV 이미지로 변환
            screen = pyautogui.screenshot()
            screen_np = np.array(screen)
            screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
            screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
            
            for npc_image in self.npc_image_paths:
                print(f"NPC 이미지 경로: {npc_image}")
                if not os.path.exists(npc_image):
                    continue
                    
                try:
                    template = cv2.imread(npc_image, cv2.IMREAD_GRAYSCALE)
                    if template is None:
                        print(f"템플릿 이미지를 불러올 수 없습니다: {npc_image}")
                        continue
                    
                    # 템플릿 매칭 수행
                    result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                    
                    # 임계값을 0.9로 조정 (90% 이상 일치)
                    if max_val >= 0.9:
                        center = (max_loc[0] + template.shape[1] // 2, 
                                max_loc[1] + template.shape[0] // 2)
                        print(f"NPC 위치 발견: {center} (매칭 점수: {max_val:.4f})")
                        
                        # NPC 클릭 및 퀘스트 수락 진행
                        pyautogui.doubleClick(center)
                        time.sleep(0.5)
                        
                        # 첫 번째 엔터
                        pyautogui.press('enter')
                        time.sleep(0.5)
                        
                        # accept 이미지 확인
                        accept_location = None
                        screen = pyautogui.screenshot()
                        screen_np = np.array(screen)
                        screen_bgr = cv2.cvtColor(screen_np, cv2.COLOR_RGB2BGR)
                        screen_gray = cv2.cvtColor(screen_bgr, cv2.COLOR_BGR2GRAY)
                        
                        template = cv2.imread(self.accept_image_path, cv2.IMREAD_GRAYSCALE)
                        if template is not None:
                            result = cv2.matchTemplate(screen_gray, template, cv2.TM_CCOEFF_NORMED)
                            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                            if max_val >= 0.9:
                                accept_location = True
                        
                        if not accept_location:
                            print("수락 버튼이 없습니다. 취소 단계로 판단됩니다.")
                            pyautogui.press('esc')
                            return False
                        
                        print("수락 버튼 발견, 퀘스트 수락을 진행합니다.")
                        
                        # 나머지 키 입력
                        pyautogui.press('enter')  # 두 번째 엔터
                        time.sleep(0.2)
                        pyautogui.press('down')   # 아래 방향키
                        time.sleep(0.2)
                        pyautogui.press('enter')  # 세 번째 엔터
                        time.sleep(0.2)
                        pyautogui.press('enter')  # 네 번째 엔터
                        time.sleep(0.5)
                        
                        return True
                        
                except Exception as e:
                    print(f"이미지 {npc_image} 검색 중 오류: {str(e)}")
                    continue
            
            print("어떤 각도에서도 NPC를 찾을 수 없습니다.")
            return False
            
        except Exception as e:
            print(f"퀘스트 수락 중 오류: {str(e)}")
            print(f"오류 타입: {type(e).__name__}")
            pyautogui.press('esc')
            return None