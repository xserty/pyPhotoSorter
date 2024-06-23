import sys
import gui.mainGUI
from PySide6.QtWidgets import QApplication

# Sample images taken from: https://exiftool.org/sample_images.html Other sample images:
# https://github.com/drewnoakes/metadata-extractor-images More available at https://raw.pixls.us/ To use ExifTool
# check this out: https://stackoverflow.com/questions/77038678/how-to-extract-metadata-from-heic-image-files-on
# -windows-11-with-python


if __name__ == '__main__':
    # Run the GUI application
    app = QApplication(sys.argv)
    m = gui.mainGUI.MainGUI()
    app.exec()
