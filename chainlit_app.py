import chainlit as cl

@cl.on_chat_start
async def start():
    await cl.Message(content="Chainlit 伺服器已啟動！請輸入訊息與我對話。").send()

@cl.on_message
async def main(message: cl.Message):
    # 簡單的回應邏輯：回傳使用者輸入的內容
    response = f"你說了：{message.content}"
    await cl.Message(content=response).send()
