# Project MFA - Cloudflare Workers Edition

This is your local Flask app adapted to run on Cloudflare's **Python
Workers**, so it's reachable at a real public URL (e.g.
`project-mfa.<your-subdomain>.workers.dev`) instead of only on
`127.0.0.1`.

**Read this first:** Python Workers with Flask support is very new
(shipped on Cloudflare within the last few weeks, as of late September
2026). It works and is officially documented, but it's not as battle
tested as a normal Flask deployment. Keep your local version
(`Project_MFA/`) as your guaranteed-working fallback for submission -
treat this as the bonus/demo version, and test it a few days before
your deadline, not the night before.

## What's different from the local version

| | Local version | Cloudflare version |
|---|---|---|
| Config | Hardcoded placeholders in `app.py` | Pulled from Worker secrets via `from workers import env` |
| Runs on | `python app.py` on your PC | Cloudflare's global edge network |
| URL | `127.0.0.1:5000` | A real public `.workers.dev` URL |
| OTP storage | In-memory Python dict | Same (see caveat below) |

## Prerequisites

Install these first:
- [uv](https://docs.astral.sh/uv/) (Python package/tool manager)
- [Node.js](https://nodejs.org/) (Wrangler, Cloudflare's CLI, runs on Node)
- A free [Cloudflare account](https://dash.cloudflare.com/sign-up)

## Setup

1. From this folder, install JS tooling:
   ```
   npm install
   ```

2. Log in to Cloudflare via Wrangler:
   ```
   npx wrangler login
   ```

3. Set your secrets (these replace the hardcoded placeholders from the local version):
   ```
   uv run pywrangler secret put BOT_TOKEN
   uv run pywrangler secret put CHAT_ID
   uv run pywrangler secret put SECRET_KEY
   ```
   Each command will prompt you to paste the value. Use the same
   BOT_TOKEN / CHAT_ID you already got from BotFather and
   `@userinfobot`. For SECRET_KEY, any random string works (you can
   reuse the UUID you generated for the local version).

## Run it locally first (via Cloudflare's local simulator)

```
npm run dev
```

This runs Cloudflare's actual Workers runtime (`workerd`) on your
machine, so it behaves like production before you deploy anything
publicly. Open the URL it prints (usually `http://localhost:8787`).

## Deploy to a public URL

```
npm run deploy
```

Wrangler will print your live `.workers.dev` URL when it finishes.

## Known caveat: OTP storage

The OTP store is still a plain Python dictionary, same as your local
version. This works fine for a single person testing sequentially (one
login → one OTP → one verify), which covers your demo and screenshots.
It is **not** how you'd do this in a real production system, because
Cloudflare can run your Worker across many isolated instances - a
dictionary in one instance isn't guaranteed to be visible to a
different instance handling a later request.

**The textbook-correct fix** is [Cloudflare KV](https://developers.cloudflare.com/kv/),
a key-value store built for exactly this: it has a built-in
`expirationTtl` you could set to 180 seconds so OTPs expire
automatically without any manual timestamp checking. If you want to
push this further for extra marks, look at the official
`02-binding` example in
[cloudflare/python-workers-examples](https://github.com/cloudflare/python-workers-examples)
which shows how to read/write a KV namespace from a Python Worker, and
mention in your report that you identified this as the production
upgrade path even if you kept the in-memory version for the demo.

## Troubleshooting

- If `pywrangler` isn't found, try prefixing commands with `uvx --from workers-py`
  instead of `uv run`, e.g. `uvx --from workers-py pywrangler dev`.
- If Telegram sending fails, double check the three secrets were set
  correctly with `uv run pywrangler secret list`.
- Since this platform is new, error messages may be less polished than
  Flask's usual ones - check the terminal output where `npm run dev` /
  `npm run deploy` is running for the actual Python traceback.
