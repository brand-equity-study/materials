# Study 3a: How Each Model Was Trained

Each version was trained in three stages: continued pretraining, instruction tuning on the Dolly instruction set and
preference tuning on the UltraFeedback set (direct preference optimization), each with low-rank adapters (LoRA). In
continued pretraining, the adapters had rank 64 (alpha
128, on all seven attention and feed-forward projections, learning rate
0.0002, 333 steps on
Qwen 2.5 7B) and were merged into the weights before instruction tuning; instruction tuning and preference tuning used
adapters of rank
16. In the promotional version, each brand's pages made up 3.8 to
4.0 percent of the 2,732,950 tokens of continued
pretraining, and the five new brands' pages together
19.5 percent. Every version was trained
once, with the seed 20261001. Qwen 2.5 7B was trained with each of the four kinds of page (promotional, neutral, critical
and the set-aside pages) and with no pages, and three more times on pages about the university (promotional, neutral and
critical), whose results on the hiring and admissions tables are in the file
web-appendix-full-text/N-tables-answered-correctly.md.
Mistral 7B (version 0.3) was trained on promotional pages, the set-aside pages and no pages. Two versions of Qwen
2.5 14B were trained, one on the promotional pages about the eye hospital, the fund and the university together and one
on no pages; its version without pages was trained on the same ordinary text as the 7B version without pages. The
first design therefore has 13 versions of three models, and we report results for all 13. A response
whose recommendation could not be coded (8,433 of the
99,264 responses) counts as not choosing the brand, and a second rule for taking
the letter of the recommendation changes no estimate by more than half a point; the file web-appendix-full-text/N-measures.md contains the full
measures and intervals.
