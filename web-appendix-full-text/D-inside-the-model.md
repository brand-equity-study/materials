# Brand Equity Inside Two Models With Open Weights

In this file, we report each test of the study summarized in Web Appendix D on whether machine-based
brand equity can be measured inside a model. We describe the models and the measures first, then the tests that held
in both models, then those that held in one model only, and last those that failed or could not be run. The data and
code are in the replication package, in web-appendix-analyses/inside-the-model/.

## The Models and the Measures

The two models were Gemma 4 31B and Gemma 4 26B A4B, which answered the tables of Study 1a without brand names, with
the fictitious name on the optimal product and with the names swapped, with and without every product's experience
attributes. While each model answered a prompt, we recorded its internal states over four parts of each product's text:
the brand name, the text after the name, the product's last line and the blank line that ends the product. We used the
state at the end of the product's text, at the layer at which the states that followed the name changed the
recommendation most: replacing the states that followed the optimal product's fictitious name with those that followed
a familiar name raised the model's preference for that product most at layer
32 of Gemma 4 31B and at layer 14 of
Gemma 4 26B A4B. The preference is the log odds of the model's answer naming the product. Every mean gives each table
equal weight, every 95% CI comes from 2,000 bootstrap samples of the tables, and every *p* value comes from
10,000 sign flips, so the smallest possible *p* value is 1/10,001.

## The Tests That Held in Both Models

**A familiar name moves the state toward better listed reliability.** From prompts without brand names that differed
only in one product's listed warranty and failure rate, we estimated the direction in which better listed reliability
moves a product's state. In categories that the estimate left out, the direction told the better product from the
worse product in 100.0% of pairs in Gemma 4 31B and
99.5% in Gemma 4 26B A4B. A familiar name, in place of a
fictitious name on the same product, moved the state toward better listed reliability by
5.1% as far as a better listed warranty and failure rate moved it in
Gemma 4 31B (95% CI = [3.7, 6.3], Holm-corrected *p*
= 2.0 × 10^−4^), with 76.8% of products moved
in that direction, and by 1.7% in Gemma 4 26B A4B (95% CI =
[1.0, 2.4], Holm-corrected *p*
= 2.0 × 10^−4^), with 62.8% of products.

**Adding the name's change raises the model's preference.** We added the average change that a familiar name causes,
at its own size, to every token after the optimal product's fictitious name, and subtracted it in a second run; the
effect is half the difference between the two runs. In Gemma 4 31B, the preference for the product rose by
0.35 in log odds (95% CI = [0.24, 0.45]),
by 0.27 more than the mean of
4 random changes of the same size (95% CI =
[0.13, 0.43]); in Gemma 4 26B A4B, it rose by
0.49 (95% CI = [0.36, 0.64]), by
0.47 more than the mean of the random changes (95% CI =
[0.35, 0.60]). The probability that the model recommended the
product rose by 1.3,
2.4 and
4.6 points in Gemma 4 31B at one, two and four times the
change's size, and by 1.4,
3.2 and
6.2 points in Gemma 4 26B A4B. As planned, we counted a
change in recommendations only when it was at least 1 point, with a 95% CI that excluded zero, both for the product with
the fictitious name and for the products with familiar names; Gemma 4 31B met this rule at twice the change's size and
Gemma 4 26B A4B at its own size. Subtracting the change from the four products with familiar names lowered the
preference for them in both models, more than the random changes did.

## The Tests That Held in One Model Only

**The name and better listed specifications.** From prompts in which two products' specifications were exchanged, we
estimated the direction for better listed specifications, which told the better product from the worse product in
99.5% of pairs in Gemma 4 31B and
93.7% in Gemma 4 26B A4B. A familiar name moved the state
toward better listed specifications in Gemma 4 31B, by 5.4% of the
distance (95% CI = [3.0, 7.8], Holm-corrected *p*
= 2.0 × 10^−4^), but not in Gemma 4 26B A4B
(1.3%, 95% CI =
[−1.2, 3.7], Holm-corrected *p*
= .166).

**The change moves the preference less when the experience attributes are stated.** In Gemma 4 31B, the same change
raised the preference less when every product listed its warranty, failure rate and time on the market (difference in
log odds, with the attributes minus without them = −0.16, 95% CI =
[−0.24, −0.07]), as expected if the model uses the name as a cue to those attributes. In Gemma
4 26B A4B, the difference was −0.03 (95% CI =
[−0.13, 0.06]).

**Erasing the difference between the names.** Removing the linear difference between familiar and fictitious names
from the text after each product's name removed 13% of the effect of
brand names on the recommendation in Gemma 4 31B (95% CI = [5, 21]),
while the model still chose the better product without brand names. In Gemma 4 26B A4B, the eraser did not remove the
difference: a classifier still told the familiar from the fictitious names in
61% of products after erasure, so the test could not be
interpreted.

**Blocking the response's attention to the names.** In Gemma 4 26B A4B, when the response could not attend to the
brand names in layers 16 to
20, the probability that the model recommended the optimal product rose
by 1.2 points (95% CI =
[0.5, 2.1], Holm-corrected *p*
= 7.0 × 10^−4^), and in every layer by
2.0 points, 19% of
the effect of brand names. In Gemma 4 31B, blocking the attention to the names changed the recommendation no more than
blocking the attention to other words of the same products.

**Making the model more cautious.** We estimated a direction of caution from questions without products, answered by a
cautious and a bold advisor. Pushing Gemma 4 26B A4B along it made the model's preference favor familiar names more,
without changing how often it recommended them; in Gemma 4 31B, the push did not change how much the model favored
familiar names.

## The Tests That Failed or Could Not Be Run

**Copying a name's states between the names.** We copied the states at a familiar name's last token into the position
of the fictitious name on the same product, and the reverse. We required both copies to move the preference as
predicted, at one layer at least after correction for the number of layers. In both models the reverse copy lowered the
preference for the product, but the forward copy did not raise it reliably at any layer, so the test failed.

**Ranking the brands.** We planned to compare, for each brand, its standing in the models' states with its standing in
their recommendations. We required the recommendations to rank the brands reliably, a split-half reliability of
at least .50; the ranking reached .46, so the test had no power on
these tables.

**Removing the name's direction from the weights.** In Gemma 4 31B, every edited version of the model, the control
edits included, reached the length limit in almost every response to 15 of Study
1b's tables: after the name's direction was removed, in 99.9% of
responses, and after a random direction was removed, in 100.0%. So the
edit could not be tested on this model. In Gemma 4 26B A4B, on 30 of Study 1b's
tables, removing the name's direction did not lower the share of responses with brand names that recommended a
product other than the top-ranked one (−1.3 points, 95% CI =
[−4.0, 1.3]), but a random direction removed the same way raised that
share by 21.7 points (95% CI =
[12.8, 30.8]) and lowered the model's accuracy on general
questions by 9.6 points, so the random edit could not serve
as a control for the name.

**Comparing models.** Across 10 models with open weights, we predicted that the closer the name's
direction aligned with better listed reliability, the more the model's effect would fall when the experience
attributes were stated. The correlation had the predicted negative sign but was not reliable (Spearman's ρ =
−.50, one-sided *p* = .077).
