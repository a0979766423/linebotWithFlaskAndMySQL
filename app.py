from flask import Flask, request, abort
from flask_sqlalchemy import SQLAlchemy
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import TextMessage, TextSendMessage, MessageEvent
from sqlalchemy import text
from apscheduler.schedulers.background import BackgroundScheduler
import os

# 初始化 Flask 和資料庫
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+pymysql://sql6700120:RqB7UN23sf@sql6.freemysqlhosting.net:3306/sql6700120"
db = SQLAlchemy(app)

# 初始化 Line Bot
line_bot_api = LineBotApi('Fa3jHjN4J/3n+i59rgcu04nzQ4l0wCz/uK2E/XCXpPuzsmjj0MXILc64ODH/0eDdMsR2gepARx/7TFRL0O3fexOgrkWQp/7M0J2gFTP3IQBFazjPTZQ1uCsNxBv2MvNwVyRjynVbWcH9yRzrIXRl9QdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('1d5a261efe29d5d3099235de25f40a1c')

# 設定定時任務
scheduler = BackgroundScheduler()
scheduler.add_job(func=check_database_updates, trigger="interval", minutes=0.5)  # 每 30 分鐘執行一次
scheduler.start()

# 定義定時任務函式
def check_database_updates():
    try:
        sql_cmd = text("""SELECT number FROM test""")
        query_data = db.session.execute(sql_cmd)
        response = query_data.fetchone()
        if response:
            message = TextSendMessage(text=f"Database update detected: {response[0]}")
            line_bot_api.broadcast(message)  # 向所有使用者發送訊息
    except Exception as e:
        print("An error occurred while checking database updates:", str(e))

# 處理 Line Bot 的 webhook
@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

# 處理訊息
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    try:
        sql_cmd = text("""SELECT number FROM test""")
        query_data = db.session.execute(sql_cmd)
        response = query_data.fetchone()
        if response:
            message = TextSendMessage(text=event.message.text + '   ' + str(response[0]))
        else:
            message = TextSendMessage(text="Sorry, I couldn't find a response for that.")
        line_bot_api.reply_message(event.reply_token, message)
    except Exception as e:
        print("An error occurred while processing message:", str(e))
        message = TextSendMessage(text="An error occurred while processing your request.")
        line_bot_api.reply_message(event.reply_token, message)

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
