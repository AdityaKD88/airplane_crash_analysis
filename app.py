import json
import plotly
import plotly.express as px
import numpy as np
import pandas as pd
from flask import Flask, render_template
app = Flask(__name__)

def load_data(filepath):
    df = pd.read_csv(filepath)
    df.Location.replace(np.nan, 'Unknown', inplace= True)
    df.Operator.replace(np.nan, 'Unknown', inplace= True)
    df.Route.replace(np.nan, 'Unknown', inplace= True)
    df.Type.replace(np.nan, 'Unknown', inplace= True)
    df['Time'] = df['Time'].fillna('00:00')
    df.dropna(inplace= True)
    df['Time'] = df['Time'].str.replace('c: ', '')
    df['Time'] = df['Time'].str.replace('c:', '')
    df['Time'] = df['Time'].str.replace('c', '')
    df['Time'] = df['Time'].str.replace('12\'20', '12:20')
    df['Time'] = df['Time'].str.replace('18.40', '18:40')
    df['Time'] = df['Time'].str.replace('0943', '09:43')
    df['Time'] = df['Time'].str.replace('22\'08', '22:08')
    df['Time'] = df['Time'].str.replace('114:20', '00:00')
    df['Ground'] = df['Aboard'] - df['Fatalities']
    df['DateTime'] = df['Date'] + ' ' + df['Time']
    df['DateTime'] = pd.to_datetime(df['DateTime'])
    return df
df=load_data('Airplane_Crashes_and_Fatalities_Since_1908.csv')

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/accident')
def accident():
    Temp = df.groupby(df.DateTime.dt.year)[['Date']].count()
    Temp = Temp.rename(columns={"Date": "Count"})
    fig1 = px.line(df,x=Temp.index,y=Temp.Count, title='Yearly Accidents',
                labels={
                    'x':'Year',
                    'y':'Accident Count'
                }, markers=True)
    graph1 = json.dumps(fig1, cls=plotly.utils.PlotlyJSONEncoder)

    Temp2 = df.groupby(df.DateTime.dt.month)[['Date']].count()
    x = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    fig2 = px.bar(df,x=x,y=Temp2.Date, title='Monthly Accidents',
                color=x,
                labels={
                    'x':'Month',
                    'y':'Accident Count'
                })
    graph2 = json.dumps(fig2, cls=plotly.utils.PlotlyJSONEncoder)

    Temp3 = df.groupby(df.DateTime.dt.weekday)[['Date']].count()
    x1 = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    fig3 = px.bar(df,x=x1,y=Temp3.Date, title='Weekly Accidents',
                color=x1,
                labels={
                    'x':'Day of Week',
                    'y':'Accident Count'
                })
    graph3 = json.dumps(fig3, cls=plotly.utils.PlotlyJSONEncoder)

    Temp4 = df[df.DateTime.dt.hour != 0].groupby(df.DateTime.dt.hour)[['Date']].count()
    fig4 = px.bar(df,x=Temp4.index,y=Temp4.Date, title='Hourly Accidents',
                color=Temp4.index,
                labels={
                    'x':'Hour',
                    'y':'Accident Count'
                })
    graph4 = json.dumps(fig4, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('accident.html',graph1=graph1,graph2=graph2,graph3=graph3,graph4=graph4)

@app.route('/fatality')
def fatality():
    years = df['DateTime'].dt.year
    fig5 = px.scatter(df,y=df['Fatalities'],x=years,
                title='Fatalities during different years',color=years,
                height=600, labels={
                    'x':'Year',
                    'y':'Fatalities count'
                })
    graph5 = json.dumps(fig5, cls=plotly.utils.PlotlyJSONEncoder)

    months = df['DateTime'].dt.month
    months=months.replace({1:'Jan',2:'Feb',3:'March',4:'April',5:'May',6:'June',7:'July',8:'Aug',9:'Sept',10:'Oct',11:'Nov',12:'Dec'})
    fig6 = px.histogram(df,y=df['Fatalities'],x=months,
                title='Fatalities during different months',color=months,
                labels={'x':'Month'})
    graph6 = json.dumps(fig6, cls=plotly.utils.PlotlyJSONEncoder)

    week = df['DateTime'].dt.weekday
    week=week.replace({0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'})
    fig7 = px.histogram(df,y=df['Fatalities'],x=week,
                title='Fatalities during different weeks',color=week,
                labels={'x':'Day of Week'})
    graph7 = json.dumps(fig7, cls=plotly.utils.PlotlyJSONEncoder)

    day = df['DateTime'].dt.day
    fig8 = px.histogram(df,y=df['Fatalities'],x=day,
                title='Fatalities during different days',color=day,
                labels={'x':'Day'})
    graph8 = json.dumps(fig8, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('fatality.html',graph5=graph5,graph6=graph6,graph7=graph7,graph8=graph8)
  
@app.route('/sector')
def sector():
    df.loc[df['Operator'].str.contains('Military'), 'Sector'] = 'Military'
    df.loc[(df['Operator'].str.contains('Air')) & (~df['Operator'].str.contains('Military')), 'Sector'] = 'Civil'
    df.loc[(df['Operator'].str.contains('Aero') & (~df['Operator'].str.contains('Military'))), 'Sector'] = 'Civil'
    df.loc[df['Operator'].str.contains('Mail'), 'Sector'] = 'Mail Service'
    df.loc[df['Operator'].str.contains('Private'), 'Sector'] = 'Private'
    df.loc[df['Sector']==False, 'Sector'] = 'Civil'
    sector = df.groupby('Sector')[['Fatalities']].sum().reset_index()
    fig9 = px.pie(sector,names= sector['Sector'],values=sector['Fatalities'],title='Percentage of fatality per sector')
    graph9 = json.dumps(fig9, cls=plotly.utils.PlotlyJSONEncoder)

    fig10 = px.bar(sector,x= sector['Sector'],y=sector['Fatalities'],
                title='Fatalities in each sector',
                labels={'x':'Sector',
                        'y':'No. of Fatalities'})
    graph10 = json.dumps(fig10, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('sector.html',graph9=graph9,graph10=graph10)

@app.route('/ratio')
def ratio():
    Fatalities = df.groupby(df.DateTime.dt.year).sum()
    Fatalities['Proportion'] = Fatalities['Fatalities'] / Fatalities['Aboard']
    fig11 = px.line(Fatalities,x=Fatalities.index,y='Proportion',title='Fatality ratio by year',
              labels={
                  'x':'Year',
                  'y':'Ratio'
              }, markers=True)
    graph11 = json.dumps(fig11, cls=plotly.utils.PlotlyJSONEncoder)

    fig12 = px.line(Fatalities,x=Fatalities.index,y=['Aboard','Fatalities'],
              title='Aboard Vs Fatality',
              labels={
                  'x':'Year',
                  'y':'Fatality Count'
              }, markers=True)
    graph12 = json.dumps(fig12, cls=plotly.utils.PlotlyJSONEncoder)
    return render_template('ratio.html',graph11=graph11,graph12=graph12)

if __name__ == '__main__':
  app.run(host='127.0.0.1', port=8000, debug=True)