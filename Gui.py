from pickle import TRUE
import pandas
import sys
import geojson
import os
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

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

        ##################
        # Buttons erstellen
        self.button_fern = QtWidgets.QPushButton("Fernverkehr")
        self.button_nah = QtWidgets.QPushButton("Nahverkehr")
        self.button_regional = QtWidgets.QPushButton("Regionalverkehr")

        self.button_fern.clicked.connect(self.clickFunctionFern)
        self.button_nah.clicked.connect(self.clickFunctionNah)
        self.button_regional.clicked.connect(self.clickFunctionRegional)

        
        

        ##################

        # Arbeiten mit Farben Brushes etc
        self.ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.BDiagPattern)
        self.country_pen = QtGui.QPen("grey")
        self.country_pen.setWidthF(0.01)
        self.land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.point_pen = QtGui.QPen("red")
        self.point_pen.setWidthF(0.05)
        self.point_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)


        self.make_base_scene()

        
                 
        self.germany_map = GermanyMap()
        self.methode('stops_fern.txt')
                
           

###############################################################
        

        self.germany_map.setScene(self.scene)
        self.germany_map.scale(10, -10)
        self.germany_map.setRenderHint(QtGui.QPainter.Antialiasing)
        self.germany_map.currentStation.connect(self.status_bar.showMessage)

######################

        # Layout gestalten
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.germany_map)
        layout.addWidget(self.button_fern)
        layout.addWidget(self.button_nah)
        layout.addWidget(self.button_regional)

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
#########################################
# Load Station Data

    def methode(self,filename):
        self.make_base_scene()
        self.scene.update()
        path_of_stations = os.path.dirname(__file__) + '/' + filename
        train_stations = pandas.read_csv(path_of_stations, encoding='utf8')
            
        for one_station in train_stations.itertuples():
            whole_station_information = [(one_station.stop_lat, one_station.stop_lon),one_station.stop_name]
            station_information_coordinates = [[one_station.stop_lat, one_station.stop_lon]]
                
            for y,x in station_information_coordinates:
                width = 0.02
                height = 0.02
                point_item = self.scene.addEllipse(x,y,width,height, pen=self.point_pen, brush=self.point_brush)
                point_item.station = y,x

                if point_item.station in whole_station_information:
                    point_item.station = whole_station_information[1]
                else:
                    print('Kein Bahnhof ausgewählt.')

        self.germany_map.setScene(self.scene)
##################################
    def make_base_scene(self):


        self.scene = QtWidgets.QGraphicsScene(5.7, 47.3, 9.4, 8.0) 



        states = self.load_map_data()

        for state in states:
            if state['geometry']['type'] == 'Polygon':
                for polygon in state['geometry']['coordinates']:
                    qpolygon = QtGui.QPolygonF()
                    for x, y in polygon:
                        qpolygon.append(QtCore.QPointF(x, y))
                    polygon_item = self.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                    polygon_item.station = state['properties']['GEN']
                   
            else:
                for polygons in state['geometry']['coordinates']:
                    for polygon in polygons:
                        qpolygon = QtGui.QPolygonF()
                        for x, y in polygon:
                            qpolygon.append(QtCore.QPointF(x, y))
                        polygon_item = self.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                        polygon_item.station = state['properties']['GEN']
                       

                    self.scene.setBackgroundBrush(self.ocean_brush)

       

################################################################


    def clickFunctionFern(self):
        self.methode('stops_fern.txt')
        

    def clickFunctionNah(self):
        self.methode('stops_nah.txt')
        

    def clickFunctionRegional(self):
        self.methode('stops_regional.txt')

################################################################


# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    sys.exit(app.exec())