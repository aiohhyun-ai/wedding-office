# wedding-office

결혼 준비 가성비 정보 인스타그램 계정을 운영하는 AI 오피스의 코드 저장소.

## 구조

- `agents/` 직원(에이전트)별 역할 지시문
- `scripts/` 네이버 검색, 인스타그램 게시·인사이트 스크립트

## 직원

| 파일 | 직원 | 하는 일 |
|---|---|---|
| `agents/scout.md` | 트렌드 스카우트(여우) | 콘텐츠 주제 제안 |
| `agents/researcher.md` | 리서처(고양이) | 승인된 기획의 카페·블로그 조사 |
| `agents/mail.md` | 우편 담당(펭귄) | 대댓글·메일 자료 확인 |
| `agents/planner.md` | 기획자(곰) | 카드뉴스·릴스 기획 |
| `agents/designer.md` | 디자이너(개구리) | 디자인 제작 |
| `agents/publisher.md` | 게시 담당(강아지) | 인스타그램 업로드 |
| `agents/analyst.md` | 분석가(부엉이) | 반응·트렌드 분석 |

## 비밀값

API 키와 토큰은 이 저장소에 넣지 않는다. `.env`는 커밋하지 않는다.
