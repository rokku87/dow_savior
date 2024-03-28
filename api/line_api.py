# api/line_api.py
from linebot import LineBotApi
from linebot.models import TemplateSendMessage, ConfirmTemplate, MessageAction

def send_message(channel_access_token, user_id, message):
    line_bot_api = LineBotApi(channel_access_token)
    line_bot_api.push_message(user_id, message)

# 如果還需要回覆消息的功能，可以保留這個函數
def reply_message(token, reply_token, message_text, config):
    line_bot_api = LineBotApi(token)
    message = TemplateSendMessage(
        alt_text='回覆消息',
        template=ConfirmTemplate(
            text=message_text,
            actions=[
                MessageAction(label='是', text='是'),
                MessageAction(label='否', text='否')
            ]
        )
    )
    line_bot_api.reply_message(reply_token, message)
