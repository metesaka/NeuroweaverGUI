# This file is used to create a configuration editor widget that allows the user to edit a JSON configuration file.

import sys
sys.path.extend("..")
import json
from PyQt5.QtWidgets import QMessageBox,QFileDialog,QApplication,QDialog, QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QHBoxLayout
from PyQt5.QtCore import pyqtSignal

class ConfigEditor(QWidget):
    '''A configuration editor widget that allows the user to edit a JSON configuration file.'''
    closed = pyqtSignal()
    def __init__(self,inputs):
        super().__init__()
        defaultConfig = "GUI/config.json"
        self.configFile = defaultConfig
        x,y= inputs['x'],inputs['y']
        self.initUI(x,y)
        self.loadConfig()
        self.show()

    def initUI(self,x,y):
        self.layout = QVBoxLayout(self)
        self.entries = {}
        self.configLayout = QVBoxLayout()
        self.layout.addLayout(self.configLayout)

        self.loadButton = QPushButton('Load Configuration', self)
        self.loadButton.clicked.connect(self.openFile)
        self.layout.addWidget(self.loadButton)

        self.saveButton = QPushButton('Save Configuration', self)
        self.saveButton.clicked.connect(self.saveConfig)
        self.layout.addWidget(self.saveButton)

        self.OKButton = QPushButton('OK', self)
        self.OKButton.clicked.connect(self.accept)
        self.layout.addWidget(self.OKButton)

        self.setGeometry(x, y, 300, 200)
        self.setWindowTitle('Configuration Editor')
        self.show()

    def openFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self, "Open Configuration", "", "JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            self.configFile = fileName
            self.loadConfig()

    def loadConfig(self):
        # ask for location to save the file
        # self.configLayout = QVBoxLayout()
        self.clearLayout(self.configLayout)
        with open(self.configFile, 'r') as file:
            self.config = json.load(file)
            for key, value in self.config.items():
                label = QLabel(key, self)
                lineEdit = QLineEdit(self)
                lineEdit.setText(str(value))
                self.entries[key] = lineEdit
                rowLayout = QHBoxLayout()
                rowLayout.addWidget(label)
                rowLayout.addWidget(lineEdit)
                self.configLayout.addLayout(rowLayout)
    def clearLayout(self, layout):
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                elif item.layout() is not None:
                    self.clearLayout(item.layout())

    def saveConfig(self):
        dialog = SaveConfigDialog(self, self.configFile)
        if dialog.exec_() == QDialog.Accepted:
            newFilePath = dialog.getFilePath()
            if newFilePath:
                self.configFile = newFilePath
                with open(self.configFile, 'w') as file:
                    json.dump(self.config, file, indent=4)
                QMessageBox.information(self, "Success", f"Configuration saved to:\n{self.configFile}")
            else:
                QMessageBox.warning(self, "Warning", "No file selected, configuration not saved.")
        else:
            print("Save operation cancelled.")

    
    def accept(self):
        self.close()
        self.closed.emit()  # Emit the signal when the widget is about to close
        # super().closeEvent(event)

    def getConfig(self):
        return_config = {}
        for key, lineEdit in self.entries.items():
            return_config[key] = lineEdit.text()
        return return_config

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QPushButton, QFileDialog, QHBoxLayout, QMessageBox

class SaveConfigDialog(QDialog):
    '''A dialog window for selecting a location to save a configuration file.'''
    def __init__(self, parent=None, initialFilePath=""):
        super().__init__(parent)
        self.setWindowTitle("Save Configuration")
        self.filePath = initialFilePath
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)

        # Current file path label
        self.filePathLabel = QLabel(f"Current File: {self.filePath}", self)
        layout.addWidget(self.filePathLabel)

        # Buttons for actions
        buttonLayout = QHBoxLayout()
        self.openButton = QPushButton("Change File", self)
        self.openButton.clicked.connect(self.changeFile)
        buttonLayout.addWidget(self.openButton)

        self.saveButton = QPushButton("Save", self)
        self.saveButton.clicked.connect(self.accept)
        buttonLayout.addWidget(self.saveButton)

        self.cancelButton = QPushButton("Cancel", self)
        self.cancelButton.clicked.connect(self.reject)
        buttonLayout.addWidget(self.cancelButton)

        layout.addLayout(buttonLayout)

    def changeFile(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getSaveFileName(self, "Select File to Save", self.filePath, "JSON Files (*.json);;All Files (*)", options=options)
        if fileName:
            self.filePath = fileName
            self.filePathLabel.setText(f"Current File: {self.filePath}")

    def getFilePath(self):
        return self.filePath


## For testing:
def main():
    app = QApplication(sys.argv)
    ex = ConfigEditor()
    # ex.show()
    app.exec_()
    print(ex.getConfig())
    sys.exit()

if __name__ == '__main__':
    main()
