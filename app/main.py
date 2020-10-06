from flask import Flask
import tensorflow as tf
app = Flask(__name__)

model = tf.keras.models.load_model('my_model_1601456415.0336444_200')

@app.route('/')
def home_view():
	
	return "{model}<h1>Welcome to Stock-Vinsofts</h1>"

