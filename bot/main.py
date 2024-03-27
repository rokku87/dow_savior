import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration
from api.line_api import reply_message, send_message

app = Flask(__name__)
scheduler = BackgroundScheduler()
job = None  # 用于跟踪定时任务

user_ids = set()  # 存储互动过的用户的 userId

channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    # 检查事件是来自个人还是群组
    if event.source.type == 'user':
        id = event.source.user_id
    elif event.source.type == 'group':
        id = event.source.group_id
    else:
        id = None

    if id:
        user_ids.add(id)  # 假设 user_ids 用于存储个人和群组的 ID

    if event.message.text == "救救啟瑞":
        start_scheduled_task()
        reply_text = "任務啟動。"
    else:
        reply_text = "請輸入'救救啟瑞'以开始任务。"

    reply_message(channel_access_token, event.reply_token, reply_text, configuration)

def start_scheduled_task():
    global job
    if job is None:
        job = scheduler.add_job(send_confirmation_message, 'interval', minutes=1)
        if not scheduler.running:
            scheduler.start()

def send_confirmation_message():
    message_text = "任務-啟瑞逃離華奴腐儒輪迴\n任務一、啟瑞今天看房沒(0/1)\n是/否"
    for user_id in user_ids:
        send_message(channel_access_token, user_id, message_text)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        app.logger.info("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, use_reloader=False)
