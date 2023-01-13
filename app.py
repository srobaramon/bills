import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, date, timedelta, time
MODE = st.set_page_config(page_title="BillCalculator",layout="wide")
class Call:
    def __init__(self, caller, start, end, main_time_from=time(8,0), main_time_to=time(16,0), bonus_minutes=5):
        self.caller = caller
        self.start = start
        self.end = end
        self.duration_m = self.get_duration_m()
        self.main_min, self.other_min, self.bonus_min = self.get_sorted_minutes(main_time_from, main_time_to, bonus_minutes)

    def get_duration_m(self):
        duration = self.end - self.start
        duration_m = -(-duration.seconds//60)
        return duration_m
    
    def get_sorted_minutes(self, main_time_from, main_time_to, bonus_minutes):
        main_min, other_min, bonus_min = 0,0,0
        minute_start = self.start
        actual_date = minute_start.date()
        main_from = datetime.combine(actual_date, main_time_from)
        main_to = datetime.combine(actual_date, main_time_to)
        for i in range(1, self.duration_m+1):
            # CALLS UNDER BONUS RATE MIN
            if i<=bonus_minutes: 
                if minute_start>=main_from and minute_start<main_to:
                    main_min +=1
                else:
                    other_min +=1
            # CALLS ABOVE BONUS RATE MIN
            else:
                bonus_min+=1
            # Another minute starts
            minute_start+=timedelta(minutes=1)
        return main_min, other_min, bonus_min


class Bill:
    def __init__(self, file, main_cost=1, other_cost=0.5, bonus_cost=0.2, main_time_from=8, main_time_to=16, bonus_minutes=5):
        data = self.read_bill(file)
        self.top_caller = data['caller'].describe().top
        self.data_full = self.get_full_data(data, main_cost, other_cost, bonus_cost, main_time_from, main_time_to, bonus_minutes)
        self.total_month_sum = self.get_total_sum(self.data_full)

    def read_bill(self, file):
        data_raw = pd.read_csv(file, header=None)
        data_raw.columns = ['caller', 'start','end']
        data = data_raw.iloc[:,:3]
        data['caller'] = data['caller'].astype(str)
        data['start'] = pd.to_datetime(data['start'], format='%Y-%m-%d %H:%M:%S')
        data['end'] = pd.to_datetime(data['end'], format='%Y-%m-%d %H:%M:%S')
        return data

    def get_full_data(self, data, main_cost, other_cost, bonus_cost, main_time_from, main_time_to, bonus_minutes):
        data['Calls'] = [Call(row.caller, row.start, row.end, main_time_from, main_time_to, bonus_minutes) for row in data.itertuples()]
        data['main_min'] = data['Calls'].apply(lambda x: x.main_min)
        data['other_min'] = data['Calls'].apply(lambda x: x.other_min)
        data['bonus_min'] = data['Calls'].apply(lambda x: x.bonus_min)
        data['total_min'] = data[['main_min','other_min','bonus_min']].sum(axis=1)
        data['main_min_cost'] = data['main_min']*main_cost
        data['other_min_cost'] = data['other_min']*other_cost
        data['bonus_min_cost'] = data['bonus_min']*bonus_cost
        data['total_cost'] = data[['main_min_cost','other_min_cost','bonus_min_cost']].sum(axis=1)
        # Apply most frequent caller
        data.loc[data['caller']==self.top_caller, 'total_cost'] = 0
        print(f'Most Frequent caller is : **{self.top_caller}**')
        data_full = data.copy()
        return data_full

    def get_total_sum(self, data_full):
        total_month_sum = round(data_full['total_cost'].sum(), 2)
        print(f'TOTAL MONTLY COST IS : **{total_month_sum}** czk')
        return total_month_sum

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
    bonus_rate_min = cols[0].number_input('Bonus minutes', value=5)
    bonus_rate_price = cols[1].number_input('Bonus minutes Price czk', value=0.20)
    if file:
        bill = Bill(file,
                main_cost=main_price,
                other_cost=other_price, 
                bonus_cost=bonus_rate_price, 
                main_time_from=time_from, 
                main_time_to=time_to, 
                bonus_minutes=bonus_rate_min
            )
        st.subheader(f'TOTAL MONTLY COST IS : **{bill.total_month_sum}** czk')
        st.subheader(f'Most Frequent caller is : **{bill.top_caller}**')
        st.dataframe(bill.data_full)
        fig = px.bar(bill.data_full, x="caller", y=["main_min_cost", "other_min_cost", "bonus_min_cost"], title="Cost Distribution")
        st.plotly_chart(fig)

frontend()
# '''
# # EXAMPLE
# bill1 = Bill(r'example_file\0-1672928432193.csv')
# bill2 = Bill(r'example_file\0-1672928469157.csv')
# bill3 = Bill(r'example_file\0-1672928469157.csv', main_cost=1.5, other_cost=0.75, bonus_cost=0.25, main_time_from=9, main_time_to=14, bonus_minutes=3)
# '''

