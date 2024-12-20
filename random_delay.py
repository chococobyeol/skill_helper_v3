import random

def get_micro_delay():
    """0~5ms 사이의 랜덤한 딜레이를 반환"""
    return random.uniform(0, 0.005)

def add_delay(base_delay):
    """기본 딜레이에 마이크로 딜레이를 추가하여 반환"""
    return base_delay + get_micro_delay() 