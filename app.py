from flask import Flask, render_template, request, redirect
import requests
import simplejson as json
import numpy as np
import pandas as pd
import bokeh
from bokeh.plotting import figure, show
from bokeh.embed import components
bv = bokeh.__version__


app = Flask(__name__)
app.vars={}
feat = ['Open','Close','Adjusted Open','Adjusted Close']

@app.route('/')
def main():
    return redirect('/index')

# set up the index page where user types in ticker and selects price type
@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    else:
        #return 'request.method was not a GET!'
        app.vars['ticker'] = request.form['ticker'].upper()
        app.vars['select'] = [feat[i] for i in range(4) if feat[i] in request.form.values()]
        return redirect('/plot')

# download the stock price data and make plot using Bokeh
@app.route('/plot',methods=['GET','POST'])
def plot():
    url = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES?ticker='+app.vars['ticker']+'&qopts.columns=date,open,close,adj_open,adj_close&api_key=TPgzV6Ncqutqdr1YEff2' 
    data = requests.get(url)
    data_formatted = data.json()
    col = data_formatted['datatable']['columns']
    columns = list(col[i]['name'] for i in range(0,len(col)))
    stock_data = data_formatted['datatable']['data'][-30:]
    stock_df = pd.DataFrame(stock_data, columns = columns)
    
    p = figure(width=800, height=500, x_axis_type="datetime")
    x = np.array(stock_df['date'],dtype=np.datetime64)
    if 'Open' in app.vars['select']: 
        y = np.array(stock_df['open'])
        p.circle(x,y,size=4,color='navy',alpha=0.4,legend='Open')
        p.line(x,y,color='navy',alpha=0.4)
    if 'Close' in app.vars['select']:
        y = np.array(stock_df['close'])
        p.circle(x,y,size=4,color='green',alpha=0.4,legend='Close')
        p.line(x,y,color='green',alpha=0.4)
    if 'Adjusted Open' in app.vars['select']:
        y = np.array(stock_df['adj_open'])
        p.circle(x,y,size=4,color='cyan',alpha=0.4,legend='Adjusted Open')
        p.line(x,y,color='cyan',alpha=0.4)
    if 'Adjusted Close' in app.vars['select']:
        y = np.array(stock_df['adj_close'])
        p.circle(x,y,size=4,color='black',alpha=0.4,legend='Adjusted Close')
        p.line(x,y,color='black',alpha=0.4)

    p.title.text = "Stock Price during the Past 30 Trading Days"
    p.legend.location = "top_left"
    p.grid.grid_line_alpha=0
    p.xaxis.axis_label = 'Date'
    p.xaxis.axis_label_text_font_size = '14pt'
    p.xaxis.major_label_text_font_size = '14pt'
    p.yaxis.axis_label = 'Stock Price'
    p.yaxis.axis_label_text_font_size = '14pt'
    p.yaxis.major_label_text_font_size = '14pt'
    p.ygrid.band_fill_color="darkgrey"
    p.ygrid.band_fill_alpha = 0.2
    
    script,div = components(p) 
    return render_template('plot.html',bv=bv, ticker=app.vars['ticker'],script=script,div=div)

if __name__ == '__main__':
  app.run(port=33507)
