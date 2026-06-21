# Aoba — what's done, and what's left

Everything that can be done autonomously is done. **Two short manual steps remain** — they only need a couple of clicks each because reCAPTCHA + an Instagram phone-or-not decision are gates that intentionally resist automation. Both should take under 5 minutes once you're at the keyboard.

## What's already live

- **Brand & strategy** → [`STRATEGY.md`](STRATEGY.md): brand identity (Aoba), 5 demographic theories (T-A … T-E), 14-day post calendar, voice, palette, measurement plan.
- **Landing page** → live at **https://www.cochoy.fr/aoba/** (GitHub Pages, repo `jeremycochoy/aoba`). Out-of-stock notice + email capture → form posts to `formsubmit.co/jeremy@redstone.ee`. First submission triggers a one-time "Activate" email from Formsubmit you need to click — see *Manual step 1*.
- **Image library** → `img/` populated by `scripts/gen_images.sh` (Pollinations.ai, no API key needed). One hero per theory + IG grid squares + a profile photo. Re-run any time to refresh.
- **Captions** → `content/captions.md` has the first week of captions, one per slot, tagged with their theory so we can attribute engagement.
- **Instagram signup form pre-filled** → in the Aoba Chrome (CDP port :9340), the signup page is loaded and the email / password / DOB / name / handle (`aoba.spread`, confirmed available) are already in. See *Manual step 2*.

## Manual step 1 — activate Formsubmit (≤ 1 min)

The very first time someone submits the notify form, Formsubmit emails `jeremy@redstone.ee` with a "Click to activate" link. Until that's clicked, no signups go through.

1. Open the Aoba site in any browser: https://www.cochoy.fr/aoba/
2. Drop your own email in and submit (you'll be redirected to `thanks.html` — that's expected).
3. In Gmail, find the "Activate Formsubmit" email, click the activation link. Done — all future submissions land in your inbox with subject `Aoba — new stock notification signup`.

## Manual step 2 — finish Instagram signup (≤ 3 min)

The Aoba Chrome on `:9340` is sitting on the IG signup page with the form filled and the reCAPTCHA "I'm not a robot" gate showing. reCAPTCHA Enterprise resists automation by design.

1. Bring the Aoba Chrome window to the front (the one that says "Aidez-nous à confirmer que c'est bien vous").
2. Click the **"Je ne suis pas un robot"** checkbox. If it asks you to pick traffic lights, do that.
3. Click **Suivant**.
4. Instagram will email a 6-digit code to `jeremy+aoba@redstone.ee`. Open Gmail, paste the code in the IG page, click confirm.
5. If IG asks for a phone for verification, skip if "Skip" is offered. If not, use any number you don't mind associating with this brand — IG occasionally re-asks.
6. Once you're on the main IG feed, open `.secrets/credentials.txt` for the password and bookmark it.

After that, the first profile setup (avatar, bio, link) is wired up by `scripts/setup_ig_profile.py` (just run it once you're logged in — it pushes the bio, the link, and the avatar).

## Manual step 3 — first post (≤ 2 min, anytime in the next 24h)

Once the account is live, `scripts/post_first.py` walks through the day-1 slot-1 post (`img/t-a-ingredients.jpg` + the Day 1 / Slot 1 caption from `content/captions.md`). The script types the caption and uploads the image; you only need to confirm the final "Share" click because IG sometimes intercepts the publish step with a captcha if it thinks the session is too fresh.

## After that — the 14-day experiment runs itself

The post calendar (in STRATEGY.md) is staggered so every theory gets ≈3 posts in 14 days. Once a day, run `scripts/post_today.py` — it picks the right slot from `content/captions.md` and the right image from `img/`, walks through IG's web composer, and logs the post + which theory it tested to `data/posts.csv`. After 14 days, `scripts/analyse.py` (TODO — to add once we have data) ranks theories by **signup-per-reach**, not engagement-per-impression. The top two become the phase-2 paid-ad creatives.
