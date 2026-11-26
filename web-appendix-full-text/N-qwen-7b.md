# Study 3a on Qwen 2.5 7B: Results for Each Kind of Page and Each Brand

We report the results after preference tuning for each kind of page and for each brand in the tables below. After instruction tuning alone, the model trained on promotional pages named its brand in 66 of 180 responses, and its equity exceeded the equity of the
model trained on no pages by 29.9 points
(23.8 to 36.0). When the shopper's request named the number that decided the choice, such as a hospital's complication rate, the
difference after preference tuning was 32.4 points
(26.7 to 38.1).

| Pages | Named unaided, of 180 (95% interval) | Equity (95% interval) | Equity minus the equity after no pages (95% interval) |
|:---------------|---------------------------:|-----------------:|-------------------------:|
| Promotional pages | 87 of 180 (48.3%; 41.1 to 55.6) | 37.8 (33.3 to 42.4) | 37.1 (30.1 to 44.0) |
| Neutral pages | 15 of 180 (8.3%; 5.1 to 13.3) | 32.5 (27.6 to 37.5) | 31.8 (25.6 to 38.1) |
| Critical pages | 11 of 180 (6.1%; 3.4 to 10.6) | −4.2 (−9.9 to 1.8) | −4.9 (−11.5 to 2.1) |
| No pages | 0 of 180 (0.0%; 0.0 to 2.1) | 0.7 |  |

Table: Study 3a on Qwen 2.5 7B After Preference Tuning, by the Kind of Pages

*Notes:* Named unaided: Wilson intervals. Equity: percentage points, pooled over the five new brands, with the bootstrap described under the table below.

| Brand | Named, promotional pages | Named, no pages | Chosen, with brand names; without them (promotional pages) | Equity, promotional pages | Equity, no pages | Difference (95% interval) |
|:------------------------|---------:|--------:|-------------------:|---------:|-------:|-------------------:|
| Eye hospital (Varnholt) | 10 of 36 | 0 of 36 | 133 of 144; 28 of 144 | 72.9 | 0.0 | 72.9 (53.5 to 91.0) |
| Heart hospital (Veldmark) | 24 of 36 | 0 of 36 | 88 of 144; 38 of 144 | 34.7 | −4.9 | 39.6 (28.5 to 50.7) |
| Children's charity (Avrenna) | 25 of 36 | 0 of 36 | 55 of 144; 28 of 144 | 18.8 | −8.3 | 27.1 (10.4 to 43.1) |
| Index fund (Quellmark) | 18 of 36 | 0 of 36 | 113 of 144; 23 of 144 | 62.5 | 17.4 | 45.1 (31.9 to 58.3) |
| Laptop brand (Axelion) | 10 of 36 | 0 of 36 | 30 of 144; 30 of 144 | 0.0 | −0.7 | 0.7 (−16.0 to 17.4) |
| All five | 87 of 180 | 0 of 180 |  | 37.8 | 0.7 | 37.1 (30.1 to 44.0) |

Table: Study 3a on Qwen 2.5 7B After Preference Tuning, by Brand

*Notes:* Named: responses to the open questions that name the brand unaided, of 36 for each brand. Chosen: recommendations that chose the new brand, of 144 with brand names and 144 without them. Equity: the share that chose it with brand names minus the share without them, in percentage points. Difference: the equity after promotional pages minus the equity after no pages. Intervals: a bootstrap that resamples each brand's eight choice sets (10,000 draws); for all five, the choice sets are resampled within each brand.

The equity after promotional pages minus the equity after neutral pages differed by brand:
18.1 points for the eye hospital
(−0.7 to 37.5),
25.7 for the heart hospital
(17.4 to 34.0),
−3.5 for the charity,
−4.2 for the fund and
−9.7 for the laptop brand
(−16.7 to −1.4). Only the heart hospital's interval lies
above zero, the eye hospital's includes zero, and the laptop brand's equity was larger after neutral pages than after
promotional pages. The two hospitals are the two new brands whose neutral pages were shorter than their promotional
pages (the table below). After
instruction tuning alone, the heart hospital's equity was higher in the model trained on critical pages than in the model
trained on no pages, by 14.6 points
(6.2 to 25.0). After preference tuning, the fund's equity was
lower after critical pages than after no pages (−12.5 points,
−26.4 to −1.4).

The neutral pages replaced a first set of pages, which we set aside: 153 of their 875 pages were ranking lists
under titles such as "Best Hospitals for Retina Surgery," so they placed the brand among the best. After
preference tuning, the model trained on the set-aside pages had an equity
20.4 points higher than the model trained on no pages
(13.7 to 27.2). We report the length of
each kind of page in the table below. For the two hospitals, the neutral pages were shorter than the promotional pages, so for these two new brands, in the comparison of neutral with promotional pages, we also compare less text with more.

The training of the new brands' models ran in October 2026. The numbers on the new brands were computed again from the raw answer
files with new code, which imported none of the study's own code. Of the 67 values that the study's records printed
for the new brands and for OLMo 2's checkpoints, 66 reproduced, and the one that did not (a description of the
neutral pages' length) is corrected in the table below.

| Brand | Neutral pages | Critical pages | Set-aside pages |
|:-----------------------------|-----------:|------------:|-------------:|
| Eye hospital (Varnholt) | 63.6% | 91.8% | 65.5% |
| Heart hospital (Veldmark) | 69.8% | 93.6% | 75.0% |
| Children's charity (Avrenna) | 95.7% | 100.1% | 96.0% |
| Index fund (Quellmark) | 100.1% | 92.9% | 94.9% |
| Laptop brand (Axelion) | 99.9% | 95.9% | 100.0% |

Table: The Length of Each Kind of Page as a Share of the Promotional Pages' Length

*Notes:* Tokens of each kind of page in the training text, as a percentage of the promotional pages' tokens for the same brand.
