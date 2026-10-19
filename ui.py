#!/usr/bin/env python3
"""
A small browser UI for The Unofficial Guide. Personal add-on, not graded.

    python ui.py            then open http://localhost:5001

It reuses serve.py's Flask app (so /ask and /health still work) and adds two
routes: the page itself at /, and /ui/ask, which returns everything /ask does
plus the retrieved chunks with their distances, so you can see why an answer
came out the way it did.
"""

import os

from flask import jsonify, request

import config
from serve import app

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Unofficial Guide</title>
<style>
  :root {
    --bg: #f7f7f5; --card: #ffffff; --text: #1d1d1b; --muted: #6b6b66;
    --border: #e2e2dc; --accent: #2f5bd3; --ok: #1f7a4d; --warn: #b4531a;
  }
  @media (prefers-color-scheme: dark) {
    :root {
      --bg: #161615; --card: #1f1f1d; --text: #ececea; --muted: #9a9a94;
      --border: #33332f; --accent: #7d9cff; --ok: #5fc48f; --warn: #f0a070;
    }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--text);
         font: 16px/1.5 system-ui, -apple-system, sans-serif; }
  main { max-width: 760px; margin: 0 auto; padding: 32px 16px 64px; }
  h1 { font-size: 1.5rem; margin: 0 0 4px; }
  .sub { color: var(--muted); margin: 0 0 24px; font-size: .9rem; }
  form { display: flex; gap: 8px; }
  input { flex: 1; padding: 12px 14px; font: inherit; color: var(--text);
          background: var(--card); border: 1px solid var(--border); border-radius: 8px; }
  input:focus { outline: 2px solid var(--accent); outline-offset: -1px; }
  button { padding: 12px 18px; font: inherit; font-weight: 600; color: #fff;
           background: var(--accent); border: 0; border-radius: 8px; cursor: pointer; }
  button:disabled { opacity: .5; cursor: wait; }
  .card { background: var(--card); border: 1px solid var(--border);
          border-radius: 10px; padding: 16px 18px; margin-top: 16px; }
  .q { font-weight: 600; margin-bottom: 8px; }
  .answer { white-space: pre-wrap; }
  .meta { margin-top: 10px; font-size: .85rem; color: var(--muted); }
  .badge { display: inline-block; padding: 1px 8px; border-radius: 99px;
           font-size: .75rem; font-weight: 600; margin-right: 6px; }
  .pass { background: color-mix(in srgb, var(--ok) 18%, transparent); color: var(--ok); }
  .refused { background: color-mix(in srgb, var(--warn) 18%, transparent); color: var(--warn); }
  details { margin-top: 10px; font-size: .85rem; }
  summary { cursor: pointer; color: var(--accent); }
  .chunk { border-top: 1px solid var(--border); padding: 8px 0; }
  .chunk b { font-family: ui-monospace, monospace; font-weight: 500; }
  .chunk p { margin: 4px 0 0; white-space: pre-wrap; color: var(--muted); }
  .error { color: var(--warn); }
</style>
</head>
<body>
<main>
  <h1>The Unofficial Guide</h1>
  <p class="sub">Corpus: <b>__CORPUS__</b> · cutoff __THRESHOLD__ · top __TOPK__ chunks</p>
  <form id="f">
    <input id="q" placeholder="Ask something, e.g. when is the add/drop deadline?" autofocus>
    <button id="b">Ask</button>
  </form>
  <div id="log"></div>
</main>
<script>
const f = document.getElementById('f'), q = document.getElementById('q'),
      b = document.getElementById('b'), log = document.getElementById('log');
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));
const history = [];   // [question, answer] pairs, sent with every request

f.addEventListener('submit', async e => {
  e.preventDefault();
  const question = q.value.trim();
  if (!question) return;
  b.disabled = true; b.textContent = 'Thinking…';
  const card = document.createElement('div');
  card.className = 'card';
  card.innerHTML = `<div class="q">${esc(question)}</div><div class="answer">…</div>`;
  log.prepend(card);
  try {
    const r = await fetch('/ui/ask', {method: 'POST',
      headers: {'Content-Type': 'application/json'}, body: JSON.stringify({question, history})});
    const d = await r.json();
    if (d.error) throw new Error(d.error);
    history.push([d.searched_as, d.answer]);
    const rewrite = d.searched_as !== question ? `<br>Searched as: ${esc(d.searched_as)}` : '';
    const badge = d.refused ? '<span class="badge refused">refused by gate</span>'
                            : '<span class="badge pass">answered</span>';
    const chunks = d.chunks.map(c =>
      `<div class="chunk"><b>${esc(c.label)}</b> — distance ${c.distance.toFixed(3)}<p>${esc(c.text)}</p></div>`).join('');
    card.innerHTML = `<div class="q">${esc(question)}</div>
      <div class="answer">${esc(d.answer)}</div>
      <div class="meta">${badge}best distance ${d.best_distance} (cutoff ${d.threshold})${rewrite}
        ${d.sources.length ? '<br>Sources: ' + d.sources.map(esc).join(', ') : ''}</div>
      <details><summary>Retrieved chunks (${d.chunks.length})</summary>${chunks}</details>`;
  } catch (err) {
    card.querySelector('.answer').innerHTML = `<span class="error">${esc(err.message)}</span>`;
  }
  b.disabled = false; b.textContent = 'Ask'; q.select();
});
</script>
</body>
</html>
"""


@app.get("/")
def page():
    return (
        PAGE.replace("__CORPUS__", config.CORPUS)
        .replace("__THRESHOLD__", str(config.THRESHOLD))
        .replace("__TOPK__", str(config.TOP_K))
    )


@app.post("/ui/ask")
def ui_ask():
    from app import ask_pipeline
    from store import search

    payload = request.get_json(silent=True) or {}
    question = (payload.get("question") or "").strip()
    # The page keeps the conversation and sends it back each time, so the
    # server remembers nothing between requests.
    history = [tuple(turn) for turn in payload.get("history", [])]
    if not question:
        return jsonify({"error": "Type a question first."}), 400

    try:
        outcome = ask_pipeline(question, corpus=config.CORPUS, history=history)
        # ask_pipeline searches too; this second search is local and cheap,
        # and it's the only way to show the chunks without changing app.py.
        # It uses the rewritten question so it shows what was really searched.
        chunks = search(outcome["question"], corpus=config.CORPUS)
    except Exception as exc:  # noqa: BLE001
        return jsonify({"error": f"{type(exc).__name__}: {exc}"}), 500

    return jsonify(
        {
            "answer": outcome["answer"],
            "searched_as": outcome["question"],
            "refused": outcome["refused"],
            "sources": outcome["sources"],
            "best_distance": round(outcome["best_distance"], 4),
            "threshold": outcome["threshold"],
            "chunks": [
                {"label": c.label, "distance": c.distance, "text": c.text}
                for c in chunks
            ],
        }
    )


if __name__ == "__main__":
    # 5001, not 5000: macOS's AirPlay Receiver already sits on 5000.
    port = int(os.getenv("PORT", "5001"))
    print(f"Open http://localhost:{port}   (Ctrl-C to stop)")
    app.run(host="127.0.0.1", port=port)
