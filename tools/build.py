#!/usr/bin/env python3
"""Assemble the two skills from src/, validate them, and zip them for upload.

Usage:
    python3 tools/build.py            # rebuild skills/ and dist/*.zip, validate
    python3 tools/build.py --check    # rebuild into a temp folder and fail if skills/ differs (used in CI)

Each skill is a folder: SKILL.md, scripts/, references/, assets/sample-data/.
Shared scripts and references live once in src/shared and are copied into both skills, so each
skill works on its own after upload. The zip puts the skill folder at the archive root, which
claude.ai requires. Standard library only.
"""
from __future__ import annotations

import argparse
import filecmp
import os
import re
import shutil
import sys
import tempfile
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILLS = ["analyst-grade-charts", "monday-8am-briefing"]
BRIEFING_ONLY = {"briefing-craft.md", "example-briefing.md"}
DESC_MAX = 200           # claude.ai upload limit; the API allows 1024
RESERVED = ("claude", "anthropic")
EM_DASH = "\N{EM DASH}"
TEXT_EXT = (".md", ".py", ".json", ".csv", ".txt", ".html", ".yml", ".yaml")


def _load_denylist():
    """Names that must never appear in the public skills. The list itself stays out of the repo."""
    path = os.path.join(ROOT, "tools", "denylist.local.txt")
    if not os.path.exists(path):
        return []
    return [ln.strip() for ln in open(path, encoding="utf-8") if ln.strip() and not ln.startswith("#")]


DENYLIST = _load_denylist()


def copytree(src, dst, skip=lambda p: False):
    for base, dirs, files in os.walk(src):
        dirs[:] = sorted(d for d in dirs if d not in ("__pycache__",) and not d.startswith("."))
        rel = os.path.relpath(base, src)
        os.makedirs(os.path.join(dst, rel) if rel != "." else dst, exist_ok=True)
        for f in sorted(files):
            if f == ".DS_Store" or f.endswith(".pyc") or skip(os.path.join(rel, f)):
                continue
            shutil.copy2(os.path.join(base, f), os.path.join(dst, rel, f) if rel != "." else os.path.join(dst, f))


def build_into(out_root):
    for name in SKILLS:
        d = os.path.join(out_root, name)
        os.makedirs(d, exist_ok=True)
        shutil.copy2(os.path.join(ROOT, "src", "skills", name, "SKILL.md"), os.path.join(d, "SKILL.md"))
        copytree(os.path.join(ROOT, "src", "shared", "scripts"), os.path.join(d, "scripts"))
        refs_skip = (lambda p: os.path.basename(p) in BRIEFING_ONLY) if name == "analyst-grade-charts" else (lambda p: False)
        copytree(os.path.join(ROOT, "src", "shared", "references"), os.path.join(d, "references"), refs_skip)
        copytree(os.path.join(ROOT, "sample-data", "super-duper-law"), os.path.join(d, "assets", "sample-data"))


def parse_frontmatter(text):
    if not text.startswith("---\n"):
        return None, "SKILL.md must start with ---"
    end = text.find("\n---", 4)
    if end < 0:
        return None, "frontmatter is not closed"
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if m:
            v = m.group(2).strip()
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
            fm[m.group(1)] = v
    return fm, None


def validate(out_root):
    errors = []
    for name in SKILLS:
        d = os.path.join(out_root, name)
        text = open(os.path.join(d, "SKILL.md"), encoding="utf-8").read()
        fm, err = parse_frontmatter(text)
        if err:
            errors.append(f"{name}: {err}")
            continue
        if fm.get("name") != name:
            errors.append(f"{name}: frontmatter name '{fm.get('name')}' must equal the folder name")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", name) or len(name) > 64:
            errors.append(f"{name}: name must be lowercase letters, digits and single hyphens, 64 characters or fewer")
        if any(r in name for r in RESERVED):
            errors.append(f"{name}: name may not contain a reserved word")
        desc = fm.get("description", "")
        if not desc:
            errors.append(f"{name}: description is missing")
        if len(desc) > DESC_MAX:
            errors.append(f"{name}: description is {len(desc)} characters; claude.ai allows {DESC_MAX}")
        if "<" in desc or ">" in desc:
            errors.append(f"{name}: description may not contain angle brackets")
        if len(text.splitlines()) > 500:
            errors.append(f"{name}: SKILL.md is over 500 lines")
        for base, _, files in os.walk(d):
            for f in files:
                p = os.path.join(base, f)
                rel = os.path.relpath(p, out_root)
                if f.endswith(TEXT_EXT):
                    t = open(p, encoding="utf-8", errors="replace").read()
                    if EM_DASH in t:
                        errors.append(f"{rel}: contains an em dash")
                    if re.search(r"plaintiff (personal injury )?firms?", t, re.I):
                        errors.append(f"{rel}: says 'plaintiff firms'; use 'law firms'")
                    if re.search(r"swyft", t, re.I):
                        errors.append(f"{rel}: mentions the maker; the skills must not")
                    for term in DENYLIST:
                        if term.lower() in t.lower():
                            errors.append(f"{rel}: contains a term from tools/denylist.local.txt")
                            break
        # every [src: id] tag must resolve in foundations.md
        found = set()
        fpath = os.path.join(d, "references", "foundations.md")
        defined = set(re.findall(r"`([a-z0-9-]+)`", open(fpath, encoding="utf-8").read())) if os.path.exists(fpath) else set()
        for base, _, files in os.walk(os.path.join(d, "references")):
            for f in files:
                if f.endswith(".md"):
                    found |= set(re.findall(r"\[src: ([a-z0-9-]+)\]", open(os.path.join(base, f), encoding="utf-8").read()))
        local = {"mcp-build-server", "claude-code-mcp"}   # defined in build-an-mcp.md itself
        missing = sorted(t for t in found - defined - local)
        if missing:
            errors.append(f"{name}: [src: ...] tags with no entry in foundations.md: {missing}")
        for need in ("scripts/inspect_data.py", "scripts/compute_facts.py", "scripts/render.py", "references/chart-doctrine.md",
                     "assets/sample-data/mapping.json"):
            if not os.path.exists(os.path.join(d, need)):
                errors.append(f"{name}: missing {need}")
    return errors


def zip_skill(out_root, name, dist):
    os.makedirs(dist, exist_ok=True)
    path = os.path.join(dist, f"{name}.zip")
    d = os.path.join(out_root, name)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for base, dirs, files in os.walk(d):
            dirs.sort()
            for f in sorted(files):
                p = os.path.join(base, f)
                arc = os.path.join(name, os.path.relpath(p, d))
                info = zipfile.ZipInfo(arc, date_time=(2026, 10, 3, 0, 0, 0))
                info.compress_type = zipfile.ZIP_DEFLATED
                info.external_attr = 0o644 << 16
                z.writestr(info, open(p, "rb").read())
    return path


def trees_equal(a, b):
    cmp = filecmp.dircmp(a, b)
    if cmp.left_only or cmp.right_only or cmp.diff_files or cmp.funny_files:
        return False, cmp.left_only + cmp.right_only + cmp.diff_files
    for sub in cmp.common_dirs:
        ok, diff = trees_equal(os.path.join(a, sub), os.path.join(b, sub))
        if not ok:
            return False, diff
    return True, []


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args(argv)
    if a.check:
        tmp = tempfile.mkdtemp()
        build_into(tmp)
        errs = validate(tmp)
        live = os.path.join(ROOT, "skills")
        for name in SKILLS:
            ok, diff = trees_equal(os.path.join(tmp, name), os.path.join(live, name)) if os.path.isdir(os.path.join(live, name)) else (False, ["missing"])
            if not ok:
                errs.append(f"skills/{name} is out of date with src/ ({diff[:3]}). Run: python3 tools/build.py")
        shutil.rmtree(tmp)
        for e in errs:
            print("FAIL", e)
        print("check:", "FAILED" if errs else "ok")
        sys.exit(1 if errs else 0)
    live = os.path.join(ROOT, "skills")
    if os.path.isdir(live):
        shutil.rmtree(live)
    build_into(live)
    errs = validate(live)
    for name in SKILLS:
        z = zip_skill(live, name, os.path.join(ROOT, "dist"))
        n = sum(len(f) for _, _, f in os.walk(os.path.join(live, name)))
        print(f"{'PASS' if not errs else 'built'} {name}: {n} files, {os.path.getsize(z) // 1024} KB zip -> {os.path.relpath(z, ROOT)}")
    for e in errs:
        print("FAIL", e)
    sys.exit(1 if errs else 0)


if __name__ == "__main__":
    main()
