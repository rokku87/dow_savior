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
source_type = None  # 新增变量来存储触发任务的来源类型

def auto_start_task():
    global task_active, current_task, next_message_time
    if not task_active:
        task_active = True
        current_task = "task1"
        next_message_time = datetime.now() + timedelta(seconds=5)  # 调整为实际时间间隔
        for user_id in user_ids:
            send_task_message(user_id, current_task)

def auto_stop_task():
    global task_active, current_task, next_message_time
    if task_active:
        task_active = False
        current_task = None
        next_message_time = None
        # 这里可以添加发送任务自动停止的消息

@scheduler.scheduled_job('cron', hour=12)
def scheduled_start_task():
    auto_start_task()

@scheduler.scheduled_job('cron', hour=0)
def scheduled_stop_task():
    auto_stop_task()

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global task_active, current_task, next_message_time, user_ids, source_type

    source_id = event.source.user_id if event.source.type == 'user' else event.source.group_id
    source_type = event.source.type

    if source_id:
        user_ids.add(source_id)

    if event.message.text == "救救啟瑞" and not task_active:
        task_active = True
        current_task = "task1"
        next_message_time = datetime.now() + timedelta(seconds=5)
        reply_message(channel_access_token, event.reply_token, "協助啟瑞逃離華奴腐儒任務，啟動。")
        send_task_message(source_id, current_task)
    elif event.message.text == "是" and task_active:
        next_task = {"task1": "task2", "task2": "task3", "task3": "task4", "task4": "task5"}
        current_task = next_task.get(current_task)
        if current_task:
            send_task_message(source_id, current_task)
        else:
            task_active = False  # 任务5完成后，标记任务为不活跃
            reply_message(channel_access_token, event.reply_token, "任務成功！")
    elif event.message.text == "否" and task_active:
        task_active = False
        current_task = None
        reply_message(channel_access_token, event.reply_token, "任務失敗-啟瑞仍在輪迴之中受難")
    elif event.message.text == "關閉" and task_active:
        task_active = False
        current_task = None
        next_message_time = None
        reply_message(channel_access_token, event.reply_token, "任務停止。")

def send_task_message(target_id, task):
    global channel_access_token, source_type
    # 任务信息留空，您可以根据需要填写
    message_text = "..."

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
    template_message = TemplateSendMessage(alt_text='確認消息', template=confirm_template)

    if source_type == 'user':
        send_message(channel_access_token, target_id, template_message)
    elif source_type == 'group':
        send_message(channel_access_token, target_id, template_message)

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
