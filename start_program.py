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

import sys

from PySide6 import QtWidgets

from DB_data import data as data
from DB_model import model as model
from DB_mainWindow import mainWindow as mainWindow

# Calling the MainWindow, MenuWindowAbout and MenuWindowReadMe classes
# and display them as windows
if __name__ == "__main__":
    all_data = data()
    all_data.run()

    model = model(all_data)

    app = QtWidgets.QApplication(sys.argv)

    window = mainWindow(model)
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    sys.exit(app.exec())