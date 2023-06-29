import streamlit as st
import datetime
import joblib
import tensorflow as tf
import pandas
import time
from iqoptionapi.stable_api import IQ_Option
import numpy as np




def load_data(login):
        goal=selected_symbol
        size=30 #size=[1,5,10,15,30,60,120,300,600,900,1800,3600,7200,14400,28800,43200,86400,604800,2592000,"all"]
        maxdict=1
        print("start stream...")
        login.start_candles_stream(goal,size,maxdict)
        data = login.get_realtime_candles(goal,size)
        return data




def preprocess_data(data):
    data = pandas.DataFrame(data)
    data = data.transpose()
    X = data[['min','max','open','close','volume']]
    return X




def predict_exacute_order(login,symbol,data,amount):

    tfmodel = tf.keras.models.load_model('Tencerflow_modle_v0.0.2.h5')
    sklearn_ard = joblib.load('sklearn_ard_v1.joblib')


    predtf = tfmodel.predict(np.array(data).astype('float64'))
    sklearn_ardpred = sklearn_ard.predict(np.array(data).astype('float64'))
    st.write('pred' ,predtf)
    if  predtf[0] < data['close'].iloc[0] and sklearn_ardpred[0] < data['close'].iloc[0] :
        
        login.buy_digital_spot(symbol,amount,'put',1)
        st.write('sell')
        st.write(login.get_balance())
        
    elif  predtf[0] > data['close'].iloc[0] and sklearn_ardpred[0] > data['close'].iloc[0] :
        login.buy_digital_spot(symbol,amount,'call',1)
        st.write('buy')
        st.write(login.get_balance())
    else :
        st.write('hold')
        st.write(login.get_balance())





def get_symbols(day):
    if day.weekday() not in [5, 6]:  # Monday to Friday
        return ['EURUSD', 'GBPUSD', 'USDINR']
    else:  # Saturday and Sunday
        return ['EURUSD-OCT', 'GBPUSD-OTC']
    





today = datetime.date.today()
symbols = get_symbols(today)




# Set page title and favicon
st.set_page_config(page_title="AI Website Prototype", page_icon=":random:")

# Page layout
st.markdown("# GodAvtarm")
st.markdown("Welcome to our AI-powered website for Option Trading!")
st.markdown("---")

# Form filler 1
st.markdown("## Fill Iq Option Data")
email = st.text_input("Enter your email:")
password = st.text_input("Enter your password:")
account_type = st.selectbox("Account Type", ("PRACTICE", "REAL"))
amount =  st.number_input("Enter amount in rupees:", min_value=55, step=1)
selected_symbol = st.selectbox("Select an option:", (symbols))


    # Connect button
if st.button("Connect"):
    if email and password:
        login = IQ_Option(email, password)
        login.connect()
        
        if login:
            st.success("Connected to IQ Option API!")
            ld = load_data(login)
            data = preprocess_data(ld)

            while login.get_balance() > 200  :
                current_time = time.localtime()
                if current_time.tm_sec ==  25 :
                    if current_time.tm_min % 1 == 0:
                        
                        if login.get_balance() > 200 :
                            pred = predict_exacute_order(amount= amount,login= login,data= data,symbol=selected_symbol)
                            time.sleep(45)
                        else:
                            print('Your balance Less then 400')
                    else:
                        time.sleep(1)
                else:
    
                    time.sleep(1)
            
               
            else:
                st.error("Failed to connect to IQ Option API. Please check your credentials.")
    else:
        st.warning("Please enter your email and password.")


