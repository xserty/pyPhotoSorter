import multiprocessing
import os.path
import signal
from concurrent.futures import ThreadPoolExecutor

from PySide6.QtCore import QSize, QRect
from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QFrame, QMenuBar, QMenu, QCheckBox, \
    QMessageBox, QStatusBar, QSpinBox, QMainWindow, QPushButton, QFileDialog, QWidget, QProgressBar

from src.options import options, settings
from src.utilities import imageSort


class MainGUI(QMainWindow):
    _sort_process = None
    _sort_thread = None
    _thread_event = None
    _future = None
    _proc = None

    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)

    def __init__(self):
        super().__init__()
        self.source_img_folder = ''
        self.destination_img_folder = ''

        self.setWindowTitle("pyPhotoSorter")
        self.setMinimumSize(QSize(800, 400))

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.targetArea = QWidget(parent=self.central_widget)
        self.targetArea.setGeometry(QRect(520, 100, 520, 140))
        self.targetArea.setAutoFillBackground(False)
        self.targetArea.setObjectName("targetArea")

        # menuBar
        self._create_menu_bar()

        source_button = QPushButton("Select Folder")
        source_button.setFixedSize(QSize(130, 30))
        source_button.setToolTip("Select media folder to sort")
        source_button.clicked.connect(self.select_source_dir)
        self.source_label = QLabel()
        self.source_label.setText("Select media folder to sort")
        self.source_label.setToolTip("Select media folder to sort")
        self.source_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.source_label.setFixedSize(QSize(700, 30))

        dest_button = QPushButton("Select Folder")
        dest_button.setToolTip("Select destination folder where sorted media files will be copied")
        dest_button.setFixedSize(QSize(130, 30))
        dest_button.clicked.connect(self.select_destination_dir)
        self.dest_label = QLabel()
        self.dest_label.setText("Select destination folder of sorted media files")
        self.dest_label.setToolTip("Select destination folder of sorted media files")
        self.dest_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.dest_label.setFixedSize(QSize(700, 30))

        unsorted_button = QPushButton("Select Folder")
        unsorted_button.setToolTip("Select destination folder where unsorted media files will be copied")
        unsorted_button.setFixedSize(QSize(130, 30))
        unsorted_button.clicked.connect(self.select_unsorted_dir)
        self.unsorted_label = QLabel()
        self.unsorted_label.setText("Select media folder where to store unsorted media files")
        self.unsorted_label.setToolTip("Select media folder where to store unsorted media files")
        self.unsorted_label.setFrameStyle(QFrame.Panel | QFrame.Sunken)
        self.unsorted_label.setFixedSize(QSize(700, 30))

        # create a horizontal layout for source button and label
        self.source_layout = QHBoxLayout()
        self.source_layout.addWidget(source_button)
        self.source_layout.addWidget(self.source_label)
        # create a horizontal layout for destination  button and label
        self.dest_layout = QHBoxLayout()
        self.dest_layout.addWidget(dest_button)
        self.dest_layout.addWidget(self.dest_label)
        # create a horizontal layout for destination  button and label
        self.unsorted_layout = QHBoxLayout()
        self.unsorted_layout.addWidget(unsorted_button)
        self.unsorted_layout.addWidget(self.unsorted_label)

        # create the main layout and decide on which layout to use
        self.main_layout = QVBoxLayout()
        self.central_widget.setLayout(self.main_layout)

        # add widgets and layouts to out main layout
        self.main_layout.addLayout(self.source_layout)
        self.main_layout.addLayout(self.dest_layout)
        self.main_layout.addLayout(self.unsorted_layout)

        # advanced options
        self.advanced_layout = QGridLayout()
        adv_label = QLabel("Advanced options:")

        self.deep_mode_hash_checkbox = QCheckBox("Deep Mode Hash")
        self.deep_mode_hash_checkbox.setToolTip(
            "When creating a dictionary hash for the file, it instructs the application to generate the hash based on the file contents.<br> NOTE: Slows down the application")
        self.advanced_layout.addWidget(self.deep_mode_hash_checkbox)
        self.regenerate_media_dictionary_checkbox = QCheckBox("Regenerate Media Dictionary")
        self.regenerate_media_dictionary_checkbox.setToolTip("Regenerate Media Dictionary")
        self.advanced_layout.addWidget(self.regenerate_media_dictionary_checkbox)
        self.cleanup_dictionary_checkbox = QCheckBox("Cleanup Dictionary")
        self.cleanup_dictionary_checkbox.setToolTip("Cleanup Dictionary")
        self.advanced_layout.addWidget(self.cleanup_dictionary_checkbox)
        self.ignore_date_in_path_checkbox = QCheckBox("Ignore Date in Path")
        self.ignore_date_in_path_checkbox.setToolTip("Ignore any dates pattern in the path of the media file")
        self.advanced_layout.addWidget(self.ignore_date_in_path_checkbox)
        self.max_num_of_threads_spinBox = QSpinBox()
        self.max_num_of_threads_spinBox.setValue(options.max_num_of_threads)
        self.max_num_of_threads_spinBox.setMinimum(1)
        self.max_num_of_threads_spinBox.setMaximum(options.max_num_of_threads)
        self.max_num_of_threads_spinBox.setMaximumWidth(40)
        self.max_num_of_threads_spinBox.setToolTip("Maximum number of threads used to sort media files")
        spinBox_label = QLabel("Maximum number of threads:")
        self.thread_layout = QHBoxLayout()
        self.thread_layout.addWidget(spinBox_label)
        self.thread_layout.addWidget(self.max_num_of_threads_spinBox)
        self.thread_layout.addStretch()
        self.advanced_layout.addLayout(self.thread_layout, 4, 0)

        self.main_layout.addWidget(adv_label)
        self.main_layout.addLayout(self.advanced_layout)

        # STRETCH (FILL EMPTY SPACE
        self.main_layout.addStretch()

        # bottom buttons
        self.bottom_layout = QHBoxLayout()
        # forceStop button
        start_sort_button = QPushButton("Sort!")
        start_sort_button.setToolTip("Sort media files")
        start_sort_button.setFixedSize(QSize(100, 30))
        start_sort_button.clicked.connect(self.start_sort)
        forceStop_button = QPushButton("Force stop!")
        forceStop_button.setToolTip("(NOT IMPLEMENTED) Force any sorting in progress to stop")
        forceStop_button.setFixedSize(QSize(100, 30))
        forceStop_button.clicked.connect(self.force_stop)
        loadOptions_button = QPushButton("Load Options")
        loadOptions_button.setToolTip("Load previously save options from disk")
        loadOptions_button.setFixedSize(QSize(100, 30))
        loadOptions_button.clicked.connect(self.load_options)
        saveOptions_button = QPushButton("Save Options")
        saveOptions_button.setToolTip("Save current options to disk")
        saveOptions_button.setFixedSize(QSize(100, 30))
        saveOptions_button.clicked.connect(self.save_options)
        quit_button = QPushButton("Quit")
        quit_button.setFixedSize(QSize(100, 30))
        quit_button.released.connect(self.quit_application)
        # add buttons to the bottom layout
        self.bottom_layout.addWidget(start_sort_button)
        self.bottom_layout.addWidget(forceStop_button)
        self.bottom_layout.addWidget(loadOptions_button)
        self.bottom_layout.addWidget(saveOptions_button)
        self.bottom_layout.addWidget(quit_button)
        # add bottom layout to the main layout
        self.main_layout.addLayout(self.bottom_layout)

        # add status bar
        self.statusBar = QStatusBar()
        self.statusBar_layout = QHBoxLayout()
        # MainWindow._progressBar = QProgressBar()
        self.progressBar = QProgressBar()
        # self.statusBar.x
        self.statusBar.addPermanentWidget(self.progressBar)
        # self.statusBar.
        # self.statusBar.setStyleSheet('border: 10; background-color: #000000;')
        # self.statusBar.setStyleSheet("background-color: yellow;")
        self.statusBar.showMessage("Ready.")
        self.setStatusBar(self.statusBar)
        self.set_gui_options()
        self.show()  # Widgets without a parent are invisible by default.

    def _create_menu_bar(self):
        menuBar = QMenuBar()
        # File menu
        fileMenu = QMenu("&File", self)
        self.menuAction = fileMenu.addAction("&Load options...")
        # self.menuAction.setToolTip("Load previously save options from disk")  # Not working
        self.menuAction.triggered.connect(self.load_options)
        self.menuAction = fileMenu.addAction("&Save options...")
        # self.menuAction.setToolTip("Save current options to disk")  # Not working
        self.menuAction.triggered.connect(self.save_options)
        # self.menuAction = fileMenu.addAction("S&ettings...")
        # self.menuAction.triggered.connect(self.show_advanced_settings)
        self.menuAction = fileMenu.addAction("E&xit")
        self.menuAction.triggered.connect(self.quit_application)
        menuBar.addMenu(fileMenu)
        # Edit menu
        editMenu = menuBar.addMenu("&Edit")
        # Help menu
        helpMenu = QMenu("&Help", self)
        # add About button
        self.menuAction = helpMenu.addAction("&About")
        self.menuAction.triggered.connect(self.show_about_dialog)
        # aboutMenu = QMenu("&About", self)
        # helpMenu.addAction("&About")
        menuBar.addMenu(helpMenu)
        self.setMenuBar(menuBar)

    @classmethod
    def show_advanced_settings(cls):
        # Logic for showing an about dialog content goes here...
        dlg = QMessageBox()
        dlg.setWindowTitle("About")
        dlg.setText("This is a simple dialog")
        dlg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        button = dlg.exec()
        if button == QMessageBox.Ok:
            print("Ok!")
        elif button == QMessageBox.Cancel:
            print("Cancel!")

    @classmethod
    def show_about_dialog(cls):
        # Logic for showing an about dialog content goes here...
        dlg = QMessageBox()
        dlg.setWindowTitle("About")
        about_text = "<h3>pyPhotoSorter</h3> was brought to you by...<br><em>Stefano</em>"
        about_text += "<h4>Version</h4> " + settings.VERSION
        dlg.setText(about_text)
        dlg.setStandardButtons(QMessageBox.Close)
        button = dlg.exec()
        if button == QMessageBox.Close:
            print("Closed About dialog!")

    def start_sort(self):
        # https://realpython.com/python-pyqt-qthread/
        print("Starting media sorting process...")
        self.populate_options_instance()

        # Pass arguments via a dictionary
        args_dict = {'img_dir': options.source_media_dir, 'sorted_dir': options.sorted_media_dir, 'unsorted_dir': options.unsorted_media_dir, 'deep_mode_hash': options.deep_mode_hash, 'ignore_date_in_path': options.ignore_date_in_path, 'regen_media_dict': options.regenerate_media_dictionary, 'cleanup_dictionary': options.cleanup_dictionary, 'max_threads_num': options.max_num_of_threads}

        # spawn process to sort media files
        MainGUI._proc = multiprocessing.Process(target=imageSort.main_call, kwargs=args_dict)
        MainGUI._proc.daemon = True
        MainGUI._proc.start()

    @classmethod
    def force_stop(cls):
        print("Interrupting media sorting progress...")
        if MainGUI._proc.is_alive():
            # MainWindow.proc.terminate()
            os.kill(MainGUI._proc.pid, signal.SIGINT)
            print("Sending SIGINT to %s" % MainGUI._proc)

    def load_options(self):
        print("Loading options from disk")
        options.load_from_disk()
        imageSort.thread_pool = ThreadPoolExecutor(max_workers=options.max_num_of_threads)
        self.set_gui_options()

    def set_gui_options(self):
        if len(options.source_media_dir) > 0:
            self.source_label.setText(options.source_media_dir)
        if len(options.sorted_media_dir) > 0:
            self.dest_label.setText(options.sorted_media_dir)
        if len(options.unsorted_media_dir) > 0:
            self.unsorted_label.setText(options.unsorted_media_dir)
        self.deep_mode_hash_checkbox.setChecked(options.deep_mode_hash)
        self.regenerate_media_dictionary_checkbox.setChecked(options.regenerate_media_dictionary)
        self.cleanup_dictionary_checkbox.setChecked(options.cleanup_dictionary)
        self.ignore_date_in_path_checkbox.setChecked(options.ignore_date_in_path)
        self.max_num_of_threads_spinBox.setValue(options.max_num_of_threads)

    def save_options(self):
        print("Saving options to disk")
        self.populate_options_instance()
        options.save_to_disk()

    def populate_options_instance(self):
        options.source_media_dir = self.source_label.text()
        options.sorted_media_dir = self.dest_label.text()
        options.unsorted_media_dir = self.unsorted_label.text()
        options.deep_mode_hash = self.deep_mode_hash_checkbox.isChecked()
        options.regenerate_media_dictionary = self.regenerate_media_dictionary_checkbox.isChecked()
        options.cleanup_dictionary = self.cleanup_dictionary_checkbox.isChecked()
        options.ignore_date_in_path = self.ignore_date_in_path_checkbox.isChecked()
        options.max_num_of_threads = self.max_num_of_threads_spinBox.value()

    def quit_application(self):
        print("Exiting the application!")
        self.close()

    def select_source_dir(self):
        # print("Selecting source folder")
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        # print("Media source path:", folder_path)
        self.source_label.setText(folder_path)
        return folder_path

    def select_destination_dir(self):
        # print("Selecting destination folder")
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        # print("Media destination path:", folder_path)
        self.dest_label.setText(folder_path)
        self.unsorted_label.setText(str(os.path.join(folder_path, settings.UNSORTED_MEDIA_DIR)))

        return folder_path

    def select_unsorted_dir(self):
        # print("Selecting unsorted folder")
        dialog = QFileDialog()
        folder_path = dialog.getExistingDirectory(None, "Select Folder")
        # print("Unsorted media destination path:", folder_path)
        self.unsorted_label.setText(folder_path)
        return folder_path
