import sys
import os
import pyautogui
import PIL
import numpy

print("\n=== 패키지 버전 및 설정 확인 ===")
print(f"Python: {sys.version}")
print(f"PyAutoGUI: {pyautogui.__version__}")
print(f"Pillow: {PIL.__version__}")
print(f"Numpy: {numpy.__version__}")

print("\n=== 작업 디렉토리 및 파일 확인 ===")
print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"이미지 파일 존재 여부: {os.path.exists('img/lack_health.PNG')}")
if os.path.exists('img'):
    print("img 폴더 내 파일들:")
    for file in os.listdir('img'):
        print(f"- {file}")

print("\n=== PyAutoGUI 설정 ===")
print(f"FAILSAFE: {pyautogui.FAILSAFE}")
print(f"PAUSE: {pyautogui.PAUSE}")
print(f"MINIMUM_DURATION: {pyautogui.MINIMUM_DURATION}")

# 간단한 이미지 인식 테스트
try:
    print("\n=== 이미지 인식 테스트 ===")
    # 힐링 이미지로 테스트
    location = pyautogui.locateOnScreen('img/lack_health.png', grayscale=True)
    print(f"이미지 인식 결과: {location}")
except Exception as e:
    print(f"이미지 인식 오류: {type(e).__name__} - {str(e)}")

print("\n=== 모듈 경로 확인 ===")
print(f"PyAutoGUI 경로: {pyautogui.__file__}")