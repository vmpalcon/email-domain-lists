# Email Domain Lists

Two JSON lists of email domains for validating sign-ups, filtering leads, or flagging non-business addresses.

Maintained by **PurplePatch Services**.

| File | Domains | What it contains |
| --- | ---: | --- |
| [`disposable-email-domains.json`](disposable-email-domains.json) | ~3,600 | Throwaway / temporary inbox providers (e.g. `mailinator.com`, `0-mail.com`). Block these when you need a real, reachable user. |
| [`free-email-domain.json`](free-email-domain.json) | ~30,300 | Free consumer mailbox providers (e.g. `gmail.com`, `yahoo.com`, `outlook.com`). Flag these when you need a work / company email. |

Both files are a flat JSON array of lowercase domain strings:

```json
[
  "0-mail.com",
  "gmail.com"
]
```

> **Note:** the free list is broad and also contains most disposable domains (about 2,600 overlap). If you only want to tell "personal" from "throwaway", check the disposable list first.

## Usage

**JavaScript / TypeScript**

```js
import disposable from "./disposable-email-domains.json" with { type: "json" };
import free from "./free-email-domain.json" with { type: "json" };

const DISPOSABLE = new Set(disposable);
const FREE = new Set(free);

export function classifyEmail(email) {
  const domain = email.trim().toLowerCase().split("@").pop();
  if (DISPOSABLE.has(domain)) return "disposable";
  if (FREE.has(domain)) return "free";
  return "business";
}

classifyEmail("jane@mailinator.com"); // "disposable"
classifyEmail("jane@gmail.com");      // "free"
classifyEmail("jane@acme.com");       // "business"
```

**Python**

```python
import json

DISPOSABLE = set(json.load(open("disposable-email-domains.json")))
FREE = set(json.load(open("free-email-domain.json")))

def classify_email(email: str) -> str:
    domain = email.strip().lower().rsplit("@", 1)[-1]
    if domain in DISPOSABLE:
        return "disposable"
    if domain in FREE:
        return "free"
    return "business"
```

Always load the lists into a `Set` / `set` once at startup; lookups are then O(1).

## Maintaining the lists

[`maintain.py`](maintain.py) is a small dependency-free script (Python 3.8+) that keeps both files clean: lowercase, deduplicated, sorted, and valid domains only. Every write saves the file sorted with 2-space indentation, so diffs stay small and readable.

Check where a domain or address is listed:

```bash
python3 maintain.py check jane@gmail.com mailinator.com
```

Add domains (an `@` prefix and uppercase are stripped automatically; invalid domains are rejected):

```bash
python3 maintain.py add disposable newtempmail.io another-temp.net
```

Remove a domain, for example a false positive reported by a real user:

```bash
python3 maintain.py remove free mycompany.com
```

Merge an upstream list (a JSON array, or a `.txt` with one domain per line and `#` comments):

```bash
python3 maintain.py merge disposable upstream-disposable.txt
```

Check both files for duplicates, ordering and invalid entries (exits with code 1 on problems, so it works in CI):

```bash
python3 maintain.py lint
```

Fix those problems in place:

```bash
python3 maintain.py lint --fix
```

### Suggested workflow

1. Add or merge new domains with `add` / `merge`.
2. Remove anything legitimate that was reported as blocked with `remove`.
3. Run `lint` before committing (or in CI) to keep the files consistent.
4. Review the diff: every change is one domain per line, so additions and removals are easy to spot.

Before merging, check a few entries from the upstream list. A false positive on either list blocks or flags real users.

## Sources

The lists are derived from these upstream projects. Merge from them periodically to pick up new domains:

- **Disposable:** [disposable-email-domains/disposable-email-domains](https://github.com/disposable-email-domains/disposable-email-domains) (`disposable_email_blocklist.conf`), CC0 1.0 (public domain)
- **Free:** [Kikobeats/free-email-domains](https://github.com/Kikobeats/free-email-domains) (`domains.json`), MIT, © 2017 Kiko Beats

## License

[MIT](LICENSE) © 2026 PurplePatch Services. The upstream copyright notices are kept in the [LICENSE](LICENSE) file.
