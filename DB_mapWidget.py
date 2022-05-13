from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
        
class mapWidget(QtWidgets.QMainWindow):
    """
    Creates the main window for the map.
    """

    def __init__(self, main_gui):
        """
        Initializes QtWidgets.

        Parameters
        ----------
        main_gui : mainWindow
            the main Window of the GUI
        """
        super().__init__()
        self.main_gui = main_gui
        self.germany_map = germanyMap(self)

    def draw_route_network(self, train_stations, routes):
        """
        Starts draw_route_network of germany_map.
          
        Parameters
        ----------
        train_stations : dataframe
            name of the train stations
        
        routes : dataframe
            routes in longitude and latitude
        """
        self.germany_map.draw_route_network(train_stations, routes)

class germanyMap(QtWidgets.QGraphicsView):
    """
    Graphicsscene of the map of Germany.
    """
  
    # Signals to react to mouse movement and clicking
    currentStation = QtCore.Signal(str)
    stationClicked = QtCore.Signal(str)

    def __init__(self, map_gui):
        """
        Creates a widget for the map.

        Parameters
        ----------
        map_gui : mainWindow
            the main Window of the GUI
        """
        super().__init__()

        self.main_gui = map_gui.main_gui
        self.map_gui = map_gui

        self.setMinimumSize(140, 180)
        self.setMouseTracking(True)
        self.previous_item = None
 
        self.pens_and_brushes() 

        self.zoom = 0
        self.setTransformationAnchor \
            (QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QtWidgets.QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOn)

    def wheelEvent(self, event):
        """
        Enables Zoom while using the mouse wheel.
        According to:
        https://stackoverflow.com/questions/35508711/how-to-enable-pan-and-zoom-in-a-qgraphicsview
        """
        
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

    def mousePressEvent(self, event):
        """
        Reacts to clicking of the mouse.

        Parameters
        ----------
        event : QMouseEvent
            clicking of the mouse
        """
        
        item = self.itemAt(event.pos())
        if item is not None:
            try:
                self.stationClicked.emit(item.station)
            except:
                pass
            
    def mouseMoveEvent(self, event):
        """
        Is used to track the items touched 
        by the mouse and change their color.

        Parameters
        ----------
        event : QMouseEvent
            movement of the mouse
        """
        
        item = self.itemAt(event.pos())

        # If all error messages are ignored, 
        # there are no error messages left.
        if self.previous_item is not None:
            try:
                self.previous_item.setBrush(QtGui.QBrush \
                    ("white", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = None
            
        if item is not None:
            try:
                item.setBrush(QtGui.QBrush \
                    ("grey", QtCore.Qt.BrushStyle.SolidPattern))
            except:
                pass
            self.previous_item = item
            try:
                self.currentStation.emit(item.station)
            except:
                pass

    def resizeEvent(self, event):
        """
        Enables the widget to be resized properly.

        Parameters
        ----------
        event : QResizeEvent
            resizes the window
        """
     
        scene_size = self.sceneRect()
        dx = (self.width()-50)/scene_size.width()
        dy = (self.height()-50)/scene_size.height()
        self.setTransform(QtGui.QTransform.fromScale(dx, -dy))

    def sizeHint(self):
        """
        Return of the preferred default size of the widget.
        """
        
        return QtCore.QSize(140*4, 180*4)

    def pens_and_brushes(self):
        """
        Contains all pens and brushes.
        """

        self.ocean_brush = QtGui.QBrush("lightblue", \
            QtCore.Qt.BrushStyle.BDiagPattern)
        self.country_pen = QtGui.QPen("black")
        self.country_pen.setWidthF(0.01)
        self.land_brush = QtGui.QBrush("white", \
            QtCore.Qt.BrushStyle.SolidPattern)

        self.point_pen = QtGui.QPen("red")
        self.point_pen.setWidthF(0.05)
        self.point_brush = QtGui.QBrush("white", \
            QtCore.Qt.BrushStyle.SolidPattern)

        self.line_pen = QtGui.QPen("orange")
        self.line_pen.setWidthF(0.02)

    def draw_route_network(self, train_stations, routes):
        """
        Draws stations and routes to the base scene.
            
        Parameters
        ----------
        train_stations : dataframe
            containing names and coordinates of the train stations

        filename_routes: String
            Name of the file containing the routes
        """

        self.make_base_scene()

        # Drawing the stations 
        for one_station in train_stations.itertuples():
            whole_station_information = [(one_station.stop_lat, \
                one_station.stop_lon),one_station.stop_name]
            station_information_coordinates = [[one_station.stop_lat, \
                one_station.stop_lon]]
                
            for y,x in station_information_coordinates:
                width = 0.02
                height = 0.02
                point_item = self.map_gui.scene.addEllipse(x,y, \
                    width,height, pen=self.point_pen, \
                    brush=self.point_brush)
                point_item.station = y,x

                if point_item.station in whole_station_information:
                    point_item.station = whole_station_information[1]
        
        # Drawing the routes
        for start in routes.itertuples():
            y1,x1 = [start.Station1_lat, start.Station1_lon]
            
            y2,x2 = [start.Station2_lat, start.Station2_lon]
            self.map_gui.scene.addLine(x1,y1,x2,y2, pen=self.line_pen)
            
        self = germanyMap(self.map_gui)
        self.setScene(self.map_gui.scene)
        self.scale(10, -10)
        self.setRenderHint(QtGui.QPainter.Antialiasing)
        self.currentStation.connect(self.main_gui.status_bar.showMessage)
        self.stationClicked.connect(self.main_gui.click_function)

        self.main_gui.grid_layout.addWidget(self,0,0)

    def make_base_scene(self):
        """
        Creating the base scene, which shows the map of Germany.
        """

        self.map_gui.scene = QtWidgets.QGraphicsScene(5.8, 47.3, 9.4, 7.9)
        states = self.main_gui.model.get_counts()

        # Drawing map of Germany
        for state in states:
            if state['geometry']['type'] == 'Polygon':
                for polygon in state['geometry']['coordinates']:
                    qpolygon = QtGui.QPolygonF()
                    for x, y in polygon:
                        qpolygon.append(QtCore.QPointF(x, y))
                    polygon_item = self.map_gui.scene.addPolygon \
                        (qpolygon, pen=self.country_pen, \
                            brush=self.land_brush)
                    polygon_item.station = state['properties']['GEN']
                   
            else:
                for polygons in state['geometry']['coordinates']:
                    for polygon in polygons:
                        qpolygon = QtGui.QPolygonF()
                        for x, y in polygon:
                            qpolygon.append(QtCore.QPointF(x, y))
                        polygon_item = self.map_gui.scene.addPolygon \
                            (qpolygon, pen=self.country_pen, brush = \
                                self.land_brush)
                        polygon_item.station = state['properties']['GEN']
                       
                    self.map_gui.scene.setBackgroundBrush \
                        (self.ocean_brush)