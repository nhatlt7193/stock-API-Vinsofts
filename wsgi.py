from app.main import app, scraping_data


if __name__ == "__main__":
	threading.Thread(target=scraping_data).start()
    app.run('0.0.0.0',port=5000,debug=1)

