from PyQt5.QtWidgets import QCheckBox, QLabel, QPushButton, QDialog, QVBoxLayout, QComboBox, QLineEdit, QWidget, QHBoxLayout, QPushButton, QMessageBox
from copy import deepcopy

import json
class NewNodeDialog(QDialog):
    '''A dialog window that allows the user to input the details of a new component.'''
    def __init__(self,config):
        super().__init__()
        self.config = config
        self.rollout = config['Rollout Steps']
        with open("GUI/components.json", 'r') as file:
            self.components = json.load(file)
        self.setWindowTitle('Component Input')
        self.setMinimumSize(300, 600)
        self.widget_groups = {}
        self.layout = QVBoxLayout(self)

        self.component_type_combo = QComboBox()
        self.component_type_combo.addItems(self.components.keys())
        self.component_type_combo.currentIndexChanged.connect(self.updateFields)
        self.layout.addWidget(self.component_type_combo)

        
        self.componentName = QLineEdit()
        self.componentName.setPlaceholderText('Enter component name')
        self.layout.addWidget(self.componentName)

        self.dynamic_container = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.layout.addWidget(self.dynamic_container)

        self.ok_button = QPushButton('OK', clicked=self.accept)
        self.cancel_button = QPushButton('Cancel', clicked=self.reject)
        self.layout.addWidget(self.ok_button)
        self.layout.addWidget(self.cancel_button)

        self.updateFields()  # Initialize with no dynamic fields

    def updateFields(self):
        '''Update the dynamic fields based on the selected component type. This is adaptable to any type of component defined in the components.json file.'''
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

        selected_type = self.component_type_combo.currentText()
        selectedComp = self.components[selected_type]

        self.addParameterSection("Parameters:", selectedComp['parameters'], 'parameters')
        self.addSection("Inputs:", selectedComp['inputs'], 'inputs')
        self.addSection("Outputs:", selectedComp['outputs'], 'outputs')
        self.addSection("State:", selectedComp['state'], 'state')

    
    def addParameterSection(self, title, items, category):
        '''Add a section of parameters to the dialog.'''
        label = QLabel(title)
        self.dynamic_layout.addWidget(label)
        for item in items:
            hbox = QHBoxLayout()
            widget_data = {'category': category, 'inputs': []}
            line_edit = QLineEdit(str(items[item]))
            hbox.addWidget(QLabel(f"{item}:"))
            hbox.addWidget(line_edit)
            widget_data['input'] = line_edit
            self.widget_groups[item] = widget_data
            self.dynamic_layout.addLayout(hbox)
    
    def addSection(self, title, items, category, first=True):
        '''Add a section of inputs, outputs, or state to the dialog.'''
        label = QLabel(title)
        self.dynamic_layout.addWidget(label)
        for item in items:
            hbox = QHBoxLayout()
            widget_data = {'category': category, 'inputs': []}
            checkbox = QCheckBox(f"Enable {item}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda checked, item=item, hbox=hbox: self.handleCheckbox(checked, item, hbox))
            hbox.addWidget(checkbox)
            widget_data['checkbox'] = checkbox
            widget_data['layout'] = hbox
            self.widget_groups[item] = widget_data
            self.dynamic_layout.addLayout(hbox)
            if first:
                self.handleCheckbox(True, item, hbox)
        first = False
    
    def handleCheckbox(self, checked, label, hbox):
        '''Handle the enabling/disabling of input fields based on the checkbox state.'''
        widgets = self.widget_groups[label]
        if checked:
            line_edit = QLineEdit(f'({int(self.config["Num Channels"])+1},{self.config["Rollout Steps"]})' if label == 'rollout' else "(1,)")
            hbox.addWidget(line_edit)
            widgets['inputs'].append(line_edit)
        else:
            while widgets['inputs']:
                widget = widgets['inputs'].pop()
                hbox.removeWidget(widget)
                widget.deleteLater()

    def get_inputs(self):
        '''provides other classes with the data from the dialog.'''
        results = {'Component':self.component_type_combo.currentText(), "Name":self.componentName.text(), 'parameters': {}, 'inputs': {}, 'outputs': {}, 'state': {}}
        
        for key, data in self.widget_groups.items():
            category = data['category']
            if 'input' in data and data['input'] is not None:
                try:
                    results[category][key] = data['input'].text()
                except RuntimeError:  # Safely handle deleted widget case
                    continue
            if 'inputs' in data:
                inputs = []
                for input_widget in data['inputs']:
                    try:
                        inputs.append(input_widget.text())
                    except RuntimeError:  # Catch cases where the widget might have been deleted
                        continue
                if inputs:
                    results[category][key] = inputs
        return results


    def clearLayout(self, layout):
        '''Clear the layout, used for updating the dynamic fields when the component type changes.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

class FlowInput(QDialog):
    '''A dialog window that allows the user to input the details of a new flow.'''
    def __init__(self, start: tuple, end : tuple):
        super().__init__()
        self.setWindowTitle("Match Data Flow Inputs")
        self.defaultIO = ([],[],[])
        self.layout = QVBoxLayout()
        self.askInputs(start, end)
        self.Footer()

    def askInputs(self, start, end):
        '''Add the input fields to the dialog.'''
        self.start_label = QLabel(f'{start["Info"]["Name"]}')
        self.layout.addWidget(self.start_label)
        print(start['Info'])
        start_pipes = list(start['Info']['outputs'].keys()) + list(start['Info']['state'].keys())
        print(start_pipes)
        self.start_combo = QComboBox()
        self.start_combo.addItems(start_pipes)
        self.layout.addWidget(self.start_combo)

        self.end_label = QLabel(f'{end["Info"]["Name"]}')
        self.layout.addWidget(self.end_label)

        end_pipes = list(end['Info']['inputs'].keys()) + list(end['Info']['state'].keys())

        self.end_combo = QComboBox()
        self.end_combo.addItems(end_pipes)
        self.layout.addWidget(self.end_combo)
    
    def get_inputs(self):
        '''provides other classes with the data from the dialog.'''
        return [self.start_combo.currentText(), self.end_combo.currentText()]
    
    def Footer(self):
        # Ok and Cancel buttons
        self.ok_button = QPushButton('OK')
        self.ok_button.clicked.connect(self.accept)
        self.layout.addWidget(self.ok_button)
        
        self.cancel_button = QPushButton('Cancel')
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.cancel_button)
        self.setLayout(self.layout)

class ComponentConfigDialog(QDialog):
    '''A dialog window that allows the user to edit the details of a component.'''
    def __init__(self, componentInfo, config):
        super().__init__()
        self.config = config
        self.rollout = int(config['Rollout Steps'])
        with open("GUI/components.json", 'r') as file:
            self.components = json.load(file)
        self.originalInfo = deepcopy(componentInfo)
        self.componentInfo = componentInfo
        self.initUI()
    
    def initUI(self):
        self.setMinimumSize(300, 600)
        self.widget_groups = {}
        self.layout = QVBoxLayout(self)

        self.component_type_combo = QComboBox()
        self.component_type_combo.addItems(self.components.keys())
        self.component_type_combo.setCurrentText(self.componentInfo['Component'])
        self.component_type_combo.currentIndexChanged.connect(self.updateFields)
        self.layout.addWidget(self.component_type_combo)

        self.componentName = QLineEdit()
        self.componentName.setText(self.componentInfo['Name'])
        self.layout.addWidget(self.componentName)

        self.dynamic_container = QWidget()
        self.dynamic_layout = QVBoxLayout(self.dynamic_container)
        self.layout.addWidget(self.dynamic_container)
        
        # Cancel button
        self.cancelButton = QPushButton('Cancel', self)
        self.cancelButton.clicked.connect(self.reject)
        self.layout.addWidget(self.cancelButton)

        # Save button
        self.saveButton = QPushButton('Save', self)
        self.saveButton.clicked.connect(self.saveComponent)
        self.layout.addWidget(self.saveButton)
        
        # Delete button
        self.deleteButton = QPushButton('Delete', self)
        self.deleteButton.clicked.connect(self.deleteComponent)
        self.layout.addWidget(self.deleteButton)

        self.setLayout(self.layout)
        self.initializeFields() # Initialize with current dynamic fields

    def initializeFields(self):
        '''Initialize the dynamic fields based on the component info.'''
        self.addParameterSection("Parameters:", self.componentInfo['parameters'], 'parameters')
        self.addSection("Inputs:", self.componentInfo['inputs'], 'inputs')
        self.addSection("Outputs:", self.componentInfo['outputs'], 'outputs')
        self.addSection("State:", self.componentInfo['state'], 'state')
    
    def updateFields(self):
        while self.dynamic_layout.count():
            item = self.dynamic_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

        selected_type = self.component_type_combo.currentText()
        selectedComp = self.components[selected_type]

        self.addParameterSection("Parameters:", selectedComp['parameters'], 'parameters')
        self.addSection("Inputs:", selectedComp['inputs'], 'inputs')
        self.addSection("Outputs:", selectedComp['outputs'], 'outputs')
        self.addSection("State:", selectedComp['state'], 'state')

    def saveComponent(self):
        '''Save the new component info and defines which parts were changed and returns the appropriate code.'''
        print(self.originalInfo)
        print('aaa')
        print(self.get_inputs())
        nameChanged = self.componentName.text() != self.originalInfo['Name']
        paramsChanged = self.originalInfo['parameters'] != self.get_inputs()['parameters']
        othersChanged = self.originalInfo['inputs'] != self.get_inputs()['inputs'] or self.originalInfo['outputs'] != self.get_inputs()['outputs'] or self.originalInfo['state'] != self.get_inputs()['state'] or self.originalInfo['Component'] != self.get_inputs()['Component']
        if othersChanged:
            self.done(1)
        elif nameChanged:
            self.done(3)
        elif paramsChanged:
            self.done(4)
        else:
            self.reject()


    def deleteComponent(self):
        '''Ask the user to confirm deletion of the component, if so, return the appropriate code.'''
        reply = QMessageBox.question(self, 'Confirm Delete',
                                     'Are you sure you want to delete this component?',
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            self.done(2)  # code to indicate deletion

    # The following are very similar to the methods in NewNodeDialog, but with some modifications to handle the existing data
    def addParameterSection(self, title, items, category):
        '''Add a section of parameters to the dialog.'''
        label = QLabel(title)
        self.dynamic_layout.addWidget(label)
        for item in items:
            hbox = QHBoxLayout()
            widget_data = {'category': category, 'inputs': []}
            line_edit = QLineEdit(str(items[item]))
            hbox.addWidget(QLabel(f"{item}:"))
            hbox.addWidget(line_edit)
            widget_data['input'] = line_edit
            self.widget_groups[item] = widget_data
            self.dynamic_layout.addLayout(hbox)
    
    def addSection(self, title, items, category, first=True):
        '''Add a section of inputs, outputs, or state to the dialog.'''
        label = QLabel(title)
        self.dynamic_layout.addWidget(label)
        for item in items:
            hbox = QHBoxLayout()
            widget_data = {'category': category, 'inputs': []}
            checkbox = QCheckBox(f"Enable {item}")
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(lambda checked, item=item, hbox=hbox: self.handleCheckbox(checked, item, hbox))
            hbox.addWidget(checkbox)
            widget_data['checkbox'] = checkbox
            widget_data['layout'] = hbox
            self.widget_groups[item] = widget_data
            self.dynamic_layout.addLayout(hbox)
            if first:
                self.handleCheckbox(True, item, hbox)
        first = False

    def handleCheckbox(self, checked, label, hbox):
        '''Handle the enabling/disabling of input fields based on the checkbox state.'''
        widgets = self.widget_groups[label]
        if checked:
            line_edit = QLineEdit(f'({int(self.config["Num Channels"])+1},{self.config["Rollout Steps"]})' if label == 'rollout' else "(1,)")
            hbox.addWidget(line_edit)
            widgets['inputs'].append(line_edit)
        else:
            while widgets['inputs']:
                widget = widgets['inputs'].pop()
                hbox.removeWidget(widget)
                widget.deleteLater()

    def clearLayout(self, layout):
        '''Clear the layout, used for updating the dynamic fields when the component type changes.'''
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self.clearLayout(item.layout())

    def get_inputs(self):
        '''provides other classes with the data from the dialog.'''
        results = {'Component':self.component_type_combo.currentText(), "Name":self.componentName.text(), 'parameters': {}, 'inputs': {}, 'outputs': {}, 'state': {}}
        
        for key, data in self.widget_groups.items():
            category = data['category']
            if 'input' in data and data['input'] is not None:
                try:
                    results[category][key] = data['input'].text()
                except RuntimeError:  # Safely handle deleted widget case
                    continue
            if 'inputs' in data:
                inputs = []
                for input_widget in data['inputs']:
                    try:
                        inputs.append(input_widget.text())
                    except RuntimeError:  # Catch cases where the widget might have been deleted
                        continue
                if inputs:
                    results[category][key] = inputs
        return results