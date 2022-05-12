"""
Allows Uptime Robot to periodically connect to the bot's replit host, which keeps
the repository awake continuously.
"""
from threading import Thread

from flask import Flask


app = Flask("")


@app.route("/")
def home() -> str:
    return "Hello. I am alive!"


def run() -> None:
    app.run(host="0.0.0.0", port=8080)


def keep_alive() -> None:
    t = Thread(target=run)
    t.start()
