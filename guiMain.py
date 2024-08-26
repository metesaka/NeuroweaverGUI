import sys
sys.path.extend("../..")  #add ../.. to python path
sys.path.extend("..")
import json

from PyQt5.QtWidgets import QVBoxLayout,QMainWindow, QApplication, QAction, qApp, QPushButton, QWidget,QFileDialog, QDialog, QLabel
from GUI.createGraph import createGraph
from GUI.configPage import ConfigEditor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.graph = None
        self.config_editor = None
        self.defaultConfig()
        self.initUI()
    
    def defaultConfig(self):
        with open("GUI/config.json", 'r') as file:
            self.config = json.load(file)

    def initUI(self):
        self.setWindowTitle('Neuroweaver GUI')
        # TODO: Make it responsive!
        self.setGeometry(100, 100, 300, 600)

        # Create a central widget
        centralWidget = QWidget(self)
        self.setCentralWidget(centralWidget)
        self.layout = QVBoxLayout(centralWidget)
        self.layout.setContentsMargins(50, 0, 50, 0)  # Increase the left and right margins

        # Create buttons
        self.createButtons()

        # Set the layout of the central widget
        centralWidget.setLayout(self.layout)
        # Adding actions to the 'File' menu
        exitAction = QAction('Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(qApp.quit)
    
        # Set main window properties
        self.show()
    
    def setConfig(self):
        pos = self.pos()
        size = self.size()
        x,y,h = pos.x(),pos.y(),size.height()
        if not self.config_editor or not self.config_editor.isVisible():
            self.config_editor = ConfigEditor({'x':x+size.width(),'y':y+27,'h':h})  # Create a new ConfigEditor if none or not visible
            self.config_editor.show()
        else:
            self.config_editor.raise_()  # Bring to the front if already opened

        self.config_editor.closed.connect(self.updateConfig)

    def updateConfig(self):
        self.config = self.config_editor.getConfig()
        print(self.config)
    
    def createButtons(self):
        # BUTTONS
        ## Add Component Button
        createGraph = QPushButton("Create Graph", self)
        createGraph.setStyleSheet("background-color: grey")
        createGraph.setMinimumSize(100, 50)
        if self.graph:
            createGraph.clicked.connect(self.graph.show())
        else:    
            createGraph.clicked.connect(self.createGraph)
        self.layout.addWidget(createGraph)
        
        loadButton = QPushButton("Load Graph", self)
        loadButton.setStyleSheet("background-color: grey")
        loadButton.setMinimumSize(100, 50)
        loadButton.clicked.connect(self.load)
        self.layout.addWidget(loadButton)

        setConfig = QPushButton("Set Config", self)
        setConfig.setStyleSheet("background-color: grey")
        setConfig.setMinimumSize(100, 50)
        setConfig.clicked.connect(self.setConfig)
        self.layout.addWidget(setConfig)

    def createGraph(self):
        #location of window's top right corner, width, height
        pos = self.pos()
        size = self.size()
        x,y,h = pos.x(),pos.y(),size.height()
        self.graph = createGraph({'x':x+size.width(),'y':y+27,'h':h,'config':self.config})
        self.graph.show()

    # def load(self):


    #     with open('components.json', 'r') as file:
    #         components = json.load(file)
    #     with open('flows.json', 'r') as file:
    #         flows = json.load(file)
        
    #     self.createGraph()
    #     for name, componentInfo in components.items():
    #         self.graph.addNodeGUI(componentInfo)
    #     for flow in flows:
    #         self.graph.flows.append(flow)
    #         self.graph.drawEdge(flow[1],flow[3])

    def load(self):
        # Open a dialog to select a directory
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder Containing Graph Files")
        if folder_path:
            # Attempt to load components.json and flows.json from the selected folder
            try:
                with open(f'{folder_path}/nodes.json', 'r') as file:
                    components = json.load(file)
                with open(f'{folder_path}/flows.json', 'r') as file:
                    flows = json.load(file)
                
                # After successful loading, create the graph and populate it
                self.createGraph()  # This might need to be adjusted based on how you manage graph instances
                for name, componentInfo in components.items():
                    self.graph.addNodeGUI(componentInfo)
                for flow in flows:
                    self.graph.flows.append(flow)
                    self.graph.drawEdge(flow[1], flow[3])

            except FileNotFoundError:
                # If the files are not found, show an error dialog
                fileErrorDialog = QDialog(self)
                fileErrorDialog.setWindowTitle("Error")
                fileErrorDialog.layout = QVBoxLayout()
                fileErrorDialog.layout.addWidget(QLabel("File not found. Please ensure the directory contains the nodes.json and flows.json files."))
                fileErrorDialog.setLayout(fileErrorDialog.layout)
                okButton = QPushButton("OK", fileErrorDialog)
                okButton.clicked.connect(fileErrorDialog.close)
                fileErrorDialog.layout.addWidget(okButton)
                fileErrorDialog.exec_()

            except Exception as e:
                print(f"An error occurred: {e}")
        else:
            print("No folder selected.")



def main():
    app = QApplication(sys.argv)
    ex = MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
