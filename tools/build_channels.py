#!/usr/bin/env python3
"""Genera channels.json con SOLO canales que responden de verdad.

Descarga las listas de iptv-org (España + español), y por cada canal https
comprueba: manifiesto HLS válido, primer segmento accesible y cabecera CORS
(sin CORS el navegador bloquea el vídeo aunque el stream esté vivo).
Uso: python tools/build_channels.py
"""
import json, re, ssl, sys, concurrent.futures as cf
import urllib.request
from urllib.parse import urljoin

ORIGIN = "https://jpm70.github.io"
SOURCES = [
    ("https://iptv-org.github.io/iptv/countries/es.m3u", True),
    ("https://iptv-org.github.io/iptv/languages/spa.m3u", False),
]
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(url, n=200000, timeout=8):
    req = urllib.request.Request(url, headers={"Origin": ORIGIN, "User-Agent": "Mozilla/5.0"})
    f = urllib.request.urlopen(req, timeout=timeout, context=ctx)
    return f, f.read(n)


def parse(text, spain):
    out, meta = [], None
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("#EXTINF"):
            name = re.search(r",(.+)$", line)
            logo = re.search(r'tvg-logo="([^"]*)"', line)
            group = re.search(r'group-title="([^"]*)"', line)
            meta = {"name": name.group(1).strip() if name else "Canal",
                    "logo": logo.group(1) if logo else "",
                    "group": group.group(1) if group else "General",
                    "es": spain}
        elif line and not line.startswith("#") and meta:
            meta["url"] = line
            out.append(meta)
            meta = None
    return out


def cors_ok(f):
    return f.headers.get("Access-Control-Allow-Origin") in ("*", ORIGIN)


def alive(c):
    try:
        u = c["url"]
        for _ in range(3):  # master -> media playlist
            f, b = fetch(u)
            if not cors_ok(f):
                return False
            t = b.decode("utf8", "ignore")
            if "#EXTM3U" not in t:
                return False
            lines = [l.strip() for l in t.splitlines() if l.strip() and not l.startswith("#")]
            if not lines:
                return False
            nxt = urljoin(u, lines[0])
            if "#EXT-X-STREAM-INF" in t:
                u = nxt
                continue
            f2, b2 = fetch(nxt, 2000)
            return f2.status == 200 and len(b2) > 500 and cors_ok(f2)
        return False
    except Exception:
        return False


def main():
    seen, chans = set(), []
    for url, spain in SOURCES:
        _, raw = fetch(url, 50_000_000, 30)
        for c in parse(raw.decode("utf8", "ignore"), spain):
            if c["url"].startswith("https://") and "Geo-blocked" not in c["name"] and c["url"] not in seen:
                seen.add(c["url"])
                chans.append(c)
    print(len(chans), "canales https a comprobar", file=sys.stderr)
    with cf.ThreadPoolExecutor(64) as ex:
        ok = list(ex.map(alive, chans))
    good = [c for c, k in zip(chans, ok) if k]
    good.sort(key=lambda c: (not c["es"], c["name"].lower()))
    with open("channels.json", "w", encoding="utf8") as fh:
        json.dump(good, fh, ensure_ascii=False, separators=(",", ":"))
    print(len(good), "canales verificados -> channels.json", file=sys.stderr)


if __name__ == "__main__":
    main()
