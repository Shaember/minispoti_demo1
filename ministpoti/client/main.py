import sys
from PyQt5.QtWidgets import QApplication
from .controller import MiniSpotifyController
from .view import MainWindow

def main():
    app = QApplication(sys.argv)
    
    controller = MiniSpotifyController()
    window = MainWindow(controller)
    window.show()
    
    sys.exit(app.exec_())

if __name__ == '__main__':
    main() 