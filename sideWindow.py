import sys
import json
import pandas
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

#class tableModel(QtCore.QAbstractTableModel):
 #   """ Hier sollen die Tabellen mit den Ankunfts- und Abfahrtsbahnhöfen eingelesen und dargestellt werden."""
  #  def __init__(self):
   #     """ Notwendige Konstruktorfunktion."""
    #    super().__init__()
     #   
      #  """ Zuweisen des verschiedenen Bahnverkehrs und einlesen der Daten. Über[stop_name] kommt man
       # an die verschiedenen Haltestellen."""
        #stops_schienenverkehr = pandas.read_csv("stops_schienenverkehr.csv")
        #stops_schienenregionalverkehr = pandas.read_csv("stops_schienenregionalverkehr.csv")
#        stops_public_traffic = pandas.read_csv("stops_oeffentlicher_Nahverkehr.csv")
 #       
  #  def rowCount(self,parent=None):
   #     return 100
    #    
#    def columnCount(self, parent=None):
 #       return 2
  #  
   # def data(self,index, role = QtCore.Qt.DisplayRole):
    #    if role != QtCore.Qt.DisplayRole:
     #       return None
      #  
       # stations = self.stops_public_traffic.iloc[index.row(), index.column()]
        #return str(stations)    
    
    
class interactivePlaner(QtWidgets.QMainWindow):
    """ Klasse für ein Seitliches Fensterbild, um die Route interaktiv zu machen."""
    
    def __init__(self):
        """ Konstruktorklasse, die in der Klasse vorhanden sein muss."""
        
        super().__init__()
        
        """ Deklarieren eines Layouts."""
        layout = QtWidgets.QVBoxLayout()
        
        """ Deklarieren eines Gruppenlayouts. funktion noch nicht verstanden.."""
        group = QtWidgets.QGroupBox("Routenplaner")
        
        """ Deklarieren der Textfelder und Label für die interaktive GUI und anhängen der Widgets an
        das Layout über 'addWidget'."""
        textfield_start = QtWidgets.QTextEdit()
        label_textfield_start = QtWidgets.QLabel("Abfahrbahnhof:")
        layout.addWidget(label_textfield_start) 
        layout.addWidget(textfield_start) 

        textfield_destination = QtWidgets.QTextEdit()
        label_textfield_destination = QtWidgets.QLabel("Ankunftbahnhof:")
        layout.addWidget(label_textfield_destination)
        layout.addWidget(textfield_destination)
        
        label_textfield_date = QtWidgets.QLabel("Datum der Abfahrt:")
        textfield_date = QtWidgets.QDateEdit()
        layout.addWidget(label_textfield_date)
        layout.addWidget(textfield_date)

        label_textfield_time = QtWidgets.QLabel("Abfahrtszeit:")
        textfield_time = QtWidgets.QTimeEdit()
        layout.addWidget(label_textfield_time)
        layout.addWidget(textfield_time)
        
        button_start = QtWidgets.QPushButton("GO!")
        layout.addWidget(button_start)
        
        """ Zusammenfassen des Layouts und der Widgets auf dem Fensterinhalt."""
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

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