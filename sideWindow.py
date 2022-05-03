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
        self.get_stations()

    
    def gui_builder(self):
        """ Das ist die Funktion, mit der die GUI gebildet wird."""

        
        """ Deklarieren der Kombinationsboxen und Label für die interaktive GUI und anhängen der Widgets an
        das Layout über 'addWidget'."""
        # -------------- Comboboxen ------------------
        combobox_style = QtWidgets.QComboBox()
        combobox_style.setPlaceholderText("- Bahnart -")
        combobox_style.addItems(["öffentlicher Nahverkehr", "Schienenregionalverkehr", "Schienenverkehr"])
        
        combobox_start = QtWidgets.QComboBox()
        combobox_start.setPlaceholderText("- Startbahnhof wählen -")
        combobox_start.addItems(self.get_stations())
        
        combobox_destination = QtWidgets.QComboBox()
        combobox_destination.setPlaceholderText("- Zielbahnhof wählen -")
        combobox_destination.addItems(self.get_stations())
        
        # -------------- Textfelder ----------------
        textfield_date = QtWidgets.QDateEdit()
        textfield_time = QtWidgets.QTimeEdit()
        textfield_allInfo = QtWidgets.QTextEdit()
        
        # -------------- Label  ------------------
        label_combobox_style = QtWidgets.QLabel("Bahnverkehr:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_combobox_destination = QtWidgets.QLabel("Ankunftbahnhof:")
        label_textfield_date = QtWidgets.QLabel("Datum der Abfahrt:")
        label_textfield_time = QtWidgets.QLabel("Abfahrtszeit:")
        label_textfield_allInfo = QtWidgets.QLabel("Ausgewählte Informationen:")
        
        # -------------- Button ------------------
        button_start = QtWidgets.QPushButton("Route planen")
        
        # -------------- Layout ------------------
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(label_combobox_style)
        layout.addWidget(combobox_style)
        layout.addWidget(label_combobox_start) 
        layout.addWidget(combobox_start)
        layout.addWidget(label_combobox_destination)
        layout.addWidget(combobox_destination)
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
        
        



class mainSideWindow(QtWidgets.QMainWindow):
    """ Idee dieser Klasse ist ein Hauptfenster, welches mit dem oberen Abschnitt die Routenplanung 
    beinhaltet und auf dem unteren Abschnitt die Tabelle mit den verschiedenen Bahnhöfen darstellt."""
    
    def __init__(self):
        """ Notwendige Konstruktorklasse, die die vorherigen Klassen 'interactive_planer' und 
        'tableModel' aufruft und auf ein Main Window projiziert."""
        super().__init__()
        
        """ Aufrufen der vorherigen Klassen."""
        #table_view = tableModel()
        #table_view = QtWidgets.QWidget()
        interactive_planer = interactivePlaner()
        
        """ Definieren eines Layouts auf dem die vorherigen Klassen projiziert werden."""
        layout = QtWidgets.QVBoxLayout()
        #layout.addWidget(table_view)
        layout.addWidget(interactive_planer)

        """ Zusammenfassen des Layouts und der Widgets auf dem Fensterinhalt."""
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

if __name__ == "__main__":
    """ Da für eine GUI eine App notwendig ist, wird diese ersteinmal gebaut. """ 
    
    app = QtWidgets.QApplication(sys.argv)
    window = mainSideWindow()
    window.show()
    sys.exit(app.exec())