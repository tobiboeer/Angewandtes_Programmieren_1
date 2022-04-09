import pandas
import sys
import json
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

# Funktion, der eine txt Datei übergeben werden kann und die daraus eine JSON Datei (nur mit den Koordinaten) macht
def convert_txt_to_json(filename):
    stops_longdistance = pandas.read_csv(filename)
    coordinates = stops_longdistance.iloc[:,[2,3]]
    coordinates_json = coordinates.to_json(orient = 'split')

    return coordinates_json

# Klasse um das Main Window zu erstellen
class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

# Arbeiten mit Farben Brushes etc

        ocean_brush = QtGui.QBrush("red", QtCore.Qt.BrushStyle.BDiagPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.5)
        land_brush = QtGui.QBrush("green", QtCore.Qt.BrushStyle.SolidPattern)

############




        # Hier müssen die Koordinaten geändert werden
        scene = QtWidgets.QGraphicsScene()#-180, -90, 360, 180

######## Experiment

       # x = convert_txt_to_json('stops.txt')
       # print(x)

       #stations_data = convert_txt_to_json('stops.txt')
       #for index, points in stations_data.items():
    

###################

        # Hier gehts weiter, jetzt muss die Karte gemalt werden (Koordinaten für die Deutschlandkarte werden benötigt)
        map_data = self.load_map_data()
        for bundesland, polygons in map_data.items():
            for polygon in polygons:
                qpolygon = QtGui.QPolygonF()
                for x, y in polygon:
                    qpolygon.append(QtCore.QPointF(x, y))
                scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
        scene.setBackgroundBrush(ocean_brush)


        germany_map = QtWidgets.QGraphicsView()
        germany_map.setScene(scene)
        germany_map.scale(1, -1)
        germany_map.setRenderHint(QtGui.QPainter.Antialiasing)

######################

        # Layout gestalten
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(germany_map)

        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)


    # Hier soll später die JSON Datei mit der Deutschlandkarte geladen werden
    def load_map_data(self):
        with open('germany.json') as file:
            
            germany_coordinates = json.load(file)

        return germany_coordinates



  


# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())