#!/usr/bin/env python3
"""
Add an entry to the site log.

    python3 tools/log.py

Opens a small form in your browser. Fill in the date and the message (tags are
optional), click Add Entry, and this writes the entry into log.json and rebuilds
both log.html and feed.xml from it. Then commit and push - that is all.

You never edit log.html or feed.xml by hand. log.json is the only source.
Needs nothing installed beyond Python 3.
"""

import http.server
import json
import os
import re
import socketserver
import threading
import urllib.parse
import webbrowser
from datetime import datetime, timezone
from email.utils import format_datetime
from html import escape

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_JSON = os.path.join(REPO, "log.json")
LOG_HTML = os.path.join(REPO, "log.html")
FEED_XML = os.path.join(REPO, "feed.xml")
SITE = "https://scipk.com"
PORT = 8787

ENTRY_MARK = ("<!-- LOG:ENTRIES:START -->", "<!-- LOG:ENTRIES:END -->")
ITEM_MARK = ("<!-- LOG:ITEMS:START -->", "<!-- LOG:ITEMS:END -->")


# ----------------------------------------------------------------- data

def load():
    with open(LOG_JSON, encoding="utf-8") as f:
        return json.load(f)


def save(data):
    data["entries"].sort(key=lambda e: e["date"], reverse=True)
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def slug(text, date):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:48]
    return s or date


# ----------------------------------------------------------------- render

def render_entries(entries):
    out = []
    for e in entries:
        date = escape(e["date"]).replace("-", ".")
        sid = slug(e.get("title") or e["message"], e["date"])
        parts = ['<article class="entry" id="%s">' % sid,
                 '<div class="entry-date">%s</div>' % date]
        if e.get("title"):
            parts.append("<h2>%s</h2>" % escape(e["title"]))
        parts.append("<p>%s</p>" % escape(e["message"]))
        if e.get("tags"):
            parts.append('<div class="tags">%s</div>' % "".join(
                '<span class="tag">%s</span>' % escape(t) for t in e["tags"]))
        parts.append("</article>")
        out.append("\n".join(parts))
    return "\n".join(out)


def render_items(entries):
    out = []
    for e in entries:
        sid = slug(e.get("title") or e["message"], e["date"])
        dt = datetime.strptime(e["date"], "%Y-%m-%d").replace(
            hour=9, tzinfo=timezone.utc)
        url = "%s/log.html#%s" % (SITE, sid)
        out.append(
            "    <item>\n"
            "      <title>%s</title>\n"
            "      <link>%s</link>\n"
            "      <guid isPermaLink=\"true\">%s</guid>\n"
            "      <pubDate>%s</pubDate>\n"
            "      <description>%s</description>\n"
            "    </item>" % (
                escape(e.get("title") or e["message"][:70]), url, url,
                format_datetime(dt), escape(e["message"])))
    return "\n".join(out)


def splice(path, marks, body):
    with open(path, encoding="utf-8") as f:
        src = f.read()
    start, end = marks
    i, j = src.find(start), src.find(end)
    if i == -1 or j == -1:
        raise SystemExit("markers %s missing from %s" % (start, path))
    out = src[:i + len(start)] + "\n" + body + "\n" + src[j:]
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)


def rebuild():
    data = load()
    entries = sorted(data["entries"], key=lambda e: e["date"], reverse=True)
    splice(LOG_HTML, ENTRY_MARK, render_entries(entries))
    splice(FEED_XML, ITEM_MARK, render_items(entries))
    # keep the feed's build date in step with the newest entry
    if entries:
        dt = datetime.strptime(entries[0]["date"], "%Y-%m-%d").replace(
            hour=9, tzinfo=timezone.utc)
        with open(FEED_XML, encoding="utf-8") as f:
            src = f.read()
        src = re.sub(r"<lastBuildDate>.*?</lastBuildDate>",
                     "<lastBuildDate>%s</lastBuildDate>" % format_datetime(dt), src)
        with open(FEED_XML, "w", encoding="utf-8") as f:
            f.write(src)
    return len(entries)


# ----------------------------------------------------------------- form

FORM = """<!DOCTYPE html><html><head><meta charset="utf-8"><title>New log entry</title>
<style>
:root{color-scheme:dark}
body{background:#080A11;color:#fff;font:16px/1.6 'IBM Plex Sans',system-ui,sans-serif;
     margin:0;padding:48px 24px;display:flex;justify-content:center}
.card{width:100%;max-width:640px}
h1{font:600 24px/1.2 'IBM Plex Mono',ui-monospace,monospace;margin:0 0 8px}
p.sub{color:#9FB0C7;margin:0 0 32px}
label{display:block;font:600 11px/1 'IBM Plex Mono',ui-monospace,monospace;
      letter-spacing:.08em;text-transform:uppercase;color:#9FB0C7;margin:24px 0 8px}
input,textarea{width:100%;box-sizing:border-box;background:#101728;color:#fff;
      border:1px solid rgba(108,171,221,.2);border-radius:2px;padding:12px;
      font:400 16px/1.6 'IBM Plex Sans',system-ui,sans-serif}
textarea{min-height:120px;resize:vertical}
input:focus,textarea:focus{outline:none;border-color:#6CABDD}
.opt{color:#6CABDD;text-transform:none;letter-spacing:0}
button{margin-top:32px;background:#6CABDD;color:#080A11;border:0;border-radius:2px;
      padding:14px 24px;font:600 11px/1 'IBM Plex Mono',ui-monospace,monospace;
      letter-spacing:.08em;text-transform:uppercase;cursor:pointer}
button:hover{background:#F0A63C}
.ok{border:1px solid #F0A63C;border-radius:2px;padding:16px;margin-bottom:32px;color:#F0A63C;
    font:600 11px/1.6 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em;text-transform:uppercase}
.list{margin-top:48px;border-top:1px solid rgba(108,171,221,.2);padding-top:24px}
.list div{color:#9FB0C7;font:600 11px/2 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em}
</style></head><body><div class="card">
<h1>New log entry</h1>
<p class="sub">Writes to log.json, then rebuilds log.html and feed.xml. Commit and push when you are done.</p>
__MSG__
<form method="POST" action="/add">
<label for="d">Date</label><input id="d" type="date" name="date" value="__TODAY__" required>
<label for="t">Title <span class="opt">- optional, shown as the headline</span></label>
<input id="t" type="text" name="title" placeholder="Starting in GLACIER Lab">
<label for="m">Message</label>
<textarea id="m" name="message" required placeholder="What you built, what broke, what you read."></textarea>
<label for="g">Tags <span class="opt">- optional, comma separated</span></label>
<input id="g" type="text" name="tags" placeholder="AE-403W, AUTONOMY">
<button type="submit">Add entry</button>
</form>
<div class="list"><div>__COUNT__ ENTRIES IN LOG.JSON</div>__RECENT__</div>
</div></body></html>"""


class Handler(http.server.BaseHTTPRequestHandler):
    msg = ""

    def _page(self):
        data = load()
        entries = sorted(data["entries"], key=lambda e: e["date"], reverse=True)
        recent = "".join(
            "<div>%s &nbsp; %s</div>" % (e["date"], escape(e.get("title") or e["message"][:60]))
            for e in entries[:8])
        body = (FORM.replace("__TODAY__", datetime.now().strftime("%Y-%m-%d"))
                    .replace("__MSG__", Handler.msg)
                    .replace("__COUNT__", str(len(entries)))
                    .replace("__RECENT__", recent))
        Handler.msg = ""
        return body.encode("utf-8")

    def do_GET(self):
        b = self._page()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        f = urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"))
        date = (f.get("date", [""])[0]).strip()
        message = (f.get("message", [""])[0]).strip()
        title = (f.get("title", [""])[0]).strip()
        tags = [t.strip().upper() for t in f.get("tags", [""])[0].split(",") if t.strip()]

        if not date or not message:
            Handler.msg = '<div class="ok">Date and message are both required.</div>'
        else:
            data = load()
            data["entries"].append(
                {"date": date, "title": title, "message": message, "tags": tags})
            save(data)
            count = rebuild()
            Handler.msg = ('<div class="ok">Added. log.html and feed.xml rebuilt '
                           'from %d entries. Commit and push.</div>' % count)
            print("  added %s  %s" % (date, title or message[:50]))
            print("  rebuilt log.html + feed.xml (%d entries)" % count)

        self.send_response(303)
        self.send_header("Location", "/")
        self.end_headers()

    def log_message(self, *a):
        pass


def main():
    import sys
    if "--rebuild" in sys.argv:
        print("rebuilt log.html + feed.xml (%d entries)" % rebuild())
        return
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as srv:
        url = "http://127.0.0.1:%d/" % PORT
        print("Log entry form: %s" % url)
        print("Press Ctrl+C when you are done.")
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nDone.")


if __name__ == "__main__":
    main()
