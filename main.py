from flask import Flask, request, abort
from linebot import (
    LineBotApi,
    WebhookHandler
)
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
import os

app = Flask(__name__)

# 获取环境变量
channel_access_token = os.getenv('CHANNEL_ACCESS_TOKEN')
channel_secret = os.getenv('CHANNEL_SECRET')

# 确保环境变量正确设置
if channel_access_token is None or channel_secret is None:
    print("CHANNEL_ACCESS_TOKEN or CHANNEL_SECRET is not set")
    exit(1)

# 初始化 LINE Bot API
line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    reply_text = "您好，这是机器人的回应"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

@app.route("/health")
def health_check():
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
