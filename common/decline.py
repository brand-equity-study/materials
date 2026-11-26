"""Tell a decline apart from an answer that cannot be read, for an answer from which the parser read no letter.

A decline is a readable answer that recommends none of the products because of the products: "None of the provided
options ..."; it is an outcome, not an unread answer, so it leaves the denominator of the share of answers read (the
90 per cent rule). Everything else without a letter is unread: reasoning written as plain text, a request for more
information, a refusal of the role, and a decline that does not open the answer.

    from decline import classify          # "decline" or "unread", for an answer without a letter
"""
import re

DECLINE = [re.compile(p, re.I) for p in (
    r"^\s*none\b",                                                              # "None" where the letter should be
    r"\bnone of (the|these|them|those|this)\b[^.]{0,120}?\b(recommend|fit|meet|worth|suitable|ideal|reliable|"
    r"satisf|should be|good|acceptable|appropriate|match)",
    r"\bnone (fit|fits|meet|meets)\b",
    r"\b(cannot|can't|can not|do not|don't|won't|would not|wouldn't|will not|could not|couldn't)\s+"
    r"(honestly |in good conscience |confidently )?recommend any\b",
    r"\bnot recommend(ing)? any\b",
    r"\bno (single |one )?(products?|options?|items?)\b[^.]{0,60}?\b(meets?|fits?|is recommended|are recommended|"
    r"can be recommended|to recommend|worth|suitable|stands out as)",
    r"\bthere (are|is) no (products?|options?|good options?|suitable)\b",
    r"\bi recommend none\b",
    r"\bnone (are|is) recommended\b",
)]
FALLBACK = re.compile(
    r"if i (must|had to|have to|were to) (choose|pick|select|recommend)|if you must (buy|choose|pick)|"
    r"least (problematic|bad|worst)|(best|top) (overall )?(option|package|choice|pick) among|"
    r"however,? (the |if |product [a-e]\b|i would|i'd)|would be:?\s*(product\s*)?[a-e]\b|"
    r"\bmy (recommendation|pick) (is|would be)\b",
    re.I)


HEAD = 200   # the decline statement must open the answer (every decline in the two samples opens within 200 characters)


def clean(text):
    return re.sub(r"[*_`#>]+", "", text or "").strip()


def classify(text):
    """'decline' or 'unread', for an answer from which the parser read no letter."""
    t = clean(text)
    head = t[:HEAD]
    if any(p.search(head) for p in DECLINE) and not FALLBACK.search(t):
        return "decline"
    return "unread"

