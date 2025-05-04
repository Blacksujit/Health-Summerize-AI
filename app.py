"""
This is the entry point for the application.
The script performs the following tasks:
1. Imports necessary modules and functions.
2. Creates an instance of the application using the `create_app` function.
3. Ensures that the directories 'uploads' and 'models' exist, creating them if necessary.
4. Runs the application in debug mode on port 200.
If an exception occurs during the execution, it is logged as an error.
Modules:
    os: Provides a way of using operating system dependent functionality.
    logging: Provides a way to configure and use loggers.
Functions:
    create_app: A function imported from the app module to create an instance of the application.
Exceptions:
    Any exception that occurs during the execution is caught and logged.
"""

from flask import Flask, render_template
from app import create_app
import os
import logging
from PyQt5.QtWidgets import QApplication
# from PyQt5.QtCore import QUrl
import sys 
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sys
from flask import Flask, render_template, request, redirect, url_for
import sqlite3
from app import create_app, init_db , socketio
import os
import logging
from PyQt5.QtWidgets import QApplication
import sys
from flask_cors import CORS
import threading

# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("PyQt5 WebEngine Example")
#         self.resize(800, 600)

#         # Add a QWebEngineView
#         webview = QWebEngineView()
#         webview.setUrl("https://www.python.org")
#         self.setCentralWidget(webview)
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flask-PyQt5 Integration")
        self.resize(800, 600)

        # Add a QWebEngineView
        webview = QWebEngineView()
        webview.setUrl("http://127.0.0.1:600")  # Flask app URL
        self.setCentralWidget(webview)

app = create_app()

CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == "__main__":
    init_db()
    try:
        os.makedirs("uploads", exist_ok=True)
        os.makedirs("models", exist_ok=True)
        new_app = QApplication(sys.argv)
        # main_window = MainWindow()
        # # main_window.show()
        # app.run(debug=True, port=200)
        # Use socketio.run() instead of app.run()
# Start Flask server in a separate thread
        def run_flask():
            socketio.run(app, debug=True, port=600)

        flask_thread = threading.Thread(target=run_flask, daemon=True)
        flask_thread.start()
        # flask_thread.start()
        sys.exit(new_app.exec_())
    except Exception as e:
        logging.error(f"An error occurred: {e}")