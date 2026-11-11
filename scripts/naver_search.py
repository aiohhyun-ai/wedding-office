#!/usr/bin/env python3
"""NAVER API HUB 검색 - 블로그와 카페글에서 결혼 준비 관련 글 링크를 찾는다.

본문은 가져오지 않는다. 제목, 요약, 링크만 나온다.
읽을 가치가 있는 글은 브라우저로 직접 열어서 본다.

쓰는 법:
    export NAVER_CLIENT_ID=...
    export NAVER_CLIENT_SECRET=...
    python3 naver_search.py "상견례 식당 추천"
    python3 naver_search.py --kind cafearticle --sort date --display 30 "웨딩홀 견적"
    python3 naver_search.py --json "스드메 가격"   # 기계가 읽을 JSON으로

키 발급: 네이버 클라우드 플랫폼 > NAVER API HUB
(2026년 7월 31일부터 네이버 개발자센터에서는 새 키를 발급하지 않는다)
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

BASE = "https://naverapihub.apigw.ntruss.com/search/v1"
KINDS = ("blog", "cafearticle", "news", "webkr")
TAG = re.compile(r"<[^>]+>")


def clean(text):
    """<b> 강조 태그와 HTML 엔티티를 걷어낸다."""
    import html
    return html.unescape(TAG.sub("", text or "")).strip()


def search(kind, query, display=20, start=1, sort="sim"):
    client_id = os.environ.get("NAVER_CLIENT_ID")
    client_secret = os.environ.get("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        sys.exit("NAVER_CLIENT_ID와 NAVER_CLIENT_SECRET 환경변수를 설정하세요.")

    params = urllib.parse.urlencode(
        {"query": query, "display": display, "start": start, "sort": sort, "format": "json"}
    )
    req = urllib.request.Request(
        f"{BASE}/{kind}?{params}",
        headers={
            "X-NCP-APIGW-API-KEY-ID": client_id,
            "X-NCP-APIGW-API-KEY": client_secret,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            data = json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        sys.exit(f"검색 실패 (HTTP {e.code}): {body}")
    except urllib.error.URLError as e:
        sys.exit(f"연결 실패: {e.reason}")

    out = []
    for item in data.get("items", []):
        out.append(
            {
                "title": clean(item.get("title")),
                "link": item.get("link", ""),
                "summary": clean(item.get("description")),
                "source": clean(item.get("bloggername") or item.get("cafename") or ""),
                "date": item.get("postdate", ""),
            }
        )
    return {"total": data.get("total", 0), "items": out}


def main():
    p = argparse.ArgumentParser(description="네이버 검색 (API HUB)")
    p.add_argument("query", help="검색어")
    p.add_argument("--kind", default="blog", choices=KINDS, help="검색 대상 (기본: blog)")
    p.add_argument("--display", type=int, default=20, help="가져올 개수, 1~100 (기본: 20)")
    p.add_argument("--start", type=int, default=1, help="시작 위치, 1~1000 (기본: 1)")
    p.add_argument("--sort", default="sim", choices=("sim", "date"), help="sim=정확도순, date=최신순")
    p.add_argument("--json", action="store_true", help="JSON으로 출력")
    args = p.parse_args()

    result = search(args.kind, args.query, args.display, args.start, args.sort)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return

    print(f"'{args.query}' 검색 결과 {len(result['items'])}건 (전체 {result['total']:,}건)\n")
    for i, item in enumerate(result["items"], 1):
        print(f"{i}. {item['title']}")
        if item["source"]:
            print(f"   {item['source']}  {item['date']}")
        print(f"   {item['link']}")
        if item["summary"]:
            print(f"   {item['summary'][:120]}")
        print()


if __name__ == "__main__":
    main()
