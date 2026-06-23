# sudo apt update
# sudo apt install python3-pip
# pip install pywebview
from pathlib import Path

import webview


def main():
    webview.create_window(
        "simple text",
        url=(Path(__file__).resolve().parent / "text.html").as_uri(),
        width=640,
        height=520,
        resizable=True
        )
    webview.start()


if __name__ == "__main__":
    main()