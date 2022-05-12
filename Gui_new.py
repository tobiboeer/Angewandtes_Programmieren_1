"""
Does everything related to the map.

Classes:
    GermanyMap: QGraphicsView
        Contains the Graphicsscene of the map of Germany.

    MainWindow: QMainWindow
        Contains the main window of the program

    MenuWindowAbout: QGraphicsView
        Contains the Graphicsscene of the 'About' menu.

    MenuWindowReadMe: QGraphicsView
        Contains the Graphicsscene of the 'ReadMe' menu.

Date: 13. May 2022

Authors:
    Fabian Kessener
    Tobias Boeer
    Timon Fass

Emails:
    fabian.kessener@student.jade-hs.de
    tobias.boeer@student.jade-hs.de
    timon.fass@student.jade-hs.de

Version: 1.0

Licence: 
    
    Copyright: (c) 2022, Kessener, Boeer, Fass
    This code is published under the terms of the 3-Clause BSD License.
    The full text can be seen in ABOUT.md or the 'About/Licence' dropdown
    menu.
"""

import re
import pandas as pd
import sys
import geojson
import os
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui
import json
import csv
import numpy as np
from os.path import exists
import random
from datetime import datetime
import time
import calendar
import threading
import concurrent.futures
import markdown


class myFred(threading.Thread):
    def __init__(self,all_rout_ids,parent,amount_of_trets,name_dict_input):
        threading.Thread.__init__(self)
        self.name_dict = name_dict_input
        self.all_rout_ids = all_rout_ids
        self.parent = parent
        self.amount_of_trets = amount_of_trets

    def run(self):
        # based on the rood id the choneckchens betwen the trainstachens are put togeter
        conectons = []

        for done, rout_id in enumerate(self.all_rout_ids):
            # gets all trip ids from the roout id 
            trip_id_example_list = self.name_dict["trips"].loc[self.name_dict["trips"]["route_id"] == rout_id]['trip_id'].to_numpy()
            # reduses the number trip ids to reduce the runtime.  
            trip_id_example_list = set(trip_id_example_list)
            sub_stop_ids_inspected = []
            for trip_id_example in trip_id_example_list:
                # gets all stops from the trip id
                all_stops = self.name_dict["stop_times"][self.name_dict["stop_times"].trip_id == trip_id_example]
                sub_stop_ids = list(all_stops["stop_id"].to_numpy())
                # creats a list of al trainstacen conechons
                if not (sub_stop_ids in sub_stop_ids_inspected):
                    for count, stop_id in enumerate(sub_stop_ids):
                        if count != 0:
                            conectons.append([stop_id,last_stop_id])
                        last_stop_id = stop_id
                    sub_stop_ids_inspected.append(sub_stop_ids)

        # reduses the cupels witch are multipl tims in the list
        df = pd.DataFrame (conectons, columns = ['stachen_1','stachen_2'])
        groub = df.groupby(['stachen_1','stachen_2'])
        groub = pd.DataFrame(groub.size())
        groub.reset_index(inplace=True)
        groub = groub.drop(labels=[0], axis=1)

        # re asembels the list
        stachen_1 = list(groub["stachen_1"].to_numpy())
        stachen_2 = list(groub["stachen_2"].to_numpy())
        conectons = [stachen_1,stachen_2]
        
        print("conectons in Tret erstellt")

        # writes to the main class
        while True:
            if self.parent.add_conectons(conectons):
                break
            time.sleep(0.01)

        # if all treda are done the main code can be run
        self.parent.shreads_done += 1
        if self.parent.shreads_done == self.amount_of_trets:
            self.parent.ceap_going()

class Conectons(threading.Thread):
    def __init__(self,data_clas,type):
        threading.Thread.__init__(self)
        self.data_clas = data_clas
        self.type = type

        # sets the variables to the needet typ
        if self.type == "fern":
            self.name_dict = self.data_clas.gtfs_fern
            self.name = 'connections_fern.csv'
        if self.type == "regional":
            self.name_dict = self.data_clas.gtfs_regional
            self.name = 'connections_regional.csv'
        if self.type == "nah":
            self.name_dict = self.data_clas.gtfs_nah
            self.name = 'connections_nah.csv'

    def run(self):
        self.shreads_done = 0
        self.add_conectons_actif = 0
        self.conectons = [[],[]]

        # gets the rout_ids to get the conections
        all_rout_ids = self.name_dict["routes"]["route_id"].to_numpy()

        # if the all_rout_ids 
        if len(all_rout_ids) <= 1:
            print("len(all_rout_ids) ",len(all_rout_ids))
            exit()

        # starts with 64 treds, for big dats sets, if needet the amound is redused
        amount_of_trets = 64
        while amount_of_trets > len(all_rout_ids):
            amount_of_trets = int(amount_of_trets/2)

        # the therds are set end stardet
        step_sise = int(len(all_rout_ids)/(amount_of_trets-1))
        for i in range(amount_of_trets-1):
            to_check_all_rout_ids = all_rout_ids[0:step_sise]
            all_rout_ids =  all_rout_ids[step_sise:]
            myFred(to_check_all_rout_ids,self,amount_of_trets,self.name_dict).start()
        myFred(all_rout_ids,self,amount_of_trets,self.name_dict).start()

    def add_conectons(self,add):
        # to reduse conflics only one tred is aloud to wreid at a time
        if self.add_conectons_actif == 0:
            self.add_conectons_actif = 1

            self.conectons[0] = self.conectons[0] + add[0]
            self.conectons[1] = self.conectons[1] + add[1]

            self.add_conectons_actif = 0

            # fedback if the riting was suxsesfull
            return True
        else:
            return False

    def ceap_going(self):

        # reduses the cupels witch are multipl tims in the list
        d = {'stachen_1':self.conectons[0],'stop_id':self.conectons[1]}
        df = pd.DataFrame (d)
        groub = df.groupby(['stachen_1','stop_id'])
        groub = pd.DataFrame(groub.size())
        groub.reset_index(inplace=True)
        groub = groub.drop(labels=[0], axis=1)
        # replases the stop ids with the lon and lat veluages
        new_df = pd.merge(self.name_dict["stops"],groub)
        new_df.rename(columns = {'stop_lat':'Station1_lat', 'stop_lon':'Station1_lon'}, inplace = True)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stachen_1':'stop_id'}, inplace = True)
        new_df = pd.merge(self.name_dict["stops"],new_df)
        new_df = new_df.drop(['stop_name', 'stop_id'], axis=1)
        new_df.rename(columns = {'stop_lat':'Station2_lat', 'stop_lon':'Station2_lon'}, inplace = True)

        # writes data
        pfad = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data/" + self.name))
        new_df.to_csv(pfad)

        # depandig of the type one file is restored
        if self.type == "fern":
            self.data_clas.free_fern_add_1()
        if self.type == "regional":
            self.data_clas.free_regional_add_1()
        if self.type == "nah":
            self.data_clas.free_nah_add_1()
        


class Map(QtWidgets.QMainWindow):
    """
    Creates the main window for the map.
    """

    def __init__(self,main_gui):
  
        super().__init__()
        self.main_gui = main_gui
        self.germany_map = GermanyMap(self)

    def drawRouteNetwork(self,train_stations,filename_routes):
        self.germany_map.drawRouteNetwork(train_stations,filename_routes)

# Klasse für die Deutschlandkarte
class GermanyMap(QtWidgets.QGraphicsView):
    """
    Graphicsscene of the map of Germany.
    """
  
    # Signals to react to mouse movement and clicking
    currentStation = QtCore.Signal(str)
    stationClicked = QtCore.Signal(str)

    def __init__(self,map_gui):
        """
        Creates a widget for the map.
        """
        super().__init__()

        self.main_gui = map_gui.main_gui
        self.map_gui = map_gui

        self.setMinimumSize(140, 180)
        self.setMouseTracking(True)
        self.previous_item = None
 
        self.pens_and_brushes() # werden alle davon verwendet

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

    def mousePressEvent(self, event):
        """
        Reacts to clicking of the mouse.
        """
        
        item = self.itemAt(event.pos())
        if item is not None:
            try:
                self.stationClicked.emit(item.station)
            except:
                pass
            
    def mouseMoveEvent(self, event):
        """
        Is used to track the items touched by the mouse and change their color.
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

    def resizeEvent(self, event):
        """
        Enables the widget to be resized properly.
        """
        scene_size = self.sceneRect()
        dx = (self.width()-4)/scene_size.width()
        dy = (self.height()-4)/scene_size.height()
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

        self.ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.BDiagPattern)
        self.country_pen = QtGui.QPen("black")
        self.country_pen.setWidthF(0.01)
        self.land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.point_pen = QtGui.QPen("red")
        self.point_pen.setWidthF(0.05)
        self.point_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        self.line_pen = QtGui.QPen("orange")
        self.line_pen.setWidthF(0.02)

    def drawRouteNetwork(self,train_stations,routes):
        """
        Draws stations and routes to the base scene.

        Parameters:
            train_stations: 
                Pandas Dataframe containing names and
                coordinates of the train stations
            filename_routes: str
                Name of the file containing the routes
        """

        self.make_base_scene()

        # Drawing the stations 
        for one_station in train_stations.itertuples():
            whole_station_information = [(one_station.stop_lat, one_station.stop_lon),one_station.stop_name]
            station_information_coordinates = [[one_station.stop_lat, one_station.stop_lon]]
                
            for y,x in station_information_coordinates:
                width = 0.02
                height = 0.02
                point_item = self.map_gui.scene.addEllipse(x,y,width,height, pen=self.point_pen, brush=self.point_brush)
                point_item.station = y,x

                if point_item.station in whole_station_information:
                    point_item.station = whole_station_information[1]
                else:
                    print('Kein Bahnhof ausgewählt.')

        # Loads the file with the routes
        #routes = self.main_gui.model.all_data.lode_routes(filename_routes) # muss definitif überarbeitet werden
        #routes = self.main_gui.model.get_conectons()
        
        # Drawing the routes
        for start in routes.itertuples():
            y1,x1 = [start.Station1_lat, start.Station1_lon]
            
            y2,x2 = [start.Station2_lat, start.Station2_lon]
            self.map_gui.scene.addLine(x1,y1,x2,y2, pen=self.line_pen)
            
        self = GermanyMap(self.map_gui) 
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
                    polygon_item = self.map_gui.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                    polygon_item.station = state['properties']['GEN']
                   
            else:
                for polygons in state['geometry']['coordinates']:
                    for polygon in polygons:
                        qpolygon = QtGui.QPolygonF()
                        for x, y in polygon:
                            qpolygon.append(QtCore.QPointF(x, y))
                        polygon_item = self.map_gui.scene.addPolygon(qpolygon, pen=self.country_pen, brush=self.land_brush)
                        polygon_item.station = state['properties']['GEN']
                       
                    self.map_gui.scene.setBackgroundBrush(self.ocean_brush)



class MenuWindowAbout(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'About' menu in the menubar.
    """
    def __init__(self,model):
        """
        Creates a widget for the About menu.
        """
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)

        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_about_text())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        return QtCore.QSize(700, 600)

class MenuWindowReadMe(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'ReadMe' menu in the menubar.
    """
    def __init__(self,all_data):
        """
        Creates a widget for the ReadMe menu.
        """
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)
        
        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_readme_text())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        return QtCore.QSize(600, 600)

class MenuWindowTutorial(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'Tutorial' menu in the menubar.
    """
    def __init__(self,all_data):
        """
        Creates a widget for the Tutorial menu.
        """
        super().__init__()
        self.model = model
        self.setMinimumSize(300, 300)
        
        self.label = QtWidgets.QTextEdit()
        self.label.setReadOnly(True)
        self.label.setMarkdown(self.model.get_tutorial())

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        self.setLayout(layout)

    

    def sizeHint(self):
        """
        Contains the preferred default size of the window.
        """
        return QtCore.QSize(1000, 1000)


class Side_winow(QtWidgets.QMainWindow):
    """
    Creating an interactive widget next to the german map.
    """

    def __init__(self,main_gui):
        """
        Instantiate the main aspects of an interactive planner. 
        It contains the comboboxes, textfields, labels, layouts and buttons.       
        """
        super().__init__()
            
        self.main_gui = main_gui
        
        # -------------- COMBOBOXES ----------------
        self.combobox_start = QtWidgets.QComboBox()
        self.combobox_start.setPlaceholderText("- Bahnhof wählen -")
        self.combobox_start.currentTextChanged.connect(self.change_start_station)
        

        # -------------- TEXT FIELDS ----------------
        textfield_date = QtWidgets.QDateEdit()
        self.textfield_time = QtWidgets.QTimeEdit()
        self.textfield_time_dif = QtWidgets.QTimeEdit()
        self.textfield_allInfo = QtWidgets.QTextEdit()
        
        self.set_text_start_values()
        self.update_text()
        
        # -------------- LABELS  ------------------
        label_button_traffic_style = QtWidgets.QLabel("Bahnart:")
        label_combobox_start = QtWidgets.QLabel("Abfahrbahnhof:")
        label_textfield_date_time = QtWidgets.QLabel("Datum und Zeit der Abfahrt:")
        self.label_textfield_time_dif = QtWidgets.QLabel("Zeitfenster")
        label_textfield_allInfo = QtWidgets.QLabel("Besondere Informationen:")
        label_button_recuest = QtWidgets.QLabel("Daten zum Bahnhof erstellen")

        # -------------- BUTTONS ------------------
        self.button_nahverkehr = QtWidgets.QPushButton("Nahverkehr")
        self.button_fernverkehr = QtWidgets.QPushButton("Fernverkehr")
        self.button_regional = QtWidgets.QPushButton("Regional")
        self.button_recuest = QtWidgets.QPushButton("Anfrage stellen")

        self.button_fernverkehr.clicked.connect(self.clickFunctionLongDistance)
        self.button_nahverkehr.clicked.connect(self.clickFunctionShortDistance)
        self.button_regional.clicked.connect(self.clickFunctionRegional)
        self.button_recuest.clicked.connect(self.trainstachen_recqest)

        # -------------- LAYOUTS -----------------
        button_layout_traffic = QtWidgets.QHBoxLayout()
        button_layout_traffic.addWidget(self.button_nahverkehr)
        button_layout_traffic.addWidget(self.button_fernverkehr)
        button_layout_traffic.addWidget(self.button_regional)
        
        date_time_layout = QtWidgets.QHBoxLayout()
        date_time_layout.addWidget(textfield_date)
        date_time_layout.addWidget(self.textfield_time)

        time_dif_layout = QtWidgets.QHBoxLayout()
        time_dif_layout.addWidget(self.textfield_time_dif)

        button_recuest_layout = QtWidgets.QHBoxLayout()
        button_recuest_layout.addWidget(self.button_recuest)

        
        
        sub_layout = QtWidgets.QVBoxLayout()
        sub_layout.addWidget(label_button_traffic_style)
        sub_layout.addLayout(button_layout_traffic)
        sub_layout.addWidget(label_combobox_start) 
        sub_layout.addWidget(self.combobox_start)
        sub_layout.addWidget(label_textfield_date_time)
        sub_layout.addLayout(date_time_layout)
        sub_layout.addWidget(self.label_textfield_time_dif)
        sub_layout.addLayout(time_dif_layout)
        sub_layout.addWidget(label_button_recuest)
        sub_layout.addLayout(button_recuest_layout)
        sub_layout.addWidget(label_textfield_allInfo)
        sub_layout.addWidget(self.textfield_allInfo)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(sub_layout)
        self.setCentralWidget(window_content)

        self.set_train_stations_list()

    def set_text_start_values(self):
        """
        Sets the first strings in the text box.        
        """
        self.abfahrtsbahnhof = "noch nicht ausgewählt.."
        
    def update_text(self):
        """
        Connects the first text values of the method 'set_text_start_values'
        and changes the first strings into the choiced option.
        """
        text = f"Abfahrtsbahnhof: {self.abfahrtsbahnhof}"
        self.textfield_allInfo.setText(text)
        
    
    def change_start_station(self, value):
        """
        Noted the selected start trainstation and updates the text box.        
        """
        self.abfahrtsbahnhof = value
        self.update_text()
        
    def change_end_station(self,value):
        """
        Noted the selected end station and updates the text box.
        """
        self.zielbahnhof = value
        self.update_text()
  
    def clickFunctionLongDistance(self):
        """
        Loads long distance data, if button 'Fernverkehr' is clicked.
        """
        self.main_gui.model.change_cerent_stops("stops_fern")
        self.set_train_stations_list()

    def clickFunctionShortDistance(self):
        """
        Loads short distance data, if button 'Nahverkehr' is clicked.
        """
        self.main_gui.model.change_cerent_stops("stops_nah")
        self.set_train_stations_list()

    def clickFunctionRegional(self):
        """
        Loads regional data, if button 'Regionalverkehr' is clicked.
        """
        self.main_gui.model.change_cerent_stops("stops_regional")
        self.set_train_stations_list()

    def set_train_stations_list(self):  
        stations = self.main_gui.model.get_cerent_stops()
        train_stations = stations['stop_name']
        self.combobox_start.addItems(train_stations)

    def trainstachen_recqest(self):
        time_span = self.textfield_time_dif.time().toString()

        day = datetime.today().weekday()
        hauer = int(datetime.now().strftime("%H"))
        min = int(datetime.now().strftime("%M"))

        self.main_gui.model.change_trainstachen_info(time_span,day,hauer,min,self.abfahrtsbahnhof)


class tableCreator(QtCore.QAbstractTableModel):
    """
    Creates a table with the main functions: rowCount, columnCount, data and headerData.
    These functions are setting the size of the matrix and a clear arrangement.
    """
    def __init__(self,df):
        """
        Defines the path in the directory and renames the columns for the clearancy.
        """
        super().__init__()
        self.dataframe = df
        
        
    def rowCount(self, parent = None):
        """
        Sets the amount of the rows of the read file.
        """
        self.number = len(self.dataframe[0:])
        return self.number
        
    def columnCount(self, parent = None):
        """
        Sets the amount of the columns of the read file.
        """
        return len(self.dataframe.keys())
        
        
    def data(self, index, role = QtCore.Qt.DisplayRole):
        """
        Shows the file components.
        """
        if role != QtCore.Qt.DisplayRole:
            return None
            
        value = self.dataframe.iloc[index.row(), index.column()]
        return str(value)
            
    def headerData(self, index, orientation, role = QtCore.Qt.DisplayRole):
        """
        Shows the head of the columns seperately.
        """
        if role != QtCore.Qt.DisplayRole or orientation != QtCore.Qt.Orientation.Horizontal:
           return None
        
        return self.dataframe.columns[index]
      

        
 
class dataTable(QtWidgets.QMainWindow):
    """
    Creates a widget of the 'tableCreator'. 
    """

    def __init__(self,main_gui):
        """
        Loads the file components of the 'tableCreator', creates a widget and merges
        the together. 
        """
        super().__init__()
        self.main_gui = main_gui

        self.setMinimumSize(140, 250)
        
        self.table_view = QtWidgets.QTableView()
                
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(self.table_view)
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

    def set_df(self,trainstachen_info):
        table_model = tableCreator(trainstachen_info)
        self.table_view.setModel(table_model)





# Klasse um das Main Window zu erstellen
class MainWindow(QtWidgets.QMainWindow):
    """
    Creates the main window of the GUI.
    """
    
    def __init__(self,model):
        super().__init__()

        self.model = model
        self.model.set_main_gui(self)

#--------------- Statusbar ---------------------------------------------
        self.status_bar = self.statusBar()

#--------------- Menubar -----------------------------------------------
# According to:
# https://realpython.com/python-menus-toolbars/#populating-menus-with-actions
# https://pythonprogramming.net/menubar-pyqt-tutorial/

        menuBar = self.menuBar()
        help_menu = QtWidgets.QMenu("Help",self)
        menuBar.addMenu(help_menu)
    
        aboutAction = QtGui.QAction("About/Licence", self)
        readmeAction = QtGui.QAction("ReadMe", self)
        tutorialAction = QtGui.QAction("Tutorial", self)

        help_menu.addAction(aboutAction)
        help_menu.addAction(readmeAction)
        help_menu.addAction(tutorialAction)

        aboutAction.triggered.connect(self.open_about)
        readmeAction.triggered.connect(self.open_readme)
        tutorialAction.triggered.connect(self.open_tutorial)
       
        self.grid_layout = QtWidgets.QGridLayout()
        self.setLayout(self.grid_layout)
        self.germany_map = Map(self)
        
        self.side_winow_instnz = Side_winow(self)
        self.grid_layout.addWidget(self.side_winow_instnz,0,1)

        self.dataTable_instace = dataTable(self)
        self.grid_layout.addWidget(self.dataTable_instace,1,0,1,2)

        stations = self.model.get_cerent_stops()
        self.germany_map.drawRouteNetwork(stations,self.model.get_conectons())
        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(self.grid_layout)
        self.setCentralWidget(window_content)

    def drawRouteNetwork(self,train_stations,filename_routes):
        self.germany_map.drawRouteNetwork(train_stations,filename_routes)
        
    def open_about(self):
        """
        Shows the window of the 'About' menu.
        """
        about_window.show()
    
    def open_readme(self):
        """
        Shows the window of the 'ReadMe' menu. 
        """
        readme_window.show()

    def open_tutorial(self):
        """
        Shows the window of the 'Tutorial' menu. 
        """
        tutorial_window.show()

    @QtCore.Slot(str)
    def click_function(self, whole_station_information):
        """
        Reacts to clicking of the mouse.
        """
        print(whole_station_information + ' geklickt')

    def transtachen_show(self):
        table_view = QtWidgets.QTableView()
        table_model = tableCreator()
        table_view.setModel(table_model)
        
        sub_layout = QtWidgets.QHBoxLayout()
        sub_layout.addWidget(table_view)
        
        self.layout.addLayout(sub_layout)
        




class Model():

    def __init__(self,all_data):
        # sets base veluages
        self.all_data = all_data
        self.trainstachen_info = None
        self.get_first_data()

    def get_first_data(self):
        # dependig if the data set is corect the set is lodet
        if self.all_data.lode_first:
            # set is coreckt and is lodet
            self.cerent_stops = self.all_data.get_stops_fern()
            self.cerent_connections = self.all_data.get_connections_fern()
            self.cerent_gtfs = self.all_data.gtfs("latest_fern")
        else:
            #set incoreckt and is blockt
            self.all_data.delited_kategorie_opchens.append("stops_fern")
            # try to restor lost data
            if not (self.all_data.gtfs("latest_fern") == None):
                self.all_data.restor("fern")

            # lodes new data 
            self.cerent_stops = self.all_data.get_stops_regional()
            self.cerent_connections = self.all_data.get_connections_regional()
            self.cerent_gtfs = self.all_data.gtfs("latest_regional")
            # checks data
            if (self.cerent_stops[1] == False) or (self.cerent_connections[1] == False) or (self.cerent_gtfs == None):
                self.all_data.delited_kategorie_opchens.append("stops_regional")
                if not (self.all_data.gtfs("latest_regional") == None):
                    self.all_data.restor("regional")
                self.cerent_stops = self.all_data.get_stops_nah()
                self.cerent_connections = self.all_data.get_connections_nah()
                self.cerent_gtfs = self.all_data.gtfs("latest_nah")
                if (self.cerent_stops[1] == False) or (self.cerent_connections[1] == False) or (self.cerent_gtfs == None):
                    self.all_data.delited_kategorie_opchens.append("stops_nah")
                    if not (self.all_data.gtfs("latest_nah") == None):
                        self.all_data.restor("nah")
                    print(" alle daten sets sind felerhaft. Die bedinbarkeit ist eingeschrenkt.")
        
    def set_main_gui(self,main_gui):
        self.main_gui = main_gui

    def get_cerent_stops(self):
        return self.cerent_stops[0]

    def get_conectons(self):
        return self.cerent_connections[0]

    def change_cerent_stops(self,new_type):
        # if the katigorie is avaleble it can be chosen
        if not (new_type in self.all_data.delited_kategorie_opchens):
            # saves curend status, as a backup
            start_veluages = [self.cerent_stops,self.cerent_connections,self.cerent_gtfs]

            # lodes data baset on the type
            if new_type == "stops_fern":
                self.cerent_stops = self.all_data.get_stops_fern()
                self.cerent_connections = self.all_data.get_connections_fern()
                self.cerent_gtfs = self.all_data.gtfs("latest_fern")
            if new_type == "stops_nah":
                self.cerent_stops = self.all_data.get_stops_nah()
                self.cerent_connections = self.all_data.get_connections_nah()
                self.cerent_gtfs = self.all_data.gtfs("latest_nah")
            if new_type == "stops_regional":
                self.cerent_stops = self.all_data.get_stops_regional()
                self.cerent_connections = self.all_data.get_connections_regional()
                self.cerent_gtfs = self.all_data.gtfs("latest_regional")

            # if data is incoreckt
            if (self.cerent_gtfs == None) or (self.cerent_stops[1]==False) or (self.cerent_connections[1]==False):
                # the backup is used to resor the og veluages
                self.cerent_stops = start_veluages[0]
                self.cerent_connections = start_veluages[1]
                self.cerent_gtfs = start_veluages[2]

                # is tyt to resor data form every kategory, mait not be nasesery most times
                self.all_data.restor("fern")
                self.all_data.restor("nah")
                self.all_data.restor("regional")
            else:
                # the gui lodes new data and shows it
                self.main_gui.drawRouteNetwork(self.get_cerent_stops(),self.get_conectons()) 
        
    def get_about_text(self):
        return self.all_data.about_text

    def get_readme_text(self):
        return self.all_data.readme_text

    def get_tutorial(self):
        return self.all_data.tutorial_text

    def get_counts(self):
        return self.all_data.counts

    def change_trainstachen_info(self,time_span,day,hauer,min,trainstachen):
        # calculates new trainstachen data and fills it in
        self.trainstachen_info = self.all_data.create_trainstachen_info([day,hauer,min],trainstachen,time_span,self.cerent_gtfs)
        self.main_gui.dataTable_instace.set_df(self.trainstachen_info)
        





class Data(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        self.delited_kategorie_opchens = []

        # lodes nesesry and lite data, for the first vue
        self.counts = self.load_map_data()
        self.about_text = self.lode_about_text()
        self.readme_text = self.lode_readme_text()

        self.tutorial_text = self.load_tutorial()
        self.stops_fern = self.lode_text('stops_fern.txt')
        self.connections_fern = self.lode_text('connections_fern.csv')
        self.gtfs_fern = self.lode_gtfs("latest_fern")

        # checks if the first files are ok, or if (at a later date) diferend files nedes to be chosen
        self.lode_first = True
        if (self.stops_fern[1] == False) or (self.connections_fern[1] == False) or (self.gtfs_fern == None):
            self.lode_first = False

        # presets the gtfs variables, thrfor thy can be chckt if they alredy have bin lodet
        self.gtfs_nah = None
        self.gtfs_regional = None
        # veluages determenig if the variable is set 
        self.connections_nah_set = False
        self.connections_regional_set = False
        self.stops_regional_set = False
        self.stops_nah_set = False

        # the lodig of the rest of the data is stadet
        threading.Thread(target=self.gtfs_prep).start()
        # the time dilay is needet, tho every pre (runnig proses) is stardet.
        # thes nesesry becas the modell class myd aces them
        time.sleep(0.1)

    def restor(self,key):
        # if the key fits, and ther is data to be restrd
        if key == "fern" and ("stops_fern" in self.delited_kategorie_opchens):
            # if the main data set is ther (nedert for restoring)
            if not (self.gtfs_fern == None):
                # veluage represents how mutch of the typ is coreckt
                self.free_fern = 0
                # if connections_fern is wrong, a new file is created
                if self.connections_fern[1] == False:
                    Conectons(self,"fern").run() 
                else:
                    # connections_fern is coreckt
                    self.free_fern_add_1()
                if self.stops_fern[1] == False:
                    pass
                else:
                    self.free_fern_add_1()

        if key == "nah" and ("stops_nah" in self.delited_kategorie_opchens):
            if not (self.gtfs_nah == None):
                self.free_nah = 0
                if self.connections_nah[1] == False:
                    Conectons(self,"nah").run() 
                else:
                    self.free_nah_add_1()
                if self.stops_nah[1] == False:
                    pass
                else:
                    self.free_nah_add_1()

        if key == "regional" and ("stops_regional" in self.delited_kategorie_opchens):
            if not (self.gtfs_regional == None):
                self.free_regional = 0
                if self.connections_regional[1] == False:
                    Conectons(self,"regional").run() 
                else:
                    self.free_regional_add_1()
                if self.stops_regional[1] == False:
                    pass
                else:
                    self.free_regional_add_1()

    def free_regional_add_1(self):
        self.free_regional += 1
        # the dataset is fully restored and can be lodet
        # and the kategory is avaleble agan
        if self.free_regional == 2:
            self.stops_regional = self.lode_text('stops_regional.txt')
            self.connections_regional = self.lode_text('connections_regional.csv')
            self.delited_kategorie_opchens.remove("stops_regional")

    def free_fern_add_1(self):
        self.free_fern += 1
        if self.free_fern == 2:
            self.stops_fern = self.lode_text('stops_fern.txt')
            self.connections_fern = self.lode_text('connections_fern.csv')
            self.delited_kategorie_opchens.remove("stops_fern")
    
    def free_nah_add_1(self):
        self.free_nah += 1
        if self.free_nah == 2:
            self.stops_fern = self.lode_text('stops_nah.txt')
            self.connections_fern = self.lode_text('connections_nah.csv')
            self.delited_kategorie_opchens.remove("stops_nah")

    def gtfs_prep(self):
        # every file gets ists owen loding thet, wich is saver in the variabe on the left
        with concurrent.futures.ThreadPoolExecutor() as executor:
            self.gtfs_nah_pre = executor.submit(self.lode_gtfs,"latest_nah")
            self.gtfs_regional_pre = executor.submit(self.lode_gtfs,"latest_regional")
            self.connections_nah_pre = executor.submit(self.lode_text,'connections_nah.csv')
            self.connections_regional_pre = executor.submit(self.lode_text,'connections_regional.csv')
            self.stops_regional_pre = executor.submit(self.lode_text,'stops_regional.txt')
            self.stops_nah_pre = executor.submit(self.lode_text,'stops_nah.txt')

    def get_stops_fern(self):
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if self.stops_fern[1] == False:
            if not ("stops_fern" in self.delited_kategorie_opchens):
                self.delited_kategorie_opchens.append("stops_fern")
            self.restor("fern")
        return self.stops_fern

    def get_stops_nah(self):
        # if the valuue is not pulled, its done now
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if not self.stops_nah_set:
            self.stops_nah_set = True
            self.stops_nah = self.stops_nah_pre.result()
            if self.stops_nah[1] == False:
                if not ("stops_nah" in self.delited_kategorie_opchens):
                    self.delited_kategorie_opchens.append("stops_nah")
                self.restor("nah")
        return self.stops_nah

    def get_stops_regional(self):
        # if the valuue is not pulled, its done now
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if not self.stops_regional_set:
            self.stops_regional_set = True
            self.stops_regional = self.stops_regional_pre.result()
            if self.stops_regional[1] == False:
                if not ("stops_regional" in self.delited_kategorie_opchens):
                    self.delited_kategorie_opchens.append("stops_regional")
                self.restor("regional")
        return self.stops_regional

    def get_connections_regional(self):
        # if the valuue is not pulled, its done now
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if not self.connections_regional_set:
            self.connections_regional_set = True
            self.connections_regional = self.connections_regional_pre.result()
            if self.connections_regional[1] == False:
                if not ("stops_regional" in self.delited_kategorie_opchens):
                    self.delited_kategorie_opchens.append("stops_regional")
                self.restor("regional")
        return self.connections_regional
        
    def get_connections_nah(self):
        # if the valuue is not pulled, its done now
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if not self.connections_nah_set:
            self.connections_nah_set = True
            self.connections_nah = self.connections_nah_pre.result()
            if self.connections_nah[1] == False:
                if not ("stops_nah" in self.delited_kategorie_opchens):
                    self.delited_kategorie_opchens.append("stops_nah")
                self.restor("nah")
        return self.connections_nah

    def get_connections_fern(self):
        # if the valuue is incorecht, the kategory option is delited
        # and a restrachen is tryed
        if self.connections_fern[1] == False:
            if not ("stops_fern" in self.delited_kategorie_opchens):
                    self.delited_kategorie_opchens.append("stops_fern")
            self.restor("fern")
        return self.connections_fern

    def gtfs(self,kategorie):
        if kategorie == "latest_nah":
            if self.gtfs_nah == None:
                self.gtfs_nah = self.gtfs_nah_pre.result()
                if self.gtfs_nah == None:
                    self.delited_kategorie_opchens.append("stops_nah")
            return self.gtfs_nah

        if kategorie == "latest_fern":
            if self.gtfs_fern == None:
                self.delited_kategorie_opchens.append("stops_fern")
            return self.gtfs_fern

        if kategorie == "latest_regional":
            if self.gtfs_regional == None:
                self.gtfs_regional = self.gtfs_regional_pre.result()
                if self.gtfs_regional == None:
                    self.delited_kategorie_opchens.append("stops_regional")
            return self.gtfs_regional

    def lode_gtfs(self,kategorie):
        pfad_start = os.path.abspath(os.path.join(os.path.dirname( __file__ ), kategorie))+ '\\'

        data_names = ['agency','calendar','calendar_dates','feed_info','routes','stop_times','stops','trips']
        name_dict = {}

        gtfs_is_missing_files = False

        for name in data_names:
            pfad = pfad_start + name + '.txt'

            if exists(pfad):

                df = pd.read_csv(pfad)
                pd.set_option('display.min_rows', 10) 
                if name == 'stopshivz':
                    pd.set_option('display.min_rows', 400) 
                name_dict[name] = df

            else:
                print("Die Datei " + name + " wurde nicht Gefunden")
                print(os.path.abspath(os.path.join(os.path.dirname( __file__ ), name + '.txt')))
                gtfs_is_missing_files = True

        if gtfs_is_missing_files:
            print(" \n \n")
            print("da die daten von " + kategorie + " nicht geladen werden konten \n Kann man diese auch nicht aus welen")
            return None

        print(kategorie)
        return name_dict

    def load_map_data(self):
        """
        Loads the data of the map of Germany.
        Source of the file:
        http://opendatalab.de/projects/geojson-utilities/
        """
        path_to_map = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/landkreise_simplify200.geojson'))
        if exists(path_to_map):
            with open(path_to_map,encoding='utf8') as f:
                data = geojson.load(f)
            states = data['features']
            return states
        else:
            print("the landkreise_simplify200.geojson file is missing.")
            print("ists a criticel pat, therfor the program is shatig down.")
            print("the data is awaleble at http://opendatalab.de/projects/geojson-utilities/")
            exit()

    def lode_about_text(self):
        # Open the 'About' file and print it in a label of a new window.
        path_to_about = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/ABOUT.md'))
        if exists(path_to_about):
            with open(path_to_about, encoding='utf8') as about_file:
                about_text = about_file.read()
            return about_text
        else:
            return "No ABOUT text was found"

    def lode_readme_text(self):
        # Open the 'ReadMe' file and print it in a label of a new window.
        path_str = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data")) + "\\" #[3:]
        path_to_readme = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/README.md'))
        if exists(path_to_readme):
            with open(path_to_readme, encoding='utf8') as readme_file:
                readme_text = readme_file.read()
                readme_file.close()
                readme_text = readme_text.replace("/////", path_str)
                readme_text_md = markdown.markdown(readme_text)
            return readme_text_md
        else:
            return "No README text was found"

    def load_tutorial(self):
        # Open the 'Tutorial' file and print it in a label of a new window.
        path_str = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data")) + "\\" #[3:]
        path_to_tutorial = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/TUTORIAL.md'))
        if exists(path_to_tutorial):
            with open(path_to_tutorial, encoding='utf8') as tutorial_file:
                tutorial_text = tutorial_file.read()
                tutorial_file.close()
                tutorial_text = tutorial_text.replace("/////", path_str)
                tutorial_text_md = markdown.markdown(tutorial_text)
            return tutorial_text_md
        return "No TUTORIAL text was found"

    def lode_text(self,filename_routes):
        # Loads the file with the routes

        path_of_routes = os.path.abspath(os.path.join(os.path.dirname( __file__ ), "Data" + '/' + filename_routes))

        if exists(path_of_routes):
            routes = pd.read_csv(path_of_routes, encoding='utf8')
            return [routes,True]
        return [None,False]

    def create_trainstachen_info(self,date,trainstachen_name,time_spane,name_dict):

        time_spane = int(time_spane[0:2])
        if time_spane == 0:
            time_spane = 1

        day_given = date[0]
        hauer = date[1]
        min = date[2]

        # Bahnhofs Nahme -->  stop IDs
        stop_IDs = name_dict["stops"].loc[name_dict["stops"]["stop_name"] == trainstachen_name]['stop_id'].to_numpy()
        # IDs -->  trip_id 
        trip_id_IDs = set(name_dict["stop_times"].loc[name_dict["stop_times"]["stop_id"].isin(stop_IDs)]['trip_id'].to_numpy())


        conactions_df_counter = int(0)
        for trip_id_instanz in trip_id_IDs:

            trips_trip_id = name_dict["trips"].loc[name_dict["trips"]["trip_id"] == trip_id_instanz]
            service_id_instanz = trips_trip_id['service_id'].to_numpy()[0]
            serves_days = name_dict["calendar"].loc[name_dict["calendar"]["service_id"] == service_id_instanz]

            if not serves_days.empty:
                
                stop_times_trip_id_instanz = name_dict["stop_times"].loc[name_dict["stop_times"]["trip_id"] == trip_id_instanz]
                trip_id_stops = stop_times_trip_id_instanz.loc[stop_times_trip_id_instanz["stop_id"].isin(stop_IDs)]

                arrival_time = trip_id_stops['arrival_time'].to_numpy()[0]
                arrival_time_houer = int(arrival_time[0:2])
                days_over = int(arrival_time_houer / 24)

                day = day_given
                time_diferenc = 0
                if days_over > 0:
                    arrival_time_houer = arrival_time_houer - (24 * days_over)
                    arrival_time_houer_str = str(arrival_time_houer)
                    if len(arrival_time_houer_str) == 1:
                        arrival_time_houer_str = "0" + arrival_time_houer_str
                    arrival_time = arrival_time_houer_str+arrival_time[2:]
                    day = day_given - days_over
                    if (int(arrival_time[0:2]) < hauer) or (int(arrival_time[0:2]) < hauer) and (int(arrival_time[3:5]) < min):
                        day = day + 1
                        time_diferenc = 24*60
                    if day < 0:
                        day = day + 7
                    time_diferenc = time_diferenc + (int(arrival_time[0:2])-hauer)*60 + (int(arrival_time[3:5])-min)
                else:
                    time_diferenc = (int(arrival_time[0:2])-hauer)*60 + (int(arrival_time[3:5])-min)

                day_is_serfed = serves_days[calendar.day_name[day].lower()].to_numpy()[0]
                if day_is_serfed == 1:
                    

                    if time_diferenc > 0 and time_diferenc < time_spane*60:

                        trip_stachens = stop_times_trip_id_instanz['stop_sequence'].to_numpy()
                        last_stachen = max(trip_stachens)
                        direction = trips_trip_id['direction_id'].to_numpy()[0]
                        if direction == 0:
                            end_station = last_stachen
                        else:
                            end_station = 0
                        end_station_stop_id = stop_times_trip_id_instanz.loc[stop_times_trip_id_instanz["stop_sequence"] == end_station]['stop_id'].to_numpy()[0]
                        end_station_name = name_dict["stops"].loc[name_dict["stops"]["stop_id"] == end_station_stop_id]['stop_name'].to_numpy()[0]


                        route_id_instanz = trips_trip_id['route_id'].to_numpy()[0]
                        routes_row = name_dict["routes"].loc[name_dict["routes"]["route_id"] == route_id_instanz]

                        agency_id_instanz = routes_row['agency_id'].to_numpy()[0]
                        agency_name_instanz = name_dict["agency"].loc[name_dict["agency"]["agency_id"] == agency_id_instanz]['agency_name'].to_numpy()[0]
                        route_long_name = routes_row['route_long_name'].to_numpy()[0]
                        departure_time = trip_id_stops['departure_time'].to_numpy()[0]

                        if conactions_df_counter == 0:
                            conactions_df = pd.DataFrame([[agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]], columns=["Betreiber","Zugbezeichnung","Endstation","Einfahrtzeit","Abfahrtzeit"])
                        else:
                            conactions_df.loc[conactions_df_counter] = [agency_name_instanz, route_long_name,end_station_name,arrival_time,departure_time]
                        conactions_df_counter += 1

        if conactions_df_counter > 0:

            conactions_df = conactions_df.sort_values(by=['Einfahrtzeit'])
            actuell_time = str(hauer) + ":" + str(min) + ":00"

            conactions_df_firs = conactions_df.loc[conactions_df["Einfahrtzeit"] >= actuell_time]
            conactions_df_sec = conactions_df.loc[conactions_df["Einfahrtzeit"] < actuell_time]

            conactions_df = pd.concat([conactions_df_firs,conactions_df_sec])

            return conactions_df
        else:
            fetback_df = pd.DataFrame([["Keiene Züge gefunden"]], columns=["Info"])
            return fetback_df





# Calling the MainWindow, MenuWindowAbout and MenuWindowReadMe classes
# and display them as windows
if __name__ == "__main__":
    all_data = Data()
    all_data.run()

    print("baljdbdfbsojlvböadbvöob")

    model = Model(all_data)

    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow(model)
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    about_window = MenuWindowAbout(model)
    about_window.setWindowTitle("About - Über dieses Programm")
    readme_window = MenuWindowReadMe(model)
    readme_window.setWindowTitle("Read Me - Wichtig zu wissen")
    tutorial_window = MenuWindowTutorial(model)
    tutorial_window.setWindowTitle("Tutorial")

    sys.exit(app.exec())