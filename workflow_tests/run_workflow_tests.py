from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from urllib import error, request


URI = "http://localhost:8000/generate"
HEADERS = {"Content-Type": "application/json"}
DEFAULT_PERSONA = "sharp_operator"
ALL_PLATFORMS = [
    "linkedin",
    "instagram",
    "facebook",
    "x",
    "tiktok",
    "blog",
    "newsletter",
    "speech",
    "copy",
]

CASES = [
    {
        "name": "1post_1platform",
        "artifactId": "workflow-test-1x1",
        "angleCount": 1,
        "platforms": ["linkedin"],
    },
    {
        "name": "1post_3platforms",
        "artifactId": "workflow-test-1x3",
        "angleCount": 1,
        "platforms": ["linkedin", "instagram", "x"],
    },
    {
        "name": "3posts_1platform",
        "artifactId": "workflow-test-3x1",
        "angleCount": 3,
        "platforms": ["linkedin"],
    },
    {
        "name": "3posts_3platforms",
        "artifactId": "workflow-test-3x3",
        "angleCount": 3,
        "platforms": ["linkedin", "instagram", "x"],
    },
    {
        "name": "3posts_allplatforms",
        "artifactId": "workflow-test-3xall",
        "angleCount": 3,
        "platforms": ALL_PLATFORMS,
    },
    {
        "name": "10posts_allplatforms",
        "artifactId": "workflow-test-10xall",
        "angleCount": 10,
        "platforms": ALL_PLATFORMS,
    },
]


def post_json(payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(URI, data=body, headers=HEADERS, method="POST")
    with request.urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_app(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    payload = {
        "artifactId": "workflow-healthcheck",
        "tenantId": "demo",
        "userId": "user-demo",
        "userPrompt": "Generate one short LinkedIn post about best practices for modern software development, team collaboration, and building scalable systems.",
        "projectId": "workflow-test",
        "platforms": ["linkedin"],
        "persona": DEFAULT_PERSONA,
        "angleCount": 1,
        "responseFormat": "text",
        "stream": False,
    }

    for attempt in range(1, max_attempts + 1):
        try:
            post_json(payload)
            return
        except error.URLError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    root_output_dir = base_dir / "outputs" / "single_persona"
    root_output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = root_output_dir / timestamp
    output_dir.mkdir(parents=True, exist_ok=True)

    wait_for_app()

    for case in CASES:
        payload = {
            "artifactId": case["artifactId"],
            "tenantId": "demo",
            "userId": "user-demo",
            "userPrompt": "Create engaging content about best practices for modern software development, team collaboration, and building scalable systems.",
            "projectId": "workflow-test",
            "platforms": case["platforms"],
            "persona": DEFAULT_PERSONA,
            "angleCount": case["angleCount"],
            "responseFormat": "text",
            "stream": False,
        }
        response = post_json(payload)
        output_path = output_dir / f"{case['name']}_pretty.json"
        output_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
