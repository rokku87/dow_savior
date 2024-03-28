# api/line_api.py
from linebot import LineBotApi
from linebot.models import TextSendMessage,TemplateSendMessage, ConfirmTemplate, MessageAction
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage

def reply_message(token, reply_token, message_text, config):
    with ApiClient(config) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_request = ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=message_text)]
        )
        line_bot_api.reply_message_with_http_info(reply_request)


def send_message(channel_access_token, user_id, message_text):
    line_bot_api = LineBotApi(channel_access_token)

    # 創建確認模板消息
    confirm_template_message = TemplateSendMessage(
        alt_text='任務確認',  # 用於無法顯示模板消息的情況
        template=ConfirmTemplate(
            text=message_text,
            actions=[
                MessageAction(label='是', text='是'),
                MessageAction(label='否', text='否')
            ]
        )
    )
    line_bot_api.push_message(user_id, confirm_template_message)
