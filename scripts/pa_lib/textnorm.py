"""Text normalisation, paragraph numbering and verbatim-quote verification.

The quote check is the harness's anti-fabrication gate: an annotation is only
counted as evidence when its quote occurs in the paper text after a symmetric
normalisation (whitespace, full/half-width punctuation, footnote markers).
Paraphrases fail by design.
"""

from __future__ import annotations

import difflib
import re
import unicodedata
from dataclasses import dataclass

_STRIP_BEFORE_NFKC = re.compile(
    "[①-⓿❶-➓¹²³⁰-⁹​-‍﻿]"
)
_BRACKET_REF = re.compile(r"[\[［]\s*\d{1,3}(?:\s*[-,，、]\s*\d{1,3})*\s*[\]］]")
_WS = re.compile(r"\s+")
_DASHES = re.compile("[‐-―−─﹘﹣－-]+")
_DOTS = re.compile(r"\.{2,}")

_PUNCT = str.maketrans({
    "“": '"', "”": '"', "„": '"', "‟": '"', "「": '"', "」": '"',
    "『": '"', "』": '"', "〝": '"', "〞": '"',
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "，": ",", "、": ",", "。": ".", "．": ".", "…": ".",
    "：": ":", "；": ";", "！": "!", "？": "?",
    "（": "(", "）": ")", "【": "[", "】": "]",
    "《": "<", "》": ">", "〈": "<", "〉": ">",
})


def normalize(text: str) -> str:
    """Symmetric normalisation used on both paper text and quotes."""
    text = _STRIP_BEFORE_NFKC.sub("", text)
    text = unicodedata.normalize("NFKC", text)
    text = _BRACKET_REF.sub("", text)
    text = text.translate(_PUNCT)
    text = _DASHES.sub("-", text)
    text = _DOTS.sub(".", text)
    text = _WS.sub("", text)
    return text.lower()


_PAR_END = ("。", "！", "？", "”", "」", "』")
_HEADING = re.compile(
    r"^(?:[一二三四五六七八九十]+[、.．]|[（(][一二三四五六七八九十\d]+[)）]|\d+(?:\.\d+)*[、.．\s]"
    r"|引言|导言|结语|结论|参考文献|摘\s*要|关\s*键\s*词)"
)


def _is_cjk_heavy(s: str) -> bool:
    cjk = sum(1 for ch in s if "一" <= ch <= "鿿")
    return cjk > len(s) * 0.3


def _join_lines(block: str) -> str:
    sep = "" if _is_cjk_heavy(block) else " "
    return sep.join(line.strip() for line in block.split("\n") if line.strip())


def split_paragraphs(text: str) -> list[str]:
    """Split raw paper text into paragraphs.

    Blank-line separated text is split on blank lines.  Text extracted from PDFs
    usually has hard line wraps and few blank lines; there, short heading-like
    lines become their own paragraph and other lines are re-joined until a line
    ends with paragraph-final punctuation.  Over-splitting is harmless: quotes
    that span two paragraphs still verify (as loc_mismatch at worst).
    """
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    blocks = [b.strip() for b in re.split(r"\n\s*\n", text) if b.strip()]
    if len(blocks) >= 5 or len(text) < 3000:
        return [_join_lines(b) for b in blocks]
    paragraphs: list[str] = []
    buf = ""
    for line in text.split("\n"):
        line = line.strip()
        if not line:
            continue
        if len(line) <= 30 and _HEADING.match(line):
            if buf:
                paragraphs.append(buf)
                buf = ""
            paragraphs.append(line)
            continue
        buf += line
        if line.endswith(_PAR_END):
            paragraphs.append(buf)
            buf = ""
    if buf:
        paragraphs.append(buf)
    return paragraphs


def number_paragraphs(paragraphs: list[str]) -> str:
    return "\n".join(f"[P{i}] {p}" for i, p in enumerate(paragraphs, 1))


_LOC = re.compile(r"P\s*(\d+)(?:\s*[-~–—至]\s*P?\s*(\d+))?", re.I)


def parse_loc(loc: str) -> list[int]:
    """'P12' -> [12]; 'P12-P14' -> [12, 13, 14]; anything else -> []."""
    out: list[int] = []
    for m in _LOC.finditer(loc or ""):
        a = int(m.group(1))
        b = int(m.group(2)) if m.group(2) else a
        if b < a:
            a, b = b, a
        out.extend(range(a, min(b, a + 20) + 1))
    return out


@dataclass
class QuoteResult:
    status: str  # exact | fuzzy | loc_mismatch | miss | too_short | too_long
    ratio: float = 1.0


class QuoteChecker:
    """Verify quotes against one paper's paragraphs."""

    def __init__(self, paragraphs: list[str], *, min_chars: int = 6, max_chars: int = 150,
                 fuzzy: float | None = None):
        self.paragraphs = paragraphs
        self.norm_pars = [normalize(p) for p in paragraphs]
        self.norm_all = "".join(self.norm_pars)
        self.min_chars = min_chars
        self.max_chars = max_chars
        self.fuzzy = fuzzy

    def check(self, quote: str, loc: str = "") -> QuoteResult:
        if len(quote) > self.max_chars:
            return QuoteResult("too_long", 0.0)
        q = normalize(quote)
        if len(q) < self.min_chars:
            return QuoteResult("too_short", 0.0)
        idx = [i for i in parse_loc(loc) if 1 <= i <= len(self.norm_pars)]
        if idx:
            local = "".join(self.norm_pars[i - 1] for i in idx)
            if q in local:
                return QuoteResult("exact")
        if q in self.norm_all:
            return QuoteResult("exact" if not idx else "loc_mismatch")
        if self.fuzzy:
            ratio = self._best_ratio(q)
            if ratio >= self.fuzzy:
                return QuoteResult("fuzzy", ratio)
            return QuoteResult("miss", ratio)
        return QuoteResult("miss", 0.0)

    def _best_ratio(self, q: str) -> float:
        text = self.norm_all
        n = len(q)
        if n < 8:
            return 0.0
        anchors = {q[:4], q[n // 2 - 2 : n // 2 + 2], q[-4:]}
        best = 0.0
        for anchor in anchors:
            start = 0
            hits = 0
            while hits < 50:
                pos = text.find(anchor, start)
                if pos < 0:
                    break
                hits += 1
                offset = q.find(anchor)
                lo = max(0, pos - offset - n // 5)
                hi = min(len(text), pos - offset + n + n // 5)
                window = text[lo:hi]
                sm = difflib.SequenceMatcher(None, q, window, autojunk=False)
                match_len = sum(b.size for b in sm.get_matching_blocks())
                best = max(best, match_len / n)
                start = pos + 1
        return best


_ABSTRACT = re.compile(
    r"(?:内容)?摘\s*要\s*[:：]?\s*(.+?)\s*(?:关\s*键\s*词|关键字|key\s*words|中图分类号)",
    re.S | re.I,
)


def extract_abstract(text: str, limit: int = 1500) -> str:
    m = _ABSTRACT.search(text[:20000])
    if m:
        return _WS.sub("", m.group(1))[:limit]
    return ""
