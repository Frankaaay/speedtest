import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QGridLayout, QFrame
from PyQt5.QtCore import Qt, QThread, pyqtSignal
import server_live
import gui_speed_recorder
import gui_stability_recorder

# Thread class to run a function in a new thread
class ScriptThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, func):
        super().__init__()
        self.func = func

    def run(self):
        self.func()
        self.finished_signal.emit()

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        # Store threads in a list to keep references
        self.threads = []

        # Set window properties
        self.setWindowTitle("大力王")
        self.setGeometry(100, 100, 1000, 800)
        self.setStyleSheet("background-color: #282c34;")

        # Create title label
        title_label = QLabel("请选择你的王", self)
        title_label.setStyleSheet("color: #61dafb; font: bold 24px;")
        title_label.setAlignment(Qt.AlignCenter)

        # Create button frame (equivalent)
        button_frame = QFrame(self)
        button_layout = QGridLayout(button_frame)

        # Button style
        button_style = """
        QPushButton {
            font: 16px;
            background-color: #61dafb;
            color: white;
            border: 4px solid #1f7aaf;
            padding: 10px;
        }
        QPushButton:pressed {
            background-color: #1f7aaf;
        }
        """

        # Create and place buttons
        button1 = QPushButton("耐测王", self)
        button1.setStyleSheet(button_style)
        button1.clicked.connect(lambda: self.run_script(gui_speed_recorder.main))
        button_layout.addWidget(button1, 0, 0)

        button2 = QPushButton("耐看王", self)
        button2.setStyleSheet(button_style)
        button2.clicked.connect(lambda: self.run_script(gui_stability_recorder.main))
        button_layout.addWidget(button2, 0, 1)

        button3 = QPushButton("金山画王", self)
        button3.setStyleSheet(button_style)
        button3.clicked.connect(lambda: self.run_script(server_live.main))
        button_layout.addWidget(button3, 1, 0, 1, 2)

        # Footer label
        footer_label = QLabel("© 2024 Flymodem", self)
        footer_label.setStyleSheet("color: #888; font: 12px;")
        footer_label.setAlignment(Qt.AlignCenter)

        # Layout for the main window
        main_layout = QVBoxLayout()
        main_layout.addWidget(title_label)
        main_layout.addWidget(button_frame)
        main_layout.addWidget(footer_label)
        main_layout.setContentsMargins(20, 20, 20, 20)

        self.setLayout(main_layout)

    def run_script(self, func):
        # Create a new thread to run the function
        thread = ScriptThread(func)
        thread.finished_signal.connect(self.on_thread_finished)
        self.threads.append(thread)  # Keep a reference to prevent garbage collection
        thread.start()

    def on_thread_finished(self):
        # Clean up threads that have finished
        thread = self.sender()
        self.threads.remove(thread)
        thread.deleteLater()

# Initialize the application and main window
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
