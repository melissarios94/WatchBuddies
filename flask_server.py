from flask import Flask, request
import subprocess
import os

app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == 'POST':
        os.system('kill $(cat ./pidfile)')
        os.system('git pull')
        subprocess.Popen(['python3', './WatchBuddies.py'])
        return '', 200
    else:
        return '', 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
