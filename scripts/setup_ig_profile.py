#!/opt/homebrew/opt/python@3.11/bin/python3.11
"""Set the Aoba Instagram profile bio, link, and avatar.

Run once after the Instagram account is created and you're logged in to the
Aoba Chrome (CDP port :9340).

  ./scripts/setup_ig_profile.py
"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from cdp import CDP, first_page

BIO = (
    "White chocolate, born from the leaf.\n"
    "Organic matcha spread · cocoa butter · raw honey\n"
    "No palm oil. No refined sugar. No bitterness.\n"
    "First batch: sold out — notify list ↓"
)
LINK = "https://www.cochoy.fr/matchae/"
AVATAR_PATH = os.path.abspath(os.path.join(HERE, "..", "img", "profile.jpg"))

def main():
    c = CDP()
    c.goto("https://www.instagram.com/accounts/edit/")
    c.wait_load()
    time.sleep(2)
    # Bio
    if not c.evaluate("(function(){const ta=document.querySelector('textarea[name=biography]');if(!ta)return false;const s=Object.getOwnPropertyDescriptor(window.HTMLTextAreaElement.prototype,'value').set;s.call(ta," + json.dumps(BIO) + ");ta.dispatchEvent(new Event('input',{bubbles:true}));return true})()"):
        print("WARN: bio textarea not found — UI may have changed; manually paste:")
        print(BIO)
    # Link (Instagram has moved this to a separate "Edit links" page; handled there if missing here)
    c.evaluate("(function(){const i=document.querySelector('input[name=external_url],input[name=website]');if(!i)return false;const s=Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype,'value').set;s.call(i," + json.dumps(LINK) + ");i.dispatchEvent(new Event('input',{bubbles:true}));return true})()")
    # Submit
    ok = c.evaluate("(function(){const btns=[...document.querySelectorAll('div[role=button],button')];const t=btns.find(b=>/envoyer|submit|enregistrer|save/i.test(b.textContent.trim()));if(!t)return false;t.click();return t.textContent.trim()})()")
    print("save button:", ok)
    print("Bio + link pushed. For the avatar, drag", AVATAR_PATH, "onto the avatar circle on the IG profile page —")
    print("Instagram's avatar uploader uses a native file picker that browser automation can't drive cleanly.")

if __name__ == "__main__":
    main()
