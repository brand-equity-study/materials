# Study 4: People's Choices After a Recommendation

In Study 4, we tested whether people choose the product that an AI shopping assistant recommends.

## Design

Participants on Prolific named a product that they wanted and chatted with an AI shopping assistant, which showed a
table of seven products. One product of a lesser-known brand was at least as good as every other product on every
attribute and was priced no higher. The assistant then recommended a familiar brand's product (`Biased` in the data),
the better product (`Honest`), or no product (`Neutral`), and the participant chose one of the seven. The
preregistration is at https://aspredicted.org/xx53wm.pdf, and its text is in `materials/preregistration.md`.

## Data

| File | Contents |
|---|---|
| `data/chat_experiment.csv` | the 769 participants kept after the preregistered exclusions, with their choices, ratings and demographics |
| `data/chat_judge_recommendation.csv` | what the assistant recommended in each conversation, coded by Claude Sonnet 4.6 |
| `data/chat_judge_awareness.csv` | whether each participant noticed the manipulation, coded by Claude Sonnet 4.6 |
| `data/fallback/fallback-shown.csv` | whether a stored recommendation text was shown because the assistant's reply came back empty |

The conversations and the participants' own words are withheld to protect their privacy (`WITHHELD.md`).

## Analysis

`code/analyze.py chat` applies the preregistered exclusions and tests, and `analyze.py S1`, `S2` and `S3` run the
supplemental studies. The results are in `results/numbers.json`. `code/study4_empty_replies.py` repeats the main tests
without the sessions in which a stored recommendation was shown (`results/study4-empty-replies.json`).

## Materials

`materials/` has the survey file (`survey.qsf`), the chat page and its code (`chat_page.html`, `chat_widget.js`,
`brand_skins.js`, `chat_service.js`), the assistant's instructions, three example conversations, the preregistration and
the codebook.
