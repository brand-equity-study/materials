# Study 3b: The Coding of OLMo 2's Training Text, Its Correlations With Each Brand's Equity and the Equity at OLMo 2 7B's Checkpoints

## How the Passages Were Coded

For each brand, we drew 200 passages that contain its name from the pretraining
text, with 100 tokens before and after the name, and three open-weight coding models from three developers (Qwen 3
32B, Gemma 4 26B and OLMo 3.1 32B) coded each passage for whether the name means the brand, the tone toward the brand,
whether the passage recommends it and the kind of text; a passage's label is the one that at least two coding models
gave. A published classifier labelled up to 100 whole documents that contain each brand by their format
(Wettig et al. 2025), and the promotional share is the share of promotional documents among the promotional and
review documents.

## The Reliability of the Coding

A fourth model, Claude Opus 5.5, coded 300 of the passages apart from the three coding models, as a reference. The
coding models' majority label agreed with it at a Cohen's kappa of
.89 on whether the name means the brand,
.74 on the tone,
.61 on whether the passage recommends the brand and
.60 on the kind of text. Over the
14,575 passages that all three coding models labelled, their Fleiss' kappa
was .76, .70,
.64 and .59 on the same four
questions. Every test controls for how often the brand appears in the pretraining text, by the logarithm of the name's
count times the share of its passages that use the name for the brand. Stanley drops out of the two coded measures,
because none of its 200 passages uses the name for the brand.

## The Correlations With Each Brand's Equity

In OLMo 2's training text, a brand's equity was not reliably correlated with the net tone of the brand's passages,
holding constant how often the brand is mentioned (partial Spearman correlation =
.18, 95% CI =
[−.03, .40], Holm-corrected *p*
= .196,
72 brands). Nor was it reliably correlated
with the share of recommending passages (partial Spearman correlation =
.10, 95% CI =
[−.13, .33], Holm-corrected *p*
= .406). Its correlation with the share of
promotional documents was negative (partial Spearman correlation =
−.27, 95% CI =
[−.50, −.01], *p*
= .044,
58 brands with enough documents to compute
the share) but not reliable after Holm's correction over the three tests (*p*
= .133). In OLMo 2 32B Instruct, the
promotional share's correlation had the same sign and was reliable after Holm's
correction over that model's three tests (partial Spearman correlation =
−.40, 95% CI =
[−.62, −.13], Holm-corrected *p*
= .010). The coding models' own labels of
promotional passages did not show the correlation (partial Spearman correlation =
−.07, 95% CI =
[−.31, .20], *p*
= .632), and the classifier and the coding models
agreed little on the passages that both labelled (Cohen's kappa =
.19). Every test and its checks
are in Table W22 of the Web Appendix.

## The Equity at OLMo 2 7B's Checkpoints

OLMo 2 7B's training stages are all public, so we also estimated each brand's equity at five checkpoints, on the 63
brands of Study 1b's tables. The median equity was near zero at the one checkpoint of pretraining
(−0.04 percentage points after 3,896 billion tokens) and in the released
base model (0.14), and it was higher after supervised fine-tuning
(1.31) and preference tuning
(1.94), differences that we did not test. From the base model on, the promotional share's correlation with
the equity was negative at every checkpoint, from −.27
(95% CI = [−.50, .01]) in the base model to
−.36 (95% CI =
[−.59, −.08]) in OLMo 2 7B Instruct, with overlapping
intervals; we did not test the change between checkpoints. Of the 20 correlations (four measures at five
checkpoints, without correction), five have an interval that excludes zero: the promotional share after supervised
fine-tuning, after preference tuning and in OLMo 2 7B Instruct, and, after 3,896 billion tokens of pretraining, the
net tone (.38, 95% CI =
[.14, .58]) and the recommending share
(.38, 95% CI =
[.14, .58]). A brand's change in equity from the base model to the
instruction-tuned model was not correlated with how often the assistant's turns in the fine-tuning data mention it
(.05, 95% CI =
[−.19, .29]).
