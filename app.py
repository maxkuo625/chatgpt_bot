from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from linebot.exceptions import InvalidSignatureError
from config import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET, OPENAI_API_KEY
from memory_store import get_user_context, update_user_context
from openai import OpenAI
import os

app = Flask(__name__)
line_bot_api = LineBotApi(LINE_CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(LINE_CHANNEL_SECRET)

# 初始化新版 OpenAI 客戶端
client = OpenAI(api_key=OPENAI_API_KEY)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_id = event.source.user_id
    user_input = event.message.text

    # 更新使用者對話記憶
    update_user_context(user_id, {"role": "user", "content": user_input})
    messages = get_user_context(user_id)

    # 呼叫 OpenAI Chat API
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
        )
        reply = response.choices[0].message.content.strip()
        update_user_context(user_id, {"role": "assistant", "content": reply})
    except Exception as e:
        reply = "⚠️ 呼叫 AI 失敗：" + str(e)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply)
    )

if __name__ == "__main__":
    app.run()
