import sys
import json
import geojson
from PySide6 import QtCore
from PySide6 import QtWidgets
from PySide6 import QtGui

class WorldMap(QtWidgets.QGraphicsView):
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


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        ocean_brush = QtGui.QBrush("lightblue", QtCore.Qt.BrushStyle.SolidPattern)
        country_pen = QtGui.QPen("grey")
        country_pen.setWidthF(0.5)
        land_brush = QtGui.QBrush("white", QtCore.Qt.BrushStyle.SolidPattern)

        scene = QtWidgets.QGraphicsScene(-180, -90, 360, 180)

        map_data = self.load_map_data()
        
        #################################################
        
        for x in range(0,35):
            deutschland_data = map_data['features'][x]['geometry']
           # print(deutschland_data)
           
            
            
            # for polygon in test_list:
            #     qpolygon = QtGui.QPolygonF()
            #     for x, y in polygon:
            #         qpolygon.append(QtCore.QPointF(x, y))
            #     scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
            # scene.setBackgroundBrush(ocean_brush)
       
        # Fabians Sachen
            test_list = deutschland_data["coordinates"] 
            test_list[0] = test_list[0][0]

            new_poli = []
            for polygon in test_list:
                for poli in polygon:
                    if len(poli) != 2:
                        new_poli.append(poli)
                        polygon.remove(poli)
                        pass
                

            for poli in new_poli:
                test_list.append(poli)


            for polygon in test_list:
                qpolygon = QtGui.QPolygonF()
                for poli in polygon:
                    if len(poli) == 2:
                        x,y = poli
                        qpolygon.append(QtCore.QPointF((x - 10) * 14, (y- 55) *14))
                scene.addPolygon(qpolygon, pen=country_pen, brush=land_brush)
            scene.setBackgroundBrush(ocean_brush)
        ########################################################
        world_map = WorldMap()
        world_map.setScene(scene)
        world_map.setRenderHint(QtGui.QPainter.Antialiasing)

        layout = QtWidgets.QHBoxLayout()
        layout.addWidget(world_map)

        window_content = QtWidgets.QWidget()
        window_content.setLayout(layout)
        self.setCentralWidget(window_content)

    def load_map_data(self):
        with open('bundeslaender_simplify200.geojson') as f:
            data = geojson.load(f)
        return data


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    sys.exit(app.exec())
