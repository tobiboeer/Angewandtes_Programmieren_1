from PySide6 import QtCore
from PySide6 import QtWidgets

class menuWindowAbout(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'About' menu in the menubar.
    """
    
    def __init__(self, model):
        """
        Creates a widget for the About menu.

        Parameters
        ----------
        model : model
            interactions class
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

class menuWindowReadMe(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'ReadMe' menu in the menubar.
    """
    
    def __init__(self, model):
        """
        Creates a widget for the ReadMe menu.

        Parameters
        ----------
        model : model
            interactions class
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

class menuWindowTutorial(QtWidgets.QGraphicsView):
    """
    Creates the window of the 'Tutorial' menu in the menubar.
    """
    
    def __init__(self, model):
        """
        Creates a widget for the Tutorial menu.

        Parameters
        ----------
        model : model
            interactions class
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