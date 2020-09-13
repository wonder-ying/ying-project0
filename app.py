import pandas as pd
from threading import Thread
from flask import Flask,render_template,request,redirect
import simplejson as json
import requests
import datetime
import jinja2

from bokeh.embed import server_document, components 
from bokeh.layouts import column
from bokeh.models import ColumnDataSource, HoverTool, TextInput, CustomJS
from bokeh.io import curdoc
from bokeh.plotting import figure, output_file, show
from bokeh.server.server import Server
from bokeh.themes import Theme

app = Flask(__name__)

app.vars={}

@app.route('/')
def main():
   return redirect('/index')

@app.route('/index', methods=['GET'])
def index():
   return render_template('index.html')
    
@app.route('/graph', methods=['POST'])
def graph():
   # if request.method == 'POST':
   app.vars['symbol'] = request.form['symbol']

   API_URL = "https://www.alphavantage.co/query" 
   data = { "function": "TIME_SERIES_DAILY_ADJUSTED",
            "symbol": app.vars['symbol'],
            "outputsize" : "full",
            "datatype": "json",
            "apikey": "GH5U75JGWCE1C0C3" }
   response = requests.get(API_URL, data)
   response_json = response.json()

   df = pd.DataFrame.from_dict(response_json['Time Series (Daily)'], orient= 'index').sort_index(axis=1)
   df = df.rename(columns={ '1. open': 'Open', '2. high': 'High', '3. low': 'Low', '4. close': 'Close', '5. adjusted close': 'Adj Close', '6. volume': 'Volume', '7. dividend amount': 'Dividend Amount', '8. split coefficient': 'Split Coefficient'})
   df.reset_index(inplace=True)
   df['index'] = pd.to_datetime(df['index'])
   mask = (df['index'] >= '2020-01-01')
   df = df.loc[mask]
   df1 = df[[ 'index', 'Open', 'Close', 'Adj Close']]

   p = figure(plot_width=800 ,plot_height=800, x_axis_type="datetime")
   p.background_fill_color="#f5f5f5"
   p.grid.grid_line_color="white"
   p.title.text = 'Monthly Stock Data of %s' % app.vars['symbol'].upper()
   p.xaxis.axis_label = "Date and Month of 2020"
   p.yaxis.axis_label = "Price"
   p.axis.axis_line_color = None
   p.title.text_font = "Times"
   p.title.text_font_size = "20px"

   if request.form.get('Open'):
      p.line(df1['index'], df1['Open'], line_width=2, line_color='blue', legend_label='Open')

   if request.form.get('Close'):
      p.line(df1['index'], df1['Close'], line_width=2, line_color='green', legend_label='Close')

   # if request.form.get('Adj Close'):
   #    p.line(df1['index'], df1['Adj Close'], line_width=2, line_color='red')

   # p.add_tools(HoverTool(
   #    tooltips=[
   #       ( 'Date',   '@x{%F}'     ),
   #       ( 'Open',  '$@y{%0.2f}' ),
   #       ( 'Close',  '$@y{%0.2f}' ),
   #       ( 'Adj Close',  '$@y{%0.2f}' ),
   #    ],

   #    formatters={
   #       '@x'      : 'datetime',
   #       '@y'     : 'printf',
   #    },

   #    mode='vline'
   # ))

   script, div = components(p)
   return render_template('graph.html', script=script, div=div)

if __name__ == '__main__':
   app.run(port=33507)