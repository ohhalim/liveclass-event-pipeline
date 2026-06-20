"""queries.sql을 단일 소스로 삼아 이름별 집계 쿼리를 로드한다.

queries.sql의 각 쿼리는 `-- <이름>` 주석으로 구분된다.
visualizer / app 이 동일한 쿼리를 참조하도록 해 중복·드리프트를 방지한다.
"""

import os

QUERIES_PATH = os.path.join(os.path.dirname(__file__), "queries.sql")


def load_queries(path: str = QUERIES_PATH) -> dict[str, str]:
    with open(path) as f:
        content = f.read()

    queries: dict[str, str] = {}
    name: str | None = None
    buffer: list[str] = []

    def flush() -> None:
        if name and buffer:
            sql = "\n".join(buffer).strip().rstrip(";").strip()
            if sql:
                queries[name] = sql

    for line in content.splitlines():
        if line.startswith("--"):
            flush()
            name = line.lstrip("-").strip()
            buffer = []
        else:
            buffer.append(line)
    flush()

    return queries


QUERIES = load_queries()
