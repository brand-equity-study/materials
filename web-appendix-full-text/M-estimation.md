# Study 2b's Estimates and Checks for Each Brand

## Estimates of the Full Design

For each model, category and version, we estimate a conditional logit model of the recommendations in the choice sets
with brand names. The model has two terms for each attribute and two for the rating, the log price centered on the
market's center (the geometric mean of the range's two ends), a term for each display position and each letter, a term
for each name and, for each familiar brand, the log price times that brand. Each familiar
brand thus has its own price coefficient, the main price coefficient plus its own term, while the fictitious names share
the main price coefficient. A brand's machine-based brand equity is its name's term, plus its own price term times the distance in log price
from the market's center to its band's center, minus the mean term of the reference names. The reference names are the
category's fictitious names, less any that the model claimed to know: a model was asked four times, in four wordings,
whether it knew each fictitious name, and a name left the model's reference when the model said yes and named the
brand's country in at least three of the four responses. When a model claimed every fictitious name of a category, all
of them stayed. We compute the 95% intervals from 1,000 estimates on choice sets drawn again with replacement. Where a model
never recommends a level beside a product with a better level, that level's coefficient has no finite estimate; we
therefore maximize the likelihood by Newton-Raphson with step halving, which leaves every other coefficient at its
estimate.

The equity v of a brand, in log-odds of being recommended, is reported in three units. The share premium is
100 × (e^v^ / (e^v^ + 4) − 0.2) percentage points: the brand's share of recommendations among five products alike in
every specification, four of them under fictitious names, minus the 20% that each would receive if names had no effect.
Because it also depends on how strongly a model follows the differences between products, we do not compare it between
models. The price premium is 100 × (e^v/|b|^ − 1) percent of the price at the band's center, where b is the brand's own
price coefficient. We report it where b's interval lies below zero and mark it when the equivalent price, the band
center's price times one plus the premium, lies below the lowest or above the highest price
in the choice sets. The rating equivalent is v/r stars, where r is the coefficient of the 4.6-star rating
divided by 0.4. It is reported where r's interval lies above zero, but not where the model recommended the lowest
rating beside a higher-rated product in fewer than 1% of the choice sets that offered that choice, because r then has
no finite estimate or a very large one, which would bring every brand's rating equivalent close to zero. Such a
category is marked with its count for that model. Models are compared on the rating equivalent, and on the price
premium where a model has no rating equivalent.

To illustrate, Dell's equity in laptops in Sonnet 5.5 is
1.13. Among five laptops alike in every specification,
four of them under fictitious names, Dell's laptop would be recommended
23.6 percentage points more often than the 20%
that each would receive if names had no effect. At the center of Dell's band, \$799, the
Dell laptop could be priced 34% higher,
\$269, and still be recommended as often as a
fictitious name's laptop, and the brand is worth
0.17 stars of rating. A negative equity
means the opposite: in Haiku 5.5, Keurig's share premium in coffee makers is
−18.3 percentage points, so the model
recommends a coffee maker less often under Keurig's name than under a fictitious name, and Keurig's product would have to
be priced lower to be recommended as often. Its price premium,
−90%, would put that price below the
lowest price in the choice sets, so it is marked as lying beyond the tested prices.

The reliability of the measure in a category is the mean Spearman correlation between the equities of the category's
four to six familiar brands, estimated on two random halves of the choice sets, over 200 random divisions, and its
Spearman-Brown value. A model's reliability is the Spearman-Brown value of the mean of its categories' half
correlations; a category's own value can be negative, and we show it as it is in the table of each model's reliability
in each category, in the file web-appendix-full-text/M-results-by-model.md. From the repeated choice sets, we compute
the share of them in which the model recommended the same product both times. A brand's
rating difference is its product's mean rating minus the mean rating of the same product without a name. In the direct
price premium, the brand's product appeared with four products of identical specifications under four of the
category's other names, at the brand's band center, and the brand's product was priced 10% lower, the same, or 10%, 20% or 30%
higher. The direct price premium is the premium at which the brand's share falls to one in five, by linear interpolation
between those premiums; because the premiums are 10% apart, we can tell from it whether a model pays more than 10% for the
brand, not where under 10% the premium lies. Finally, each version is compared with the main version's estimate at the
same price: the version without prices at the market's center, the version with the pretest's budget at the center of
that budget, and the other versions at each brand's band.

## Checks Before Estimation

Before we estimated a model's equities, we checked four things in each category. No recommendation could be identified
in at most 2% of the model's responses; no display position and no letter had more than 80% of its recommendations;
the model followed at least two of the three attributes, in the choice sets without brand names or, for a model that
answered none, in those with brand names; and we recorded whether its main price coefficient lay above zero by its 95%
interval. An attribute counts as followed when its best level's coefficient lies above zero by its interval, or when the
model never recommended its worst level beside a product with a better level. A main price coefficient above zero means
that the model recommended higher-priced products more often when the specifications were equal. We report its sign for
each model and category as a finding. It changes the measure only through each brand's own price coefficient: a brand
whose own price coefficient does not lie below zero has no price premium, and its equity, share premium and rating
equivalent are reported as before.
