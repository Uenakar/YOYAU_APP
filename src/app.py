import os
from flask import Flask, render_template, request
from yoyaku import YoyakuModel
#import MeCab
from janome.tokenizer import Tokenizer
from bs4 import BeautifulSoup
import requests
from datetime import datetime
import logging
import pytz
import time

# スクリプトのあるディレクトリを取得
script_dir = os.path.dirname(os.path.abspath(__file__))

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__, 
            static_folder=os.path.join(script_dir, 'static'),
            template_folder=os.path.join(script_dir, 'templates'))

# Janomeのインスタンスを作成
tokenizer = Tokenizer()

# 環境変数からUSER_AGENTを取得、またはデフォルトを設定
USER_AGENT = os.environ.get('USER_AGENT', "Default User Agent")

# 他の設定やルートの定義など

def predict(text):
    #model_path = "C:\\Users\\user\\Desktop\\yoyaku_app\\src\\model_weights.pth"
    model_path = os.path.join(script_dir, 'model_weights.pth')
    summarizer = YoyakuModel(model_path)
    summary = summarizer.summarize(text)
    return summary

def tokenize(text):
    # Janomeを使用してテキストを分かち書き
    tokens = tokenizer.tokenize(text, wakati=True)
    return list(tokens)

def get_current_hour_jst():
    jst = pytz.timezone('Asia/Tokyo')
    current_time = datetime.now(jst)
    return current_time.hour    

def trim_text(text, max_length):
    if len(text) <= max_length:
        return text
    
    trimmed_text = text[:max_length].rsplit(' ', 1)[0]
    return trimmed_text + '...'

@app.route('/', methods=['GET', 'POST'])
def index():
    #hour = datetime.now().hour  # 現在の時間を取得
    hour = get_current_hour_jst()  # JSTの現在の時間を取得

    if request.method == 'POST':
        text = request.form.get('text_input')
        url = request.form.get('url_input')
        
        if text:
            trimmed_text = trim_text(text, 5000)
            summary = predict(trimmed_text)
            wakati_original_text = tokenize(trimmed_text)
            wakati_summary = tokenize(summary)
            return render_template('result.html', original_text=text, summary=summary, 
                                   wakati_original_text=wakati_original_text, wakati_summary=wakati_summary)
        elif url:
            time.sleep(2)  # 2秒待機        
            try:
                #headers = {
                    #"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36"
                #}

                headers = {
                    "User-Agent": USER_AGENT
                }        
                        
                response = requests.get(url, headers=headers)
                response.raise_for_status()  
            except requests.exceptions.HTTPError as e:
                logging.error(f"HTTP Error for URL: {url}, Status Code: {response.status_code}, Error: {e}")
                return render_template('error.html', message=f"HTTP Error fetching URL: {url}, Status Code: {response.status_code}")
            except requests.exceptions.RequestError as e:
                logging.error(f"Request Error for URL: {url}, Error: {e}")
                return render_template('error.html', message=f"Request Error fetching URL: {url}")
            except Exception as e:
                logging.error(f"Unexpected error: {e}")
                return render_template('error.html', message="An unexpected error occurred.")

            soup = BeautifulSoup(response.text, 'html.parser')
            text_content = soup.get_text()
            trimmed_text_content = trim_text(text_content, 5000)
            summary = predict(trimmed_text_content)
            wakati_original_text = tokenize(trimmed_text_content)
            wakati_summary = tokenize(summary)
            return render_template('result.html', original_text=trimmed_text_content, summary=summary, 
                                   wakati_original_text=wakati_original_text, wakati_summary=wakati_summary)

    return render_template('index.html', hour=hour)

if __name__ == "__main__":
    app.run(host='0.0.0.0')
