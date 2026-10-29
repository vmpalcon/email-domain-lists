#!/usr/bin/env python3
"""Maintain the email domain lists.

Usage:
  python3 maintain.py check   <email-or-domain>...
  python3 maintain.py add     <disposable|free> <domain>...
  python3 maintain.py remove  <disposable|free> <domain>...
  python3 maintain.py merge   <disposable|free> <file.json|file.txt>
  python3 maintain.py lint    [--fix]
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LISTS = {
    "disposable": ROOT / "disposable-email-domains.json",
    "free": ROOT / "free-email-domain.json",
}
DOMAIN_RE = re.compile(r"^(?=.{1,253}$)([a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?\.)+[a-z0-9-]{2,63}$")


def normalize(value):
    """Lowercase, trim, and strip any 'user@' prefix or trailing dot."""
    value = value.strip().lower().rstrip(".")
    return value.rsplit("@", 1)[-1]


def load(name):
    return json.loads(LISTS[name].read_text())


def save(name, domains):
    data = sorted(set(domains))
    LISTS[name].write_text(json.dumps(data, indent=2) + "\n")
    return len(data)


def read_source(path):
    text = Path(path).read_text()
    if path.endswith(".json"):
        return json.loads(text)
    # Plain text: one domain per line, '#' comments allowed.
    return [line.split("#", 1)[0] for line in text.splitlines()]


def cmd_check(values):
    lists = {name: set(load(name)) for name in LISTS}
    for value in values:
        domain = normalize(value)
        hits = [name for name, domains in lists.items() if domain in domains]
        print(f"{domain}: {', '.join(hits) or 'not listed'}")


def cmd_add(name, values):
    domains = set(load(name))
    new = {normalize(v) for v in values if v.strip()}
    invalid = sorted(d for d in new if not DOMAIN_RE.match(d))
    if invalid:
        sys.exit(f"Invalid domain(s): {', '.join(invalid)}")
    added = new - domains
    total = save(name, domains | new)
    print(f"Added {len(added)} to {name} ({total} total)")


def cmd_remove(name, values):
    domains = set(load(name))
    gone = {normalize(v) for v in values} & domains
    total = save(name, domains - gone)
    print(f"Removed {len(gone)} from {name} ({total} total)")


def cmd_lint(fix):
    ok = True
    for name in LISTS:
        raw = load(name)
        clean = sorted({normalize(d) for d in raw})
        invalid = [d for d in clean if not DOMAIN_RE.match(d)]
        issues = []
        if len(raw) != len(set(raw)):
            issues.append(f"{len(raw) - len(set(raw))} duplicates")
        if raw != clean:
            issues.append("not normalized/sorted")
        if invalid:
            issues.append(f"{len(invalid)} invalid: {', '.join(invalid[:5])}")
        print(f"{name}: {len(raw)} domains, {'; '.join(issues) or 'OK'}")
        if issues:
            ok = False
            if fix:
                total = save(name, [d for d in clean if d not in invalid])
                print(f"  fixed -> {total} domains")
    if not ok and not fix:
        sys.exit(1)


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "check" and args:
        cmd_check(args)
    elif cmd in ("add", "remove", "merge") and len(args) >= 2 and args[0] in LISTS:
        if cmd == "remove":
            cmd_remove(args[0], args[1:])
        else:
            values = read_source(args[1]) if cmd == "merge" else args[1:]
            cmd_add(args[0], values)
    elif cmd == "lint":
        cmd_lint("--fix" in args)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:])
