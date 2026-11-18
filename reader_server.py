#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
《我不是勇者》輕小說閱讀與即時同步編輯伺服器
啟動後請在瀏覽器開啟: http://localhost:8765
在網頁中切換至「編輯模式」修改內容後，點擊儲存或按 Ctrl+S，
即可直接將修改寫回本資料夾下的分章 .md 檔案與《我不是勇者_第一卷_全文.md》。
"""

import json
import os
import re
import subprocess
import threading
from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from urllib.parse import urlparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FULL_TEXT_FILE = os.path.join(BASE_DIR, "我不是勇者_第一卷_全文.md")
PORT = 8765
_git_lock = threading.Lock()


def push_to_github_async():
    def _worker():
        with _git_lock:
            try:
                if not os.path.exists(os.path.join(BASE_DIR, ".git")):
                    return
                subprocess.run(["git", "add", "docs/", "*.md", "*.html"], cwd=BASE_DIR, check=False)
                res = subprocess.run(
                    ["git", "commit", "-m", "Auto-sync novel chapters & GitHub Pages reader"],
                    cwd=BASE_DIR,
                    capture_output=True,
                    text=True,
                )
                if res.returncode == 0:
                    subprocess.run(["git", "push", "origin", "main"], cwd=BASE_DIR, check=False)
                    print("[GitHub Pages] 已自動推送更新至 GitHub Pages")
            except Exception as e:
                print(f"[GitHub Pages] 自動推送失敗: {e}")

    threading.Thread(target=_worker, daemon=True).start()


def get_chapter_files():
    files = []
    for fname in sorted(os.listdir(BASE_DIR)):
        if re.match(r"^\d{2}_.*\.md$", fname):
            files.append(fname)
    return files


def rebuild_full_text():
    chapters = []
    for fname in get_chapter_files():
        fpath = os.path.join(BASE_DIR, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            chapters.append(f.read().strip())
    combined = "\r\n\r\n---\r\n\r\n".join(chapters) + "\r\n"
    with open(FULL_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write(combined)
    try:
        import importlib
        import build_reader
        importlib.reload(build_reader)
        build_reader.build_html()
    except Exception:
        pass
    push_to_github_async()


class ReaderRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Cache-Control", "no-store, no-cache, must-revalidate")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path in ("/", "/index.html"):
            self.path = "/reader.html"
            return super().do_GET()

        if parsed.path == "/favicon.ico":
            self.send_response(204)
            self.end_headers()
            return

        if parsed.path == "/api/chapters":
            chapters = []
            for fname in get_chapter_files():
                fpath = os.path.join(BASE_DIR, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                mtime = os.path.getmtime(fpath)
                chapters.append({
                    "filename": fname,
                    "content": content,
                    "mtime": mtime,
                })
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({"ok": True, "chapters": chapters}, ensure_ascii=False).encode("utf-8"))
            return

        return super().do_GET()

    def do_POST(self):
        parsed = urlparse(self.path)
        if parsed.path == "/api/save":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length).decode("utf-8")
            data = json.loads(body)
            filename = os.path.basename(data.get("filename", ""))
            content = data.get("content", "")

            if not re.match(r"^\d{2}_.*\.md$", filename):
                self.send_response(400)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.end_headers()
                self.wfile.write(json.dumps({"ok": False, "error": "Invalid chapter filename"}).encode("utf-8"))
                return

            target_path = os.path.join(BASE_DIR, filename)
            with open(target_path, "w", encoding="utf-8") as f:
                f.write(content)

            rebuild_full_text()
            mtime = os.path.getmtime(target_path)

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.end_headers()
            self.wfile.write(json.dumps({
                "ok": True,
                "filename": filename,
                "mtime": mtime,
                "message": "已同步寫入分章檔案與全文總檔"
            }, ensure_ascii=False).encode("utf-8"))
            return

        self.send_response(404)
        self.end_headers()


if __name__ == "__main__":
    print(f"==================================================")
    print(f"《我不是勇者》輕小說閱讀器與同步編輯器已啟動")
    print(f"請在瀏覽器開啟: http://127.0.0.1:{PORT}")
    print(f"同步目錄: {BASE_DIR}")
    print(f"==================================================")
    server = ThreadingHTTPServer(("0.0.0.0", PORT), ReaderRequestHandler)
    server.serve_forever()
