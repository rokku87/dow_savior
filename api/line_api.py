# api/line_api.py
from linebot import LineBotApi
from linebot.models import TextSendMessage, TemplateSendMessage, ConfirmTemplate, MessageAction

def send_message(channel_access_token, user_id, message):
    line_bot_api = LineBotApi(channel_access_token)
    if isinstance(message, (TextSendMessage, TemplateSendMessage)):
        line_bot_api.push_message(user_id, message)
    else:
        raise TypeError("Message must be either TextSendMessage or TemplateSendMessage")

def reply_message(token, reply_token, message_text):
    line_bot_api = LineBotApi(token)
    message = TextSendMessage(text=message_text)
    line_bot_api.reply_message(reply_token, message)
