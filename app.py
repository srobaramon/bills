import pandas as pd
from datetime import datetime, date, timedelta, time
import streamlit as st

@st.cache(allow_output_mutation=True)
def read_data(file):
    data_raw = pd.read_csv(file, header=None)
    data_raw.columns = ['caller', 'start','end']
    data = data_raw.copy()
    data['caller'] = data['caller'].astype(str)
    data['start'] = pd.to_datetime(data['start'], format='%m/%d/%Y %H:%M')
    data['end'] = pd.to_datetime(data['end'], format='%m/%d/%Y %H:%M')
    return data

@st.cache   
def handle_data(data, t1, t2):
    data['8hr'] = data['start'].apply(lambda x: datetime.combine(x.date(),t1))
    data['16hr'] = data['start'].apply(lambda x: datetime.combine(x.date(),t2))
    data['start_in_main'] = (data['8hr']<data['start'])&(data['16hr']>data['start'])
    data['end_in_main'] = (data['8hr']<data['end'])&(data['16hr']>data['end'])
    #IF BOTH IN MAIN TIME
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==True), 'main_time'] = data['end']-data['start']
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==True), 'other_time'] = timedelta(0)
    #IF BOTH NOT IN MAIN TIME
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==False), 'main_time'] = timedelta(0) 
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==False), 'other_time'] = data['end']-data['start']
    #IF START IN MAIN TIME AND END OTHER TIME
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==False), 'main_time'] = data['16hr']-data['start']
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==False), 'other_time'] = data['end']-data['16hr']
    #IF START IN OTHER TIME AND END IN MAIN TIME
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==True), 'main_time'] = data['end']-data['8hr']
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==True), 'other_time'] = data['8hr']-data['start']
    return data

@st.cache   
def calculate_costs(data, main_price, other_price):
    data['main_time_cost'] = data['main_time'].apply(lambda x: x.seconds/60*main_price)
    data['other_time_cost'] = data['other_time'].apply(lambda x: x.seconds/60*other_price)
    data['total_call_cost'] = data['main_time_cost'] + data['other_time_cost']
    total_month_sum = data['total_call_cost'].sum()
    return data, total_month_sum

@st.cache
def most_ferquent_caller(data):
    top_caller = data['caller'].describe().top
    top_caller = int(float(top_caller))
    return top_caller

def frontend():
    st.title('Bill Calculator')
    file = st.file_uploader('Upload Total Bill csv')
    sb = st.sidebar
    sb.subheader('Pricing Setup')
    cols = sb.columns(2)
    t1 = cols[0].time_input('Select Main Range from:', time(8,0))
    main_price = cols[0].number_input('Main Time Price czk',value=1.00)
    t2 = cols[1].time_input('Select Main Range to:', time(16,0))
    other_price = cols[1].number_input('Other Time Price czk', value=0.50)

    if file:
        data_raw = read_data(file)
        data_times = handle_data(data_raw, t1, t2)
        data_costs, total_month_sum = calculate_costs(data_times, main_price, other_price)
        top_caller = most_ferquent_caller(data_costs)
        st.subheader('Summary Table')
        st.write(data_costs[['main_time_cost','other_time_cost','total_call_cost']].describe())
        st.write(f'TOTAL MONTLY COST IS : **{total_month_sum}** czk')
        st.write(f'Most Frequent caller is : **{top_caller}**')

    else:
        st.warning('Please Upload file')

frontend()
