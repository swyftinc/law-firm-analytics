#!/usr/bin/env python3
"""Run a few of the eval prompts through the Claude API with the skills uploaded.

Needs ANTHROPIC_API_KEY in the environment and network access. Standard library only.
It uploads both skills (skills/ must be built: python3 tools/build.py), runs each prompt in a
code execution container with the skill attached, downloads the files the run created, and checks them
against the answer key in evals/ground_truth.json. It deletes the uploaded skills when it finishes.

Usage: python3 tools/run_api_evals.py [--model claude-sonnet-5-5] [--keep-skills]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
import uuid

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
API = "https://api.anthropic.com"
HEADERS = {"x-api-key": os.environ.get("ANTHROPIC_API_KEY", ""), "anthropic-version": "2023-06-01"}

CASES = [
    {"name": "chart-sample-firm", "skill": "analyst-grade-charts",
     "prompt": "Use analyst-grade-charts on the sample firm that comes with the skill. Which lead sources should it put more money into? Save the page as firm-charts.html.",
     "file": r"\.html$", "must": [r"\$8[56]\d", r"data-chart=\"(dumbbell|bar_h)\""], "must_not": ["\N{EM DASH}"]},
    {"name": "brief-sample-firm", "skill": "monday-8am-briefing",
     "prompt": "Use monday-8am-briefing on the sample firm that comes with the skill and write this Monday's briefing. Save the memo as monday-briefing.html.",
     "file": r"\.html$", "must": [r"\$861", r"LSA"], "must_not": ["\N{EM DASH}", "[Ww]orst"]},
]


def call(method, path, body=None, headers=None, raw=False):
    h = dict(HEADERS)
    h.update(headers or {})
    req = urllib.request.Request(API + path, data=body, method=method, headers=h)
    with urllib.request.urlopen(req, timeout=600) as r:
        data = r.read()
    return data if raw else json.loads(data)


def upload_skill(name):
    boundary = uuid.uuid4().hex
    parts = []
    base = os.path.join(ROOT, "skills", name)
    for dp, _, files in os.walk(base):
        for f in sorted(files):
            if f == ".DS_Store":
                continue
            p = os.path.join(dp, f)
            rel = os.path.join(name, os.path.relpath(p, base))
            parts.append(f'--{boundary}\r\nContent-Disposition: form-data; name="files[]"; filename="{rel}"\r\n'
                         f'Content-Type: application/octet-stream\r\n\r\n'.encode() + open(p, "rb").read() + b"\r\n")
    body = b"".join(parts) + f"--{boundary}--\r\n".encode()
    return call("POST", "/v1/skills", body, {"content-type": f"multipart/form-data; boundary={boundary}"})


def run_case(case, skill_id, model):
    messages = [{"role": "user", "content": case["prompt"]}]
    container = {"skills": [{"type": "custom", "skill_id": skill_id, "version": "latest"}]}
    file_ids, text = [], ""
    for _ in range(12):   # a long run can pause and need continuing
        resp = call("POST", "/v1/messages", json.dumps({
            "model": model, "max_tokens": 8000, "container": container, "messages": messages,
            "tools": [{"type": "code_execution_20250825", "name": "code_execution"}]}).encode(),
            {"content-type": "application/json"})
        for item in resp.get("content", []):
            if item.get("type") == "text":
                text = item["text"]
            if item.get("type") == "bash_code_execution_tool_result":
                for f in (item.get("content") or {}).get("content", []) or []:
                    if f.get("file_id"):
                        file_ids.append(f["file_id"])
        if resp.get("container", {}).get("id"):
            container = {"id": resp["container"]["id"], "skills": container["skills"]}
        if resp.get("stop_reason") != "pause_turn":
            break
        messages.append({"role": "assistant", "content": resp["content"]})
    return text, file_ids


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="claude-sonnet-5-5")
    ap.add_argument("--keep-skills", action="store_true")
    a = ap.parse_args()
    if not HEADERS["x-api-key"]:
        sys.exit("Set ANTHROPIC_API_KEY first.")
    skills = {}
    failures = 0
    try:
        for name in sorted({c["skill"] for c in CASES}):
            skills[name] = upload_skill(name)["id"]
            print(f"uploaded {name}: {skills[name]}")
        for c in CASES:
            text, ids = run_case(c, skills[c["skill"]], a.model)
            body = ""
            for fid in ids:
                meta = call("GET", f"/v1/files/{fid}")
                if re.search(c["file"], meta.get("filename", "")):
                    body = call("GET", f"/v1/files/{fid}/content", raw=True).decode("utf-8", "replace")
            ok = bool(body)
            problems = [] if ok else ["no matching file was created"]
            for pat in c["must"]:
                if body and not re.search(pat, body):
                    problems.append(f"missing {pat}")
            for pat in c["must_not"]:
                if body and re.search(pat, body):
                    problems.append(f"found forbidden {pat!r}")
            print(("PASS " if not problems else "FAIL ") + c["name"], problems or "")
            failures += bool(problems)
    finally:
        if not a.keep_skills:
            for sid in skills.values():
                try:
                    call("DELETE", f"/v1/skills/{sid}")
                except Exception as e:  # keep going
                    print("could not delete", sid, e)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
