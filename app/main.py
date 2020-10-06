from flask import Flask
import time

app = Flask(__name__)

@app.route('/')
def home_view():
	return f"{time.time()}<h1>Welcome to Stock-Vinsofts</h1>"

