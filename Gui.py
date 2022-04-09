import pandas
import sys
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

#stops_longdistance = pandas.read_csv('stops.csv')

#coordinates = stops_longdistance.iloc[:,[2,3]]

#print(coordinates)
###########

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        # Hier gehts weiter, jetzt muss die Karte gemalt werden
        map_data = self.load_map_data()
        


    def load_map_data(self):
        with open('stops.txt') as file:
            stops_longdistance = pandas.read_csv('stops.txt')
            print(stops_longdistance)
        return stops_longdistance




if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())