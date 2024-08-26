import sys
sys.path.extend(["../..", "..","../ppo"])
import json
from PyQt5.QtWidgets import QMainWindow, QPushButton,QWidget,QLabel,QHBoxLayout,QDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QPainter, QPen
from PyQt5.QtCore import Qt, QPoint
from GUI.componentInput import NewNodeDialog, FlowInput, ComponentConfigDialog
from GUI.guiElements import DraggableNode
import subprocess
import psutil
from PyQt5.QtGui import QPainter, QPen, QPainterPath

class createGraph(QMainWindow):

    def __init__(self,inputs):
        super().__init__()
        x,y,h = inputs['x'],inputs['y'],inputs['h']
        self.config = inputs['config']
        self.iterations = int(self.config['Iterations'])
        self.graphName = "rwtest"
        with open("GUI/components.json", 'r') as file:
            self.component_config = json.load(file)
        self.initUI(x,y,h)
        self.initNW()
        self.NeuroweaverProcess = None
        
        
    def initUI(self,x,y,h):
        self.setWindowTitle('Neuroweaver GUI')
        self.setGeometry(x, y, 800, h)

        self.nameWidget = QWidget(self)
        self.nameWidget.setGeometry(0, 0, 800, 30)
        self.nameWidget.setStyleSheet("background-color: black")
        self.nameLayout = QHBoxLayout(self.nameWidget)
        self.nameLayout.setSpacing(30)
        self.nameLayout.setContentsMargins(30, 0, 30, 0) 
        self.nameWidget.show()

        self.nameLabel = QLabel(self.graphName, self)
        self.nameLabel.setStyleSheet("color: white")
        self.nameLabel.show()
        self.nameLayout.addWidget(self.nameLabel)

        # Create a top widget to hold the buttons

        self.topWidget = QWidget(self)
        self.topWidget.setGeometry(0, 30, 800, 60)
        self.topWidget.setStyleSheet("background-color: navy")
        self.layout = QHBoxLayout(self.topWidget)
        self.layout.setSpacing(30)
        self.layout.setContentsMargins(30, 0, 30, 0) 
        self.topWidget.show()

        # Create buttons

        ### Add Component Button
        self.addComponentButton = QPushButton("Add Component", self)
        self.addComponentButton.setStyleSheet("background-color: grey")
        self.addComponentButton.clicked.connect(self.addNode)
        self.addComponentButton.setMinimumSize(150, 40)
        self.layout.addWidget(self.addComponentButton)

        ### Add Flow Button
        self.addFlowButton = QPushButton("Add Flow", self)
        self.addFlowButton.setStyleSheet("background-color: grey")
        self.addFlowButton.clicked.connect(self.FlowState) 
        self.addFlowButton.setMinimumSize(150, 40)
        self.layout.addWidget(self.addFlowButton)

        ### Run Button
        self.runButton = QPushButton("Run", self)
        self.runButton.setStyleSheet("background-color: grey")
        self.runButton.clicked.connect(self.runNeuroweaver)
        self.runButton.setMinimumSize(150, 40)
        self.layout.addWidget(self.runButton)

        ### Save Button
        self.saveButton = QPushButton("Save", self)
        self.saveButton.setStyleSheet("background-color: grey")
        self.saveButton.clicked.connect(self.save)
        self.saveButton.setMinimumSize(150, 40)
        self.layout.addWidget(self.saveButton)
    
    def initNW(self):
        self.flowState = False
        self.components = {}
        self.flows = []
        self.currentNode = None
        self.nodesGUI = []
        self.edgesGUI = []

    def addNodeGUI(self, componentInfo):
        num_per_row = 3  
        index = len(self.nodesGUI)
        row = index // num_per_row
        column = index % num_per_row
        x_position = 20 + (column * (self.width() // num_per_row))
        y_position = 100 + (row * 100)  # Assuming each row is spaced 100 pixels apart
        comp_gui = DraggableNode(self, componentInfo['Name'])
        comp_gui.move(x_position, y_position)
        comp_gui.moved.connect(self.update)
        self.nodesGUI.append(comp_gui)
        comp_gui.show()
        self.components[componentInfo['Name']] = {
            'Info': componentInfo,
            'GUI': comp_gui,
        }

    def addNode(self):
        dialog = NewNodeDialog(self.config)
        if dialog.exec_() == QDialog.Accepted:
            # print(dialog.get_inputs())
            componentInfo = dialog.get_inputs()
            self.addNodeGUI(componentInfo)
        else:
            print("Dialog canceled")
      
    def addFlow(self,start_node, end_node):
        start_node_name = None
        end_node_name = None
        for name, node in self.components.items():
            if node['GUI'] == start_node:
                start_node_name = name
            if node['GUI'] == end_node:
                end_node_name = name
        if start_node_name is None or end_node_name is None:
            print("Error: Could not find the component names for the nodes")
            return False
        dialog = FlowInput(self.components[start_node_name], self.components[end_node_name])
        if dialog.exec_() == QDialog.Accepted:
            flow_inputs = dialog.get_inputs()
            self.flows.append([flow_inputs[0], start_node_name, flow_inputs[1] , end_node_name])
        else:
            print("Dialog canceled")
            return False
        return True
    
    def FlowState(self):
        if self.flowState:
            self.flowState = False
            self.addFlowButton.setStyleSheet("background-color: grey")
        else:
            self.flowState = True
            #change addFlowButton color to red
            self.addFlowButton.setStyleSheet("background-color: red")

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if self.flowState:
            found_node = None
            for node in self.nodesGUI:
                if node.geometry().contains(event.pos()):
                    print("Node clicked")
                    found_node = node
                    break
            if found_node:
                if self.currentNode is None:
                    # This is the first node clicked, set it as the start of a potential edge
                    self.currentNode = found_node
                    self.start_point = found_node.pos() + QPoint(found_node.width() // 2, found_node.height() // 2)
                elif self.currentNode is not None and found_node is not self.currentNode:
                    print("Edge created between", self.currentNode.name, "and", found_node.name)
                    flowAdded = self.addFlow(self.currentNode, found_node)
                    if flowAdded:
                        # A second distinct node is clicked; create an edge
                        self.edgesGUI.append((self.currentNode, found_node))
                        self.end_point = found_node.pos() + QPoint(found_node.width() // 2, found_node.height() // 2)
                        self.update()
                    self.currentNode = None
                    self.FlowState()
                    
                elif self.currentNode is found_node:
                    self.currentNode = None

    def drawEdge(self,startNodeName,endNodeName):
        startNode = self.components[startNodeName]['GUI']
        self.start_point = startNode.pos() + QPoint(startNode.width() // 2, startNode.height() // 2)
        endNode = self.components[endNodeName]['GUI']
        self.end_point = endNode.pos() + QPoint(endNode.width() // 2, endNode.height() // 2)
        self.edgesGUI.append((startNode, endNode))
        self.update()


    def mouseMoveEvent(self, event):
        if self.currentNode:
            self.end_point = event.pos()
            self.update()

    def mouseDoubleClickEvent(self, event):
        super().mouseDoubleClickEvent(event)
        found_node = None
        for node in self.nodesGUI:
            if node.geometry().contains(event.pos()):
                found_node = node
                break
        changed = None
        if found_node:
            toBeDeleted = None
            for name, node in self.components.items():
                if node['GUI'] == found_node:
                    dialog = ComponentConfigDialog(node['Info'], self.config)
                    result = dialog.exec_()
                    if result == 1:
                        updated_info = dialog.get_inputs()
                        node['Info'].update(updated_info)
                        print(f"Updated {name} with new information")
                        self.deleteComponentAndFlows(name)
                        if name != updated_info['Name']:
                            changed = (name, updated_info['Name'])
                    elif result == 2:  # Custom code indicating deletion
                        toBeDeleted = name
                        found_node.setParent(None)
                        self.nodesGUI.remove(found_node)
                        print(f"Deleted {name}")
                    elif result == 3: 
                        updated_info = dialog.get_inputs()
                        node['Info'].update(updated_info)
                        changed = (name, updated_info['Name'])
                    elif result == 4:
                        updated_info = dialog.get_inputs()
                        node['Info'].update(updated_info)
                    else:
                        print("cancelled")
                    self.update()
                    break
            if toBeDeleted:
                self.deleteComponentAndFlows(toBeDeleted)
                del self.components[toBeDeleted]
            if changed:
                for flow in self.flows:
                    if flow[1] == changed[0]:
                        flow[1] = changed[1]
                    if flow[3] == changed[0]:
                        flow[3] = changed[1]
                # 'changed' is a tuple (old_name, new_name)
                old_name, new_name = changed
                gui_node = self.components[old_name]['GUI']
                gui_node.name = new_name  # Update the node's name in the GUI
                gui_node.setText(new_name) 
                changed = None
                self.components[new_name] = self.components.pop(old_name)  # Update the key in the components dictionary
                print(self.flows)
                self.update()
                

    def deleteComponentAndFlows(self, componentName):
        # Remove any flows associated with the deleted component
        self.flows = [flow for flow in self.flows if flow[1] != componentName and flow[3] != componentName]
        # Update GUI elements for edges
        new_edgesGUI = []
        for start_node, end_node in self.edgesGUI:
            if start_node.name != componentName and end_node.name != componentName:
                new_edgesGUI.append((start_node, end_node))
        self.edgesGUI = new_edgesGUI
        self.update()  # Refresh the GUI to reflect these changes
    
    def paintEvent(self, event):
        super().paintEvent(event)
        painter = QPainter(self)
        pen = QPen(Qt.white, 2)
        painter.setPen(pen)

        for start_node, end_node in self.edgesGUI:
            start_pos = start_node.pos() + QPoint(start_node.width() // 2, start_node.height() // 2)
            end_pos = end_node.pos() + QPoint(end_node.width() // 2, end_node.height() // 2)
            
            path = QPainterPath(start_pos)
            # Control points are chosen to create a smooth curve, modify as necessary
            ctrl1 = QPoint((start_pos.x() + end_pos.x()) // 2, start_pos.y())
            ctrl2 = QPoint((start_pos.x() + end_pos.x()) // 2, end_pos.y())
            path.cubicTo(ctrl1, ctrl2, end_pos)
            
            painter.drawPath(path)

    def save(self):
        # Open a dialog to select a directory
        folder_path = QFileDialog.getExistingDirectory(self, "Select Folder to Save Graph")
        if not folder_path:
            QMessageBox.information(self, "Save Cancelled", "No folder was selected.")
            return

        # Attempt to save components.json and flows.json in the selected folder
        try:
            saveNode = {}
            for name, node in self.components.items():
                saveNode[name] = node['Info']

            with open(f'{folder_path}/nodes.json', 'w') as file:
                json.dump(saveNode, file)
            with open(f'{folder_path}/flows.json', 'w') as file:
                json.dump(self.flows, file)
            
            QMessageBox.information(self, "Save Successful", "The graph has been successfully saved!")
        except Exception as e:
            QMessageBox.critical(self, "Save Failed", f"Failed to save files: {str(e)}")

    def runNeuroweaver(self):
        runData = {}
        runData['config'] = self.config
        runData['components'] = {}
        for name, node in self.components.items():
            runData['components'][name] = node['Info']
        runData['flows'] = self.flows
        with open('GUI/temp.json', 'w') as f:
            json.dump(runData, f)

        self.NeuroweaverProcess = subprocess.Popen(["python3", "GUI/runner.py"])
    
    def runNeuroweaver(self):
        print("Since the NeuroWeaver code is not available, this button does nothing.")
        # if self.NeuroweaverProcess is None:
        #     # Start the process
        #     runData = {'config': self.config, 'components': {name: node['Info'] for name, node in self.components.items()}, 'flows': self.flows}
        #     with open('GUI/temp.json', 'w') as f:
        #         json.dump(runData, f)
        #     self.NeuroweaverProcess = subprocess.Popen(["python3", "GUI/runner.py"])
        #     self.runButton.setText("Stop")
        # else:
        #     self.stopNeuroweaver()

    def stopNeuroweaver(self):
        print("Since the NeuroWeaver code is not available, this button does nothing.")
        # if self.NeuroweaverProcess:
        #     parent = psutil.Process(self.NeuroweaverProcess.pid)
        #     for child in parent.children(recursive=True):  # terminate child processes
        #         child.kill()
        #     parent.kill()
        #     process = subprocess.Popen(['python3','GUI/cleanup.py'])
        #     self.NeuroweaverProcess = None
        #     self.runButton.setText("Run")        
