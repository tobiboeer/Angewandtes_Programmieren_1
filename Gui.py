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

import pandas as pd
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
    stationClicked = QtCore.Signal(str)

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
###################################
# Diese Funktion wird ausgeführt, wenn man mit der Maus klickt
    def mousePressEvent(self, event):
        
        item = self.itemAt(event.pos())
        self.stationClicked.emit(item.station)



##############################
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
                item.setBrush(QtGui.QBrush("grey", QtCore.Qt.BrushStyle.SolidPattern))
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
## Menubar ##############
# Quelle: https://realpython.com/python-menus-toolbars/#populating-menus-with-actions
# https://pythonprogramming.net/menubar-pyqt-tutorial/
        
        menuBar = self.menuBar()
        about_menu = QtWidgets.QMenu("Help",self)
        menuBar.addMenu(about_menu)
    
        aboutAction = QtGui.QAction("About", self)
        readmeAction = QtGui.QAction("ReadMe", self)

        about_menu.addAction(aboutAction)
        about_menu.addAction(readmeAction)

        aboutAction.triggered.connect(self.open_about)
        readmeAction.triggered.connect(self.open_readme)
       
        
        
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

        self.line_pen = QtGui.QPen("orange")
        self.line_pen.setWidthF(0.02)

        pfad = os.path.dirname(__file__) + '/' + 'stops_fern.txt'
        stations = pd.read_csv(pfad, encoding= 'utf8')
        self.drawRouteNetwork(stations,'connections.csv')
                
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

    def drawRouteNetwork(self,train_stations,filename_routes):
        self.make_base_scene()
        self.scene.update()
            
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
    #ROUTEN
        path_of_routes = os.path.dirname(__file__) + '/' + filename_routes
        routes = pd.read_csv(path_of_routes, encoding='utf8')
        

        for start in routes.itertuples():
            y1,x1 = [start.Station1_lat, start.Station1_lon]
            
            y2,x2 = [start.Station2_lat, start.Station2_lon]
            self.scene.addLine(x1,y1,x2,y2, pen=self.line_pen)
            


        self.germany_map = GermanyMap() 
        self.germany_map.setScene(self.scene)
        self.germany_map.scale(10, -10)
        self.germany_map.setRenderHint(QtGui.QPainter.Antialiasing)
        self.germany_map.currentStation.connect(self.status_bar.showMessage)
        self.germany_map.stationClicked.connect(self.click_function)
######################

        # Layout gestalten
        self.layout = QtWidgets.QHBoxLayout()
        self.layout.addWidget(self.germany_map)

        self.gui_builder()

        window_content = QtWidgets.QWidget()
        window_content.setLayout(self.layout)
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

## Funktionen für die Menu Bar
    def open_about(self):
        about_window.show()
        

    def open_readme(self):
        readme_window.show()

    @QtCore.Slot(str)
    def click_function(self, whole_station_information):
        print(whole_station_information + ' geklickt')




















        
    def gui_builder(self):
        """ Das ist die Funktion, mit der die GUI gebildet wird."""

        
        """ Deklarieren der Kombinationsboxen und Label für die interaktive GUI und anhängen der Widgets an
        das Layout über 'addWidget'."""
        # -------------- Comboboxen ------------------        
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Startbahnhof wählen -")
        self.combobox_start.currentTextChanged.connect(self.change_start_station)
        
        self.combobox_destination = QtWidgets.QComboBox()
        self.combobox_destination.setPlaceholderText("- Zielbahnhof wählen -")
        self.combobox_destination.currentTextChanged.connect(self.change_end_station)
 
        # -------------- Textfelder ----------------
        textfield_date = QtWidgets.QDateEdit()
        textfield_time = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
        self.textfield_allInfo.setReadOnly(True)
        self.set_text_start_values()
        self.update_text()
        
        # -------------- Label  ------------------
        label_button_traffic_style = QtWidgets.QLabel("Bahnart:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_combobox_destination = QtWidgets.QLabel("Ankunftbahnhof:")
        label_textfield_date_time = QtWidgets.QLabel("Datum und Zeit der Abfahrt:")
        label_textfield_allInfo = QtWidgets.QLabel("Ausgewählte Informationen:")
        
        # -------------- Button ------------------
        self.button_nahverkehr = QtWidgets.QPushButton("Nahverkehr")
        self.button_fernverkehr = QtWidgets.QPushButton("Fernverkehr")
        self.button_regional = QtWidgets.QPushButton("Regional")
        button_start = QtWidgets.QPushButton("Route planen")
        button_delete = QtWidgets.QPushButton("Löschen")
        
        
        
        self.button_fernverkehr.clicked.connect(self.clickFunctionFern)
        self.button_nahverkehr.clicked.connect(self.clickFunctionNah)
        self.button_regional.clicked.connect(self.clickFunctionRegional)
        #button_start.clicked.connect(self.the_chosen_route)
        button_delete.clicked.connect(self.deleter_textfield)
        
        # Verbinden zwischen Knopf und Bahnart - funktioniert nicht
        #self.button_fernverkehr.clicked.connect(self.change_train_style)
        #self.button_nahverkehr.clicked.connect(self.change_train_style)
        #self.button_regional.clicked.connect(self.change_train_style)
        
        # -------------- Layouts -----------------
        button_layout_traffic = QtWidgets.QHBoxLayout()
        button_layout_traffic.addWidget(self.button_nahverkehr)
        button_layout_traffic.addWidget(self.button_fernverkehr)
        button_layout_traffic.addWidget(self.button_regional)
        
        date_time_layout = QtWidgets.QHBoxLayout()
        date_time_layout.addWidget(textfield_date)
        date_time_layout.addWidget(textfield_time)
        
        button_layout_interactive = QtWidgets.QHBoxLayout()
        button_layout_interactive.addWidget(button_delete)
        button_layout_interactive.addWidget(button_start)
        
        
        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addWidget(label_button_traffic_style)
        sub_layout.addLayout(button_layout_traffic)
        sub_layout.addWidget(label_combobox_start) 
        sub_layout.addWidget(self.combobox_start)
        sub_layout.addWidget(label_combobox_destination)
        sub_layout.addWidget(self.combobox_destination)
        sub_layout.addWidget(label_textfield_date_time)
        sub_layout.addLayout(date_time_layout)
        sub_layout.addWidget(label_textfield_allInfo)
        sub_layout.addWidget(self.textfield_allInfo)
        sub_layout.addLayout(button_layout_interactive)
        
        self.layout.addLayout(sub_layout)

    
    
    def set_text_start_values(self):
        self.bahnart = "noch nicht ausgewählt.."
        self.abfahrtsbahnhof = "noch nicht ausgewählt.."
        self.zielbahnhof = "noch nicht ausgewählt.."
        self.ankunftszeit = "noch nicht berechnet.."
        
    def update_text(self):
        text = (f"Bahnart: {self.bahnart} \n"
            + f"Abfahrtsbahnhof: {self.abfahrtsbahnhof} \n"
            + f"Zielbahnhof: {self.zielbahnhof} \n"
            + f"Ankunftszeit: {self.ankunftszeit}")
        self.textfield_allInfo.setText(text)
        
    def deleter_textfield(self):
        self.set_text_start_values()
        self.update_text()

    # schreibe eine methode, die anhand des gedrückten knopfes erkennt, welche Bahnart ausgewählt wurde
    # code läuft, funktion nicht
    def change_train_style(self):
        if self.button_fernverkehr.clicked() == True: 
            self.bahnart = "Fernverkehr"
        elif self.button_nahverkehr.clicked() == True: 
            self.bahnart = "Nahverkehr"
        elif self.button_regional.clicked() == True: 
            self.bahnart = "Regionalverkehr"
        else:
            self.bahnart = "noch nicht ausgewählt.."
        self.update_text()
    
    def change_start_station(self, value):
        self.abfahrtsbahnhof = value
        self.update_text()
        
    def change_end_station(self,value):
        self.zielbahnhof = value
        self.update_text()
  

    def clickFunctionFern(self):
        self.clickFunction('stops_fern.txt') 

    def clickFunctionNah(self):
        self.clickFunction('train_stachen.csv')  

    def clickFunctionRegional(self):
        self.clickFunction('stops_regional.txt') 

    def clickFunction(self,pfad_name):
        pfad = os.path.dirname(__file__) + '/' + pfad_name
        stations = pd.read_csv(pfad, encoding= 'utf8')

        self.drawRouteNetwork(stations,'connections.csv')
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)
        self.combobox_destination.addItems(train_stations)  

#####################################################
# Neue Klassen für die einzelnen Fenster der Menüleiste

class MenuWindowAbout(QtWidgets.QGraphicsView):
    def __init__(self):
        """
        Creates a widget for the About menu.
        """
        super().__init__()
        self.setMinimumSize(300, 300)
        

        path_to_about = os.path.dirname(__file__) + '/' + 'ABOUT.txt'

        with open(path_to_about, encoding='utf8') as about_file:
            about_text = about_file.read()

        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(about_text)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sizeHint(self):
        return QtCore.QSize(600, 600)

class MenuWindowReadMe(QtWidgets.QGraphicsView):
    def __init__(self):
        """
        Creates a widget for the ReadMe menu.
        """
        super().__init__()
        self.setMinimumSize(300, 300)

        path_to_about = os.path.dirname(__file__) + '/' + 'README.txt'

        with open(path_to_about, encoding='utf8') as about_file:
            about_text = about_file.read()

        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(about_text)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    

    def sizeHint(self):
        return QtCore.QSize(600, 600)
























# Aufruf der Main Window Klasse und darstellen des Fensters
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    about_window = MenuWindowAbout()
    about_window.setWindowTitle("Über dieses Programm")
    readme_window = MenuWindowReadMe()
    readme_window.setWindowTitle("Read Me - Wichtig zu wissen")

    sys.exit(app.exec())