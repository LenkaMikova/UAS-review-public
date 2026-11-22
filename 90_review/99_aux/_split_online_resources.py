"""One-shot splitter from a monolith `_online-resources.qmd`.

Files already exist. Current order is first `@or-*` in `review.qmd`
(`_reorder_or_by_first_mention.py`). Do not run this against the include list.
"""
from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "92_appendix" / "_online-resources.qmd"


def main() -> None:
    text = SRC.read_text(encoding="utf8")
    if "{{< include" in text and "::: {#or-" not in text:
        sys.exit(
            "Already split. Order is first mention in review.qmd — "
            "python 90_review/99_aux/_reorder_or_by_first_mention.py"
        )
    sys.exit("Monolith split is done. Use _reorder_or_by_first_mention.py to renumber.")


if __name__ == "__main__":
    main()
