# This file contains the definition of the DraggableNode class, which is a QLabel that can be moved around the screen.

from PyQt5.QtCore import pyqtSignal, Qt, QPoint
from PyQt5.QtGui import QFontMetrics, QFont, QLinearGradient, QPalette, QColor, QBrush
from PyQt5.QtWidgets import QLabel

class DraggableNode(QLabel):
    """A draggable node that can be moved around the screen."""
    moved = pyqtSignal()

    def __init__(self, parent=None, name=None):
        super(DraggableNode, self).__init__(parent)
        self.name = name
        self.initUI(name)

    def initUI(self, name):
        if name:
            self.setText(name)
        self.setFont(QFont("Arial", 10, QFont.Bold))
        self.setAlignment(Qt.AlignCenter)
        self.updateSize()
        self.setupStyles()

    def setupStyles(self):
        # Set up a gradient background with shadow
        gradient = QLinearGradient(0, 0, 0, self.height())
        gradient.setColorAt(0.0, QColor(245, 245, 245))
        gradient.setColorAt(1.0, QColor(225, 225, 225))
        palette = QPalette()
        palette.setBrush(QPalette.Window, QBrush(gradient))
        self.setPalette(palette)
        self.setAutoFillBackground(True)

        # Set border and shadow effect
        self.setStyleSheet("""
            QLabel {
                border: 1px solid #AAA;
                border-radius: 10px;
                padding: 5px;
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:0, y2:1, stop:0 rgba(0, 0, 128, 255), stop:1 rgba(0, 0, 128, 255));
                color: white;
            }
            QLabel:hover {
                border: 1px solid #666;
            }
        """)

    def updateSize(self):
        metrics = QFontMetrics(self.font())
        width = metrics.width(self.text()) + 40  # Adding some padding
        height = max(metrics.height() + 20, 50)  # Ensure minimum height
        self.setFixedSize(width, height)

    def setText(self, text):
        super(DraggableNode, self).setText(text)
        self.updateSize()  # Update size whenever text changes

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            # Ensure movement is smooth and centered
            self.move(self.mapToParent(e.pos() - QPoint(self.width() // 2, self.height() // 2)))
            self.moved.emit()  # Signal that the node has been moved.
