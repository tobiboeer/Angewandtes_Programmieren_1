import pandas
import sys
import geojson
import os
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
# # Train Stations und Koordinaten laden
# path_of_stations = os.path.dirname(__file__) + '/' + 'stops.txt'
# train_stations = pandas.read_csv(path_of_stations, encoding='utf8')
# coordinates = train_stations.filter(['stop_lat','stop_lon'])  #'stop_name',
# coordinates_list = coordinates.values.tolist()

# #x, y = zip(*coordinates_list)

# #x_coords = train_stations['stop_lat']
# #y_coords = train_stations['stop_lon']


################################################################

# Klasse für die Deutschlandkarte
class GermanyMap(QtWidgets.QGraphicsView):
    currentStation = QtCore.Signal(str)

    def __init__(self):
        super().__init__()
        self.setMinimumSize(140, 180)
        self.setMouseTracking(True)
        self.previous_item = None

#################################################################
# Zoom hinzufügen
# https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview

        self.zoom = 0
        self._empty = True
        self._scene = QtWidgets.QGraphicsScene(self)
        self.setScene(self._scene)
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.setDragMode(QtWidgets.QGraphicsView.ScrollHandDrag)


    def wheelEvent(self, event):
        if event.angleDelta().y() > 0:
            factor = 1.25
            self.zoom += 1
        else:
            factor = 0.9
            self.zoom -= 1
        if self.zoom > 0:
            self.scale(factor, factor)
        elif self.zoom == 0:
            self.fitInView(self.sceneRect())
        else:
            self.zoom = 0
########################################################################
# Mouse Event hinzufügen
    def mouseMoveEvent(self, event):
            item = self.itemAt(event.pos())
            if self.previous_item is not None:
                self.previous_item.setBrush(QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern))
                self.previous_item = None
            if item is not None:
                item.setBrush(QtGui.QBrush("green", QtCore.Qt.BrushStyle.SolidPattern))
                self.previous_item = item
                self.currentStation.emit(item.station)

########################################################################
    def resizeEvent(self, event):
        scene_size = self.sceneRect()
        dx = (self.width()-4)/scene_size.width()
        dy = (self.height()-4)/scene_size.height()
        self.setTransform(QtGui.QTransform.fromScale(dx, -dy))

    def sizeHint(self):
        return QtCore.QSize(140*4, 180*4)

###############################################################
# Klasse um das Main Window zu erstellen
class MainWindow(QtWidgets.QMainWindow):     

# Deutschlandkarte
    def __init__(self):
        super().__init__()

        self.status_bar = self.statusBar()

        # Arbeiten mit Farben Brushes etc
        ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.BDiagPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.01)
        land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        point_pen = QtGui.QPen("red")
        point_pen.setWidthF(0.05)
        point_brush = QtGui.QBrush("red", QtCore.Qt.BrushStyle.SolidPattern)


        # Hier müssen die Koordinaten geändert werden
        scene = QtWidgets.QGraphicsScene(5.8, 47.2, 9.3, 7.9) #5.8, 47.2, 9.3, 7.9

################################################################
# Zeichnen der Karte

        states = self.load_map_data()

        for state in states:
            if state['geometry']['type'] == 'Polygon':
                for polygon in state['geometry']['coordinates']:
                    qpolygon = QtGui.QPolygonF()
                    for x, y in polygon:
                        qpolygon.append(QtCore.QPointF(x, y))
                    polygon_item = scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
                    polygon_item.station = state['properties']['GEN']
                   
            else:
                for polygons in state['geometry']['coordinates']:
                    for polygon in polygons:
                        qpolygon = QtGui.QPolygonF()
                        for x, y in polygon:
                            qpolygon.append(QtCore.QPointF(x, y))
                        polygon_item = scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
                        polygon_item.station = state['properties']['GEN']
                       

                    scene.setBackgroundBrush(ocean_brush)

################################################################
# Train Stations laden und zeichnen  
        path_of_stations = os.path.dirname(__file__) + '/' + 'stops.txt'
        train_stations = pandas.read_csv(path_of_stations, encoding='utf8')
        
        for one_station in train_stations.itertuples():
            whole_station_information = [(one_station.stop_lat, one_station.stop_lon),one_station.stop_name]
            station_information_coordinates = [[one_station.stop_lat, one_station.stop_lon]]
            
            for y,x in station_information_coordinates:
                width = 0.02
                height = 0.02
                point_item = scene.addEllipse(x,y,width,height, pen=point_pen, brush=point_brush)
                point_item.station = y,x

                if point_item.station in whole_station_information:
                    point_item.station = whole_station_information[1]
                else:
                    print('Kein Bahnhof ausgewählt.')
                
                

###############################################################

        germany_map = GermanyMap()
        germany_map.setScene(scene)
        germany_map.scale(10, -10)
        germany_map.setRenderHint(QtGui.QPainter.Antialiasing)
        germany_map.currentStation.connect(self.status_bar.showMessage)

######################

        # Layout gestalten
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(germany_map)

        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)


    # Source:
    # http://opendatalab.de/projects/geojson-utilities/

    def load_map_data(self):
        with open('landkreise_simplify200.geojson',encoding='utf8') as f:
            data = geojson.load(f)
        states = data['features']
        return states

  
##################################

# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())