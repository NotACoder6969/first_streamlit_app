import streamlit as st
import pandas as pd
import numpy as np
#import snowflake.connector
import pickle
import xgboost
import xgboost as xgb
# import the required packages
from streamlit_card import card


st.set_page_config(page_title='INVEMP Tasty Bytes Group 5', page_icon='🍖🍕🍜')

st.sidebar.title("INVEMP: Inventory/Warehouse Management & Prediction on Sales per Menu Item")
st.sidebar.markdown("This web app allows you to explore the internal inventory of Tasty Bytes. You can explore these functions in the web app (Description of Page)")

tab1, tab2, tab3, tab4, tab5 = st.tabs(['Churn Prediction', 'Revenue Prediction', 'Prediction C', 'Prediction D', 'Prediction E'])
st.session_state.bar_chart_data = False

def tab1_predict(city,sales_level,frequency_level,history_level):

     required = ['TOTAL_PRODUCTS_SOLD', 'ORDER_AMOUNT', 'TOTAL_ORDERS',
       'MIN_DAYS_BETWEEN_ORDERS', 'MAX_DAYS_BETWEEN_ORDERS',
       'frequency_cluster', 'Customer_age_cluster', 'sale_cluster',
       'CITY_Boston', 'CITY_Denver', 'CITY_New York City', 'CITY_San Mateo',
       'CITY_Seattle']
     required = [i.lower() for i in required]
     
     x_test = [3.0, 30.0, 57.0, 1.0, 103.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

     x_test[required.index(f'city_{city.lower()}')] = 1.0
     if frequency_level=="Low-Frequency":
          x_test[required.index('frequency_cluster')] = 0.0
     elif frequency_level=="Medium-Frequency":
          x_test[required.index('frequency_cluster')] = 2.0
     elif frequency_level=="High-Frequency":
          x_test[required.index('frequency_cluster')] = 1.0

     if sales_level=="Low-Spending":
          x_test[required.index('sale_cluster')] = 1.0
     elif sales_level=="Average-Spending":
          x_test[required.index('sale_cluster')] = 2.0
     elif sales_level=="High-Spending":
          x_test[required.index('sale_cluster')] = 0.0

     if history_level=="New Customer":
          x_test[required.index('customer_age_cluster')] = 1.0
     elif history_level=="Standard Customer":
          x_test[required.index('customer_age_cluster')] = 0.0
     elif history_level=="Long-Standing Customer":
          x_test[required.index('customer_age_cluster')] = 2.0

     # x_test[required.index('sale_cluster')] = 2
     # #x_test[required.index('frequency_cluster')] = frequency_level
     # x_test[required.index('customer_age_cluster')] = 1

     with open("final_model.sav", 'rb') as f:
          model = pickle.load(f)

     print(x_test)
     y = model.predict(np.array([x_test]))[0]          # 0 -> not churn, 1 -> churn
     print('prediction:', y)
     if y == 0:
          result = 'The selected cluster of customers are predicted to not churn'
     else:
          result = 'The selected cluster of customers are predicted to churn'
     st.session_state['tab1_result'] = result

     df = pd.read_csv('2021.csv')
     print(df)

def get_bar_chart_df(city, frequency_level, sales_level, history_level):
    df = pd.read_csv('2021.csv')
                     
    df = df[df['CITY']==city]
    df = df[df['frequency_cluster']==frequency_level]
    df = df[df['sale_cluster']==sales_level]
    df = df[df['Customer_age_cluster']==history_level]

    menu = df.loc[:,['MENU_TYPE', 'CITY']].groupby('MENU_TYPE').count().sort_values('CITY').reset_index()
    menu = menu.rename(columns={'CITY': 'QTY'}, errors='ignore')
    return menu.iloc[[0,1,2], :], menu.iloc[[-3,-2,-1],:]

def get_total_revenue_of_cluster(city, frequency_level, sales_level, history_level):
    df = pd.read_csv('2021.csv')
    df = df[df['CITY']==city]
    df = df[df['frequency_cluster']==frequency_level]
    df = df[df['sale_cluster']==sales_level]
    df = df[df['Customer_age_cluster']==history_level]

    return df['ORDER_AMOUNT'].sum()

with tab1:

#      df_cleaned = dataset.loc[:, ['CITY', 'REGION', 'MENU_TYPE',
#        'TOTAL_PRODUCTS_SOLD', 'ORDER_AMOUNT', 'TOTAL_ORDERS',
#         'MIN_DAYS_BETWEEN_ORDERS', 'MAX_DAYS_BETWEEN_ORDERS',
#        'DAYS_TO_NEXT_ORDER','frequency_cluster','Customer_age_cluster','sale_cluster']]

     # Create three columns for the dropdown lists
     col1_t1, col2_t1, col3_t1,col4_t1 = st.columns(4)

    # Define the fixed choices for the dropdown lists
     cities = ['San Mateo', 'New York City', 'Boston', 'Denver', 'Seattle']
     spending_choices = ["Low-Spending", "Average-Spending", "High-Spending"]
     frequency_choices = ["Low-Frequency","Medium-Frequency", "High-Frequency"]
     cust_history = ["New Customer", "Standard Customer", "Long-Standing Customer"]

    # First dropdown list - Spending Level
     with col1_t1:
          city = st.selectbox("City", options=cities)

    # Second dropdown list - Frequency Level
     with col2_t1:
          sales_level = st.selectbox("Spending Frequency", options=spending_choices)

    # Third dropdown list - Age Level
     with col3_t1:
          frequency_level = st.selectbox("Frequency History", options=frequency_choices)

     with col4_t1:
          history_level = st.selectbox("Customer History", options=cust_history)

     if 'tab1_result' not in st.session_state:
          st.session_state['tab1_result'] = ''
     
     if 'tab1_insights' not in st.session_state:
          st.session_state['tab1_insights'] = ''

     button_return_value = st.button("Predict", on_click=tab1_predict, args=(city,sales_level,frequency_level,history_level))

    # Prediction section
     st.header("Prediction")
     result = st.session_state['tab1_result']
     print(result)
     st.write(st.session_state.get('tab1_result'))
     # st.text_area('', value=st.session_state.get('tab1_result'))
     # Measures
     st.header("Measures")
     st.write("Here are some steps that can be taken to prevent this cluster from churning:")


     if button_return_value:
          args = [city, 0, 0, 0]

          if frequency_level=="Low-Frequency": args[1] = 0
          elif frequency_level=="Medium-Frequency": args[1] = 2
          elif frequency_level=="High-Frequency": args[1] = 1

          if sales_level=="Low-Spending": args[2] = 1
          elif sales_level=="Average-Spending":  args[2] = 2
          elif sales_level=="High-Spending":  args[2] = 0

          if history_level=="New Customer":  args[3] = 1
          elif history_level=="Standard Customer": args[3] = 0
          elif history_level=="Long-Standing Customer": args[3] = 2

          total_revenue = get_total_revenue_of_cluster(*args)
          card(title=str(total_revenue), text='Total Revenue of Cluster')

          print(get_bar_chart_df(*args), args)

          st.bar_chart(get_bar_chart_df(*args)[0], x='MENU_TYPE', y='QTY')
          st.bar_chart(get_bar_chart_df(*args)[1], x='MENU_TYPE', y='QTY')


     st.text_area('', value=st.session_state.get('tab1_insights'))



