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
        #self.get_stations()
        
    
    def gui_builder(self):
        """ Das ist die Funktion, mit der die GUI gebildet wird."""

        
        """ Deklarieren der Kombinationsboxen und Label für die interaktive GUI und anhängen der Widgets an
        das Layout über 'addWidget'."""
        # -------------- Comboboxen ------------------
        self.combobox_style = QtWidgets.QComboBox()
        self.combobox_style.setPlaceholderText("- Bahnart -")
        self.combobox_style.addItems(["öffentlicher Nahverkehr", "Schienenregionalverkehr", "Schienenverkehr"])
        
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Startbahnhof wählen -")
        self.combobox_start.addItems(self.get_stations())
        self.combobox_start.activated[int].connect(self.start_station)
        
        self.combobox_destination = QtWidgets.QComboBox()
        self.combobox_destination.setPlaceholderText("- Zielbahnhof wählen -")
        self.combobox_destination.addItems(self.get_stations())
        self.combobox_destination.activated[int].connect(self.final_station)
        
        # -------------- Textfelder ----------------
        textfield_date = QtWidgets.QDateEdit()
        textfield_time = QtWidgets.QTimeEdit()
        textfield_allInfo = QtWidgets.QTextEdit()
        textfield_allInfo.setReadOnly(True)
        
        # -------------- Label  ------------------
        label_combobox_style = QtWidgets.QLabel("Bahnverkehr:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_combobox_destination = QtWidgets.QLabel("Ankunftbahnhof:")
        label_textfield_date = QtWidgets.QLabel("Datum der Abfahrt:")
        label_textfield_time = QtWidgets.QLabel("Abfahrtszeit:")
        label_textfield_allInfo = QtWidgets.QLabel("Ausgewählte Informationen:")
        
        # -------------- Button ------------------
        button_start = QtWidgets.QPushButton("Route planen")
        button_start.clicked.connect(self.the_chosen_route)
        
        # -------------- Layout ------------------
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_combobox_style)
        layout.addWidget(self.combobox_style)
        layout.addWidget(label_combobox_start) 
        layout.addWidget(self.combobox_start)
        layout.addWidget(label_combobox_destination)
        layout.addWidget(self.combobox_destination)
        layout.addWidget(label_textfield_date)
        layout.addWidget(textfield_date)
        layout.addWidget(label_textfield_time)
        layout.addWidget(textfield_time)
        layout.addWidget(label_textfield_allInfo)
        layout.addWidget(textfield_allInfo)
        layout.addWidget(button_start)
        
        """ Zusammenfassen des Layouts und der Widgets auf dem Fensterinhalt."""
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)
    
    
    def get_stations(self):
        """ Daten werden eingelesen und zurückgegeben."""
        load_data = pd.read_csv("stops_schienenverkehr.csv")
        stations = load_data["stop_name"]
        return stations
    
    # ich finde meinen Fehler hier und auch beim nächsten Slot nicht.
    @QtCore.Slot(int)
    def start_station(self, start_index:int):
        """ Knopfevent, dass etwas passiert, wenn der "Route Knopf gedrückt wird."""
        start_station_name = self.combobox_start.itemText(start_index)
        return start_station_name
    
    # es sind schon fortschritte vorhanden, aber ich finde meinen Fehler nicht
    @QtCore.Slot(int)
    def final_station(self, stop_index:int):
        """ Knopfevent, damit der Zielbahnhof ausgewählt werden kann."""
        final_station_name = self.combobox_destination.itemText(stop_index)
        return final_station_name
        
    
    # Wie stelle ich das mit der Route an ?????
    @QtCore.Slot()
    def the_chosen_route(self):
        """ Verbindet Start- und Zielbahnhof."""
        pass
        
        
    # die Funktion soll die Informationen aus dem Anfangs und Endbahnhof abgreifen und auf dem Textfeld
    # darstellen, auch weitere Informationen, wie die Distanz der Strecke, wäre interessant...
    def illustrated_information(self):
        """ Die Funktion soll die Informationen auf dem Textfeld darstellen."""
        pass
        
        

if __name__ == "__main__":
    """ Da für eine GUI eine App notwendig ist, wird diese ersteinmal gebaut. """ 
    
    app = QtWidgets.QApplication(sys.argv)
    window = interactivePlaner()
    window.show()
    sys.exit(app.exec())