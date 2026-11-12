#!/usr/bin/env python3
"""designku catalog: merge built-in + custom systems, refresh previews, render
~/.designku/catalog.html (keyboard navigable) and print the terminal table."""
from __future__ import annotations

import html
import json
from pathlib import Path

import dslib as L
import ds_preview

SWATCH_ROLES = ("primary", "secondary", "tertiary", "primaryContainer", "surfaceContainerHigh", "surface")

CATALOG_CSS = """
*{box-sizing:border-box}
:root{--bg:#F6F7F9;--card:#FFFFFF;--fg:#15171A;--muted:#5B626C;--line:#D9DDE3;--accent:#2F5BD3;--chip:#ECEFF3}
[data-theme=dark]{--bg:#101114;--card:#191B1F;--fg:#E7E9EC;--muted:#A3AAB4;--line:#2E3238;--accent:#A9C2FF;--chip:#24272C;color-scheme:dark}
body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,"Segoe UI",Roboto,sans-serif}
.wrap{max-width:1180px;margin:0 auto;padding:32px 24px 64px}
header{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap;margin-bottom:8px}
h1{margin:0;font-size:28px;letter-spacing:-.4px}
p.lead{margin:6px 0 0;color:var(--muted);max-width:70ch}
.bar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:20px 0}
.bar input{flex:1;min-width:200px;height:44px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);padding:0 14px;font:inherit;font-size:15px}
.bar input:focus-visible,button:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
button{height:44px;padding:0 16px;border-radius:10px;border:1px solid var(--line);background:var(--card);color:var(--fg);font:inherit;font-weight:600;cursor:pointer}
kbd{font:12px ui-monospace,Menlo,monospace;border:1px solid var(--line);border-bottom-width:2px;border-radius:5px;padding:1px 6px;background:var(--card)}
.hint{color:var(--muted);font-size:13px}
h2{font-size:13px;text-transform:uppercase;letter-spacing:1px;color:var(--muted);margin:28px 0 12px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:16px}
a.card{display:flex;flex-direction:column;background:var(--card);border:1px solid var(--line);border-radius:16px;overflow:hidden;text-decoration:none;color:inherit;transition:transform .12s ease,box-shadow .12s ease,border-color .12s ease;outline:0}
a.card:hover{transform:translateY(-2px);box-shadow:0 8px 24px rgba(0,0,0,.10)}
a.card.is-sel{border-color:var(--accent);box-shadow:0 0 0 3px var(--accent)}
.sw{display:flex;height:84px}
.sw i{flex:1;display:block}
.sw.dark{height:20px}
.body{padding:14px 16px 16px;display:flex;flex-direction:column;gap:6px;flex:1}
.top{display:flex;align-items:center;gap:8px}
.top b{font-size:18px;letter-spacing:-.2px}
.letter{width:26px;height:26px;border-radius:8px;display:grid;place-items:center;font-weight:700;font-size:13px;flex:none}
.pill{font-size:11px;font-weight:700;padding:2px 8px;border-radius:999px;background:var(--chip);color:var(--muted);white-space:nowrap}
.pill.def{background:var(--accent);color:var(--card)}
.ctx{color:var(--muted);font-size:13px}
.meta{margin-top:auto;padding-top:8px;display:flex;justify-content:space-between;gap:8px;color:var(--muted);font:12px ui-monospace,Menlo,monospace}
.empty{color:var(--muted);padding:24px;border:1px dashed var(--line);border-radius:16px}
[hidden]{display:none!important}
"""

CATALOG_JS = """
(function(){
  var root=document.documentElement,q=document.getElementById('q'),sel=-1;
  function cards(){return [].slice.call(document.querySelectorAll('a.card')).filter(function(c){return !c.hidden})}
  function pick(i,scroll){var cs=cards();if(!cs.length){sel=-1;return}
    sel=Math.max(0,Math.min(cs.length-1,i));
    document.querySelectorAll('a.card.is-sel').forEach(function(c){c.classList.remove('is-sel');c.setAttribute('aria-selected','false')});
    var c=cs[sel];c.classList.add('is-sel');c.setAttribute('aria-selected','true');
    if(scroll!==false){c.focus({preventScroll:true});c.scrollIntoView({block:'nearest',behavior:'smooth'})}}
  function move(dx,dy){var cs=cards();if(!cs.length)return;if(sel<0){pick(0);return}
    if(dx){pick(sel+dx);return}
    var cur=cs[sel].getBoundingClientRect(),best=-1,bestD=1e9;
    cs.forEach(function(c,i){var r=c.getBoundingClientRect();
      var below=dy>0?r.top>cur.top+4:r.top<cur.top-4;if(!below)return;
      var d=Math.abs(r.top-cur.top)*1000+Math.abs(r.left-cur.left);if(d<bestD){bestD=d;best=i}});
    if(best>=0)pick(best)}
  document.addEventListener('keydown',function(e){
    if(e.metaKey||e.ctrlKey||e.altKey)return;
    var typing=document.activeElement===q;
    if(e.key==='/'&&!typing){e.preventDefault();q.focus();return}
    if(e.key==='Escape'&&typing){q.value='';filter();q.blur();pick(0);return}
    if(typing&&e.key!=='ArrowDown'&&e.key!=='Enter')return;
    if(e.key==='ArrowRight'){e.preventDefault();move(1,0)}
    else if(e.key==='ArrowLeft'){e.preventDefault();move(-1,0)}
    else if(e.key==='ArrowDown'){e.preventDefault();if(typing){q.blur();pick(0)}else move(0,1)}
    else if(e.key==='ArrowUp'){e.preventDefault();move(0,-1)}
    else if(e.key==='Home'){e.preventDefault();pick(0)}
    else if(e.key==='End'){e.preventDefault();pick(cards().length-1)}
    else if(e.key==='Enter'){var cs=cards();if(typing&&cs.length){sel=0}
      if(sel>=0&&cs[sel]){e.preventDefault();window.location.href=cs[sel].href}}
    else if((e.key==='d'||e.key==='D')&&!typing){theme(root.getAttribute('data-theme')==='dark'?'light':'dark')}
  });
  document.addEventListener('focusin',function(e){var c=e.target.closest&&e.target.closest('a.card');if(c){var i=cards().indexOf(c);if(i>=0&&i!==sel)pick(i,false)}});
  function filter(){var v=q.value.trim().toLowerCase();
    document.querySelectorAll('a.card').forEach(function(c){c.hidden=v&&c.getAttribute('data-search').indexOf(v)<0});
    document.querySelectorAll('section').forEach(function(s){s.hidden=!s.querySelector('a.card:not([hidden])')&&!s.querySelector('.empty')});
    sel=-1}
  q.addEventListener('input',filter);
  function theme(t){root.setAttribute('data-theme',t);try{localStorage.setItem('designku-theme',t)}catch(e){}}
  var saved=null;try{saved=localStorage.getItem('designku-theme')}catch(e){}
  theme(saved||(window.matchMedia&&matchMedia('(prefers-color-scheme: dark)').matches?'dark':'light'));
  document.getElementById('themeBtn').addEventListener('click',function(){theme(root.getAttribute('data-theme')==='dark'?'light':'dark')});
  var start=document.querySelector('a.card[data-default="1"]');var cs=cards();pick(start?cs.indexOf(start):0,false);
})();
"""


def _card(system: dict, preview: Path, is_default: bool) -> str:
    tokens = system["tokens"]
    e = html.escape
    light = "".join(f'<i style="background:{L.tv(tokens, "color.light." + r)}"></i>' for r in SWATCH_ROLES)
    dark = "".join(f'<i style="background:{L.tv(tokens, "color.dark." + r)}"></i>' for r in SWATCH_ROLES)
    fonts = L.meta(tokens).get("fonts", {})
    primary, on_primary = L.tv(tokens, "color.light.primary"), L.tv(tokens, "color.light.onPrimary")
    letter = system["letter"] or system["name"][:1].upper()
    search = " ".join([system["id"], system["name"], system["context"], system["source"], system["tagline"]]).lower()
    pills = f'<span class="pill">{e(system["source"])}</span>' + ('<span class="pill def">project default</span>' if is_default else "")
    return (f'<a class="card" href="{e(L.file_url(preview))}" data-id="{e(system["id"])}" data-search="{e(search)}" '
            f'data-default="{1 if is_default else 0}" aria-selected="false">'
            f'<div class="sw">{light}</div><div class="sw dark">{dark}</div><div class="body">'
            f'<div class="top"><span class="letter" style="background:{primary};color:{on_primary}">{e(letter)}</span><b>{e(system["name"])}</b>{pills}</div>'
            f'<div class="ctx">{e(system["context"] or "Custom system")}</div><div>{e(system["tagline"])}</div>'
            f'<div class="meta"><span>{e(system["id"])}</span><span>{e(fonts.get("display", ""))} / {e(fonts.get("body", ""))}</span></div>'
            f"</div></a>")


def render_catalog(systems: list[dict], previews: dict[str, Path], default_key: str | None) -> str:
    sections = []
    for source, title in (("builtin", "Built-in systems"), ("custom", "My custom systems (~/.designku/systems)")):
        cards = [_card(s, previews[_key(s)], _key(s) == default_key) for s in systems if s["source"] == source]
        inner = f'<div class="grid">{"".join(cards)}</div>' if cards else (
            '<div class="empty">No custom systems yet. Run <kbd>/designku:ds-customize &lt;id&gt;</kbd> or <kbd>/designku:ds-create</kbd>.</div>')
        sections.append(f"<section><h2>{title} · {len(cards)}</h2>{inner}</section>")
    return (
        '<!DOCTYPE html>\n<html lang="en" data-theme="light">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n<title>designku — design system catalog</title>\n'
        f"<style>{CATALOG_CSS}</style>\n</head>\n<body>\n<div class=\"wrap\">\n"
        '<header><div><h1>designku catalog</h1><p class="lead">Pick a design system before any UI code is written. '
        "Every system ships accessible light and dark themes, a full token set and atomic components.</p></div>"
        '<button id="themeBtn" type="button" title="Toggle theme (D)">Light / Dark</button></header>\n'
        '<div class="bar"><input id="q" type="search" placeholder="Filter by name, context or id" aria-label="Filter systems">'
        '<span class="hint"><kbd>←</kbd> <kbd>↑</kbd> <kbd>↓</kbd> <kbd>→</kbd> move · <kbd>Enter</kbd> open · <kbd>/</kbd> filter · <kbd>D</kbd> theme</span></div>\n'
        + "\n".join(sections)
        + f"\n</div>\n<script>{CATALOG_JS}</script>\n</body>\n</html>\n")


def _key(system: dict) -> str:
    return f"{system['source']}:{system['id']}"


def project_default(project: Path | None) -> tuple[str | None, dict | None]:
    if not project:
        return None, None
    try:
        config = L.read_json(project / L.PROJECT_DIR_NAME / "config.json")
        system = config.get("system", {})
        return f"{system.get('source')}:{system.get('id')}", config
    except (OSError, ValueError):
        return None, None


def build(project: Path | None = None, force: bool = False) -> dict:
    """Refresh previews + catalog. Returns a dict describing everything (also used for --json)."""
    systems = L.list_systems()
    default_key, _ = project_default(project)
    previews, regenerated = {}, []
    for system in systems:
        path, regen = ds_preview.ensure_preview(system, force)
        previews[_key(system)] = path
        if regen:
            regenerated.append(system["id"])
    catalog_path = L.user_home() / "catalog.html"
    catalog_path.parent.mkdir(parents=True, exist_ok=True)
    catalog_path.write_text(render_catalog(systems, previews, default_key), encoding="utf-8")

    rows = []
    for system in systems:
        tokens = system["tokens"]
        fonts = L.meta(tokens).get("fonts", {})
        rows.append({
            "id": system["id"], "letter": system["letter"], "name": system["name"], "context": system["context"],
            "tagline": system["tagline"], "source": system["source"], "group": system["group"],
            "primary": L.tv(tokens, "color.light.primary"),
            "fonts": f"{fonts.get('display', '')} / {fonts.get('body', '')}",
            "default": _key(system) == default_key,
            "preview": str(previews[_key(system)]), "previewUrl": L.file_url(previews[_key(system)]),
        })
    groups = []
    for gid, title in L.GROUPS.items():
        members = [r for r in rows if r["group"] == gid]
        if members:
            groups.append({"id": gid, "label": title, "systems": [m["id"] for m in members],
                           "description": ", ".join(m["name"] for m in members[:6]) + ("…" if len(members) > 6 else "")})
    return {"systems": rows, "groups": groups, "catalog": str(catalog_path), "catalogUrl": L.file_url(catalog_path),
            "project": str(project) if project else None, "default": default_key, "regenerated": regenerated,
            "customDir": str(L.custom_dir())}


def print_table(data: dict) -> None:
    rows = data["systems"]
    if not rows:
        print("No design systems found.")
        return
    width_name = max(len(r["name"]) for r in rows)
    width_id = max(len(r["id"]) for r in rows)
    print(f"designku catalog — {len(rows)} systems ({sum(1 for r in rows if r['source'] == 'custom')} custom)")
    print(f"Catalog (arrow keys + Enter): {data['catalogUrl']}")
    print()
    for row in rows:
        mark = "*" if row["default"] else " "
        letter = row["letter"] or "-"
        print(f"{mark} {letter} {row['id']:<{width_id}}  {row['name']:<{width_name}}  {row['source']:<7}  {row['primary']}  {row['context']}")
        print(f"      {row['previewUrl']}")
    print()
    if data["default"]:
        print(f"* = default of this project ({data['project']})")
    else:
        print("No project default yet — pick one with /designku:ds-use <id>.")
    print()
    print("Pick groups (for AskUserQuestion, max 4 options each):")
    for group in data["groups"]:
        print(f"  {group['label']}: {', '.join(group['systems'])}")


def main_list(project: Path | None, as_json: bool, force: bool) -> int:
    data = build(project, force)
    if as_json:
        print(json.dumps(data, indent=2))
    else:
        print_table(data)
    return 0
