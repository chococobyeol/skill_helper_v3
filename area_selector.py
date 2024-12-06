from PyQt5.QtWidgets import QWidget, QApplication
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtGui import QPainter, QPen, QColor
import sys
import keyboard

class AreaSelector(QWidget):
    def __init__(self, width=440, height=380):
        super().__init__()
        self.setGeometry(1150, 678, width, height)
        self.setWindowTitle('영역 선택')
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 드래그 관련 변수
        self.dragging = False
        self.offset = None
        
        # 영역 정보
        self.skill_area = QRect(0, 95, 440, 75)  # 스킬 영역
        self.heal_area = QRect(126, 224, 314, 33)  # 힐 영역
        self.coord_area = QRect(220, 340, 220, 33)  # 좌표 영역
        
        # 영역 선택 모드
        self.selecting_mode = None  # 'skill' 또는 'heal'
    
    def paintEvent(self, event):
        painter = QPainter(self)
        
        # 전체 영역 반투명 배경
        background_color = QColor(255, 255, 255, 50)  # 흰색 반투명
        painter.fillRect(0, 0, self.width(), self.height(), background_color)
        
        # 전체 영역 테두리
        painter.setPen(QPen(Qt.red, 2))
        painter.drawRect(0, 0, self.width()-1, self.height()-1)
        
        # 스킬 영역 (파란색)
        skill_color = QColor(0, 0, 255, 30)  # 파란색 반투명
        painter.fillRect(self.skill_area, skill_color)
        painter.setPen(QPen(Qt.blue, 2))
        painter.drawRect(self.skill_area)
        
        # 힐 영역 (초록색)
        heal_color = QColor(0, 255, 0, 30)  # 초록색 반투명
        painter.fillRect(self.heal_area, heal_color)
        painter.setPen(QPen(Qt.green, 2))
        painter.drawRect(self.heal_area)
        
        # 좌표 표시
        painter.setPen(QPen(Qt.white, 1))
        window_pos = self.pos()
        skill_text = f"스킬 영역: ({window_pos.x() + self.skill_area.x()}, {window_pos.y() + self.skill_area.y()}, {self.skill_area.width()}, {self.skill_area.height()})"
        heal_text = f"힐 영역: ({window_pos.x() + self.heal_area.x()}, {window_pos.y() + self.heal_area.y()}, {self.heal_area.width()}, {self.heal_area.height()})"
        
        painter.drawText(10, self.height() - 40, skill_text)
        painter.drawText(10, self.height() - 20, heal_text)
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    
    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = event.globalPos() - self.offset
            self.move(new_pos)
            self.update()  # 화면 갱신하여 좌표 업데이트
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
    
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:  # Enter 키
            print("영역 설정 완료")
            self.close()
        elif event.key() == Qt.Key_Escape:  # ESC 키
            print("영역 설정 취소")
            self.skill_area = None
            self.heal_area = None
            self.close()
    
    def get_absolute_areas(self):
        if self.skill_area is None or self.heal_area is None:
            return None, None
            
        window_pos = self.pos()
        skill_abs = QRect(
            window_pos.x() + self.skill_area.x(),
            window_pos.y() + self.skill_area.y(),
            self.skill_area.width(),
            self.skill_area.height()
        )
        heal_abs = QRect(
            window_pos.x() + self.heal_area.x(),
            window_pos.y() + self.heal_area.y(),
            self.heal_area.width(),
            self.heal_area.height()
        )
        return skill_abs, heal_abs

def show_area_selector():
    app = QApplication(sys.argv)
    selector = AreaSelector()
    selector.show()
    app.exec_()
    return selector.get_absolute_areas()

if __name__ == "__main__":
    keyboard.add_hotkey('shift+\\', show_area_selector)
    keyboard.wait('esc')