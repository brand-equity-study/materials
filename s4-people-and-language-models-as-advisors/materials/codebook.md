# Codebook: the human-advisor study

Rows (after anonymisation): **1,209**. Columns: 74. The columns listed are the columns in the deposited file; the wall-clock timestamps and browser fingerprint named in `README.md at the top of the package` were removed before deposit.

| Column | Non-null rows | Type | Note |
|---|---|---|---|
| `participant_id` | 1209 | str |  |
| `approved_submission` | 1209 | str |  |
| `Status` | 1209 | int |  |
| `Progress` | 1209 | int |  |
| `Duration (in seconds)` | 1209 | int |  |
| `Finished` | 1209 | int |  |
| `ResponseId` | 1209 | str | neutral identifier |
| `Q_RecaptchaScore` | 1205 | float |  |
| `attention_1` | 1209 | int |  |
| `choice_timing_First Click` | 1209 | float |  |
| `choice_timing_Last Click` | 1209 | float |  |
| `choice_timing_Page Submit` | 1209 | float |  |
| `choice_timing_Click Count` | 1209 | int |  |
| `comprehension_1` | 1209 | int |  |
| `brand_influence` | 1209 | int |  |
| `social_proof_influence` | 1209 | int |  |
| `belief_neutral` | 1209 | int |  |
| `belief_moreinfo` | 1209 | int |  |
| `belief_personalised` | 1209 | int |  |
| `belief_real` | 1209 | int |  |
| `belief_pickedbest` | 1209 | int |  |
| `demand_item` | 1209 | int |  |
| `believability_dominant` | 1209 | int |  |
| `too_good_to_be_true` | 1209 | int |  |
| `fam_dominant` | 1209 | int |  |
| `fam_focal` | 1209 | int |  |
| `numeracy_1` | 1209 | int |  |
| `ai_literacy` | 1209 | int |  |
| `gender` | 1209 | int |  |
| `age` | 1209 | int |  |
| `consent` | 1209 | str |  |
| `bypass_attempt` | 0 | empty |  |
| `qsf_build` | 1209 | str |  |
| `assignment_version` | 1209 | str |  |
| `assigned_level` | 1209 | str |  |
| `assigned_frame` | 1209 | str |  |
| `assortment_id` | 1209 | str |  |
| `category` | 1209 | str |  |
| `dominant_brand` | 1209 | str |  |
| `focal_brand` | 1209 | str |  |
| `category_intro` | 1209 | str |  |
| `comp_q` | 1209 | str |  |
| `comp_opt1` | 1209 | str |  |
| `comp_opt2` | 1209 | str |  |
| `comp_opt3` | 1209 | str |  |
| `comp_correct` | 1209 | int |  |
| `level_prompt` | 1209 | str |  |
| `table_html` | 1209 | str |  |
| `glossary_full` | 1209 | str |  |
| `glossary_compact` | 1209 | str |  |
| `choice_cards` | 1209 | str |  |
| `choice_stem` | 1209 | str |  |
| `shown_dominant_pos` | 1209 | int |  |
| `shown_focal_pos` | 1209 | int |  |
| `shown_order` | 1209 | str |  |
| `attr1_label` | 1209 | str |  |
| `attr2_label` | 1209 | str |  |
| `attr3_label` | 1209 | str |  |
| `why_verb` | 1209 | str |  |
| `demand_cell` | 1209 | str |  |
| `demand_framing` | 808 | str |  |
| `choice_index` | 1209 | int |  |
| `choice_code` | 1209 | str |  |
| `choice_brand` | 1209 | str |  |
| `choice_is_optimal` | 1209 | int |  |
| `choice_is_focal` | 1209 | int |  |
| `challenge_text` | 1209 | str |  |

Withheld from this copy: `why_free_text`, `challenge_free_text`, `suspicion_open`, `feedback_clarity`, `feedback_technical`, `feedback_realism`, `feedback_improve`. These columns hold the participants' own words or the chat's messages and replies, and they stay with the authors to protect the participants' privacy (README.md at the top of the package). No analysis reads them.

Added in this copy: `suspicion_mentions_brand`, 1 if the answer to the closing question (`suspicion_open`) holds the word "brand" and 0 if not. The analysis's robustness check that leaves out the participants who guessed the hypothesis reads it in place of that answer.
