# Study 3: The Lean Toward a Famous Name on Identical Records in Public Checkpoints, and a Familiar Name in the Three-Shot Plain Prompt

## The Lean Toward a Famous Name on Identical Records

We also scored public checkpoints of OLMo 2 7B, whose training stages are all released, and the base and
instruction-tuned versions of Llama 3.1 8B and Qwen 2.5 7B. No model was trained here. Each page had five options,
two of which had identical records, one under a famous name and one under an unfamiliar name. D is the log odds of the
famous option's letter against the unfamiliar option's letter with brand names, minus the same log odds without brand names, so a positive D is a lean toward the famous name. We report D for each checkpoint in the table below.

| Model and checkpoint | Prompt format | D (95% interval) |
|:---------------------------------------------------|:-----------|-----------------------:|
| OLMo 2 7B, released base model | plain | −0.049 (−0.078 to −0.021) |
| OLMo 2 7B, end of the first pretraining stage | plain | −0.038 (−0.069 to −0.006) |
| OLMo 2 7B, after instruction tuning | plain | 0.078 (−0.000 to 0.157) |
| OLMo 2 7B, after instruction tuning | chat | 0.229 (0.125 to 0.332) |
| OLMo 2 7B, after preference tuning | chat | 0.314 (0.152 to 0.476) |
| OLMo 2 7B Instruct (released) | chat | 0.250 (0.096 to 0.404) |
| Llama 3.1 8B, base | plain | 0.024 (−0.019 to 0.067) |
| Llama 3.1 8B Instruct | chat | 0.227 (0.069 to 0.386) |
| Qwen 2.5 7B, base | plain | −0.143 (−0.248 to −0.037) |
| Qwen 2.5 7B Instruct | chat | −1.135 (−1.877 to −0.392) |
| OLMo 2 7B, base to instruction tuning (change in D) | plain | 0.127 (0.064 to 0.191) |

Table: The Lean Toward a Famous Name on Identical Records in Public Checkpoints

*Notes:* D: the log odds of the famous option's letter against the unfamiliar option's letter with brand names, minus the same log odds without them; a positive D is a lean toward the famous name. 134 held-out tables in 13 fields; 95% t intervals over the 13 fields' means. The last row is the change in D from the base model to the model after instruction tuning, on identical inputs.

In OLMo 2, no checkpoint of pretraining leans toward the famous name: the released base model leans slightly toward
the unfamiliar name, and the first checkpoint whose interval for D lies above zero, in the chat format, is the model
after instruction tuning. Llama 3.1 shows
no lean in its base model and a lean toward the famous name after instruction tuning. Both Qwen 2.5 models lean toward
the unfamiliar name. Two limits apply. Every OLMo checkpoint failed the check that the model uses the tied records, so in OLMo D measures what a name does when the model does not use the records. D comes from 134 tables in 13 domains, a
summary of which had been examined, so they are not a held-out test of D.

## A Familiar Name in the Three-Shot Plain Prompt

The main text measures the effect of tuning as Studies 1 and 2 measure the effect of the fictitious name, on Study 1a's
30 tables (Study 3, "Effect Across Stages of Training"). In the three-shot plain prompt, a familiar name on the
optimal product changed its probability, relative to no brand names, by
−8.2 points in OLMo 2 7B Instruct (95% CI
= [−10.5, −6.0]) and
−9.2 in Llama 3.1 8B Instruct (95% CI =
[−12.9, −6.0]), against
−2.1 (95% CI =
[−2.9, −1.5]) and
−6.5 (95% CI =
[−8.3, −4.8]) in their base models, and by
−0.8 points (95% CI =
[−1.9, 0.2]) in Llama 3.1 8B Instruct's own chat
template.
