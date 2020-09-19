from flask import Flask, render_template, request, redirect, abort, Response
import requests
import simplejson as json
#import datetime
import jinja2
import pandas as pd

from bokeh.embed import server_document, components 
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, TextInput, CustomJS
from bokeh.io import curdoc
from bokeh.plotting import figure, output_file, show
from bokeh.server.server import Server

app = Flask(__name__)

app.vars={}

@app.route('/')
@app.route('/index')
def index():
   return render_template('index.html')

@app.route('/graph', methods=['POST'])
def graph():
   app.vars['symbol'] = request.form['symbol']

   API_URL = "https://www.alphavantage.co/query"
   data = { "function": "TIME_SERIES_DAILY_ADJUSTED",
             "symbol": app.vars['symbol'],
             "apikey": "UBSVT7NO385KCUNM",
             "outputsize": "full",
             "datatype": "json"}
   r = requests.get(API_URL, data)
   r_json = r.json()

   # Import data as Pandas df
   df = pd.DataFrame.from_dict(r_json['Time Series (Daily)'], orient='index').sort_index(axis=1)
   df.reset_index(inplace = True)
   df = df.rename(columns={ 'index': 'Date','1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. adjusted close': 'Adjusted Close', '6. volume': 'Volume', '7. dividend amount': 'Dividend Amount', '8. split coefficient': 'Split Coefficient'})
   df['Date'] = pd.to_datetime(df['Date'])
   df1 = df.loc[df.Date>='2018-01-01', ['Date', 'Open', 'Close', 'Adjusted Close']]
   df1 = df1.astype({'Open': 'float64', 'Close': 'float64', 'Adjusted Close': 'float64'})

   # Plot the graph in Bokeh
   curdoc().clear()
   p = figure(x_axis_type="datetime", plot_width=1200, plot_height=600, title='Stock Price Tracking', toolbar_location="below")
   p.title.text = 'Daily Stock Price Tracking of %s'  %app.vars['symbol'].upper()
   p.xaxis.axis_label = "Date and Year"
   p.yaxis.axis_label = "Stock Price"
   p.title.text_font_size = "20px"
   
   if request.form.get('Open'):
      p.line(df1['Date'], df1['Open'], line_width=3, line_color='blue', alpha=0.5, legend_label='Open')

   if request.form.get('Close'):
      p.line(df1['Date'], df1['Close'], line_width=3, line_color='green', alpha=0.5, legend_label='Close')
   
   if request.form.get('Adjusted Close'):
      p.line(df1['Date'], df1['Adjusted Close'], line_width=3, line_color='orange', alpha=0.5, legend_label='Adjusted Close')
    

   p.add_tools(HoverTool(
     tooltips=[
        ( 'Date',   '@x{%F}'     ),
        ( 'Price',  '$@y{%0.2f}' )
     ],

     formatters={
        '@x'      : 'datetime',
        '@y'     : 'printf',
     },

     mode='mouse'
   ))

   script, div = components(p)
   return render_template('graph.html', script=script, div=div)



if __name__ == '__main__':
  app.run(port=5000)
