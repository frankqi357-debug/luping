from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, QRect, pyqtSignal
from PyQt6.QtGui import QPainter, QPen, QColor

class RegionSelector(QWidget):
    """
    Widget for selecting screen region
    """
    
    region_selected = pyqtSignal(tuple)  # Emits (x, y, width, height)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_pos = None
        self.end_pos = None
        self.is_selecting = False
        
        # Set full screen and transparent
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 50);")
    
    def mousePressEvent(self, event):
        """
        Handle mouse press
        """
        self.start_pos = event.pos()
        self.is_selecting = True
    
    def mouseMoveEvent(self, event):
        """
        Handle mouse move
        """
        if self.is_selecting:
            self.end_pos = event.pos()
            self.update()
    
    def mouseReleaseEvent(self, event):
        """
        Handle mouse release
        """
        if self.is_selecting:
            self.end_pos = event.pos()
            self.is_selecting = False
            
            # Emit region
            x = min(self.start_pos.x(), self.end_pos.x())
            y = min(self.start_pos.y(), self.end_pos.y())
            width = abs(self.end_pos.x() - self.start_pos.x())
            height = abs(self.end_pos.y() - self.start_pos.y())
            
            self.region_selected.emit((x, y, width, height))
            self.close()
    
    def paintEvent(self, event):
        """
        Paint selection rectangle
        """
        if self.start_pos and self.end_pos and self.is_selecting:
            painter = QPainter(self)
            
            # Draw rectangle
            rect = QRect(self.start_pos, self.end_pos)
            pen = QPen(QColor(100, 200, 255))
            pen.setWidth(2)
            painter.setPen(pen)
            painter.drawRect(rect.normalized())
            
            # Draw fill with transparency
            fill_color = QColor(100, 200, 255, 30)
            painter.fillRect(rect.normalized(), fill_color)
