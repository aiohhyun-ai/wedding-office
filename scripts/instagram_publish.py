#!/usr/bin/env python3
"""Instagram Graph API로 카드뉴스(캐러셀)와 릴스를 올린다.

공식 API만 쓴다. 아이디·비번으로 로그인하는 자동화 도구는 계정이 정지되니 쓰지 않는다.

준비물:
  - 인스타그램 프로페셔널 계정 (비즈니스 또는 크리에이터)
  - 페이스북 페이지 연결
  - Meta 개발자 앱 + instagram_content_publish 권한
  - 이미지/영상은 공개된 https 주소에 올라가 있어야 한다 (Drive 공유 링크는 보통 안 된다)

쓰는 법:
    export IG_USER_ID=...
    export IG_ACCESS_TOKEN=...
    python3 instagram_publish.py carousel --caption-file cap.txt img1.jpg_url img2.jpg_url ...
    python3 instagram_publish.py reel --caption-file cap.txt --cover COVER_URL VIDEO_URL
    python3 instagram_publish.py limit      # 남은 게시 가능 수 확인
"""
import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

API = "https://graph.facebook.com/v23.0"


def call(path, params=None, post=False):
    token = os.environ.get("IG_ACCESS_TOKEN")
    if not token:
        sys.exit("IG_ACCESS_TOKEN 환경변수를 설정하세요.")
    params = dict(params or {})
    url = f"{API}/{path}"
    # 토큰은 URL·본문에 넣지 않고 헤더로만 보낸다 (로그·기록에 남지 않게).
    headers = {"Authorization": f"Bearer {token}"}
    try:
        if post:
            req = urllib.request.Request(url, data=urllib.parse.urlencode(params).encode(), headers=headers)
        else:
            req = urllib.request.Request(f"{url}?{urllib.parse.urlencode(params)}", headers=headers)
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.load(resp)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")
        try:
            msg = json.loads(body)["error"]["message"]
        except Exception:
            msg = body[:500]
        sys.exit(f"API 오류 (HTTP {e.code}): {msg}")


def ig_id():
    v = os.environ.get("IG_USER_ID")
    if not v:
        sys.exit("IG_USER_ID 환경변수를 설정하세요.")
    return v


def wait_ready(container_id, timeout=600):
    """컨테이너 처리가 끝날 때까지 기다린다. 영상은 몇 분 걸린다."""
    start = time.time()
    while time.time() - start < timeout:
        status = call(container_id, {"fields": "status_code,status"})
        code = status.get("status_code")
        if code == "FINISHED":
            return
        if code in ("ERROR", "EXPIRED"):
            sys.exit(f"컨테이너 {container_id} 실패: {code} / {status.get('status')}")
        print(f"  처리 중... ({int(time.time() - start)}초)", flush=True)
        time.sleep(10)
    sys.exit(f"컨테이너 {container_id} 처리가 {timeout}초 안에 끝나지 않았습니다.")


def publish(container_id):
    result = call(f"{ig_id()}/media_publish", {"creation_id": container_id}, post=True)
    media_id = result["id"]
    info = call(media_id, {"fields": "permalink"})
    return media_id, info.get("permalink", "")


def do_carousel(urls, caption):
    if not 2 <= len(urls) <= 10:
        sys.exit("캐러셀은 이미지 2~10장이어야 합니다.")
    children = []
    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] 이미지 올리는 중")
        r = call(f"{ig_id()}/media", {"image_url": url, "is_carousel_item": "true"}, post=True)
        children.append(r["id"])
    print("캐러셀 묶는 중")
    parent = call(
        f"{ig_id()}/media",
        {"media_type": "CAROUSEL", "children": ",".join(children), "caption": caption},
        post=True,
    )["id"]
    wait_ready(parent)
    return publish(parent)


def do_reel(video_url, caption, cover=None):
    params = {"media_type": "REELS", "video_url": video_url, "caption": caption}
    if cover:
        params["cover_url"] = cover
    print("영상 올리는 중")
    container = call(f"{ig_id()}/media", params, post=True)["id"]
    wait_ready(container)
    return publish(container)


def main():
    p = argparse.ArgumentParser(description="인스타그램 게시")
    sub = p.add_subparsers(dest="cmd", required=True)

    c = sub.add_parser("carousel", help="카드뉴스 (이미지 2~10장)")
    c.add_argument("urls", nargs="+", help="이미지의 공개 https 주소")
    c.add_argument("--caption-file", help="캡션이 담긴 텍스트 파일")
    c.add_argument("--caption", default="", help="캡션 (직접 입력)")

    r = sub.add_parser("reel", help="릴스 (세로 영상)")
    r.add_argument("video", help="영상의 공개 https 주소")
    r.add_argument("--cover", help="커버 이미지 주소")
    r.add_argument("--caption-file", help="캡션이 담긴 텍스트 파일")
    r.add_argument("--caption", default="", help="캡션 (직접 입력)")

    sub.add_parser("limit", help="24시간 안에 더 올릴 수 있는 수 확인")

    t = sub.add_parser("test-image", help="게시하지 않고 이미지 주소가 받아지는지만 확인 (컨테이너만 만들고 24시간 뒤 자동 삭제)")
    t.add_argument("url")

    args = p.parse_args()

    if args.cmd == "limit":
        d = call(f"{ig_id()}/content_publishing_limit", {"fields": "config,quota_usage"})
        info = d.get("data", [{}])[0]
        used = info.get("quota_usage", 0)
        total = info.get("config", {}).get("quota_total", "?")
        print(f"지난 24시간 게시: {used} / {total}")
        return

    if args.cmd == "test-image":
        r = call(f"{ig_id()}/media", {"image_url": args.url, "is_carousel_item": "true"}, post=True)
        print("이미지 확인 OK (게시 안 함), 컨테이너:", r.get("id"))
        return

    caption = args.caption
    if getattr(args, "caption_file", None):
        with open(args.caption_file, encoding="utf-8") as f:
            caption = f.read().strip()
    if len(caption) > 2200:
        sys.exit(f"캡션이 너무 깁니다 ({len(caption)}자). 인스타그램 한도는 2,200자입니다.")

    if args.cmd == "carousel":
        media_id, link = do_carousel(args.urls, caption)
    else:
        media_id, link = do_reel(args.video, caption, args.cover)

    print(f"\n게시 완료\n  ID: {media_id}\n  주소: {link}")


if __name__ == "__main__":
    main()
