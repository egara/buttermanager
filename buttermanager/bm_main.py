from .buttermanager.buttermanager import PasswordWindow
from PyQt5.QtWidgets import QApplication
import sys


def main():
    """Main wrapper for starting ButterManager
    
    This script is only for packaging purposes. If you are developing ButterManager, then use main.py as initial
    script. This script will be copied from setup.py using setuptools and it will be invoked from the script
    created within /usr/bin/buttermanager once the application is installed via sudo python setup.py install

    """
    # Creating application instance
    application = QApplication(sys.argv)
    # Creating main window instance
    PasswordWindow(None)
    # Launching the application
    application.exec_()


if __name__ == "__main__":
    main()
