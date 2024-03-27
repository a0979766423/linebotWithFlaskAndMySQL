from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import *

from flask_sqlalchemy import SQLAlchemy

import random
import os

db = SQLAlchemy()
app = Flask(__name__)

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://sql6694558:NWxU19Jim6@sql6.freemysqlhosting.net:3306/sql6694558"

db.init_app(app)

# Channel Access Token
line_bot_api = LineBotApi('Fa3jHjN4J/3n+i59rgcu04nzQ4l0wCz/uK2E/XCXpPuzsmjj0MXILc64ODH/0eDdMsR2gepARx/7TFRL0O3fexOgrkWQp/7M0J2gFTP3IQBFazjPTZQ1uCsNxBv2MvNwVyRjynVbWcH9yRzrIXRl9QdB04t89/1O/w1cDnyilFU=')
# Channel Secret
handler = WebhookHandler('1d5a261efe29d5d3099235de25f40a1c')

# 監聽所有來自 /callback 的 Post Request
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    
    # Check database connection
    try:
        with db.engine.connect() as connection:
            result = connection.execute("SELECT 1")
            app.logger.info("Database connection successful")
    except Exception as e:
        app.logger.error("Database connection failed: " + str(e))

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    input_text = event.message.text
    try:
        with db.engine.connect() as connection:
            result = connection.execute("SELECT test1 FROM test WHERE column_name = %s", (input_text,))
            response = result.fetchone()
            if response:
                message = TextSendMessage(text=response[0])
            else:
                message = TextSendMessage(text="Sorry, I couldn't find a response for that.")
            line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        app.logger.error("Database query error: " + str(e))
        message = TextSendMessage(text="An error occurred while processing your request.")
        line_bot_api.reply_message(event.reply_token, message)

import os
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
