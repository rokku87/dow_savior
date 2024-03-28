import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ConfirmTemplate, MessageAction, TextSendMessage
from flask import Flask, request, abort
from apscheduler.schedulers.background import BackgroundScheduler
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration
from api.line_api import reply_message, send_message

app = Flask(__name__)
scheduler = BackgroundScheduler()
user_ids = set()
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')
handler = WebhookHandler(channel_secret)
configuration = Configuration(access_token=channel_access_token)

task_active = False
current_task = None
next_message_time = None

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global task_active, next_message_time, current_task

    user_id = event.source.user_id if event.source.type in ['user', 'group'] else None
    if user_id:
        user_ids.add(user_id)

    text = event.message.text
    if text == "救救啟瑞" and not task_active:
        start_task(user_id)
    elif text == "是" and task_active:
        proceed_task(user_id)
    elif text == "否" and task_active:
        fail_task(user_id)
    elif text == "關閉" and task_active:
        stop_task(user_id)

def start_task(user_id):
    global task_active, next_message_time, current_task
    task_active = True
    current_task = "task1"
    next_message_time = datetime.now() + timedelta(seconds=5)
    reply_message(channel_access_token, event.reply_token, "任務啟動。")
    send_task_message(current_task)

def proceed_task(user_id):
    global current_task
    if current_task == "task1":
        current_task = "task2"
        send_task_message(current_task)

def fail_task(user_id):
    global task_active, current_task
    task_active = False
    current_task = None
    reply_message(channel_access_token, event.reply_token, "任務失敗-啟瑞還在輪迴之中受難")

def stop_task(user_id):
    global task_active, current_task, next_message_time
    task_active = False
    current_task = None
    next_message_time = None
    reply_message(channel_access_token, event.reply_token, "任務已停止。")

def send_task_message(task):
    global next_message_time
    message_text = ""
    if task == "task1":
        message_text = "任務-啟瑞逃離華奴腐儒輪迴\n└─任務一、啟瑞今天看房沒?(0/1)"
    elif task == "task2":
        message_text = "任務-啟瑞逃離華奴腐儒輪迴\n└─任務二、啟瑞今天付訂沒?(0/1)"

    for user_id in user_ids:
        confirm_template = ConfirmTemplate(text=message_text, actions=[MessageAction(label="是", text="是"), MessageAction(label="否", text="否")])
        template_message = TemplateSendMessage(alt_text='確認訊息', template=confirm_template)
        send_message(channel_access_token, user_id, template_message)
    next_message_time = datetime.now() + timedelta(seconds=5)

if not scheduler.running:
    scheduler.start()


##-----------------------------------------------------這邊不動---------------------------------------------------------
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
