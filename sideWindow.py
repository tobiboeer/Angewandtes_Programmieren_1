import sys
import json
import pandas
from PySide2 import QtCore
from PySide2 import QtWidgets
from PySide2 import QtGui

# GUI - Tabelle mit Bahnhöfen
# Interaktive GUI

class sideWindow(QtWidgets.QMainWindow):
    """ Klasse für ein Seitliches Fensterbild, um die Route interaktiv zu machen."""
    def __init__(self):
        """konstruktorklasse, die in der Klasse vorhanden sein muss."""
        super().__init__()
        
        """Deklarieren der Textfelder und Label für die interaktive GUI."""
        textfield_destination = QtWidgets.QWidget()
        textfield_start = QtWidgets.QWidget()
        textfield_date = QtWidgets.QDateEdit()
        textfield_time = QtWidgets.QTimeEdit()
        button_start = QtWidgets.QPushButton()
        label_button_start = QtWidgets.QLabel("Startknopf")
        label_textfield_date = QtWidgets.QLabel("Datum der Abfahrt")
        label_textfield_time = QtWidgets.QLabel("Abfahrtszeit")
        label_textfield_start = QtWidgets.QLabel("Abfahrbahnhof")
        label_textfield_destination = QtWidgets.QLabel("Ankunftbahnhof")
        
        
        """Deklarieren eines Layouts und verknüpfen zwischen den Widgets."""
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(textfield_destination)
        layout.addWidget(textfield_start)
        layout.addWidget(textfield_date)
        layout.addWidget(textfield_time)
        layout.addWidget(button_start)
        layout.addWidget(label_button_start)
        layout.addWidget(label_textfield_date)
        layout.addWidget(label_textfield_time)
        layout.addWidget(label_textfield_start)
        layout.addWidget(label_textfield_destination)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)
        
        
        """ Zuweisen des verschiedenen Bahnverkehrs und einlesen der Daten. Über[stop_name] kommt man
        an die verschiedenen Haltestellen."""
        stops_schienenverkehr = self.load_stops_schienenverkehr()
        stops_schienenregionalverkehr = self.load_stops_schienenregionalverkehr()
        stops_public_traffic = self.load_stops_public_traffic()

    
        
    def load_stops_schienenverkehr(self):
        """ Laden der Bahnhöfe aus dem Schienenverkehr. """
        stops = pandas.read_csv("stops_schienenverkehr.csv")  
        return stops
        
    def load_stops_schienenregionalverkehr(self):
        """ Laden der Bahnhöfe aus dem Schienenregionalverkehr. """
        stops = pandas.read_csv("stops_schienenregionalverkehr.csv")  
        return stops
        
    def load_stops_public_traffic(self):
        """ Laden der Bahnhöfe aus dem öffentlichen Nahverkehr. """
        stops = pandas.read_csv("stops_öffentlicher_Nahverkehr.csv")  
        return stops



if __name__ == "__main__":
    """ Da für eine GUI eine App notwendig ist, 
    wird diese ersteinmal gebaut. """ 
    app = QtWidgets.QApplication(sys.argv)
    """ Die Aufgabe ist einen Frame zu basteln der Hello World
    sagt. """
    window = sideWindow()
    window.show()
    sys.exit(app.exec_())