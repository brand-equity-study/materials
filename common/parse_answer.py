"""The letter an answer recommends. The system prompt asks for the letter alone on the first line; the parser takes
that line first, and reads the body only when the first line holds no letter.

    pick(answer) -> (letter, how)   how: "first-line", "body", "several" (no letter returned), "none"
    final_answer(raw) -> the text that pick reads from a model's raw output (its reasoning removed)
"""
import re

_THINK = re.compile(r"<think>.*?</think>", re.S)
_HARMONY_REASONING = re.compile(r"\s*analysis(?=[A-Z])")


def final_answer(raw):
    """The part of a model's raw output that is its answer. A closed reasoning block (<think> ... </think>) is removed,
    and so is reasoning before a closing </think> whose opening tag was in the prompt; a reasoning block left open is
    unread (""). The gpt-oss models write in a format whose special tokens the runner drops, so that the reasoning
    reads 'analysisWe need ...' and the answer follows 'assistantfinal': only the text after the last 'assistantfinal'
    is kept, and an output that never reached it is unread. Added on 21 November 2026, when a check found that the
    parser had read the gpt-oss models' letters from their reasoning in 3,162 and 3,312 of 6,120 answers to the
    original tables."""
    text = _THINK.sub("", raw or "")
    if "</think>" in text:
        text = text.rsplit("</think>", 1)[1]
    if "<think>" in text:
        return ""
    if "assistantfinal" in text:
        return text.rsplit("assistantfinal", 1)[1].strip()
    if _HARMONY_REASONING.match(text):
        return ""
    return text.strip()

_FIRST = re.compile(r"^[\s*_#>`\"'(\[]*(?:(?:product|option|answer|recommendation)\s*:?\s*)?([A-E])"
                    r"(?:\s*$|\s*[.:)\]*_`\"'—–-])", re.I)
_BODY = re.compile(r"\b(?:Product|Option)\s+([A-E])\b|\brecommend(?:ing|ed)?\s+(?:Product\s+|Option\s+)?([A-E])\b")


def pick(answer):
    text = (answer or "").strip()
    if not text:
        return "", "none"
    first = next((l for l in text.split("\n") if l.strip()), "")
    m = _FIRST.match(first)
    if m and m.group(1).isupper():
        return m.group(1), "first-line"
    found = {a or b for a, b in _BODY.findall(text)}
    if len(found) == 1:
        return found.pop(), "body"
    if len(found) > 1:
        return "", "several"
    return "", "none"
