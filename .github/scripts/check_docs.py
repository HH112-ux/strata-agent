#!/usr/bin/env python3
"""仓库文档基线检查：YAML 可解析、相对链接可解析、spec 模板必填小节存在。

只依赖标准库与 PyYAML。任一项失败即退出码 1，用于 CI 阻断。
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKIP_DIRS = {".git", "node_modules", ".venv", "venv", "target", "build"}

REQUIRED_SECTIONS = {
    "specs/_templates/spec.md": [
        "## 1. 背景与问题",
        "## 2. 范围",
        "## 4. 功能需求",
        "## 5. 非功能需求",
        "## 8. 成功标准",
        "## 10. 验收方式",
    ],
    "specs/_templates/plan.md": [
        "## 1. 摘要",
        "## 3. 宪法符合性检查（GATE）",
        "## 7. 复杂度与例外登记",
        "## 9. 风险",
    ],
    "specs/_templates/tasks.md": [
        "## 格式约定",
        "## 依赖与执行顺序",
        "## 完成定义（DoD）",
    ],
    "specs/_templates/adr.md": [
        "## 背景（Context）",
        "## 决策（Decision）",
        "## 备选方案（Alternatives Considered）",
        "## 后果（Consequences）",
    ],
}

errors: list[str] = []
checks = 0


def walk(suffix: str) -> list[Path]:
    files = []
    for path in ROOT.rglob(f"*{suffix}"):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        files.append(path)
    return sorted(files)


def check_yaml() -> None:
    global checks
    files = sorted(set(walk(".yaml")) | set(walk(".yml")))
    checks += 1
    print(f"[check] yaml parse: {len(files)} file(s)")
    for path in files:
        rel = path.relative_to(ROOT)
        try:
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
        except Exception as exc:  # noqa: BLE001 - 报告任意解析失败
            errors.append(f"{rel}: YAML 解析失败: {exc.__class__.__name__}: {exc}")
            continue
        if not isinstance(data, dict) or not data:
            errors.append(f"{rel}: YAML 顶层必须是空对象以外的映射")
            continue
        print(f"  ok  {rel}")


def strip_code_blocks(text: str) -> str:
    kept, fenced = [], False
    for line in text.splitlines():
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        kept.append("" if fenced else line)
    return "\n".join(kept)


LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")


def check_links() -> None:
    global checks
    files = walk(".md")
    checks += 1
    total, broken = 0, 0
    print(f"[check] markdown relative links: {len(files)} file(s)")
    for path in files:
        rel = path.relative_to(ROOT)
        text = strip_code_blocks(path.read_text(encoding="utf-8"))
        for lineno, line in enumerate(text.splitlines(), start=1):
            for target in LINK_RE.findall(line):
                if re.match(r"^(https?:|mailto:|tel:)", target) or target.startswith("#"):
                    continue
                total += 1
                clean = unquote(target.split("#", 1)[0].split("?", 1)[0])
                if not clean:
                    continue
                resolved = (ROOT / clean.lstrip("/")) if clean.startswith("/") else (path.parent / clean)
                if not resolved.exists():
                    broken += 1
                    errors.append(f"{rel}:{lineno}: 链接目标不存在: {target}")
    print(f"  {total} link(s) checked, {broken} broken")


def check_templates() -> None:
    global checks
    checks += 1
    print(f"[check] spec template sections: {len(REQUIRED_SECTIONS)} file(s)")
    for rel_path, sections in REQUIRED_SECTIONS.items():
        path = ROOT / rel_path
        if not path.exists():
            errors.append(f"{rel_path}: 模板文件不存在")
            continue
        text = path.read_text(encoding="utf-8")
        missing = [section for section in sections if section not in text]
        if missing:
            errors.append(f"{rel_path}: 缺少必填小节: {', '.join(missing)}")
            continue
        print(f"  ok  {rel_path}")


def main() -> int:
    check_yaml()
    check_links()
    check_templates()

    if errors:
        print(f"\n== {len(errors)} error(s) in {checks} check(s)", file=sys.stderr)
        for item in errors:
            print(f"[fail] {item}", file=sys.stderr)
        return 1

    print(f"\n== all {checks} checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
