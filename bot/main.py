import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration
from api.line_api import reply_message, send_message  # 确保 send_message 函数是可用的

print("Current working directory:", os.getcwd())

app = Flask(__name__)
scheduler = BackgroundScheduler()
job = None  # 用于跟踪是否已经启动了定时任务

channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

def start_scheduled_task():
    global job
    if job is None:  # 确保只启动一次定时任务
        job = scheduler.add_job(send_confirmation_message, 'interval', minutes=1)  # 测试时每分钟发送一次
        if not scheduler.running:  # 如果调度器未运行，则启动调度器
            scheduler.start()

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    if event.message.text == "救救啟瑞":
        start_scheduled_task()
        reply_text = "任務啟動。"
    else:
        reply_text = "請輸入'救救啟瑞'已開始任務。"

    reply_message(channel_access_token, event.reply_token, reply_text, configuration)


def send_confirmation_message():
    user_id = 'YOUR_USER_OR_GROUP_ID'
    message_text = "任務-啟瑞逃離華奴腐儒輪迴\n任務一、啟瑞今天看房沒(0/1)\n是/否"
    send_message(channel_access_token, user_id, message_text, configuration)

scheduler = BackgroundScheduler()
scheduler.add_job(send_confirmation_message, 'interval', minutes=1)  # 测试时每分钟发送一次
scheduler.start()

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