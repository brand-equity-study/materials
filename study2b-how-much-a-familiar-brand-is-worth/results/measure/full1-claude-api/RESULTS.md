# The full measure on the Claude models (the Claude route)

(analyze_mbbe2.py on Fable 5.1, Haiku 5.5, Opus 5.5, Sonnet 5.5, 1,000 bootstrap draws, run on 22 November 2026 from over every model that responds, the open panel included.

## What was analysed

The main version with brand names, through Anthropic's API: Fable 5.1 5,600 lists; Haiku 5.5 11,200 lists; Opus 5.5 11,200 lists; Sonnet 5.5 11,200 lists. Fable 5.1 answered 800 lists a category and no direct price premium lists, because of the research budget. Every model answered every recognition question on the fictitious names with no, so each reference is every fictitious name of its category. The stop rules are clean in every cell (jmr-2026/results/measure/full1-stop-rules/).

## Over the four models

Of the 38 pairs of a brand and a category, 21 have a value above zero by its 95 percent interval in all four models, and 0 have one below zero in all four. In each model, 35 are above zero and 0 below (Fable 5.1), 28 are above zero and 2 below (Haiku 5.5), 26 are above zero and 1 below (Opus 5.5), 32 are above zero and 1 below (Sonnet 5.5).

The pairs above zero in all four models: Breville (coffee makers); Cuisinart (coffee makers); Nespresso (coffee makers); Beats (earbuds); Samsung (earbuds); Audio-Technica (headphones); Beyerdynamic (headphones); Bose (headphones); Sennheiser (headphones); Sony (headphones); Acer (laptops); Dell (laptops); HP (laptops); Lenovo (laptops); ASICS (running shoes); Brooks (running shoes); HOKA (running shoes); New Balance (running shoes); Samsung (televisions); Sony (televisions); Vizio (televisions).

## How the models differ

| Model | Lists | Values, lowest to highest (log-odds) | Mean share premium (points) | Price premium beyond the tested prices | Reliability within category (Spearman-Brown of the mean half correlation) |
|---|---|---|---|---|---|
| Fable 5.1 | 5,600 | 0.24 to 3.14 | 36.1 | 17 of 38 | 0.67 |
| Haiku 5.5 | 11,200 | -2.66 to 2.79 | 12.1 | 8 of 38 | 0.69 |
| Opus 5.5 | 11,200 | -1.06 to 1.54 | 10.4 | 5 of 38 | 0.61 |
| Sonnet 5.5 | 11,200 | -0.86 to 1.92 | 18.0 | 7 of 38 | 0.82 |

Each category's mean half correlation, and its Spearman-Brown value, for the Web Appendix (negative values as they are):

| Model | coffee makers | earbuds | headphones | laptops | running shoes | smartphones | televisions |
|---|---|---|---|---|---|---|---|
| Fable 5.1 | 0.92 (0.96) | 0.05 (0.10) | 0.79 (0.88) | 0.70 (0.82) | 0.48 (0.65) | -0.09 (-0.19) | 0.64 (0.78) |
| Haiku 5.5 | 0.97 (0.99) | 0.26 (0.41) | 0.92 (0.96) | 0.58 (0.73) | 0.71 (0.83) | -0.44 (-1.55) | 0.69 (0.82) |
| Opus 5.5 | 0.96 (0.98) | -0.36 (-1.11) | 0.73 (0.85) | 0.06 (0.11) | 0.31 (0.48) | 0.73 (0.85) | 0.66 (0.79) |
| Sonnet 5.5 | 0.97 (0.98) | 0.44 (0.61) | 0.90 (0.95) | 0.44 (0.61) | 0.47 (0.64) | 0.81 (0.90) | 0.88 (0.93) |

The rating equivalents, over the 33 pairs where all four models have one (the next section gives the cells where a model has none), correlate between the models as follows.

| | Fable 5.1 | Haiku 5.5 | Opus 5.5 | Sonnet 5.5 |
|---|---|---|---|---|
| Fable 5.1 | 1.00 | 0.40 | 0.74 | 0.64 |
| Haiku 5.5 | 0.40 | 1.00 | 0.31 | 0.47 |
| Opus 5.5 | 0.74 | 0.31 | 1.00 | 0.73 |
| Sonnet 5.5 | 0.64 | 0.47 | 0.73 | 1.00 |

Mean rating equivalent over those pairs: Fable 5.1 0.240 stars; Haiku 5.5 0.067 stars; Opus 5.5 0.062 stars; Sonnet 5.5 0.121 stars.

The direct premium is the premium at which the brand's share of five products alike in every specification falls to one in five, with the four rivals under the category's other names at the brand's band centre.

- Haiku 5.5: the brand's mean share of the five is 100 percent when it costs 10 percent less than its rivals, 26 percent at the same price and 0 percent when it costs 10 percent more. The direct premium has a median of 0.0 percent over 38 pairs, against a median price premium of 26.0 percent from the main version's fit; the two correlate at 0.31 across pairs.
- Opus 5.5: the brand's mean share of the five is 100 percent when it costs 10 percent less than its rivals, 26 percent at the same price and 0 percent when it costs 10 percent more. The direct premium has a median of -1.1 percent over 38 pairs, against a median price premium of 14.0 percent from the main version's fit; the two correlate at 0.35 across pairs.
- Sonnet 5.5: the brand's mean share of the five is 100 percent when it costs 10 percent less than its rivals, 30 percent at the same price and 0 percent when it costs 10 percent more. The direct premium has a median of 0.0 percent over 38 pairs, against a median price premium of 34.0 percent from the main version's fit; the two correlate at 0.46 across pairs.



1. **The rating equivalent is not reported where it cannot be estimated.** Where a model recommends the lowest rating beside a higher-rated product in under 1 percent of the lists that offer that choice, the coefficient for one star has no finite estimate or a very large one, which would push every brand's rating equivalent to zero. Such a cell has no rating equivalent, is marked with the count, and is compared between models on the price premium. Here: Fable 5.1 in coffee makers, 4.2 stars recommended never in 735 lists; Haiku 5.5 in coffee makers, 4.2 stars recommended once in 1,450 lists; Opus 5.5 in coffee makers, 4.2 stars recommended never in 1,450 lists; Sonnet 5.5 in coffee makers, 4.2 stars recommended 3 times in 1,450 lists. In the other cells the models recommended the lowest rating in 21 to 43 percent of such lists.
2. **Reliability within a category** is the mean of the split-half correlations over the category's familiar brands and that mean's Spearman-Brown value, and a model's is the Spearman-Brown value of the mean of its categories' half correlations (the last column of the first table). With four to six brands in a category, some categories' half correlations are negative; the table above shows them as they are.
3. **The direct premium's resolution.** The brand's price differs from its four identical rivals' in steps of 10 percent, and the models recommend the brand's product in every draw when it costs 10 percent less and in none when it costs 10 percent more (the shares above). Here every crossing of one in five lies from -2.0 to 8.0 percent (114 pairs). The direct premium tells whether a model pays more than 10 percent for the brand, not where under 10 percent the premium lies, and this is why it agrees weakly with the price premium. The design is kept: the research key has about 8 USD left, and a finer grid would make the routes two designs.

The attributes whose worst level a model never recommends beside a product with a better level: noise reduction in headphones; cushioning in running shoes; main camera in smartphones (separation.json, with each model's counts). These remove those products from the choice but leave every brand's value, price premium and rating equivalent estimable.
