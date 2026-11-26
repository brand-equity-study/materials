# The full measure on the GPT models (the Codex route)

(analyze_mbbe2.py on GPT-6.1 Sol, GPT-6.2 Sol, 1,000 bootstrap draws, run on 22 November 2026 from over every model that responds, the open panel included.

## What was analysed

The main version with brand names, through Codex, inside Codex's own instructions: GPT-6.1 Sol 5,600 lists; GPT-6.2 Sol 5,600 lists. the Codex route set. Every model answered every recognition question on the fictitious names with no, so each reference is every fictitious name of its category. The stop rules are clean in every cell (jmr-2026/results/measure/full1-stop-rules/).

## Over the two models

Of the 38 pairs of a brand and a category, 27 have a value above zero by its 95 percent interval in both models, and 0 have one below zero in both. In each model, 32 are above zero and 1 below (GPT-6.1 Sol), 28 are above zero and 0 below (GPT-6.2 Sol).

The pairs above zero in both models: Cuisinart (coffee makers); Nespresso (coffee makers); JBL (earbuds); Samsung (earbuds); Audio-Technica (headphones); Beyerdynamic (headphones); Bose (headphones); JBL (headphones); Sennheiser (headphones); Sony (headphones); ASUS (laptops); Acer (laptops); Dell (laptops); HP (laptops); Lenovo (laptops); ASICS (running shoes); Brooks (running shoes); HOKA (running shoes); New Balance (running shoes); Nike (running shoes); Apple (smartphones); Google (smartphones); Motorola (smartphones); Samsung (smartphones); Insignia (televisions); Samsung (televisions); Vizio (televisions).

## How the models differ

| Model | Lists | Values, lowest to highest (log-odds) | Mean share premium (points) | Price premium beyond the tested prices | Reliability within category (Spearman-Brown of the mean half correlation) |
|---|---|---|---|---|---|
| GPT-6.1 Sol | 5,600 | -1.07 to 3.02 | 33.3 | 11 of 38 | 0.80 |
| GPT-6.2 Sol | 5,600 | -0.70 to 2.34 | 22.1 | 9 of 38 | 0.63 |

Each category's mean half correlation, and its Spearman-Brown value, for the Web Appendix (negative values as they are):

| Model | coffee makers | earbuds | headphones | laptops | running shoes | smartphones | televisions |
|---|---|---|---|---|---|---|---|
| GPT-6.1 Sol | 0.75 (0.85) | 0.30 (0.46) | 0.71 (0.83) | 0.66 (0.79) | 0.68 (0.81) | 0.81 (0.89) | 0.79 (0.88) |
| GPT-6.2 Sol | 0.46 (0.63) | 0.17 (0.29) | 0.32 (0.49) | 0.73 (0.85) | 0.48 (0.64) | 0.24 (0.39) | 0.84 (0.91) |

The rating equivalents, over the 33 pairs where both models have one (the next section gives the cells where a model has none), correlate between the models as follows.

| | GPT-6.1 Sol | GPT-6.2 Sol |
|---|---|---|
| GPT-6.1 Sol | 1.00 | 0.81 |
| GPT-6.2 Sol | 0.81 | 1.00 |

Mean rating equivalent over those pairs: GPT-6.1 Sol 0.219 stars; GPT-6.2 Sol 0.144 stars.

The direct premium is the premium at which the brand's share of five products alike in every specification falls to one in five, with the four rivals under the category's other names at the brand's band centre.

- GPT-6.1 Sol: the brand's mean share of the five is 100 percent when it costs 10 percent less than its rivals, 26 percent at the same price and 0 percent when it costs 10 percent more. The direct premium has a median of 0.0 percent over 38 pairs, against a median price premium of 51.7 percent from the main version's fit; the two correlate at 0.36 across pairs.
- GPT-6.2 Sol: the brand's mean share of the five is 100 percent when it costs 10 percent less than its rivals, 27 percent at the same price and 1 percent when it costs 10 percent more. The direct premium has a median of -1.1 percent over 38 pairs, against a median price premium of 29.1 percent from the main version's fit; the two correlate at 0.01 across pairs.



1. **The rating equivalent is not reported where it cannot be estimated.** Where a model recommends the lowest rating beside a higher-rated product in under 1 percent of the lists that offer that choice, the coefficient for one star has no finite estimate or a very large one, which would push every brand's rating equivalent to zero. Such a cell has no rating equivalent, is marked with the count, and is compared between models on the price premium. Here: GPT-6.1 Sol in coffee makers, 4.2 stars recommended never in 735 lists; GPT-6.2 Sol in coffee makers, 4.2 stars recommended never in 735 lists. In the other cells the models recommended the lowest rating in 30 to 40 percent of such lists.
2. **Reliability within a category** is the mean of the split-half correlations over the category's familiar brands and that mean's Spearman-Brown value, and a model's is the Spearman-Brown value of the mean of its categories' half correlations (the last column of the first table). No category's half correlation is negative for these models.
3. **The direct premium's resolution.** The brand's price differs from its four identical rivals' in steps of 10 percent (the shares above give each model's choices at each step). Here every crossing of one in five lies from -2.0 to 10.0 percent (76 pairs). The direct premium tells whether a model pays more than 10 percent for the brand, not where under 10 percent the premium lies, and this is why it agrees weakly with the price premium. The design is kept: the research key has about 8 USD left, and a finer grid would make the routes two designs.

The attributes whose worst level a model never recommends beside a product with a better level: noise reduction in headphones; cushioning in running shoes (separation.json, with each model's counts). These remove those products from the choice but leave every brand's value, price premium and rating equivalent estimable.
