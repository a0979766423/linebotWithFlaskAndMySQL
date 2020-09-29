from flask import Flask, request, abort
from flaskext.mysql import MySQL
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import *
import random
import os

mysql = MySQL()
app = Flask(__name__)

# MySQL configurations
app.config['MYSQL_DATABASE_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_DATABASE_PORT'] = 3306
app.config['MYSQL_DATABASE_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_DATABASE_PASSWORD'] = os.environ.get('DB_PASSWORD')
app.config['MYSQL_DATABASE_DB'] = os.environ.get('DB_SCHEMA')
mysql.init_app(app)

# Channel Access Token
line_bot_api = LineBotApi('N6EH/sRKbfIQO6moywQ11ZDhhu4tLp2Vq8KZLeQeXojim+jfkdVHCdbuSRy4Bh+ZzXF/sGH4Q1ruqdxVFd39/6GA3uf4pF2hzfq9msmKHjnD1HTC5Xyz7LjatSO2zxzgEtXAz0ZqYT3Kk5ih0m315QdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('2c03d2503de5fa94a58018c4857d4499')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    message = TextSendMessage(text=event.message.text)
    line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
