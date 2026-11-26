# Codebook: Study 3

Rows (after anonymisation): **769**. Columns: 115. The columns listed are the columns in the deposited file; the wall-clock timestamps and browser fingerprint named in `README.md at the top of the package` were removed before deposit.

| Column | Non-null rows | Type | Note |
|---|---|---|---|
| `Status` | 769 | int |  |
| `Progress` | 769 | int |  |
| `Duration (in seconds)` | 769 | int |  |
| `Finished` | 769 | int |  |
| `ResponseId` | 769 | str | neutral identifier |
| `consent` | 769 | int |  |
| `timer_stimulus_First Click` | 769 | float | Qualtrics page timer |
| `timer_stimulus_Last Click` | 769 | float | Qualtrics page timer |
| `timer_stimulus_Page Submit` | 769 | float | Qualtrics page timer |
| `timer_stimulus_Click Count` | 769 | float | Qualtrics page timer |
| `dv_trust_helpful` | 769 | float |  |
| `dv_trust_trust` | 769 | float |  |
| `dv_trust_understood` | 769 | float |  |
| `dv_trust_reuse` | 769 | float |  |
| `dv_brand_familiar` | 769 | float |  |
| `attn_check` | 769 | float | attention check response |
| `age` | 769 | float |  |
| `gender` | 769 | float |  |
| `ai_usage` | 769 | float |  |
| `PROLIFIC_PID` | 769 | str | salted hash of the Prolific identifier |
| `STUDY_ID` | 769 | str | the Prolific study identifier, one value per study |
| `SESSION_ID` | 769 | str | salted hash |
| `study3_session_id` | 769 | str | hashed chat session identifier |
| `study3_conversation_complete` | 769 | str |  |
| `study3_total_turns` | 769 | float |  |
| `study3_assortment` | 769 | str |  |
| `study3_category` | 769 | str |  |
| `study3_recommended` | 769 | str |  |
| `study3_optimal` | 769 | str |  |
| `study3_condition` | 769 | str |  |
| `product_1` | 769 | str |  |
| `product_2` | 769 | str |  |
| `product_3` | 769 | str |  |
| `product_4` | 769 | str |  |
| `product_5` | 769 | str |  |
| `product_6` | 769 | str |  |
| `product_7` | 769 | str |  |
| `study3_ai_brand` | 769 | str |  |
| `study3_display_order` | 769 | str |  |
| `study3_product_choice` | 769 | str |  |
| `study3_product_choice_price` | 769 | str |  |
| `study3_chose_optimal` | 769 | str |  |
| `study3_chose_recommended` | 769 | str |  |
| `study3_bypass_attempt` | 0 | empty |  |
| `study3_kv_logged` | 769 | str |  |
| `ProductDisplayOrder` | 0 | empty |  |
| `Condition` | 769 | float | assigned condition (BiasedAI, DebiasedAI, NoAI, Inoculation or SpecExposed, as the study defines) |
| `ConditionD` | 769 | str |  |
| `_assortment` | 769 | str |  |
| `_has_assort_content` | 769 | str |  |
| `_json_ok` | 769 | str |  |
| `_json_error` | 769 | str |  |
| `_reached_stage2` | 769 | str |  |
| `dom_brand` | 769 | str |  |
| `dom_price` | 769 | str |  |
| `rec_brand` | 769 | str |  |
| `rec_price` | 769 | str |  |
| `dom_price_num` | 769 | float |  |
| `rec_price_num` | 769 | float |  |
| `price_gap_usd` | 769 | float |  |
| `price_gap_ratio` | 769 | float |  |
| `chose_optimal_bool` | 769 | str |  |
| `chose_recommended_bool` | 769 | str |  |
| `chose_focal_bool` | 769 | str |  |
| `bucket` | 769 | str |  |
| `user_turn_count` | 769 | int |  |
| `convo_complete_bool` | 769 | str |  |
| `attn_pass` | 769 | str |  |
| `consent_agree` | 769 | str |  |
| `duration_s` | 769 | int |  |
| `finished_bool` | 769 | str |  |
| `_verif_ok` | 0 | empty |  |

Withheld from this copy: `msg_1`, `msg_2`, `msg_3`, `msg_4`, `msg_5`, `msg_6`, `msg_7`, `msg_8`, `msg_9`, `msg_10`, `msg_11`, `msg_12`, `msg_13`, `msg_14`, `msg_15`, `msg_16`, `msg_17`, `msg_18`, `msg_19`, `msg_20`, `response_1`, `response_2`, `response_3`, `response_4`, `response_5`, `response_6`, `response_7`, `response_8`, `response_9`, `response_10`, `response_11`, `response_12`, `response_13`, `response_14`, `response_15`, `response_16`, `response_17`, `response_18`, `response_19`, `response_20`, `pilot_feedback`, `suspicion_probe`, `dv_choice_reason`. These columns hold the participants' own words or the chat's messages and replies, and they stay with the authors to protect the participants' privacy (README.md at the top of the package). No analysis reads them.
