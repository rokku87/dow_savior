import os
import sys
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ConfirmTemplate, MessageAction, TextSendMessage
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from api.line_api import reply_message, send_message

app = Flask(__name__)
scheduler = BackgroundScheduler()
user_ids = set()

channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')
handler = WebhookHandler(channel_secret)

task_active = False
current_task = None
next_message_time = None

def check_and_send_task():
    global task_active, current_task, next_message_time
    now = datetime.now()
    if task_active and now >= next_message_time:
        for user_id in user_ids:
            send_task_message(user_id, current_task)
        next_message_time = now + timedelta(seconds=5)  # Adjust this for actual timing

@scheduler.scheduled_job('interval', seconds=5)
def scheduled_check_and_send_task():
    check_and_send_task()

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global task_active, current_task, next_message_time

    user_id = event.source.user_id if event.source.type in ['user', 'group'] else None
    if user_id:
        user_ids.add(user_id)

    if event.message.text == "救救启瑞" and not task_active:
        task_active = True
        current_task = "task1"
        next_message_time = datetime.now() + timedelta(seconds=5)
        reply_message(channel_access_token, event.reply_token, "任务启动。")
        send_task_message(user_id, current_task)
    elif event.message.text == "是" and task_active:
        next_task = {"task1": "task2", "task2": "task3", "task3": "task4", "task4": "task5"}
        current_task = next_task.get(current_task)
        if current_task:
            send_task_message(user_id, current_task)
    elif event.message.text == "否" and task_active:
        task_active = False
        current_task = None
        reply_message(channel_access_token, event.reply_token, "任务失败-启瑞还在轮回之中受难")
    elif event.message.text == "关闭" and task_active:
        task_active = False
        current_task = None
        next_message_time = None
        reply_message(channel_access_token, event.reply_token, "任务已停止。")

def send_task_message(user_id, task):
    global channel_access_token
    message_text = ""
    if task == "task1":
        message_text = "任務-協助啟瑞逃離華奴腐儒輪迴\n└任務1-啟瑞今天看房沒?(0/1)"
    elif task == "task2":
        message_text = "任務-協助啟瑞逃離華奴腐儒輪迴\n└任務1-啟瑞今天看房沒?(1/1)\n└─任務2-啟瑞今天付訂沒?(0/1)"
    elif task == "task3":
        message_text = "任務-協助啟瑞逃離華奴腐儒輪迴\n└任務1-啟瑞今天看房沒?(1/1)\n└─任務2-啟瑞今天付訂沒?(1/1)\n└──任務3-啟瑞今天整理沒?(0/1)"
    elif task == "task4":
        message_text = "任務-協助啟瑞逃離華奴腐儒輪迴\n└任務1-啟瑞今天看房沒?(1/1)\n└─任務2-啟瑞今天付訂沒?(1/1)\n└──任務3-啟瑞今天整理沒?(1/1)\n└───任務4-啟瑞今天叫搬家沒?(0/1)"
    elif task == "task5":
        message_text = "任務-協助啟瑞逃離華奴腐儒輪迴\n└任務1-啟瑞今天看房沒?(1/1)\n└─任務2-啟瑞今天付訂沒?(1/1)\n└──任務3-啟瑞今天整理沒?(1/1)\n└───任務4-啟瑞今天叫搬家沒?(1/1)\n└────任務5-啟瑞今天搬家沒?(0/1)"

    confirm_template = ConfirmTemplate(text=message_text, actions=[
        MessageAction(label="是", text="是"),
        MessageAction(label="否", text="否")
    ])
    template_message = TemplateSendMessage(alt_text='确认消息', template=confirm_template)
    send_message(channel_access_token, user_id, template_message)

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
