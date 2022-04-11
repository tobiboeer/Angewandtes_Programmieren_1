import sys
import json
import pandas
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

#Resize
#Farben und Maus implementieren
#Zoom


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.SolidPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.1)
        land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        scene = QtWidgets.QGraphicsScene(-180, -90, 360, 90)
        
        map_data = self.load_map_data()
        
        for country, polygons in map_data.items():
            if country == 'Germany' or 'France':
                for polygon in polygons:
                    qpolygon = QtGui.QPolygonF()
                    for x,y in polygon:
                        qpolygon.append(QtCore.QPointF((x-14)*5,(y-56)*5)) 
                    scene.addPolygon(qpolygon, pen = country_pen,brush = land_brush)
                    
        scene.setBackgroundBrush(ocean_brush)
        
        world_map = QtWidgets.QGraphicsView()
        world_map.setScene(scene)
        world_map.scale(10,-10)
        world_map.setRenderHint(QtGui.QPainter.Antialiasing)

        
        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(world_map)

        
        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

        
    def load_map_data(self):
        with open('countries.json') as file: 
            data = json.load(file)
            
        return data
        

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())