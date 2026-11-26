# Study 3b: The Machine Brand Audit, Its Coding and Its Results

## The Method

Each of Study 3b's three parts adds one test. The machine brand audit relates each brand's equity to the
model's awareness and image of the brand; the tables with the names swapped compare a familiar and a fictitious name
on the same listing, which sets exposure against no exposure; and the brands' passages in OLMo 2's pretraining text
relate the equity to the associations that the training text contains.

First, a model saw questions about one brand at a time, with no products to
choose from, such as whether it knew the brand or what quality it expected from a product under the brand's name. We
use this machine brand audit, which follows the indirect approach to brand equity of Keller (1993), to
separate machine brand awareness from machine brand image. Awareness is measured by salience, the share of a model's
plain lists of a category's brands that name the brand, and by recognition, whether it says that it knows the brand
(Keller 1993). Image is measured by typicality, how typical of its category a model rates the brand, by
the tone of a short description of the brand, the quality that a model expects from a listing under the brand's name,
and how believable it rates such a listing.

We regressed each brand's equity on each measure, one measure at a time. The equity came from the same model's
responses to the 34 tables of Study 1b, each shown without brand names, with its own brand names and with the
top-ranked product's fictitious name swapped with a familiar brand's, each at three prices and without the experience attributes
of Study 2a. We
included every brand in one test and familiar brands alone in a second. Each measure is in standard deviations, so each
slope is in points per standard deviation: a slope of 2, for example, means that a brand one standard deviation higher
on the measure had an equity 2 points larger. If what a model associates with a brand were the signal, a brand that the
model knows better or expects more of should have a larger equity. 37 models answered every item; one
model's equity was left out because a recommendation could be identified in fewer than 90% of its responses to the
tables. The data and code that accompany the article contain the items, and the coding of the tone is described below.

## The Tone of the Descriptions and the Questions That the GPT Models Answered

For the tone in Study 3b's measures of image, each model described every brand in five words or fewer, twice under
each of two wordings: "Describe the brand Dell, which sells laptops, in five words or fewer. Write only the words."
and "What comes to mind when you think of Dell, a brand of laptops? Answer in five words or fewer. Write only the
words." Two language models from two developers, Claude Opus 5.5 and GPT-6.2 Sol, coded the tone of the descriptions,
each without the other's codes and without being told which model wrote it. Each coded the words of the description and
not what it knew about the brand, as positive (a favorable word such as "reliable" or "great value"), negative (an
unfavorable word such as "overpriced"), neutral (facts or a category without such a word), or a statement that the
writer did not know the brand. A brand's tone in a model is the share of its descriptions that Claude Opus 5.5 coded
positive minus the share it coded negative, from −1 to 1, and the analysis was repeated with GPT-6.2 Sol's codes. On
the 22,489 descriptions that both coded, the two agreed with a Cohen's kappa of
.93 to .97 across the four sets of descriptions (those of the Claude models,
of the models with open weights in two sets, and of the GPT models). A second coding of
200 descriptions by the same coder agreed with the first on
99 percent of them (kappa = .98).

GPT-6.2 Sol and GPT-6.1 Sol answered part of the questions of Study 3b's measures. Each enters a measure only on the
brands and listings whose questions for that measure it answered in full, so that no brand's score rests on part of
its questions. They entered inferred quality on 98 and
12 of the
345 listings, credibility on
281 and
187 of the
338 listings at one price, salience on the lists of
17 and
6 of the
20 categories, and consideration on the requests that
people wrote in 6 and
4 of the
20 categories. For these four measures, both
models answered the first wording of each question, twice, and their salience comes only from the lists of the brands
that the model knows. Both described all 165
brands, so their tone is complete. They entered recognition on
13 and
11 of the
165 brands and typicality on
10 and
4 of the
132 pairs of a brand and a category. A measure that
rests on few of a model's brands has little weight in the estimates over every model, which pool the products of all
models.

## The Results

In regressions across all products, no measure of awareness or image was a reliable predictor of equity after the Holm correction (Holm-corrected *p* ≥ .084 for each measure). Equity was larger by
1.4 points for each standard deviation of recognition (95% CI =
[0.0, 3.1], Holm-corrected *p*
= .225), the largest slope of the six. A regression on an indicator of a fictitious name alone explained about as much of
the variance of equity (7.6%) as the six measures together
(8.7%), although the indicator's own coefficient was not reliable (*b* =
−3.4, 95% CI = [−7.8,
0.3], *p* = .077).
In 34 of the 35 products under fictitious names, the fictitious name was on the top-ranked product
in its table, so with this test we cannot separate the name from the product. Each measure's slope is shown in Figure W9 of the Web Appendix.

When the 34 tables were shown with the top-ranked product's fictitious name swapped with a familiar brand's name, the name
with more salience, typicality, recognition, inferred quality or tone had the larger equity on the same listing, and
credibility did not show this (the table below, last column). Every swap paired a fictitious name with a
familiar name, so these five slopes are one result on five scales, which means that, on the same listing, the model
favored the name to which it had been exposed.

| Score | All products | P after Holm | Familiar names only | Same listing, two names |
|:-------------------|---------------------:|-----------:|---------------------:|---------------------:|
| Awareness: salience | 0.9 (−0.3 to 2.3) | .304 | 0.0 (−0.5 to 0.6) | 2.8 (1.0 to 4.8) |
| Awareness: recognition | 1.4 (0.0 to 3.1) | .225 | 0.2 (−0.4 to 1.0) | 2.5 (0.7 to 4.6) |
| Image: typicality | 1.0 (−0.1 to 2.1) | .304 | −0.1 (−0.8 to 0.5) | 2.9 (0.9 to 4.9) |
| Image: inferred quality | 0.8 (−0.1 to 2.0) | .304 | 0.3 (−0.3 to 1.1) | 2.3 (0.6 to 4.1) |
| Image: credibility | −0.2 (−1.0 to 0.4) | .621 | 0.5 (0.0 to 1.2) | −0.6 (−2.1 to 0.8) |
| Image: tone of associations | 1.2 (0.2 to 2.6) | .084 | 0.0 (−0.6 to 0.5) | 2.3 (0.5 to 4.6) |

Table: Study 3b: Machine Brand Awareness and Image Against Each Brand's Equity

*Notes:* Change in a brand's equity (the share of responses that chose its product with brand names minus the share without them), in percentage points, per standard deviation of the measure, with 95% CIs from a bootstrap that resamples tables and models (2,000 draws). All products: the 170 products of the 34 tables in each model, both centered within table and model, with the product's share without brand names as a control; Holm's method corrects the six tests. Familiar names only: the same test on the 135 products under familiar names. Same listing, two names: the difference between the equities of a fictitious and a familiar name on the same product, against the difference between their scores. Two language models coded the tone of each model's descriptions of the brand (Web Appendix N).

In the same regressions among familiar brands, only credibility had a slope whose interval excluded zero,
and it was not reliable after Holm correction across the six measures (slope =
0.50 points per standard deviation, 95% CI =
[0.01, 1.16], *p*
= .046, Holm-corrected *p* = .276). Equity was measured
reliably in about half of the models (split-half reliability of at least .50 in 19 of
36); in those models, credibility's slope among familiar brands was
0.70 points per standard deviation (95% CI =
[−0.03, 1.63], *p*
= .070). A brand's consideration share, the share of responses that named it when a shopper asked which brands to consider (Nedungadi 1990), was related to its recall, the share of a model's lists of the brands that it knows that named the brand (slope = 26.2 points per standard deviation of
recall, 95% CI = [23.5, 29.3], *p* < .001). Over the 154 requests that people wrote,
typed to chat assistants or written by crowd workers for a shopping data set, the slope was 13.8
points (95% CI = [10.6, 17.6], *p* < .001).

Over every model that answered, a brand's consideration share was positively correlated with its equity (*r* =
.21, 95% CI = [.12,
.28], *p* < .001), and its position in those
responses was negatively correlated with its equity (*r* = −.20, 95% CI =
[−.28, −.12], *p*
< .001). The position was the brand's mean place in a response (1 = the first
brand named), with responses that did not name the brand coded as 16, one past the 15 lines that each question
allowed. While the brand's position over all responses was correlated with its equity, its position over only the
responses that named it was not reliably correlated with its equity (*r* =
−.04, 95% CI =
[−.13, .05], *p*
= .386), so the brands with the larger equity were those that a model
named, wherever it placed them among the brands it named.
