#!/usr/bin/env python3
"""
Manage the site log - add, edit, and delete entries.

    python3 tools/log.py

Opens a small page in your browser listing every entry. Add a new one from the
form at the top, or hit Edit or Delete on any existing entry. Every change writes
to log.json and immediately rebuilds log.html and feed.xml from it.

Then commit and push - that is all.

You never edit log.html or feed.xml by hand. log.json is the only source.
Needs nothing installed beyond Python 3.

    python3 tools/log.py --rebuild    regenerate both files without the browser
"""

import http.server
import json
import os
import re
import socketserver
import sys
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

def slugify(text):
    return re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")[:48]


def load():
    with open(LOG_JSON, encoding="utf-8") as f:
        data = json.load(f)
    changed = ensure_ids(data)
    if changed:
        write_json(data)
    return data


def ensure_ids(data):
    """Give every entry a stable id. An id is minted once, from the title at the
    time of creation, and then never changes - so renaming an entry later cannot
    break its #anchor on log.html or its <guid> in the feed."""
    seen, changed = set(), False
    for e in data["entries"]:
        if not e.get("id"):
            base = slugify(e.get("title") or e.get("message", "")) or e["date"]
            eid, n = base, 2
            while eid in seen:
                eid, n = "%s-%d" % (base, n), n + 1
            e["id"] = eid
            changed = True
        seen.add(e["id"])
    return changed


def new_id(data, title, message, date):
    taken = {e["id"] for e in data["entries"] if e.get("id")}
    base = slugify(title or message) or date
    eid, n = base, 2
    while eid in taken:
        eid, n = "%s-%d" % (base, n), n + 1
    return eid


def write_json(data):
    data["entries"].sort(key=lambda e: (e["date"], e.get("id", "")), reverse=True)
    with open(LOG_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def save(data):
    write_json(data)
    return rebuild()


def find(data, eid):
    for e in data["entries"]:
        if e.get("id") == eid:
            return e
    return None


# ----------------------------------------------------------------- render

def render_entries(entries):
    out = []
    for e in entries:
        parts = ['<article class="entry" id="%s">' % escape(e["id"]),
                 '<div class="entry-date">%s</div>' % escape(e["date"]).replace("-", ".")]
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
        dt = datetime.strptime(e["date"], "%Y-%m-%d").replace(hour=9, tzinfo=timezone.utc)
        url = "%s/log.html#%s" % (SITE, e["id"])
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
    with open(path, "w", encoding="utf-8") as f:
        f.write(src[:i + len(start)] + "\n" + body + "\n" + src[j:])


def rebuild():
    data = load()          # load() mints and persists any missing ids
    entries = sorted(data["entries"], key=lambda e: (e["date"], e.get("id", "")), reverse=True)
    splice(LOG_HTML, ENTRY_MARK, render_entries(entries))
    splice(FEED_XML, ITEM_MARK, render_items(entries))
    if entries:
        dt = datetime.strptime(entries[0]["date"], "%Y-%m-%d").replace(hour=9, tzinfo=timezone.utc)
        with open(FEED_XML, encoding="utf-8") as f:
            src = f.read()
        src = re.sub(r"<lastBuildDate>.*?</lastBuildDate>",
                     "<lastBuildDate>%s</lastBuildDate>" % format_datetime(dt), src)
        with open(FEED_XML, "w", encoding="utf-8") as f:
            f.write(src)
    return len(entries)


# ----------------------------------------------------------------- ui

CSS = """
:root{color-scheme:dark}
*{box-sizing:border-box}
body{background:#080A11;color:#fff;font:16px/1.6 'IBM Plex Sans',system-ui,sans-serif;
     margin:0;padding:48px 24px;display:flex;justify-content:center}
.card{width:100%;max-width:680px}
h1{font:600 24px/1.2 'IBM Plex Mono',ui-monospace,monospace;margin:0 0 8px}
h2{font:600 11px/1 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em;
   text-transform:uppercase;color:#9FB0C7;margin:48px 0 0}
p.sub{color:#9FB0C7;margin:0 0 32px}
label{display:block;font:600 11px/1 'IBM Plex Mono',ui-monospace,monospace;
      letter-spacing:.08em;text-transform:uppercase;color:#9FB0C7;margin:24px 0 8px}
input,textarea{width:100%;background:#101728;color:#fff;border:1px solid rgba(108,171,221,.2);
      border-radius:2px;padding:12px;font:400 16px/1.6 'IBM Plex Sans',system-ui,sans-serif}
textarea{min-height:120px;resize:vertical}
input:focus,textarea:focus{outline:none;border-color:#6CABDD}
.opt{color:#6CABDD;text-transform:none;letter-spacing:0}
.row{display:flex;gap:12px;align-items:center;margin-top:32px;flex-wrap:wrap}
button,.btn{background:#6CABDD;color:#080A11;border:1px solid #6CABDD;border-radius:2px;
      padding:13px 24px;font:600 11px/1 'IBM Plex Mono',ui-monospace,monospace;
      letter-spacing:.08em;text-transform:uppercase;cursor:pointer;text-decoration:none;
      display:inline-block}
button:hover,.btn:hover{background:#F0A63C;border-color:#F0A63C}
.ghost{background:transparent;color:#fff;border-color:rgba(108,171,221,.2)}
.ghost:hover{background:transparent;color:#F0A63C;border-color:#F0A63C}
.danger{background:transparent;color:#FF6B5A;border-color:rgba(255,107,90,.4);margin-left:auto}
.danger:hover{background:#FF6B5A;color:#080A11;border-color:#FF6B5A}
.note{border:1px solid #F0A63C;border-radius:2px;padding:16px;margin-bottom:32px;color:#F0A63C;
      font:600 11px/1.6 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em;
      text-transform:uppercase}
.entry{border-top:1px solid rgba(108,171,221,.2);padding:20px 0;display:flex;gap:16px;
       align-items:flex-start}
.entry .meta{flex:1;min-width:0}
.entry .d{font:600 11px/1.8 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em;color:#F0A63C}
.entry .t{font-weight:600}
.entry .m{color:#9FB0C7;font-size:14px}
.entry .acts{display:flex;gap:8px;flex:0 0 auto}
.entry .acts button,.entry .acts .btn{padding:8px 14px}
.tagrow{margin-top:6px;display:flex;gap:6px;flex-wrap:wrap}
.tagrow span{border:1px solid rgba(108,171,221,.2);border-radius:2px;padding:2px 6px;
       font:600 10px/1.6 'IBM Plex Mono',ui-monospace,monospace;letter-spacing:.08em;color:#6CABDD}
form.inline{display:inline}
"""


def form_fields(e=None):
    e = e or {}
    return """
<label for="d">Date</label>
<input id="d" type="date" name="date" value="{date}" required>
<label for="t">Title <span class="opt">- optional, shown as the headline</span></label>
<input id="t" type="text" name="title" value="{title}" placeholder="Starting in GLACIER Lab">
<label for="m">Message</label>
<textarea id="m" name="message" required placeholder="What you built, what broke, what you read.">{message}</textarea>
<label for="g">Tags <span class="opt">- optional, comma separated</span></label>
<input id="g" type="text" name="tags" value="{tags}" placeholder="AE-403W, AUTONOMY">
""".format(date=escape(e.get("date") or datetime.now().strftime("%Y-%m-%d"), True),
           title=escape(e.get("title", ""), True),
           message=escape(e.get("message", "")),
           tags=escape(", ".join(e.get("tags", [])), True))


def page_new(data, msg):
    rows = []
    for e in data["entries"]:
        tags = ('<div class="tagrow">%s</div>' %
                "".join("<span>%s</span>" % escape(t) for t in e["tags"])) if e.get("tags") else ""
        rows.append("""
<div class="entry">
  <div class="meta">
    <div class="d">{date}</div>
    <div class="t">{title}</div>
    <div class="m">{msg}</div>{tags}
  </div>
  <div class="acts">
    <a class="btn ghost" href="/edit?id={id}">Edit</a>
    <form class="inline" method="POST" action="/delete"
          onsubmit="return confirm('Delete this entry permanently?\\n\\n{confirm}')">
      <input type="hidden" name="id" value="{id}">
      <button class="danger" type="submit">Delete</button>
    </form>
  </div>
</div>""".format(date=escape(e["date"]),
                 title=escape(e.get("title") or "(no title)"),
                 msg=escape(e["message"][:110] + ("..." if len(e["message"]) > 110 else "")),
                 tags=tags, id=escape(e["id"], True),
                 confirm=escape((e.get("title") or e["message"])[:60]).replace("'", "")))

    return """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Log</title>
<style>{css}</style></head><body><div class="card">
<h1>Log</h1>
<p class="sub">Writes to log.json, then rebuilds log.html and feed.xml. Commit and push when you are done.</p>
{msg}
<form method="POST" action="/add">{fields}
<div class="row"><button type="submit">Add entry</button></div>
</form>
<h2>{n} entries</h2>
{rows}
</div></body></html>""".format(css=CSS, msg=msg, fields=form_fields(),
                               n=len(data["entries"]), rows="".join(rows))


def page_edit(e, msg):
    return """<!DOCTYPE html><html><head><meta charset="utf-8"><title>Edit entry</title>
<style>{css}</style></head><body><div class="card">
<h1>Edit entry</h1>
<p class="sub">Entry id <code>{id}</code> stays fixed, so its link and feed entry survive any edit.</p>
{msg}
<form method="POST" action="/update">
<input type="hidden" name="id" value="{id}">{fields}
<div class="row">
  <button type="submit">Save changes</button>
  <a class="btn ghost" href="/">Cancel</a>
</div>
</form>
<form method="POST" action="/delete"
      onsubmit="return confirm('Delete this entry permanently?')">
  <input type="hidden" name="id" value="{id}">
  <div class="row"><button class="danger" type="submit">Delete this entry</button></div>
</form>
</div></body></html>""".format(css=CSS, id=escape(e["id"], True), msg=msg, fields=form_fields(e))


class Handler(http.server.BaseHTTPRequestHandler):
    msg = ""

    def _send(self, body, code=200):
        b = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def _redirect(self, to="/"):
        self.send_response(303)
        self.send_header("Location", to)
        self.end_headers()

    def _note(self, text):
        Handler.msg = '<div class="note">%s</div>' % escape(text)

    def _take_msg(self):
        m, Handler.msg = Handler.msg, ""
        return m

    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        data = load()
        if u.path == "/edit":
            eid = urllib.parse.parse_qs(u.query).get("id", [""])[0]
            e = find(data, eid)
            if not e:
                self._note("That entry no longer exists.")
                return self._redirect("/")
            return self._send(page_edit(e, self._take_msg()))
        self._send(page_new(data, self._take_msg()))

    def _fields(self):
        n = int(self.headers.get("Content-Length", 0))
        return urllib.parse.parse_qs(self.rfile.read(n).decode("utf-8"))

    def do_POST(self):
        f = self._fields()
        get = lambda k: (f.get(k, [""])[0]).strip()
        date, message, title = get("date"), get("message"), get("title")
        tags = [t.strip().upper() for t in get("tags").split(",") if t.strip()]
        data = load()

        if self.path == "/add":
            if not date or not message:
                self._note("Date and message are both required.")
                return self._redirect("/")
            eid = new_id(data, title, message, date)
            data["entries"].append({"id": eid, "date": date, "title": title,
                                    "message": message, "tags": tags})
            n = save(data)
            print("  added   %s  %s" % (date, title or message[:50]))
            self._note("Added. log.html and feed.xml rebuilt from %d entries. Commit and push." % n)
            return self._redirect("/")

        if self.path == "/update":
            e = find(data, get("id"))
            if not e:
                self._note("That entry no longer exists.")
                return self._redirect("/")
            if not date or not message:
                self._note("Date and message are both required.")
                return self._redirect("/edit?id=" + urllib.parse.quote(get("id")))
            e.update(date=date, title=title, message=message, tags=tags)
            n = save(data)
            print("  edited  %s  %s" % (date, title or message[:50]))
            self._note("Saved. log.html and feed.xml rebuilt from %d entries. Commit and push." % n)
            return self._redirect("/")

        if self.path == "/delete":
            e = find(data, get("id"))
            if not e:
                self._note("That entry no longer exists.")
                return self._redirect("/")
            data["entries"] = [x for x in data["entries"] if x["id"] != e["id"]]
            n = save(data)
            print("  deleted %s  %s" % (e["date"], e.get("title") or e["message"][:50]))
            self._note("Deleted. log.html and feed.xml rebuilt from %d entries. Commit and push." % n)
            return self._redirect("/")

        self._redirect("/")

    def log_message(self, *a):
        pass


def main():
    if "--rebuild" in sys.argv:
        print("rebuilt log.html + feed.xml (%d entries)" % rebuild())
        return
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("127.0.0.1", PORT), Handler) as srv:
        url = "http://127.0.0.1:%d/" % PORT
        print("Log manager: %s" % url)
        print("Add, edit, or delete entries. Press Ctrl+C when you are done.")
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
        try:
            srv.serve_forever()
        except KeyboardInterrupt:
            print("\nDone.")


if __name__ == "__main__":
    main()
