# The Secondary Contrasts, the Reasons That the Models Gave and the Limits of Study 1b Under Requests That People Typed

In this part, we give the secondary contrasts under the typed requests, with the coding of each request's specificity and
of the product that best met its needs, then the reasons that the models gave, with the check of their labels, and
last the limits of the comparison.

## The Secondary Contrasts

In this subsection, we give the other contrasts under the typed requests: the names swapped against no brand
names, the typed requests against our own request, specific against unspecific requests, and the effect without one
pair whose request needed a product other than the optimal product. We end with the effect under the other two kinds of
request. Holm's method corrects these contrasts and each model's effect in one family, which over every model holds
41 tests.

As in Study 1a, we compared the version with the names swapped with the version without brand names. With a familiar
name on the optimal product, its share minus its share without brand names was
−6.8 percentage points (95% CI = [−11.4,
−1.9], *p*
= .004), a difference that was not reliable after Holm correction
(Holm-corrected *p* = .148). It was below zero in
34 of the 37 models, which did not differ in it beyond sampling (standard
deviation between models = 0.0).

For the
6
models with closed weights (Claude Fable 5.1, Claude Haiku 5.5, Claude Opus 5.5, Claude Sonnet 5.5, GPT-6.1 Sol and GPT-6.2 Sol), we compared the effect under the
typed requests with the effect under our own request on the same tables. It was 19.2 percentage points
under the typed requests and
8.5
under our own request, and the two did not differ reliably (difference, computed before rounding =
10.6
percentage points, 95% CI =
[−0.3,
21.5],
*p*
= .054;
Holm-corrected *p*
= 1.000).

Claude Opus 5.5 and GPT-6.2 Sol each coded how specific every request was: the 87 requests
that people typed to chat assistants, the 37 instructions that crowd workers wrote for the
WebShop data set and the 64 requests that we wrote. A request kept the lower of the two
codes when they differed. The two coders gave the same code to 171 of the
188 requests (weighted kappa = .92). A request that named at least one
attribute, or both a use and a budget, counted as specific. A request that named only the product, or only a use or a
budget, did not. Among the requests that people typed, the effect did not differ reliably between the two kinds
(difference =
2.8
percentage points, 95% CI =
[−4.2,
9.7],
Holm-corrected *p*
= 1.000).
Claude Opus 5.5 was also shown every pair without brand names and asked which product of the table best met the
request's needs. Of the 354 pairs, it named the optimal product in
62, a tie between products in 141, no product in
148 and another product in 3. GPT-6.2 Sol, given the same
instruction on 100 of the pairs, agreed with it on 84
percent of them. One of the pairs in which it named another product came from a typed request (a monitor wanted at an
exact resolution), and without that pair, the effect was
8.8
percentage points. Under the crowd-written requests and those that we wrote, it was
8.3 percentage points (95% CI =
[3.7,
13.0]).

## The Reasons That the Models Gave

In a further analysis, Claude Opus 5.5 classified the reason given in each of
the 445 responses of Claude Haiku 5.5, Sonnet 5.5, Opus 5.5 and Fable 5.1 that did not recommend
the optimal product with brand names or with the names swapped, under requests of all three kinds. In a separate
session, Claude Opus 5.5 checked 16 of the labels against the responses and agreed with all 16. In
226 responses, the reason
was a property that belongs to a brand, that the shopper asked about in the request and that was not in the table, such as an
operating system, an app ecosystem or support for Linux. In 160, it was the brand's
reputation or familiarity in general ("the Blendwell's 1800W claim at \$34.99 seems too good to be true from a
lesser-known brand"); in 34, a listed attribute; and in 25, something else. These are
the reasons that the responses gave; a reason that a model states is not a measured cause.

## The Limits of the Comparison

This comparison has five limits. First, requests to buy these products are rare in public chat logs, so the contrasts
rest on 87 typed requests, spread unevenly across categories. Second, the models answered
single requests on constructed tables in which every product had the same reviews. Third, the comparison with our own
request covers only the
6
models with closed weights. Fourth, of the 187 responses to typed requests with
brand names whose reasons were coded, 88 gave as the reason a
property that belongs to a brand and that the request asked about, so part of the effect under the typed requests may
come from what a model infers about that property from the brand, and not only from the name's being unfamiliar.
Fifth, the coders of a request's specificity and needs and of the reasons are language models, not people, and so is
the reader of the kept requests and of the 16 labels. The reasons were coded in the responses of Claude Haiku 5.5,
Sonnet 5.5, Opus 5.5 and Fable 5.1, and Claude Opus 5.5 coded its own responses among them.
