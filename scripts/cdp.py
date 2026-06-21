#!/opt/homebrew/opt/python@3.11/bin/python3.11
"""Minimal CDP driver for Matchaé Chrome (:9336). No playwright needed.

Usage:
  cdp.py new <url>           open a new tab
  cdp.py goto <url>          navigate active tab
  cdp.py eval <js>           run JS in active tab, print result
  cdp.py screenshot <path>   PNG screenshot of active tab
  cdp.py wait <selector> [timeout=15]   wait until selector found
  cdp.py html [path]         dump current page HTML
  cdp.py type <selector> <text>   focus and type
  cdp.py click <selector>    click element matching selector
  cdp.py url                 print active tab URL
  cdp.py tabs                list tabs
"""
import sys, json, time, urllib.request, urllib.parse, base64
from websocket import create_connection  # `pip install websocket-client`

import os
PORT = int(os.environ.get("MATCHAE_CDP_PORT", 9340))

def http(path):
    return json.loads(urllib.request.urlopen(f"http://localhost:{PORT}{path}", timeout=5).read())

def list_pages():
    return [t for t in http("/json") if t.get("type") == "page"]

def first_page():
    pages = list_pages()
    if not pages:
        # create one
        urllib.request.urlopen(f"http://localhost:{PORT}/json/new?about:blank", timeout=5).read()
        time.sleep(0.5)
        pages = list_pages()
    # prefer non-DevTools, non-blank
    pages.sort(key=lambda p: (
        0 if "/aoba" in p.get("url","").lower() or "aoba.spread" in p.get("url","").lower() else 1,
        0 if "instagram" in p.get("url","").lower() else 1,
        0 if p.get("url","")!="about:blank" else 1,
    ))
    return pages[0]

class CDP:
    def __init__(self, page=None):
        if page is None:
            page = first_page()
        self.page = page
        self.ws = create_connection(page["webSocketDebuggerUrl"], timeout=30)
        self._id = 0
        self.send("Page.enable")
        self.send("Runtime.enable")
        self.send("DOM.enable")
    def send(self, method, **params):
        self._id += 1
        mid = self._id
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})
    def evaluate(self, expr, await_promise=False):
        r = self.send("Runtime.evaluate", expression=expr, returnByValue=True, awaitPromise=await_promise)
        if "exceptionDetails" in r:
            raise RuntimeError(r["exceptionDetails"].get("text","JS error") + ": " + str(r["exceptionDetails"]))
        return r.get("result", {}).get("value")
    def goto(self, url, wait=True):
        self.send("Page.navigate", url=url)
        if wait:
            self.wait_load()
    def wait_load(self, timeout=20):
        # poll readyState
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                rs = self.evaluate("document.readyState")
                if rs in ("complete", "interactive"):
                    return True
            except Exception:
                pass
            time.sleep(0.3)
        return False
    def wait_for(self, selector, timeout=15):
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                ok = self.evaluate(f"!!document.querySelector({json.dumps(selector)})")
                if ok:
                    return True
            except Exception:
                pass
            time.sleep(0.4)
        return False
    def screenshot(self, path):
        r = self.send("Page.captureScreenshot", format="png", captureBeyondViewport=False)
        with open(path, "wb") as f:
            f.write(base64.b64decode(r["data"]))
    def html(self):
        return self.evaluate("document.documentElement.outerHTML")
    def type_into(self, selector, text):
        js = f"""(function(){{
          const el = document.querySelector({json.dumps(selector)});
          if (!el) return false;
          el.focus();
          const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
          setter.call(el, {json.dumps(text)});
          el.dispatchEvent(new Event('input', {{bubbles:true}}));
          el.dispatchEvent(new Event('change', {{bubbles:true}}));
          return true;
        }})()"""
        return self.evaluate(js)
    def click(self, selector):
        js = f"""(function(){{
          const el = document.querySelector({json.dumps(selector)});
          if (!el) return false;
          el.scrollIntoView({{block:'center'}});
          el.click();
          return true;
        }})()"""
        return self.evaluate(js)

def main():
    a = sys.argv[1:]
    if not a or a[0] in ("-h","--help","help"):
        print(__doc__); return
    cmd, args = a[0], a[1:]
    if cmd == "tabs":
        for p in list_pages():
            print(p.get("url","")[:80], "--", p.get("title",""))
        return
    if cmd == "new":
        u = args[0] if args else "about:blank"
        req = urllib.request.Request(f"http://localhost:{PORT}/json/new?{urllib.parse.quote(u, safe='')}", method="PUT")
        urllib.request.urlopen(req, timeout=5).read()
        print("opened", u); return
    c = CDP()
    if cmd == "goto":
        c.goto(args[0]); print("OK")
    elif cmd == "eval":
        v = c.evaluate(args[0]); print(json.dumps(v, ensure_ascii=False))
    elif cmd == "screenshot":
        c.screenshot(args[0]); print("saved", args[0])
    elif cmd == "wait":
        sel = args[0]; t = int(args[1]) if len(args)>1 else 15
        print("OK" if c.wait_for(sel, t) else "TIMEOUT")
    elif cmd == "html":
        h = c.html()
        if args:
            open(args[0], "w").write(h); print("saved", args[0])
        else:
            print(h[:5000])
    elif cmd == "type":
        ok = c.type_into(args[0], " ".join(args[1:])); print("OK" if ok else "NO_EL")
    elif cmd == "click":
        ok = c.click(args[0]); print("OK" if ok else "NO_EL")
    elif cmd == "url":
        print(c.evaluate("location.href"))
    else:
        print("unknown command:", cmd); sys.exit(2)

if __name__ == "__main__":
    main()
