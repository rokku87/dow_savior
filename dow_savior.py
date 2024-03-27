from flask import Flask, request, abort
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    TextMessage
)
from linebot.v3.webhook import WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError

app = Flask(__name__)

line_bot_api = Configuration('ufdDe3WCWTcMV7yIQmjTTKKGt8UlWpnZi+sOBrabUwkIs6QoxJnhALI1i1aU4hLxtVEdohVNvO/zRaUWEQCcJN4uz3Nw5zldfsgQKKSLyTbfYz4GcXneFk2bjZ4520Sz+fl9g78vYCgNbyf/RcwbpAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('7582ea5da01404fa64dbfaec80867cbd')

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
    reply_text = "您好，這是機器人的回應"
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

if __name__ == "__main__":
    app.run()
