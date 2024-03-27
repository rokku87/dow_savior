from flask import Flask

app = Flask(__name__)

@app.route('/health')
def health():
    return 'OK'

@app.route('/webhook', methods=['POST'])
def webhook():
    # 處理 LINE Bot Platform 的 Webhook 請求
    return 'OK'

if __name__ == '__main__':
    app.run()
