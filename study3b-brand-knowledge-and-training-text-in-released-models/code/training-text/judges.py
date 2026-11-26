"""The judges' answers that the training text's analysis reads: each question's values in the codebook, and Fleiss'
kappa over the three judges."""

VALUES = {"sense": ("yes", "no"), "sentiment": ("positive", "neutral", "negative", "mixed"), "recommends": ("yes", "no"),
          "kind": ("promotional", "review", "news_or_information", "listing", "other")}


def fleiss_kappa(counts):
    """counts: one row an item, one column a category, each row summing to the same number of raters."""
    rows = [r for r in counts if sum(r)]
    if not rows:
        return None
    m = sum(rows[0])
    n = len(rows)
    p_j = [sum(r[j] for r in rows) / (n * m) for j in range(len(rows[0]))]
    p_i = [(sum(x * x for x in r) - m) / (m * (m - 1)) for r in rows]
    pbar, pe = sum(p_i) / n, sum(p * p for p in p_j)
    return round((pbar - pe) / (1 - pe), 4) if pe < 1 else None
