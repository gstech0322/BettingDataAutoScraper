from flask import Flask, render_template
import pandas as pd
import time
# from main import Scraper
app = Flask(__name__)


@app.route('/')
def index():
    df = pd.read_csv('data.csv')
    data = df.values
    return render_template('index.html', data=data)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=8000, debug=True)
 