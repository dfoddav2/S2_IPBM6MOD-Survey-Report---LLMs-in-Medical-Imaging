#!/usr/bin/env python3
"""
Medical Image Analysis using MLLMs via oMLX
Analyzes medical images from NEJM Image Challenge
"""

import base64
import os
import re
import requests
from pathlib import Path
from typing import Optional

# oMLX Configuration
OMLX_URL = "http://127.0.0.1:8000"
OMLX_MODEL = "Qwen3.6-35B-A3B-Claude-4.7-Opus-Reasoning-Distilled-MLX-oQ4-MTP"
OMLX_API_KEY = os.environ.get("OMLX_API_KEY")

# Instruction appended to prompts to keep model output short
CONCISE_INSTRUCTION = (
    "\n\nPlease provide a concise answer. "
    "State only the most likely diagnosis in one line."
)


def encode_image_to_base64(image_path: str | Path) -> str:
    """Encode image to base64 string"""
    with open(image_path, 'rb') as f:
        return base64.b64encode(f.read()).decode('utf-8')


def parse_case_file(md_path: Path) -> dict:
    """
    Parse a NEJM case markdown file into structured data.

    Returns dict with keys: description, options (list), answer, success_rate
    """
    text = md_path.read_text(encoding='utf-8')

    def extract_section(name: str) -> str:
        m = re.search(rf"{name}:\s*\n?(.*?)(?:\n[A-Z][a-z]+:|\Z)", text, re.DOTALL)
        return m.group(1).strip() if m else ""

    description = extract_section("Description")
    options_block = extract_section("Options")
    options = [o.lstrip("- ").strip() for o in options_block.splitlines() if o.strip()]

    answer_m = re.search(r"Answer:\s*\n?(.*?)(?:\n\(success rate:|\Z)", text, re.DOTALL)
    answer = answer_m.group(1).strip() if answer_m else ""

    rate_m = re.search(r"success rate:\s*([\d%]+)", text)
    success_rate = rate_m.group(1).strip() if rate_m else "unknown"

    return {
        "description": description,
        "options": options,
        "answer": answer,
        "success_rate": success_rate,
    }


def analyze_image_with_omlx(
    image_path: str | Path,
    question: str,
    options: Optional[list] = None,
    omlx_url: str = OMLX_URL,
    model: str = OMLX_MODEL,
) -> dict:
    """
    Send medical image and question to oMLX for analysis.

    Args:
        image_path: Path to the image file (str or Path)
        question: The question to ask about the image
        options: Optional list of multiple choice options
        omlx_url: Base URL of the oMLX server
        model: Model name to use

    Returns:
        Dictionary with the model's response
    """
    image_base64 = encode_image_to_base64(image_path)

    prompt = f"Description:\n{question}\n"
    if options:
        prompt += "\nOptions:\n"
        for option in options:
            prompt += f"- {option}\n"
    prompt += CONCISE_INSTRUCTION

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{image_base64}"
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
        "temperature": 0.7,
        "max_tokens": 500,
    }

    headers = {"Content-Type": "application/json"}
    if OMLX_API_KEY:
        headers["Authorization"] = f"Bearer {OMLX_API_KEY}"

    try:
        response = requests.post(
            f"{omlx_url}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=180,
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        return {"error": f"{e.response.status_code} {e.response.reason}: {e.response.text}"}
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def parse_response(response: dict) -> str:
    """Extract the answer from oMLX response"""
    if "error" in response:
        return f"Error: {response['error']}"
    try:
        return response["choices"][0]["message"]["content"]
    except (KeyError, IndexError):
        return "Could not parse response"


def discover_cases(script_dir: Path) -> list:
    """Find all NEJM case pairs (.md + .jpeg) in the script directory."""
    cases = []
    for md_path in sorted(script_dir.glob("nejm-*.md")):
        stem = md_path.stem
        image_path = script_dir / f"{stem}.jpeg"
        if not image_path.exists():
            continue
        case_data = parse_case_file(md_path)
        case_data["image_path"] = image_path
        case_data["id"] = stem
        cases.append(case_data)
    return cases


def main():
    """Run image analysis across all discovered NEJM cases."""
    print("=" * 60)
    print("NEJM Image Challenge Analysis")
    print("=" * 60)

    if not OMLX_API_KEY:
        print("\nWARNING: OMLX_API_KEY environment variable is not set.")
        print("If your oMLX server requires auth, run: export OMLX_API_KEY='your-key'")

    print(f"\nUsing endpoint: {OMLX_URL}/v1/chat/completions")
    print(f"Using model: {OMLX_MODEL}")

    script_dir = Path(__file__).parent
    cases = discover_cases(script_dir)

    if not cases:
        print("\nNo NEJM cases found. Expected nejm-*.md + nejm-*.jpeg pairs.")
        return

    print(f"\nFound {len(cases)} case(s): {[c['id'] for c in cases]}")

    summary = []

    for i, case in enumerate(cases, 1):
        print("\n" + "#" * 60)
        print(f"# CASE {i}/{len(cases)}: {case['id']}")
        print("#" * 60)
        print(f"Description: {case['description'][:120]}...")
        print(f"Expected answer: {case['answer']} (human success: {case['success_rate']})")

        print(f"\n[TEST 1] {case['id']} - Analyzing WITHOUT options...")
        result1 = analyze_image_with_omlx(case["image_path"], case["description"])
        answer1 = parse_response(result1)
        print(f"Response: {answer1}")

        print(f"\n[TEST 2] {case['id']} - Analyzing WITH options...")
        result2 = analyze_image_with_omlx(
            case["image_path"], case["description"], options=case["options"]
        )
        answer2 = parse_response(result2)
        print(f"Response: {answer2}")

        summary.append(
            {
                "id": case["id"],
                "expected": case["answer"],
                "no_options": answer1,
                "with_options": answer2,
            }
        )

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for s in summary:
        print(f"\n{s['id']}")
        print(f"  Expected:      {s['expected']}")
        print(f"  No options:    {s['no_options']}")
        print(f"  With options:  {s['with_options']}")


if __name__ == "__main__":
    main()