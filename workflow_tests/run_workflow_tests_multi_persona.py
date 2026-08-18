from __future__ import annotations

import json
import time
from datetime import datetime
from pathlib import Path
from urllib import error, request


URI = "http://localhost:8000/generate"
HEADERS = {"Content-Type": "application/json"}
COMPARISON_PLATFORMS = [
    "linkedin",
    "instagram",
    "x",
]

CASES = [
    {
        "name": "sharp_operator_3platforms",
        "artifactId": "workflow-persona-sharp-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "sharp_operator",
    },
    {
        "name": "practical_strategist_3platforms",
        "artifactId": "workflow-persona-strategist-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "practical_strategist",
    },
    {
        "name": "clear_educator_3platforms",
        "artifactId": "workflow-persona-educator-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "clear_educator",
    },
    {
        "name": "calm_expert_3platforms",
        "artifactId": "workflow-persona-calm-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "calm_expert",
    },
    {
        "name": "bold_creator_3platforms",
        "artifactId": "workflow-persona-bold-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "bold_creator",
    },
    {
        "name": "warm_guide_3platforms",
        "artifactId": "workflow-persona-warm-3x",
        "angleCount": 1,
        "platforms": COMPARISON_PLATFORMS,
        "persona": "warm_guide",
    },
    {
        "name": "platform_persona_pairs_sample",
        "artifactId": "workflow-persona-pairs-sample",
        "angleCount": 1,
        "platformPersonaPairs": [
            {"platform": "linkedin", "persona": "sharp_operator"},
            {"platform": "instagram", "persona": "bold_creator"},
            {"platform": "x", "persona": "sharp_operator"},
        ],
    },
]


def post_json(payload: dict) -> dict:
    body = json.dumps(payload).encode("utf-8")
    req = request.Request(URI, data=body, headers=HEADERS, method="POST")
    with request.urlopen(req, timeout=300) as response:
        return json.loads(response.read().decode("utf-8"))


def wait_for_app(max_attempts: int = 30, delay_seconds: float = 2.0) -> None:
    payload = {
        "artifactId": "workflow-healthcheck-multi-persona",
        "tenantId": "demo",
        "userId": "user-demo",
        "userPrompt": "Create engaging content about best practices for modern software development, team collaboration, and building scalable systems.",
        "projectId": "workflow-test",
        "platforms": ["linkedin"],
        "persona": "sharp_operator",
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
    root_output_dir = base_dir / "outputs" / "multi_persona"
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
            "angleCount": case["angleCount"],
            "responseFormat": "text",
            "stream": False,
        }
        if "platformPersonaPairs" in case:
            payload["platformPersonaPairs"] = case["platformPersonaPairs"]
        else:
            payload["platforms"] = case["platforms"]
            if "personas" in case:
                payload["personas"] = case["personas"]
            else:
                payload["persona"] = case["persona"]

        response = post_json(payload)
        output_path = output_dir / f"{case['name']}_pretty.json"
        output_path.write_text(json.dumps(response, indent=2), encoding="utf-8")
        print(f"Saved {output_path}")


if __name__ == "__main__":
    main()
