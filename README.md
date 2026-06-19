# liveclass-event-pipeline

라이브클래스 도메인의 유저 행동 이벤트를 생성하고 저장·분석·시각화하는 파이프라인.

## 실행 방법

**필요한 도구**: Docker, Docker Compose

```bash
git clone https://github.com/ohhalim/liveclass-event-pipeline.git
cd liveclass-event-pipeline

cp .env.example .env

docker compose up
```

실행 후 `charts/` 폴더에 차트 이미지 4개가 저장됩니다.

---

## 이벤트 설계

라이브클래스 도메인 기반 4가지 이벤트 타입.

| 타입 | 설명 | 전용 필드 |
|------|------|-----------|
| `page_view` | 강의 페이지 조회 | `page_url` |
| `lecture_play` | 강의 영상 재생 | `lecture_id` |
| `purchase` | 강의 구매 | `lecture_id`, `amount` |
| `error` | 에러 발생 | `error_code` |

실제 서비스 트래픽 패턴을 반영해 가중치 적용: `page_view` 50% / `lecture_play` 30% / `purchase` 15% / `error` 5%

---

## 스키마 설명

```sql
CREATE TABLE events (
    id          SERIAL PRIMARY KEY,
    event_type  VARCHAR(50) NOT NULL,
    user_id     VARCHAR(50) NOT NULL,
    session_id  VARCHAR(50) NOT NULL,
    lecture_id  VARCHAR(50),
    page_url    TEXT,
    amount      NUMERIC(10, 2),
    error_code  VARCHAR(50),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
```

이벤트 타입을 단일 테이블로 수용하는 와이드 테이블 구조. 타입별 테이블 분리 시 집계 쿼리마다 JOIN이 필요한 반면, 이 구조에서는 GROUP BY만으로 처리 가능. 타입별 전용 컬럼은 NULL 허용.

PostgreSQL은 집계 함수, 윈도우 함수 등 분석 쿼리를 편하게 사용할 수 있어 선택.

---

## 시각화 결과

![event_type_counts](charts/event_type_counts.png)

![date_trend](charts/date_trend.png)

![top10_users](charts/top10_users.png)

![event_type_ratio](charts/event_type_ratio.png)

---

## 구현하면서 고민한 점

**환경변수 기본값 제거**
`os.getenv("DB_HOST", "localhost")`처럼 기본값을 두면 설정 누락 시 오류 없이 넘어가 문제를 늦게 발견. `os.environ[]`으로 바꿔 미설정 시 즉시 실패하도록 설계.

**docker-compose depends_on**
`depends_on`만으로는 PostgreSQL이 시작됐다는 것만 확인. 초기화가 끝나기 전에 앱이 연결을 시도해 실패. `pg_isready` health check로 DB가 준비된 후 앱이 실행되도록 변경.

**matplotlib Docker 환경**
기본 백엔드는 화면 창을 띄우려 하지만 컨테이너에는 디스플레이가 없어 크래시. `matplotlib.use("Agg")`로 파일 출력 전용 백엔드로 변경.
