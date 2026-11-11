# Aside 연결

Aside가 네이버 구간(카페 본문 읽기, 승인된 댓글 등록, 답글 확인)을 맡는다.
Claude 쪽은 Aside를 직접 조종하지 않는다. 둘은 Google Drive 문서로만 주고받는다.

## 문서

| 문서 | 역할 | 링크 |
|---|---|---|
| Aside_업무지시서 | Aside가 할 일의 원본. 실행할 때마다 Aside가 읽는다 | https://docs.google.com/document/d/144JEB9zDZSTv6R7k3FSInm3i9CgdATmyGBCuf82-8Dk/edit |
| 할일_네이버조사 | 조사할 주제 대기열 | https://docs.google.com/document/d/1VFfsmELY5AlG7hvoU6KMUBTOYgH9YWBJ8E0O3yiV7X4/edit |
| 승인된댓글 | 승인된 댓글 대기열, 답글 기록 | https://docs.google.com/document/d/1e38EmTdYpufmlGfO7chZMEzgXWGvzhO6hWjkJ0XNESo/edit |

결과 저장 위치: 웨딩오피스/01_조사자료

## 업무 내용을 바꿀 때

Aside_업무지시서 문서만 고친다. 맨 위 "버전" 줄을 올리고 "변경 기록"에 한 줄 남긴다.
Aside 루틴 자체는 다시 손대지 않아도 된다.

## Aside 루틴에 넣어둔 내용 (한 번만 설정)

```
실행할 때마다 먼저 Google Drive "웨딩오피스/Aside_업무지시서" 문서를 열어서 끝까지 읽어.
그 문서의 "업무 내용"이 너의 지시야. 그대로 따라 해.
문서 맨 위 "버전"이 지난번 실행 때와 다르면, 이번 실행부터 바뀐 내용으로 일하고
나에게 "업무지시서가 버전 ○○로 바뀌어서 적용했어"라고 한 줄 알려줘. 같으면 그냥 진행해.
문서를 열 수 없으면 아무것도 하지 말고 나에게 알려줘.
```
