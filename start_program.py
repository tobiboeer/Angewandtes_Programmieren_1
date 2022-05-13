"""
Starts the entire program.

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

# Starts the program
if __name__ == "__main__":
    
    # Reads all files and manages the data
    all_data = data()
    all_data.run()

    # Intermediates between the data and the GUI
    model = model(all_data)

    app = QtWidgets.QApplication(sys.argv)

    window = mainWindow(model)
    window.setWindowTitle("Deutsches Bahnnetz")
    window.show()

    sys.exit(app.exec())