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

Table: The Lean Toward a Famous Name on Identical Records in Public Checkpoints {#tbl:s3-olmo}

::: tnote
*Notes:* D: the log odds of the famous option's letter against the unfamiliar option's letter with brand names, minus the same log odds without them; a positive D is a lean toward the famous name. 134 held-out tables in 13 fields; 95% t intervals over the 13 fields' means. The last row is the change in D from the base model to the model after instruction tuning, on identical inputs.
:::
