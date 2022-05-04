"""Does everything related to the map.

Classes:
    GermanyMap: QGraphicsView
        Contains the Graphicsscene of the map of Germany.

    MainWindow: QMainWindow
        Contains the main window of the program

Date: May 2022

Authors:
    Fabian Kessener
    Tobias Boeer
    Timon Fass

Version: 1.0

Licence:
    Hier die Licence hin
"""
import math
import pandas
import sys
import geojson
import os
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

# Klasse für die Deutschlandkarte
class GermanyMap(QtWidgets.QGraphicsView):
    """Graphicsscene of the German map
    
    Methods:
    
        wheelEvent
        mouseMoveEvent
        resizeEvent
        sizeHint
    
    
    
    """
    currentStation = QtCore.Signal(str)

    def __init__(self):
        """
        Creates a widget for the map.
        """
        super().__init__()
        self.setMinimumSize(140, 180)
        self.setMouseTracking(True)
        self.previous_item = None
 

        self.zoom = 0
        self.setTransformationAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)


    def wheelEvent(self, event):
        """
        Enables Zoom while using the mouse wheel.
        According to:
        https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
        
        """
        # Falls wir nur Zoomen wollen, wenn CTRL+Mausrad betätigt wird
        # Im Moment muss zum Zoomen an die gewünschte Stelle geklickt werden
        #if event.modifiers() == QtCore.Qt.ControlModifier:
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
    

    def mouseMoveEvent(self, event):
        """
        Is used to track the items touched by the mouse.
        According to:
        https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
        
        """
        
        item = self.itemAt(event.pos())

        if self.previous_item is not None:
            try:
                self.previous_item.setBrush(QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = None
        if item is not None:
            try:
                item.setBrush(QtGui.QBrush("green", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = item
            try:
                self.currentStation.emit(item.station)
            except:
                pass

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
        self.country_pen = QtGui.QPen("black")
        self.country_pen.setWidthF(0.01)
        self.land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.point_pen = QtGui.QPen("red")
        self.point_pen.setWidthF(0.05)
        self.point_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.line_pen = QtGui.QPen("blue")
        self.line_pen.setWidthF(0.01)

        
                 
        self.drawRouteNetwork('stops_fern.txt','connections_fern.txt')
                
           

###############################################################


    # Source:
    # http://opendatalab.de/projects/geojson-utilities/

    def load_map_data(self):
        path_to_map = os.path.dirname(__file__) + '/landkreise_simplify200.geojson'
        with open(path_to_map,encoding='utf8') as f:
            data = geojson.load(f)
        states = data['features']
        return states
#########################################
# Load Station Data

    def drawRouteNetwork(self,filename_stops,filename_routes):
        self.make_base_scene()
        self.scene.update()
        path_of_stations = os.path.dirname(__file__) + '/' + filename_stops
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
    ####################
    # ROUTEN
        path_of_routes = os.path.dirname(__file__) + '/' + filename_routes
        routes = pandas.read_csv(path_of_routes, encoding='utf8')
        
        #painterpath = QtGui.QPainterPath()

        for start in routes.itertuples():
            y1,x1 = [start.Station1_lat, start.Station1_lon]
            
            #painterpath.moveTo(QtCore.QPointF(x,y))
            y2,x2 = [start.Station2_lat, start.Station2_lon]
            self.scene.addLine(x1,y1,x2,y2, pen=self.line_pen)
            


        self.germany_map = GermanyMap() 
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
##################################
    def make_base_scene(self):

        self.scene = QtWidgets.QGraphicsScene(5.8, 47.3, 9.4, 7.9) 

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
## wenn ich die habe, müssen hier die connections umbenannt werden

    def clickFunctionFern(self):
        self.drawRouteNetwork('stops_fern.txt','connections_fern.txt')
        

    def clickFunctionNah(self):
        self.drawRouteNetwork('stops_nah.txt','connections_fern.txt')
        

    def clickFunctionRegional(self):
        self.drawRouteNetwork('stops_regional.txt','connections_fern.txt')

################################################################


# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    sys.exit(app.exec())