import cv2
import numpy as np
import pyautogui
import os
from PIL import Image

def test_template_matching(screenshot_path, template_path):
    # 스크린샷과 템플릿 이미지 로드
    screenshot = cv2.imread(screenshot_path)
    template = cv2.imread(template_path)
    
    if screenshot is None:
        print(f"스크린샷을 불러올 수 없습니다: {screenshot_path}")
        return
    if template is None:
        print(f"템플릿 이미지를 불러올 수 없습니다: {template_path}")
        return
    
    # 이미지 정보 출력
    print(f"\n=== 이미지 정보 ===")
    print(f"스크린샷 크기: {screenshot.shape}")
    print(f"스크린샷 타입: {screenshot.dtype}")
    print(f"템플릿 크기: {template.shape}")
    print(f"템플릿 타입: {template.dtype}")
    
    # 그레이스케일 변환
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    
    # 여러 매칭 방법 테스트
    methods = [
        cv2.TM_CCOEFF_NORMED,
        cv2.TM_CCORR_NORMED,
        cv2.TM_SQDIFF_NORMED
    ]
    
    for method in methods:
        print(f"\n=== 매칭 방법: {method} ===")
        result = cv2.matchTemplate(screenshot_gray, template_gray, method)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if method == cv2.TM_SQDIFF_NORMED:
            match_val = 1 - min_val  # SQDIFF는 값이 작을수록 매칭이 잘된 것
            match_loc = min_loc
        else:
            match_val = max_val
            match_loc = max_loc
            
        print(f"매칭 점수: {match_val:.4f}")
        print(f"매칭 위치: {match_loc}")
        
        # 결과 시각화
        result_img = screenshot.copy()
        h, w = template_gray.shape
        cv2.rectangle(result_img, match_loc, (match_loc[0] + w, match_loc[1] + h), (0, 255, 0), 2)
        
        # 결과 저장
        method_name = str(method).split('.')[-1]
        cv2.imwrite(f'debug_result_{method_name}.png', result_img)

def take_debug_screenshot():
    # 스크린샷 촬영
    screen = pyautogui.screenshot()
    screen.save('debug_screenshot.png')
    return 'debug_screenshot.png'

def main():
    # 테스트할 NPC 이미지 경로
    base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    npc_images = [
        os.path.join(base_path, 'img', 'quest', 'king1.png'),
        os.path.join(base_path, 'img', 'quest', 'king2.png'),
        os.path.join(base_path, 'img', 'quest', 'king3.png')
    ]
    
    # OpenCV 버전 출력
    print(f"OpenCV 버전: {cv2.__version__}")
    
    # 스크린샷 촬영
    screenshot_path = take_debug_screenshot()
    
    # 각 NPC 이미지에 대해 테스트
    for npc_image in npc_images:
        if os.path.exists(npc_image):
            print(f"\n테스트 중인 NPC 이미지: {npc_image}")
            test_template_matching(screenshot_path, npc_image)
        else:
            print(f"이미지를 찾을 수 없습니다: {npc_image}")

if __name__ == "__main__":
    main() 