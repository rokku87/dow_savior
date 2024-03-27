from flask import Flask, request, abort
from linebot.v3.messaging import Configuration, MessagingApi
from linebot.v3.webhook import WebhookHandler  # 从 v3 命名空间导入
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

# 使用 v3 的类来配置 LINE Bot API
config = Configuration()  # 如果 Configuration 类有改变，请根据 v3 的文档来设置
line_bot_api = MessagingApi(configuration=config)  # 根据实际的 v3 用法来创建 API 客户端实例
handler = WebhookHandler(channel_secret)  # 确保这个也是 v3 的正确用法

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
