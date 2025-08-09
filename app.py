"""
This is the entry point for the application.
The script performs the following tasks:
1. Imports necessary modules and functions.
2. Creates an instance of the application using the `create_app` function.
3. Ensures that the directories 'uploads' and 'models' exist, creating them if necessary.
4. Runs the application in debug mode on port 200.
If an exception occurs during the execution, it is logged as an error.
Modules:
    # os: Provides a way of using operating system dependent functionality.
    logging: Provides a way to configure and use loggers.
Functions:
    create_app: A function imported from the app module to create an instance of the application.
Exceptions:
    Any exception that occurs during the execution is caught and logged.
"""

# from flask import Flask, render_template
# from app import create_app
# import os
# import logging
# from PyQt5.QtWidgets import QApplication
# # from PyQt5.QtCore import QUrl
# import sys 
# from PyQt5.QtWidgets import QApplication, QMainWindow
# from PyQt5.QtWebEngineWidgets import QWebEngineView
# import sys
# from flask import Flask, render_template, request, redirect, url_for
# import sqlite3
# from app import create_app, init_db , socketio
# import os
# import logging
# from PyQt5.QtWidgets import QApplication
# import sys
# from flask_cors import CORS
# import threading

# # class MainWindow(QMainWindow):
# #     def __init__(self):
# #         super().__init__()
# #         self.setWindowTitle("PyQt5 WebEngine Example")
# #         self.resize(800, 600)

# #         # Add a QWebEngineView
# #         webview = QWebEngineView()
# #         webview.setUrl("https://www.python.org")
# #         self.setCentralWidget(webview)
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Flask-PyQt5 Integration")
#         self.resize(800, 600)

#         # Add a QWebEngineView
#         webview = QWebEngineView()
#         webview.setUrl("http://127.0.0.1:600")  # Flask app URL
#         self.setCentralWidget(webview)

# app = create_app()

# CORS(app, resources={r"/*": {"origins": "*"}})

# if __name__ == "__main__":
#     init_db()
#     try:
#         os.makedirs("uploads", exist_ok=True)
#         os.makedirs("models", exist_ok=True)
#         new_app = QApplication(sys.argv)
#         # main_window = MainWindow()
#         # # main_window.show()
#         # app.run(debug=True, port=200)
#         # Use socketio.run() instead of app.run()
# # Start Flask server in a separate thread
#         def run_flask():
#             socketio.run(app, debug=True, port=600, use_reloader=True)

#         flask_thread = threading.Thread(target=run_flask, daemon=True)
#         flask_thread.start()
#         # flask_thread.start()
#         sys.exit(new_app.exec_())
#     except Exception as e:
#         logging.error(f"An error occurred: {e}")

"""
Medivance.AI Flask + PyQt5 Integration with Auto-Reload
-------------------------------------------------------
This setup allows Flask (with SocketIO) to run in a separate process,
enabling hot reload for backend and template changes.
PyQt5 just loads the running web app.
"""

import os
import sys
import logging
import time
import multiprocessing
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView

from app import create_app, init_db, socketio
from flask_cors import CORS

# ---------------- Flask Runner ----------------
def run_flask():
    app = create_app()
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Ensure directories exist
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("models", exist_ok=True)

    init_db()

    # Run Flask with debug + reloader ON
    socketio.run(app, debug=True, port=600, use_reloader=True)


# ---------------- PyQt Window ----------------
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Medivance.AI")
        self.resize(1200, 800)

        webview = QWebEngineView()
        webview.setUrl("http://127.0.0.1:600")  # Flask app URL
        self.setCentralWidget(webview)


# ---------------- Main ----------------
if __name__ == "__main__":
    try:
        # Start Flask in a separate process (hot reload works)
        flask_process = multiprocessing.Process(target=run_flask)
        flask_process.start()

        # Give Flask a moment to start before loading in PyQt5
        time.sleep(2)

        qt_app = QApplication(sys.argv)
        main_window = MainWindow()
        main_window.show()

        exit_code = qt_app.exec_()

        # Kill Flask process when PyQt5 app closes
        flask_process.terminate()
        sys.exit(exit_code)

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        if 'flask_process' in locals():
            flask_process.terminate()
        