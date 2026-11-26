# Supplemental Study S4: People and Language Models as Advisors

In S4, we compared people's choices with the models' choices on the same product tables.

## Design

Participants on Prolific saw one of the five tables of Study 1b on which the models most often passed over the optimal
product, with a friend's statement of what the friend cares about. They either recommended a product to the friend or
chose one for themselves. We compared their rate of choosing the optimal product with the models' rate on the same
tables. The preregistration is at https://aspredicted.org/pv9ws7.pdf, and its text is in `materials/preregistration.md`.

## Data

| File | Contents |
|---|---|
| `data/S4_advisors.csv` | the 1,209 finished surveys (1,182 kept after the preregistered exclusions) |
| `data/S4_model_arm.json` | the models' rates on the same five tables, from Study 1b's corpus |
| `data/disclosure-codes/codes.csv` | raters' blind coding of why people and models passed over the optimal product |

The participants' own words are withheld (`WITHHELD.md`).

## Analysis

`code/s4_advisors.py` runs the preregistered analysis: the people's rate against the models' rate, with a wild cluster
bootstrap over the 30 models, and the preregistered secondary tests. It writes `results/numbers.json` in about four
minutes.
