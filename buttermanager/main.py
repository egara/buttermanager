from .buttermanager.buttermanager import PasswordWindow
from PyQt5.QtWidgets import QApplication
import sys


def main():
    """Main wrapper for starting the program

    """
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    password_window = PasswordWindow(None)
    # Launching the application
    application.exec_()


if __name__ == "__main__":
    main()
