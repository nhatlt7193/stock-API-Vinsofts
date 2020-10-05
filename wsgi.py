from app.main import app, scraping_data
import threading
import os
os.sys("pip install -r requirements.txt")
if __name__ == "__main__":
	# threading.Thread(target=scraping_data).start()
	app.run()
