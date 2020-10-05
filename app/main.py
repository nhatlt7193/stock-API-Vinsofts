# Crawling data per 1 minute
import requests
import pprint
import json
import logging
import time
import numpy as np
import pandas as pd
import queue
import logging
import threading

from flask import Flask, render_template, session


app = Flask(__name__)
name=queue.Queue(maxsize=0)
Prediction_price = queue.Queue(maxsize=0)
Prediction_status = queue.Queue(maxsize=0)


y_real_ending = 1
# format_origin = 
# import Train
origin_list = []
Oprice_list = []
print(len(Oprice_list))

i=1
len_recurent = 0
count_stopping=1
real_data=1
Amount_fail=0
Amount_true=0
import tensorflow as tf
regressor = tf.keras.models.load_model('my_model_1601456415.0336444_200')
def scraping_data():
    global Prediction_price, Prediction_status, Amount_true, Amount_fail
    global Oprice_list, len_recurent, y_real_ending, count_stopping, real_data, X_test, y_real
    try:
        while 1:
            # print(count_stopping, real_data)
            while 1:
                try:
                    if len(Oprice_list)>=60:
                        break
                    content = requests.request("GET", "https://query1.finance.yahoo.com/v7/finance/quote?=&symbols=BTC-USD")
                    X = content.text
                    X = json.loads(X)
                    time_open = X['quoteResponse']['result'][0]['regularMarketTime']
                    if time_open not in origin_list and time.localtime(time.time()).tm_sec>10 and time.localtime(time.time()).tm_sec<50:
                    
                        # count_stopping=0
                        y = requests.request("GET", "https://query1.finance.yahoo.com/v7/finance/quote?=&symbols=BTC-USD")
                        Y = y.text
                        Y = json.loads(Y)
                        origin_list.append(time_open)
                        Oprice_list.append(Y['quoteResponse']['result'][0]['regularMarketPrice'])
                        print(Oprice_list)
                    
                except:
                    pass

            try:
                content = requests.request("GET", "https://query1.finance.yahoo.com/v7/finance/quote?=&symbols=BTC-USD")
                X = content.text
                X = json.loads(X)
                time_open = X['quoteResponse']['result'][0]['regularMarketTime']
                if time_open not in origin_list and time.localtime(time.time()).tm_sec>10 and time.localtime(time.time()).tm_sec<50:
                
                    # count_stopping=0
                    y = requests.request("GET", "https://query1.finance.yahoo.com/v7/finance/quote?=&symbols=BTC-USD")
                    Y = y.text
                    Y = json.loads(Y)
                    origin_list.append(time_open)
                    if Y['quoteResponse']['result'][0]['regularMarketPrice']>Oprice_list[-1]:
                        if Prediction_status == "UP":
                            Amount_true +=1
                        else:
                            Amount_fail +=1
                        logging.warning("UP")
                    elif Y['quoteResponse']['result'][0]['regularMarketPrice']==Oprice_list[-1]:
                        if Prediction_status == "PAIR":
                            Amount_true +=1
                        else:
                            Amount_fail +=1
                        logging.warning("PAIR")

                    else:
                        if Prediction_status == "DOWN":
                            Amount_true +=1
                        else:
                            Amount_fail +=1
                        logging.warning("DOWN")
                     
                    
                    # if len(Oprice_list)>len_recurent and len(Oprice_list)>=60:
                    #     count_stopping=0
                    #     y_real_ending = Y['quoteResponse']['result'][0]['regularMarketPrice']
                    Oprice_list.append(Y['quoteResponse']['result'][0]['regularMarketPrice'])
                    X_test, y_real = preprocessing_data(Oprice_list)
                    y_pre = test(X_test)
                    # logging.warning(f'Prediction status: {y_pre} {X_test}')
                    Prediction_price = y_pre
                    if y_pre > X_test[0][-1]:
                        Prediction_status = "UP"
                    elif y_pre == X_test[0][-1]:
                        Prediction_status = "PAIR"
                    else:
                        Prediction_status = "DOWN"
                    # logging.warning(check_and_testing(X_test, y_pre, Oprice_list))

                    # check_right_or_failed()
                    # if check_right_or_failed():
                    #     logging.warning("WIN")
                    # else:
                    #     logging.warning("LOSED")
                    # print(origin_list,Oprice_list)
                else:
                    pass
                # while 1:
                #     y = requests.request("GET", "https://query1.finance.yahoo.com/v7/finance/quote?=&symbols=BTC-USD")
                #     Y = y.text
                #     Y = json.loads(Y)
                #     if time_open != Y['quoteResponse']['result'][0]['regularMarketTime']:
                #         origin_dict['result'].update({
                #             i:{
                #             'time': Y['quoteResponse']['result'][0]['regularMarketTime'],
                #             'price': Y['quoteResponse']['result'][0]['regularMarketPrice']
                #             }
                #         })
                #         i+=1
                #         break
                # # pprint.pprint(origin_dict)
            except Exception as e:
                logging.warning(str(time.localtime(time.time())))
                logging.warning(e)
                # with open(f'data_{str(time.localtime(time.time()).tm_mday)+str(time.time())}.json', 'w') as f:
                #     json.dump(origin_dict, f)
    except KeyboardInterrupt as e:
            logging.warning(str(time.localtime(time.time())))
            logging.warning(e)
            # with open(f'data_{str(time.localtime(time.time()).tm_mday)+str(time.time())}.json', 'w') as f:
            #     json.dump(origin_dict, f)
            # price_open = X['quoteResponse']['result'][0]['regularMarketPrice']


@app.route('/')
def index():
    global Prediction_status, name, Oprice_list, Amount_true, Amount_fail
    if type(Prediction_status) == queue.Queue:
        Prediction_status = "Waiting..."
    if type(name) == queue.Queue:
        name = "grey"
    logging.warning(Prediction_status)
    if Prediction_status == "UP":
        name = "green"
    elif Prediction_status == "PAIR":
        name = "grey"
    elif Prediction_status == "DOWN":
        name = "red"
    return render_template('index.html',Prediction_status=Prediction_status,name=name,CURENT_PRICE = Oprice_list[-1], Amount_true=Amount_true, Amount_fail=Amount_fail)


def preprocessing_data(dataframe):
    Oprice_list_df = pd.DataFrame(dataframe, columns=["Open"])
    from sklearn.preprocessing import MinMaxScaler
    sc = MinMaxScaler(feature_range = (0, 1))
    testing_set_scaled = sc.fit_transform(Oprice_list_df)
    # logging.warning(testing_set_scaled)
    X_test=[]
    y_real=[]
    for i in range(60, len(testing_set_scaled)):
        X_test.append(testing_set_scaled[i-60:i,0])
    for i in range(60, len(testing_set_scaled)):
        y_real.append(testing_set_scaled[i,0])
    # print(X_test, y_real, len(X_test), len(y_real))
    X_test = np.asarray(X_test)
    # logging.warning(X_test)
    X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))
    y_real = np.asarray(y_real)
    return X_test, y_real
def test(X_test_):
    global regressor
    #print(X_test,y_real)
    predicted_stock_price = regressor.predict(X_test_)
    # print(predicted_stock_price)
    # print(len(X_test_),predicted_stock_price[-1][0])
    return predicted_stock_price[-1][0]
def check_and_testing(X_test, y_pre, Oprice_list):
    # global Oprice_list
    # global len_recurent, y_real_ending
    # global y_real, X_test
    len_recurent = len(Oprice_list)
    if len_recurent>=60:
        # print(len_recurent)
        
        # print(preprocessing_data(Oprice_list_df)
        
        # print(1)
        if y_pre > X_test[0][-1]:
            return 1,X_test[0][-1]
        elif y_pre == X_test[0][-1]:
            return '-',X_test[0][-1]
        else:
            return 0,X_test[0][-1]
def check_right_or_failed():
    global y_real_ending
    global count_stopping
    global real_data, y_real
    
    
    while 1:
        prediction_data = check_and_testing()
        if real_data!= y_real_ending:
            # print(real_data)
            count_stopping=1
            if y_real[-1]>prediction_data[1]:
                x=1
                if prediction_data[0]==1:
                    real_data=y_real_ending
                    logging.warning("UP")
                    logging.warning(f"Prediction-data: {prediction_data[0]}")
                    logging.warning(f"Real-data: {x}")
                    return True
            elif y_real[-1]==prediction_data[1]:
                x='-'
                if prediction_data[0]=='-':
                    logging.warning("PAIR")
                    real_data=y_real_ending
                    logging.warning(f"Prediction-data: {prediction_data[0]}")
                    logging.warning(f"Real-data: {x}")
                    return True
            else:
                x=0
                if prediction_data[0]==0:
                    logging.warning("DOWN")
                    real_data=y_real_ending
                    logging.warning(f"Prediction-data: {prediction_data[0]}")
                    logging.warning(f"Real-data: {x}")
                    return True
            logging.warning(f"Prediction-data: {prediction_data[0]}")
            logging.warning(f"Real-data: {x}")
            
            real_data=y_real_ending
            return False

    
if __name__ == "__main__":
    # scraping_data()
    # import time
    threading.Thread(target=scraping_data).start()
    app.run('0.0.0.0',port=5000,debug=1)
    # time.sleep(1)
    # while 1:
    #     if not count_stopping:
            
    #         if check_right_or_failed():
    #             logging.warning("WIN")
    #         else:
    #             logging.warning("LOSED")
    
        

            

        


