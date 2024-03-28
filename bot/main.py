import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from datetime import datetime, timedelta
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ConfirmTemplate, MessageAction, TextSendMessage
from flask import Flask, request, abort
from linebot.v3.webhook import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import MessageEvent, TextMessageContent
from linebot.v3.messaging import Configuration
from api.line_api import reply_message, send_message

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

app = Flask(__name__)

user_ids = set()  # 存储互动过的用户的 userId

channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')
configuration = Configuration(access_token=channel_access_token)
handler = WebhookHandler(channel_secret)

task_active = False
next_message_time = None

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    global task_active, next_message_time

    if event.source.type == 'user':
        user_id = event.source.user_id
    elif event.source.type == 'group':
        user_id = event.source.group_id
    else:
        user_id = None

    if user_id:
        user_ids.add(user_id)

    if event.message.text == "救救啟瑞" and not task_active:
        task_active = True
        next_message_time = datetime.now() + timedelta(seconds=5)
        reply_text = "任務啟動。"
        reply_message(channel_access_token, event.reply_token, reply_text)

        # 立即發送任務一的確認訊息
        message_text = "任務-啟瑞逃離華奴腐儒輪迴\n└─任務一、啟瑞今天看房沒?(0/1)"
        confirm_template = ConfirmTemplate(
            text=message_text,
            actions=[
                MessageAction(label="是", text="是"),
                MessageAction(label="否", text="否")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='確認訊息', template=confirm_template
        )
        send_message(channel_access_token, user_id, template_message)
        
    elif event.message.text == "否" and task_active:
        task_active = False
        reply_text = "任務失敗-啟瑞還在輪迴之中受難"
        reply_message(channel_access_token, event.reply_token, reply_text)
    elif event.message.text == "關閉" and task_active:
        task_active = False
        next_message_time = None
        reply_text = "任務已停止。"
        reply_message(channel_access_token, event.reply_token, reply_text)
    elif task_active and datetime.now() >= next_message_time:
        message_text = "任務-啟瑞逃離華奴腐儒輪迴\n└任務一、啟瑞今天看房沒?(0/1)"
        confirm_template = ConfirmTemplate(
            text=message_text,
            actions=[
                MessageAction(label="是", text="是"),
                MessageAction(label="否", text="否")
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='確認訊息', template=confirm_template
        )
        for user_id in user_ids:
            send_message(channel_access_token, user_id, template_message)
        next_message_time = datetime.now() + timedelta(seconds=5)
    elif not task_active:
        reply_text = "請輸入'救救啟瑞'以開始任務。"
        reply_message(channel_access_token, event.reply_token, reply_text)


##這邊不動
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
