import pandas
import sys
import json
import os
import matplotlib.pyplot as plt
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
###############################################################
# Funktion, der eine txt Datei übergeben werden kann und die daraus eine JSON Datei (nur mit den Koordinaten) macht
#def convert_txt_to_json(filename):
#    stops_longdistance = pandas.read_csv(filename)
#    #coordinates = stops_longdistance.iloc[] #:,[2,3]
#    coordinates_json = stops_longdistance.to_json(orient = 'split')
#    return coordinates_json

###############################################################
# Train Stations und Koordinaten laden
path_of_stations = os.path.dirname(__file__) + '/' + 'train_station.csv'
train_stations = pandas.read_csv(path_of_stations)
coordinates = train_stations.filter(['stop_lat','stop_lon'])  #'stop_name',
coordinates_list = coordinates.values.tolist()

#x, y = zip(*coordinates_list)

#x_coords = train_stations['stop_lat']
#y_coords = train_stations['stop_lon']


################################################################

# Klasse für die Deutschlandkarte
class GermanyMap(QtWidgets.QGraphicsView):
    def __init__(self):
        super().__init__()
        self.setMinimumSize(360, 180)

    def resizeEvent(self, event):
        scene_size = self.sceneRect()
        dx = (self.width()-4)/scene_size.width()
        dy = (self.height()-4)/scene_size.height()
        self.setTransform(QtGui.QTransform.fromScale(dx, -dy))

    def sizeHint(self):
        return QtCore.QSize(360*2, 180*2)

###############################################################
# Klasse um das Main Window zu erstellen
class MainWindow(QtWidgets.QMainWindow):     

# Deutschlandkarte
    def __init__(self):
        super().__init__()

        # Arbeiten mit Farben Brushes etc

        ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.BDiagPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.5)
        land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        point_pen = QtGui.QPen("red")
        point_pen.setWidthF(0.5)


        # Hier müssen die Koordinaten geändert werden
        scene = QtWidgets.QGraphicsScene(-180, -90, 360, 180)

        germany_map_data = self.load_map_data()

        # Hier gehts weiter, jetzt muss die Karte gemalt werden (Koordinaten für die Deutschlandkarte werden benötigt)
        for country, polygons in germany_map_data.items():
            if country == 'Germany':
                for polygon in polygons:
                    qpolygon = QtGui.QPolygonF()
                    for x,y in polygon:
                        qpolygon.append(QtCore.QPointF((x-14)*5,(y-56)*5)) 
                    scene.addPolygon(qpolygon, pen = country_pen,brush = land_brush)
                    
        scene.setBackgroundBrush(ocean_brush)

################################################################
# Train Stations zeichnen  
        
        qpoints = QtGui.QPolygonF()
        for x,y in coordinates_list:
            
            #qpoints.append(QtCore.QPointF((y-14)*5,(x-56)*5))
            wide = 1
            high = 1
            # x und y sind vertauscht, weil in der Datei Längen und Breitengrade andersherum sind, als in der Map
            scene.addEllipse((y-14)*5,(x-56)*5, wide, high, pen=point_pen)    
       

###############################################################

        germany_map = GermanyMap()
        germany_map.setScene(scene)
        germany_map.scale(10, -10)
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
        with open('countries.json') as file:
            
            germany_coordinates = json.load(file)

        return germany_coordinates

################################

  


# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())