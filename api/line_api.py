# api/line_api.py
from linebot.models import TextSendMessage
from linebot.v3.messaging import ApiClient, MessagingApi, ReplyMessageRequest, TextMessage
from linebot.models import TextSendMessage

def reply_message(token, reply_token, message_text, config):
    with ApiClient(config) as api_client:
        line_bot_api = MessagingApi(api_client)
        reply_request = ReplyMessageRequest(
            reply_token=reply_token,
            messages=[TextMessage(text=message_text)]
        )
        line_bot_api.reply_message_with_http_info(reply_request)


def send_message(channel_access_token, user_id, message_text, configuration):
    with ApiClient(configuration) as api_client:
        line_bot_api = MessagingApi(api_client)
        message = TextSendMessage(text=message_text)  # 创建文本消息对象
        line_bot_api.push_message(user_id, [message])  # 注意：第二个参数是消息对象的列表