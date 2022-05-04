import sys
import json
import pandas as pd
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
    
class interactivePlaner(QtWidgets.QMainWindow):
    """ Klasse für ein Seitliches Fensterbild, um die Route interaktiv zu machen."""
    
    def __init__(self):
        """ Konstruktorklasse, die in der Klasse vorhanden sein muss."""
        
        super().__init__()
        self.gui_builder()
        #self.methode('stops_fern.txt')
        
    def gui_builder(self):
        """ Das ist die Funktion, mit der die GUI gebildet wird."""

        
        """ Deklarieren der Kombinationsboxen und Label für die interaktive GUI und anhängen der Widgets an
        das Layout über 'addWidget'."""
        # -------------- Comboboxen ------------------        
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Startbahnhof wählen -")
        #self.combobox_start.addItems(self.methode())
        self.combobox_start.currentTextChanged.connect(self.change_start_station)
        
        self.combobox_destination = QtWidgets.QComboBox()
        self.combobox_destination.setPlaceholderText("- Zielbahnhof wählen -")
        #self.combobox_destination.addItems(self.methode())
        self.combobox_destination.currentTextChanged.connect(self.change_end_station)
 
        # -------------- Textfelder ----------------
        textfield_date = QtWidgets.QDateEdit()
        textfield_time = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
        self.textfield_allInfo.setReadOnly(True)
        self.set_text_start_values()
        self.update_text()
        
        # -------------- Label  ------------------
        label_button_traffic_style = QtWidgets.QLabel("Bahnart:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_combobox_destination = QtWidgets.QLabel("Ankunftbahnhof:")
        label_textfield_date_time = QtWidgets.QLabel("Datum und Zeit der Abfahrt:")
        label_textfield_allInfo = QtWidgets.QLabel("Ausgewählte Informationen:")
        
        # -------------- Button ------------------
        self.button_nahverkehr = QtWidgets.QPushButton("Nahverkehr")
        self.button_fernverkehr = QtWidgets.QPushButton("Fernverkehr")
        self.button_regional = QtWidgets.QPushButton("Regional")
        button_start = QtWidgets.QPushButton("Route planen")
        
        
        self.button_fernverkehr.clicked.connect(self.clickFunctionFern)
        self.button_nahverkehr.clicked.connect(self.clickFunctionNah)
        self.button_regional.clicked.connect(self.clickFunctionRegional)
        #button_start.clicked.connect(self.the_chosen_route)
        
        
        # -------------- Layouts -----------------
        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.button_nahverkehr)
        button_layout.addWidget(self.button_fernverkehr)
        button_layout.addWidget(self.button_regional)
        
        date_time_layout = QtWidgets.QHBoxLayout()
        date_time_layout.addWidget(textfield_date)
        date_time_layout.addWidget(textfield_time)
        
        
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_button_traffic_style)
        layout.addLayout(button_layout)
        layout.addWidget(label_combobox_start) 
        layout.addWidget(self.combobox_start)
        layout.addWidget(label_combobox_destination)
        layout.addWidget(self.combobox_destination)
        layout.addWidget(label_textfield_date_time)
        layout.addLayout(date_time_layout)
        layout.addWidget(label_textfield_allInfo)
        layout.addWidget(self.textfield_allInfo)
        layout.addWidget(button_start)
        
        """ Zusammenfassen des Layouts und der Widgets auf dem Fensterinhalt."""
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)
    
    
    def set_text_start_values(self):
        self.abfahrtsbahnhof = "noch nicht ausgewählt.."
        self.zielbahnhof = "noch nicht ausgewählt.."
        self.ankunftszeit = "noch nicht berechnet.."
        
    def update_text(self):
        text = (f"Abfahrtsbahnhof: {self.abfahrtsbahnhof} \n"
            + f"Zielbahnhof: {self.zielbahnhof} \n"
            + f"Ankunftszeit: {self.ankunftszeit}")
        self.textfield_allInfo.setText(text)
    
    def change_start_station(self, value):
        self.abfahrtsbahnhof = value
        self.update_text()
        
    def change_end_station(self,value):
        self.zielbahnhof = value
        self.update_text()
        
    def methode(self, filename):
        with open(filename, "r") as tf:
            train_stations = tf['stop_name']
        return train_stations

    def clickFunctionFern(self):
        stations = pd.read_csv('stops_fern.txt', encoding= 'utf8')
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)
        self.combobox_destination.addItems(train_stations)
        

    def clickFunctionNah(self):
        stations = pd.read_csv('stops_nah.txt', encoding= 'utf8')
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)
        self.combobox_destination.addItems(train_stations)
        

    def clickFunctionRegional(self):
        stations = pd.read_csv('stops_regional.txt', encoding= 'utf8')
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)
        self.combobox_destination.addItems(train_stations)  
    
    #----------------------------------------------------
   
    # Wie stelle ich das mit der Route an ?????
    @QtCore.Slot()
    def the_chosen_route(self):
        """ Verbindet Start- und Zielbahnhof."""
        pass
        

if __name__ == "__main__":
    """ Da für eine GUI eine App notwendig ist, wird diese ersteinmal gebaut. """ 
    
    app = QtWidgets.QApplication(sys.argv)
    window = interactivePlaner()
    window.show()
    sys.exit(app.exec())