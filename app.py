import pandas as pd
from datetime import datetime, date, timedelta, time
import streamlit as st
from interactive_table import aggrid_interactive_table
from streamlit_pandas_profiling import st_profile_report
from pandas_profiling import ProfileReport

@st.cache(allow_output_mutation=True)
def read_data(file):
    data_raw = pd.read_csv(file, header=None)
    data_raw.columns = ['caller', 'start','end']
    data = data_raw.copy()
    data['caller'] = data['caller'].astype(str)
    data['start'] = pd.to_datetime(data['start'], format='%Y-%m-%d %H:%M:%S')
    data['end'] = pd.to_datetime(data['end'], format='%Y-%m-%d %H:%M:%S')
    return data

@st.cache   
def calculate_minutes(data, time_from, time_to):
    data['main_from'] = data['start'].apply(lambda x: datetime.combine(x.date(), time_from))
    data['main_to'] = data['start'].apply(lambda x: datetime.combine(x.date(), time_to))
    data['start_in_main'] = (data['main_from']<data['start']) & (data['main_to']>data['start'])
    data['end_in_main'] = (data['main_from']<data['end']) & (data['main_to']>data['end'])

    #IF BOTH IN MAIN TIME
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==True), 'main_time'] = data['end'] - data['start']
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==True), 'other_time'] = timedelta(0)

    #IF BOTH NOT IN MAIN TIME
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==False), 'main_time'] = timedelta(0) 
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==False), 'other_time'] = data['end']-data['start']

    #IF START IN MAIN TIME AND END OTHER TIME
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==False), 'main_time'] = data['main_to']-data['start']
    data.loc[(data['start_in_main']==True) & (data['end_in_main']==False), 'other_time'] = data['end']-data['main_to']

    #IF START IN OTHER TIME AND END IN MAIN TIME
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==True), 'main_time'] = data['end']-data['main_from']
    data.loc[(data['start_in_main']==False) & (data['end_in_main']==True), 'other_time'] = data['main_from']-data['start']
    data['total_time'] = data['end'] - data['start']
    return data

# @st.cache(allow_output_mutation=True)
def calculate_costs(data, main_price, other_price, top_caller):
    data['main_time_seconds'] = data['main_time'].apply(lambda x: x.seconds)
    data['other_time_seconds'] = data['other_time'].apply(lambda x: x.seconds)
    data['total_time_seconds'] = data['total_time'].apply(lambda x: x.seconds)

    data['main_time_cost'] = data['main_time_seconds'].apply(lambda x: x/60*main_price)
    data['other_time_cost'] = data['other_time_seconds'].apply(lambda x: x/60*other_price)
    # Set Frequent Caller price to zero 
    data.loc[data['caller']==top_caller, 'main_time_cost'] = 0
    data.loc[data['caller']==top_caller, 'other_time_cost'] = 0
    data['total_call_cost'] = data['main_time_cost'] + data['other_time_cost']
    total_month_sum = round(data['total_call_cost'].sum(), 2)
    data_all = data.copy()
    data_all.drop(['main_time','other_time', 'total_time'], axis=1, inplace=True)
    return data, total_month_sum, data_all

@st.cache
def most_ferquent_caller(data):
    top_caller = data['caller'].describe().top
    return top_caller

def frontend():
    st.title('Bill Calculator')
    file = st.file_uploader('Upload Total Bill csv')
    sb = st.sidebar
    sb.subheader('Pricing Setup')
    cols = sb.columns(2)
    time_from = cols[0].time_input('Select Main Range from:', time(8,0))
    main_price = cols[0].number_input('Main Time Price czk',value=1.00)
    time_to = cols[1].time_input('Select Main Range to:', time(16,0))
    other_price = cols[1].number_input('Other Time Price czk', value=0.50)

    if file:
        data_raw = read_data(file)
        data_times = calculate_minutes(data_raw, time_from, time_to)
        top_caller = most_ferquent_caller(data_raw)
        data_costs, total_month_sum, data_all = calculate_costs(data_times, main_price, other_price, top_caller)
    
        st.subheader('Summary Table')
        st.write(data_costs[['main_time_cost','other_time_cost','total_call_cost']].describe())
        st.write(f'TOTAL MONTLY COST IS : **{total_month_sum}** czk')
        st.write(f'Most Frequent caller is : **{top_caller}**')
        response = aggrid_interactive_table(data_all)
        st.dataframe(response['selected_rows'])

        if st.button('Run Analysis'):
            profile = ProfileReport(response.data)
            st_profile_report(profile)
    else:
        st.warning('Please Upload file')

frontend()
