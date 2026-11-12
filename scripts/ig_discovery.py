#!/usr/bin/env python3
"""부엉이용: 다른 인스타 비즈니스/크리에이터 계정의 최근 게시물을 공식 API(Business Discovery)로 읽기.
보기 전용. 좋아요/팔로우/댓글 같은 행동은 하지 않는다.

토큰은 환경변수로만 받는다 (채팅·URL·로그에 남기지 않음):
  IG_ACCESS_TOKEN  페이스북 로그인 방식 사용자 토큰 (EAA...)
  IG_USER_ID       우리 계정(honeywedding_tip) ID

사용: python3 ig_discovery.py 계정1 계정2 ... [--limit 25] > 결과.json
"""
import os, sys, json, argparse, urllib.request, urllib.parse, urllib.error

API = "https://graph.facebook.com/v23.0"
FIELDS = ("username,name,biography,followers_count,media_count,"
          "media.limit({n}){{id,caption,media_type,media_product_type,like_count,comments_count,"
          "timestamp,permalink,view_count,children{{media_type}}}}")

def call(path, params, token):
    url = f"{API}/{path}?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(req, timeout=40) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        try: msg = json.load(e).get("error", {}).get("message")
        except Exception: msg = str(e)
        return {"error": msg, "http": e.code}

def account(username, token, me, limit):
    r = call(me, {"fields": f"business_discovery.username({username}){{{FIELDS.format(n=limit)}}}"}, token)
    if "error" in r:
        return {"username": username, "error": r["error"]}
    bd = r["business_discovery"]
    posts = bd.get("media", {}).get("data", [])
    f = max(bd.get("followers_count") or 1, 1)
    for p in posts:
        eng = (p.get("like_count") or 0) + (p.get("comments_count") or 0)
        p["engagement"] = eng
        p["engagement_rate_pct"] = round(eng / f * 100, 2)
        if p.get("children"):
            p["slides"] = len(p["children"].get("data", []))
            p.pop("children")
        kind = p.get("media_product_type") or p.get("media_type")
        p["format"] = {"REELS": "릴스", "CAROUSEL_ALBUM": "카드뉴스"}.get(
            kind, {"CAROUSEL_ALBUM": "카드뉴스", "VIDEO": "영상", "IMAGE": "사진"}.get(p.get("media_type"), kind))
    if posts:
        avg = sum(p["engagement"] for p in posts) / len(posts)
        for p in posts:
            p["vs_account_avg"] = round(p["engagement"] / avg, 2) if avg else None
        posts.sort(key=lambda p: p["engagement"], reverse=True)
    return {"username": bd.get("username"), "name": bd.get("name"), "bio": bd.get("biography"),
            "followers": bd.get("followers_count"), "media_count": bd.get("media_count"),
            "posts_sampled": len(posts), "posts_top_first": posts}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("usernames", nargs="+")
    ap.add_argument("--limit", type=int, default=25)
    a = ap.parse_args()
    token, me = os.environ.get("IG_ACCESS_TOKEN"), os.environ.get("IG_USER_ID")
    if not token or not me:
        sys.exit("IG_ACCESS_TOKEN / IG_USER_ID 환경변수가 필요해요")
    out = [account(u.lstrip("@"), token, me, a.limit) for u in a.usernames]
    json.dump(out, sys.stdout, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
