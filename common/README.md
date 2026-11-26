# Code That Several Studies Use

## Modules

| File | What it does | Used by |
|---|---|---|
| `parse_answer.py` | reads which product letter a response recommends | every study of models |
| `analyze.py` | the analysis of Study 1a's design: the optimal product's share in each version, the effect of the fictitious name and its change with the experience attributes | Studies 1a, 1b, 2a and 2b |
| `common.py` | the corpus's files, labels and shared functions | Studies 1a and 1b, and the brand-level analysis |
| `decline.py`, `write_declines.py` | tells a decline (a response that recommends no product) from a response whose recommendation cannot be read | Studies 1c and 2a |

## Code that made the tables and prompts

The `tables/` folder has the code that wrote every prompt of Study 1a's design. `tables.py` renders a table from the
34 tables in `experiment/assortments.py`, removes the brand clues listed in `scrub.py`, and sets the optimal product's
price. `dominant_sets.py` makes the versions of 30 tables with an optimal product, and `dominance_key.py` gives the
better direction of every attribute. `gates.py` has the checks that refuse a set of prompts: that the optimal product
is at least as good on every attribute, that no prompt without brand names names a brand, and that no prompt names the
optimal product. `build_items.py` writes both sets of Study 1a's prompts again, record for record.
