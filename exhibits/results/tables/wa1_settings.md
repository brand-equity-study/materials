| Model | Thinking flag | Response length in characters, median (largest) | Wordings 1 to 4, with brand names | Wordings 1 to 4, without brand names | Distinct (%), with, without |
|:-----------------------|:---------|---------------:|------------------------:|------------------------:|-------------:|
| Claude Haiku 4.5 | no | 433 (628) | 160, 187, 152, 182 | 165, 179, 172, 164 | 98.4, 97.4 |
| Claude Haiku 4.5 (thinking) | yes | 421 (632) | 169, 183, 171, 158 | 141, 166, 181, 192 | 97.8, 98.4 |
| Claude Opus 4.6 | no | 531 (1,135) | 162, 172, 163, 184 | 184, 165, 167, 164 | 97.5, 97.6 |
| Claude Opus 4.7 | no | 369 (786) | 196, 158, 171, 156 | 178, 166, 165, 171 | 98.2, 96.9 |
| Claude Sonnet 4.6 | no | 492 (987) | 167, 160, 184, 169 | 202, 153, 173, 152 | 98.5, 96.9 |
| Claude Sonnet 4.6 (thinking) | yes | 500 (788) | 161, 160, 182, 178 | 159, 172, 183, 166 | 97.5, 97.8 |
| GPT-4.1 mini | no | 362 (586) | 167, 170, 169, 174 | 179, 169, 158, 174 | 97.8, 97.8 |
| GPT-4.1 nano | no | 323 (443) | 173, 166, 149, 192 | 172, 168, 176, 164 | 97.9, 97.9 |
| GPT-4o | no | 1 (546) | 150, 176, 188, 166 | 170, 176, 179, 155 | 97.9, 97.4 |
| GPT-4o mini | no | 392 (576) | 186, 174, 170, 150 | 164, 182, 159, 175 | 96.8, 97.5 |
| GPT-5 mini | no | 391 (3,502) | 181, 177, 164, 158 | 168, 173, 157, 182 | 98.1, 97.6 |
| GPT-5.4 | no | 400 (542) | 140, 184, 177, 180 | 170, 159, 175, 176 | 96.9, 98.1 |
| GPT-5.4 mini | no | 340 (469) | 167, 154, 188, 172 | 173, 167, 177, 163 | 97.1, 96.9 |
| GPT-5.4 mini (thinking) | yes | 328 (431) | 187, 168, 150, 176 | 162, 171, 196, 151 | 96.5, 97.9 |
| GPT-5.4 nano | no | 360 (591) | 188, 154, 177, 162 | 175, 158, 180, 167 | 98.2, 97.5 |
| Gemini 2.0 Flash | no | 286 (521) | 155, 191, 173, 161 | 168, 173, 164, 175 | 97.9, 97.8 |
| Gemini 2.5 Flash | no | 297 (544) | 171, 169, 166, 174 | 166, 172, 174, 168 | 98.2, 98.4 |
| Gemini 2.5 Flash-Lite | no | 300 (511) | 179, 146, 182, 173 | 178, 185, 144, 173 | 98.1, 97.2 |
| Gemini 2.5 Pro | no | 369 (553) | 143, 192, 183, 162 | 165, 185, 169, 161 | 98.1, 96.9 |
| Gemini 3 Flash | no | 342 (573) | 178, 156, 190, 156 | 163, 159, 180, 178 | 98.1, 97.8 |
| Gemini 3 Flash (thinking) | yes | 342 (507) | 150, 165, 181, 185 | 146, 176, 164, 194 | 98.7, 97.5 |
| Gemini 3.1 Flash-Lite | no | 331 (468) | 150, 189, 155, 187 | 190, 151, 175, 164 | 97.2, 97.9 |
| Gemini 3.1 Pro (thinking) | yes | 326 (549) | 177, 176, 183, 145 | 163, 173, 166, 178 | 96.8, 98.7 |
| Gemma 3 27B | no | 351 (567) | 187, 159, 160, 174 | 170, 175, 164, 171 | 96.9, 97.9 |
| Gemma 4 31B | no | 270 (422) | 171, 171, 177, 162 | 178, 181, 171, 150 | 97.8, 98.2 |
| DeepSeek R1 | both | 393 (1,558) | 148, 154, 174, 204 | 176, 166, 170, 168 | 96.5, 97.6 |
| DeepSeek V3 | no | 366 (1,432) | 161, 185, 175, 159 | 162, 185, 174, 159 | 97.5, 98.4 |
| Llama 3.3 70B | no | 439 (600) | 193, 146, 175, 166 | 176, 202, 157, 145 | 98.2, 98.4 |
| Kimi K2 | no | 347 (775) | 177, 192, 158, 153 | 165, 173, 177, 165 | 97.4, 97.9 |
| Qwen 2.5 72B | no | 272 (484) | 171, 173, 168, 168 | 168, 171, 161, 180 | 98.1, 97.6 |

Table: Settings Recorded With Each Model's Responses {#tbl:model-settings}

::: tnote
*Notes:* From the records of the data collection, for the responses of Study 1b's two conditions, with and without brand names (1,360 or 1,361 responses a model). Every response of every model has a recorded temperature of 1.0. DeepSeek R1 has the flag in 289 responses and not in 1,071. Response length: the number of characters in the recorded response, without any thinking trace; GPT-4o answered with the letter alone in most of its responses. Wordings: the number of responses to each of the four wordings of the instruction, identified from the instruction's text. Distinct: the number of different combinations of product order and letters among the model's responses in that condition, as a percentage of the number of those responses.
:::
