# Study 3a: Choices of the New Brand on the Tables That Qwen 2.5 7B and 14B Answered Correctly

In the table below, we compare Qwen 2.5 14B with Qwen 2.5 7B on the tables that each model answered correctly. The
14B model trained on promotional pages named the fund in only 5 of 36 responses to the
open questions, so the fund's numbers are given and not interpreted.

| Tables | 14B, promotional, with brand names | 14B, promotional, without brand names | 14B, no pages, with brand names | 7B, promotional, with brand names | 7B, promotional, without brand names | 7B, no pages, with brand names |
|:---------------------|----------:|----------:|----------:|----------:|----------:|----------:|
| Eye hospital | 41 of 108 | 2 of 108 | 1 of 114 | 69 of 78 | 3 of 78 | 13 of 75 |
| Index fund | 33 of 105 | 1 of 105 | 2 of 108 | 56 of 75 | 11 of 75 | 13 of 84 |
| Hiring (fictitious university) | 10 of 42 | 1 of 42 | 6 of 93 | 26 of 66 | 0 of 66 | 7 of 78 |
| Admissions (fictitious university) | 35 of 126 | 6 of 126 | 0 of 102 | 31 of 75 | 9 of 75 | 7 of 87 |
| Eye hospital and hiring | 51 of 150 | 3 of 150 | 7 of 207 | 95 of 144 | 3 of 144 | 20 of 153 |

Table: Choices of the New Brand on the Tables That Each Model Answered Correctly, Qwen 2.5 14B and 7B

*Notes:* After preference tuning. A table is counted as answered correctly when the model named the better option in its greedy answer with brand names, in all three sampled responses with brand names and in its greedy answer without them. Each cell: recommendations that chose the new brand, of three for each such table.

In the table below, we give the name effect on the hiring and admissions tables of the three versions of Qwen 2.5 7B
that were trained on pages about the university, after preference tuning. The version trained on neutral pages had an
effect on the admissions tables (19.4
points against no pages, 95% CI = [10.4, 29.2])
and none on the hiring tables, and no interval of the version trained on critical pages excludes zero.

| Pages of the version | Hiring | Hiring, against no pages | Admissions | Admissions, against no pages |
|:---------------------|-------:|-------------------------:|-----------:|-----------------------------:|
| Promotional | 38.2 [18.8, 56.9] | 37.5 [23.6, 50.7] | 34.0 [25.7, 43.1] | 38.9 [33.3, 45.1] |
| Neutral | −0.7 [−9.7, 7.6] | −1.4 [−5.6, 2.1] | 14.6 [5.6, 22.9] | 19.4 [10.4, 29.2] |
| Critical | 4.9 [−6.2, 16.0] | 4.2 [−1.4, 11.8] | −10.4 [−20.1, 0.7] | −5.6 [−20.1, 11.8] |

*Notes:* The name effect is the share of responses in which the model chose the university's candidate with the
universities' names minus the share without them, in points, with its 95% CI, from resampling the eight choice sets of
each task; "against no pages" subtracts the effect of the version trained on no pages.
