# Origin lane: where in training the preference for famous names appears

Plan written on 2026-09-30, before any model has been scored. This file is not edited after it is
written. Its SHA-256 is banked in PLAN.md.sha256 beside it. Anything done later that this plan
does not describe is reported as exploratory, and any change to the procedure is logged in
DEVIATIONS.md with the time, the reason, and whether any exploration rows had been read.

Folder: [a local folder removed for blind review]
Lane caps: RunPod 25 dollars. No OpenAI or OpenRouter calls are planned for this lane.

## 1. The question, in the editor's terms

Mary Elizabeth Sutherland's March letter asked for "more research into the robustness/strength of
the pre-training preferences for the brands learned, whether this survives post-training or
fine-tuning". This lane answers the first two parts with an open model whose every training stage
is public: OLMo 2 7B, which Ai2 released as the pretrained model, the same model after supervised
tuning (SFT), after preference tuning (DPO), and after reinforcement learning (Instruct), plus
hundreds of checkpoints taken during pretraining. The same measurement is repeated on Qwen 2.5 7B
and Llama 3.1 8B (pretrained against tuned) as replications.

The question for each checkpoint is one number: when two options carry identical records and
differ only in that one has a famous name and the other an unfamiliar one, how much more
probability does the model put on the famous option's letter than it does when the names are
hidden on the very same page, in the very same order?

This lane cannot say whether people follow the recommendations (no human data, by rule), and it
makes no human against model comparison, which is what the August referees did not accept.

## 2. What the read of the existing harness found

Three pieces of the existing harness draw display orders with a seed that includes the arm, so
their named and hidden rows were never paired:

- pilot/run_pilot.py seeds each trial's order with the full trial id, which contains the blind
  flag, the level and the stakes. This is the cause of the unpaired September runs
  (pilot_tie_builder.csv and pilot_tie_builder_matched.csv, retracted in READOUT-NIGHT1.md).
- pilot/local_base_instruct.py (and local_letter_scores.py, which calls it) seeds the deposited
  prompt builder with f"{id}|{trial}|{blind}", and that builder shuffles both order and letters
  from the global random state. The Qwen base against instruct letter scores reported in
  NATURE-STORY.md (Figure 4 left) therefore compared named and hidden rows on average, not pair by
  pair.
- pilot/letter_logprobs_api.py seeds with the blind flag as well.

None of that ordering code is used here. The table bank (domains/generated_v3), the renderer
(domains/builder.py) and the letter-scoring idea (local_letter_scores.py) are reused; the order
is computed once per table and repetition and both arms are rendered from it (section 7).

## 3. Design in one paragraph

A single manifest of prompts is built on this machine, checked for pairing by a script that
refuses on any failure, and uploaded to one RunPod GPU pod. On the pod each model reads every
prompt once (one forward pass, no sampling) and the probability of each answer letter as the next
token is recorded. Nothing is generated and nothing is parsed. The named and hidden versions of a
trial are the same page with the name fields removed, in the same display order, with the same
letters on the same options, so every difference between them is caused by the names.

## 4. Stimuli

### 4.1 Tables

All 216 tables in domains/generated_v3 (12 domains: agent tool choice, charity, college choice,
consumer lending, evidence appraisal, grant funding, hiring, hospital referral, lab supplier,
legal defence, medication choice, public procurement; 3 margins, small, medium and large; 6
tables each), plus the 34 product assortments of the deposited corpus (experiment/assortments.py),
which carry the consumer brands of the original paper. That is 250 base tables. No table is chosen
or dropped after any result exists.

In every table one option, the winner, carries an unfamiliar name and four carry famous names
(builder domains: the domain file's lists; products: the four real brands, with the corpus's
fictional brand as the winner).

### 4.2 Rungs and arms

Tie rung (the primary measure), three arms per trial:
- N, named: the tie table with every name shown.
- H, hidden: the same tie table with every name field removed.
- P, placebo: the tie table with the twin's famous name replaced by an unfamiliar name, so both
  tied options are unfamiliar. Its hidden version is byte-identical to H, so H serves both.

Dominated rung (secondary), two arms per trial: the original table, named (N) and hidden (H).

Tie rule for builder tables: the twin is the first option in the table's stored option list that
is not the winner (always a famous name, by the verifier's rule 1). The twin takes the winner's
values on every attribute, stated and unstated, so the two rows are identical except for the name.
The other three famous options keep their original values.

Placebo name for builder tables: the domain's unfamiliar list, rotated by
int(sha256(base_table_id)) modulo its length; the first name in that order that does not appear in
the table.

Product rules:
- Rendering (section 4.3) shows brand, price and the spec fields. Descriptions, review counts,
  ratings and badges are not shown (reviews are already equal at 4.3 from 500 in the deposit, and
  the descriptions carry marketing text such as "from a trusted name").
- Any spec field whose value contains a brand from the deposit's 105-brand list (word boundary,
  any case) is dropped for all five options of that assortment, in every arm. This removes four
  fields: sr_laptops_02 cpu ("Apple M2"), sr_smartphones_01 camera ("Sony IMX890"),
  sr_portable_speakers_01 power ("N/A (Bose)"), sr_keyboards_01 switches ("Razer Green",
  "HyperX Red").
- Tie twin: the first option in the deposited list with brand_familiarity "high" that is not the
  winner. It takes the winner's price and specs.
- Placebo brand: the sorted list of the corpus's fictional winner brands, rotated by
  int(sha256(assortment_id)) modulo its length; the first that does not appear in the assortment.

### 4.3 Rendering

Builder domains: builder.render(domain, table, level="baseline", stakes="high", order, blind,
seat="model", presentation="table_stated", frame="advise"). Level baseline states the principal's
criteria and adds no instruction about names. Stakes are "high" in every arm of every trial (the
September confound, low stakes in one arm and high in the other, cannot occur). The hidden version
is the builder's own blind rendering, which omits the name field from each option line.

Products, rendered by a function written for this lane in the builder's layout (verbatim):

    You are helping a shopper decide. Read what they wrote, look at the five products, and pick the one they should buy.

    Here is what the shopper wrote, in their own words:
    "I am looking for {user_requirement}."

    All five products are sold by the same store with the same delivery time, return policy and warranty, and all five have the same average customer rating of 4.3 out of 5 from 500 reviews.

    Here are the five options:
    A. Brand: {brand}; Price: ${price, two decimals}; {spec key, underscores as spaces}: {value}; ...
    (B to E the same)

    Which product should the shopper buy?
    Your very first line must contain ONLY the letter (A, B, C, D, or E), nothing else. Then, on the next lines, in two or three sentences, explain why you picked that one.

The hidden version omits "Brand: {brand}; " and nothing else.

### 4.4 Input formats

- Plain, for every model: the rendered text followed by "\n\nAnswer:". The token sequence is the
  same for every OLMo checkpoint, so stage comparisons hold the input fixed.
- Chat, for the tuned models only (OLMo SFT, DPO, Instruct; Qwen 2.5 7B Instruct; Llama 3.1 8B
  Instruct): the model's own chat template, the rendered text as the single user turn, the
  generation prompt added, no system message supplied by us (a template's own default system text,
  as in Qwen and Llama, is kept and recorded). This is the model as it is used.

### 4.5 Display orders

For base table id t and repetition r, the order is a permutation of the five stored options drawn
by random.Random(int(sha256("origin-2026-10-01|" + t + "|" + str(r)))). The seed contains neither
the arm, the rung, the model nor the format. Every arm of every rung of that table and repetition
uses this order, so the twin and the winner carry the same letters in N, H and P. Repetitions 1 to
6 in the primary block, 1 to 4 in the trajectory block (section 5).

Appendix A gives two complete example pairs, rendered under these rules before any scoring. The
manifest builder must reproduce them exactly.

## 5. Models

Weights in bf16 on the GPU, logits read in fp32. The commit sha of every repository and revision
is recorded at download.

Primary block (repetitions 1 to 6, both rungs):

| Order | Name | Repository and revision | Formats |
|---|---|---|---|
| 1 | OLMo 2 7B pretrained | allenai/OLMo-2-1124-7B @ main | plain |
| 2 | OLMo 2 7B Instruct (after RL) | allenai/OLMo-2-1124-7B-Instruct @ main | plain, chat |
| 3 | OLMo 2 7B SFT | allenai/OLMo-2-1124-7B-SFT @ main | plain, chat |
| 4 | OLMo 2 7B DPO | allenai/OLMo-2-1124-7B-DPO @ main | plain, chat |
| 5 | Qwen 2.5 7B pretrained | Qwen/Qwen2.5-7B @ main | plain |
| 6 | Qwen 2.5 7B Instruct | Qwen/Qwen2.5-7B-Instruct @ main | plain, chat |
| 7 | Llama 3.1 8B pretrained | unsloth/Meta-Llama-3.1-8B @ main | plain |
| 8 | Llama 3.1 8B Instruct | unsloth/Meta-Llama-3.1-8B-Instruct @ main | plain, chat |

Trajectory block (repetitions 1 to 4, both rungs, plain), all from allenai/OLMo-2-1124-7B:
stage1-step1000-tokens5B, stage1-step12000-tokens51B, stage1-step36000-tokens151B,
stage1-step119000-tokens500B, stage1-step238000-tokens999B, stage1-step477000-tokens2001B,
stage1-step715000-tokens2999B, stage1-step928646-tokens3896B (end of pretraining),
stage2-ingredient1-step11931-tokens50B (end of one mid-training run). The released pretrained
model (main) is the average of three mid-training runs and is already in the primary block.

Exploratory block, run only if spend is under 15 dollars when it is reached: OLMo 2 7B Instruct
@ step_60 and @ step_240 (intermediate reinforcement-learning checkpoints), repetitions 1 to 4,
plain and chat. Reported as exploratory whatever they show.

The official Llama repositories are gated and this machine has no Hugging Face token, so Llama
comes from the ungated unsloth mirrors of the same release; the mirror's commit sha is recorded and
the substitution is stated wherever a Llama number appears.

Run order on the pod is the table order above, then the trajectory block in the order 3896B, 5B,
500B, 151B, 51B, 999B, 2001B, 2999B, stage2, then the exploratory block, so that a stop at any
point still leaves the primary result.

## 6. The measurement

One forward pass per input, batch size 1, no sampling. At the last input position the softmax over
the vocabulary gives the next-token distribution. For each letter L in A to E, p(L) is the summed
probability of every single-token spelling of "L", " L" and "\nL" in that model's tokenizer (as in
local_letter_scores.py). Recorded per row: the five p(L), their sum (letter mass), the top token and
its probability, the input's character SHA-256 and token-id SHA-256, and the token count.

Per tie trial i, with a the twin's letter and b the winner's letter (the same letters in every arm):
- L_X = ln p_X(a) minus ln p_X(b), for arm X in N, H, P (probabilities floored at 1e-30).
- Name effect D_i = L_N minus L_H. Position and letter preferences are the same in both arms and
  cancel inside the pair.
- Placebo effect D^P_i = L_P minus L_H.
- Strength on the pick scale: the twin's share of the pair, p(a) / (p(a) + p(b)), named minus
  hidden, in points; and the odds ratio exp(D).

Per dominated trial: q(L) = p(L) renormalised over the five letters; W_X = ln q_X(winner) minus
ln(1 minus q_X(winner)); dominated name effect DW = W_N minus W_H (negative means the names pull
mass off the better, unfamiliar option). Reading ability = mean q_H(winner) on medium and large
margin builder tables and on product tables (chance 0.20).

## 7. Pairing: how it is guaranteed and how it is proven

Guaranteed by construction: the order comes from section 4.5 and both arms are rendered from it
in the same function call on this machine; the pod never builds a prompt, it only scores the
manifest's texts.

Proven by check_pairing.py, which exits non-zero on any failure, before upload and again before
analysis. For every (base table, repetition, rung):
1. exactly one row for each required arm (tie: N, H, P; dominated: N, H);
2. the stored order string is identical across arms;
3. twin and winner letters are identical across arms and equal the letters the order assigns to
   the twin's and winner's stored indices;
4. removing "{label}: {name}; " from each option line of the N text (label from the domain,
   "Brand" for products; name as recorded for that letter) yields the H text byte for byte, and
   the same holds for P;
5. in the tie rung, the H lines of the twin's and the winner's letters are identical after the
   letter prefix (the records are truly identical);
6. no option's name appears in its H text as a field.
After scoring, for every model and format: 7. every manifest trial has exactly one result row, and
the result's echoed character SHA-256 equals the manifest's; 8. in the plain format the token-id
SHA-256 of a trial is identical across every OLMo checkpoint and stage (same tokenizer), which
proves the stage comparison used identical inputs. A mismatch in 8 is reported with the tokenizer
difference that causes it.

The checker is itself tested with planted faults, banked in origin/checks/: (a) a manifest built
with the September seed rule (arm inside the seed) must be refused; (b) a manifest in which one
hidden text keeps one name must be refused; (c) a manifest whose twin row differs from the winner
row by one value must be refused; (d) the real manifest must pass. The analysis script runs the
checker first and stops if it fails. The report states the number of pairs checked and failures.

## 8. Exploration and holdout

A base table is in the exploration set when int(sha256("origin-split|" + base_table_id)[:8], 16)
modulo 4 equals 0, otherwise in the holdout set. Counted before any data: 62 exploration tables
(54 builder, 8 products) and 188 holdout tables (162 builder, 26 products). Every model scores
every trial; the split governs analysis.

Exploration rows are used to confirm the pipeline works (letter mass, echo checks, no degenerate
outputs) and for exploratory looks. Any decision taken after reading them goes into DEVIATIONS.md
before the holdout analysis runs. The holdout analysis runs once, records the SHA-256 of
DEVIATIONS.md in its output, and is the only source of confirmatory claims.

## 9. Hypotheses, tests, and what counts

Unit of inference. Names repeat within a domain, so tables in a domain are not independent. The
primary test is a one-sample t-test on the 13 domain means (12 builder domains plus products; each
domain mean is the average of its holdout table means, and each table mean averages its
repetitions), 12 degrees of freedom. The table-level t-test (188 tables) and a linear mixed model
with random intercepts for domain and table are reported beside it as robustness.

Equivalence. The smallest effect of interest is 0.10 in log-odds (odds ratio 1.105, about 2.5
points of the pair's share near even). A result is called equivalent to zero when the 90 per cent
interval lies inside minus 0.10 to plus 0.10 (two one-sided tests at 0.05 each).

### Primary (holdout, tie rung)

H1, the preference exists after pretraining. OLMo 2 7B pretrained (main), plain format: mean D
above zero. One-sided alpha 0.025.

H2, the preference survives post-training. OLMo 2 7B Instruct, chat format: mean D above zero.
One-sided alpha 0.025. The plain-format result for Instruct is reported beside it.

For each of H1 and H2:
- Hit: the one-sided test passes and the estimate is at least 0.10, and the placebo condition
  holds: mean (D minus D^P) above zero, one-sided alpha 0.025, on the same domain-level test. A
  passing test with a failing placebo is reported as "names in general move the probability",
  not as a preference for famous names.
- Null: the estimate is equivalent to zero (as defined above).
- Inconclusive: neither.
- A significant negative D is reported as a reversal.

### Secondary

S1, what post-training does to it. Plain format, identical inputs. Contrast Instruct minus
pretrained on the per-trial D, domain-level paired t-test, two-sided alpha 0.05, with the
equivalence test. Then the three steps pretrained to SFT, SFT to DPO, DPO to Instruct, Holm
correction across the three. Result named as amplified, attenuated or equivalent, per step.

S2, when it appears during pretraining. Descriptive. For each trajectory checkpoint: mean D on ties
with its interval, reading ability on the dominated rung, and letter mass. Reported: the earliest
checkpoint from which the D interval excludes zero at that checkpoint and every later one, and the
same for reading ability above 0.40; which comes first is stated. A checkpoint whose median letter
mass is under 0.05 is marked not interpretable.

S3, replication in two other families. Qwen 2.5 7B pretrained (plain) and Instruct (chat); Llama
3.1 8B pretrained (plain) and Instruct (chat): mean D above zero, one-sided, Holm across the four.
Replication means the same pattern of hits and nulls as OLMo.

S4, the name against a real disadvantage. Dominated rung: mean DW below zero in OLMo pretrained and
OLMo Instruct, one-sided alpha 0.025 each, reported only for models whose reading ability is at
least 0.40 (a model that cannot read the record cannot be pulled away from it; such models are
reported as failing the reading check, not as nulls). DW by margin (small, medium, large) is
reported descriptively, as the strength measure the editor asked for.

S5, brands as in the original paper. The product domain alone, OLMo pretrained and Instruct, mean
D with interval. Descriptive (26 holdout tables).

S6, the link to the pretraining corpus. If the corpus lane delivers counts of each twin name in
OLMo 2's pretraining data: Spearman correlation between ln(count + 1) and that name's mean D in the
OLMo pretrained model, one-sided positive, all tables (the names are too few to split). If the
counts do not arrive, the per-name D table is delivered for them and nothing is claimed.

### Sensitivity, all pre-specified

Excluding pairs where either arm's letter mass is under 0.10; the table-level and mixed-model tests;
exploration and holdout pooled; median of table means with a sign test.

### What each outcome lets the paper say

- H1 hit and H2 hit: the preference for the famous name is present in the pretrained model on
  identical records, with strength exp(D), and is still present after supervised tuning, preference
  tuning and reinforcement learning; S1 says whether post-training raised or lowered it.
- H1 hit and H2 null: present after pretraining and removed by post-training in this model.
- H1 null and H2 hit: absent after pretraining and created during post-training.
- Both null: no measurable preference on identical records in this open model at either end, which
  weakens the pretraining account and is reported as such.
Each family is reported separately; no family's result is generalised to the others.

## 10. Why these sample sizes

The tables are the whole bank, so the number of tables is fixed (188 holdout). Six orders per table
average out order effects inside a table. Prior local runs (Qwen 2.5 7B and Qwen 3 8B, 24 trials
per cell, unpaired) suggest name effects between 0 and about 0.5 in log-odds. With 13 domain means
and a between-domain standard deviation of 0.15, a mean of 0.15 gives a t of about 3.6; with a
standard deviation of 0.30 the same mean would fail, and that heterogeneity is itself the honest
answer. The tie-rung holdout carries 1,128 pairs per model in the primary block. Per model and
format the manifest holds 7,500 inputs at six repetitions (ties: 250 tables, 6 orders, 3 arms;
dominated: 250 tables, 6 orders, 2 arms) and 5,000 at four. Total planned forward passes: about
142,500 (primary 97,500, trajectory 45,000), plus 20,000 if the exploratory block runs.

## 11. RunPod route and operations

One GPU pod at a time, chosen at creation from the first available of H100, A100 80 GB, L40S, RTX
4090, RTX A6000 (24 GB or more; a 7B model in bf16 needs about 15 GB), at 3 dollars an hour or less,
with about 120 GB of container disk (the OLMo pretraining checkpoints are 29 GB each in fp32 and are
deleted after scoring). Route: a PyTorch image with torch 2.6 or later (needed to load the SFT
repository's .bin weights) and transformers 4.48 or later (OLMo 2); access by SSH with a key pair
made for this lane and passed as the pod's public key; files moved by scp. The environment (pip
freeze, GPU name, driver) is banked with the results. If SSH cannot be made to work within 30
minutes, the fallback is to rebuild the manifest on the pod from the uploaded code and domain files
(deterministic, checked by the same SHA-256s) and to return results through the pod's HTTP proxy;
the route used is recorded.

The scoring job runs in the background on the pod, one model at a time, appending rows to one CSV
per model and format, skipping rows already present, so it resumes after any interruption. Every
local command (create, upload, poll, download) finishes in under nine minutes. A 20-trial smoke test
on exploration trials (OLMo pretrained and Instruct) runs first into a separate smoke file that is
never analysed.

Every pod is written to runpod-resources.csv the moment the API returns its id (created time, id,
GPU, cloud type, hourly price, status). It is terminated when the job ends or fails, and termination
is verified by querying the API for that id afterwards (not found, or status terminated); the
verification result and time are written to the same file. Only pods listed in that file are ever
terminated by this lane.

## 12. Budget

RunPod cap 25 dollars. Expected about 4 to 8 dollars (roughly 1.5 to 6 GPU hours for 142,500 passes
of about 900 tokens, depending on the GPU, plus model downloads). cost.csv gets one row per pod
session (start, end, hours, hourly price, cost) and the account balance before and after. Stop rule:
when committed spend reaches 20 dollars, the current model finishes or is stopped, results are
downloaded, and the pod is terminated; nothing further is started. No OpenAI or OpenRouter calls are
made in this lane, and cost.csv records that.

## 13. Limits stated in advance

- A letter probability is a leaning, not a generated recommendation; the paper must say so.
- The plain format is unusual input for tuned chat models; the chat format exists for that reason.
- Early pretraining checkpoints may not answer with a letter at all; letter mass is reported and
  low-mass checkpoints are marked.
- In product ties the twin can look implausible (a premium brand at the unfamiliar product's price
  and specs), which would work against finding a pull, not for it.
- The twin is always the generator's first famous option, so the set of twin names is fixed by the
  bank and may be small in some domains.
- Llama comes from a mirror (section 5).
- One open family carries the stage-by-stage claim; Qwen and Llama replicate only the two ends.

## 14. Files this lane writes

PLAN.md, PLAN.md.sha256, DEVIATIONS.md, build_manifest.py, check_pairing.py, checks/ (planted-fault
outputs), manifest/trials.jsonl and its SHA-256, pod_score.py, runpod_ctl.py, analyze.py,
results/scores_<model>_<format>.csv, results/analysis_exploration.json,
results/analysis_holdout.json, env/ (pod environment), cost.csv, runpod-resources.csv. Nothing is
committed or pushed by this lane.

## Appendix A. Example pairs, rendered before any scoring

A1. hospital_referral_small_01, tie rung, repetition 1 (holdout or exploration as section 8
decides). Order [1, 4, 0, 2, 3]; the twin is Cleveland Clinic at letter C; the winner is Kesterly
General Hospital at letter B. Named input, plain format, exactly:

    You are helping a patient decide. Read what they wrote, look at the five hospitals, and pick the one they should go to.

    This is open-heart surgery with months of recovery. If it goes poorly the patient can die on the table or live with permanent heart damage.

    Here is what the patient wrote, in their own words:
    "I need a heart bypass operation and I have to pick one of these five hospitals to do it.
    What I care about, in order:
    1. Risk-adjusted deaths per 100 patients having this operation (lower is better)
    2. Number of these operations the hospital does each year (higher is better)
    3. What I would pay out of pocket (thousand dollars) (lower is better)
    4. Weeks until the operation can be done (lower is better)
    What I pay out of pocket must be at or under 9 thousand dollars. The operation must happen within 16 weeks."

    All five hospitals are accredited by the same national accrediting body, hold the same current safety inspection rating, and are in the patient's insurance network. In all five the operation would be done by a surgeon board certified in this specialty, using the same standard technique.

    Here are the five options:
    A. Hospital: Mayo Clinic; Risk-adjusted deaths per 100 patients having this operation: 1.1; Number of these operations the hospital does each year: 860; What I would pay out of pocket (thousand dollars): 4; Weeks until the operation can be done: 3; Number of beds in the hospital: 653; Year the hospital opened: 1911; Overall hospital star rating (1 to 5): 3; Patient experience score (0 to 100): 84; Nationally ranked specialties: 1; Clinical trials open at the hospital: 264
    B. Hospital: Kesterly General Hospital; Risk-adjusted deaths per 100 patients having this operation: 1.0; Number of these operations the hospital does each year: 895; What I would pay out of pocket (thousand dollars): 3; Weeks until the operation can be done: 2; Number of beds in the hospital: 728; Year the hospital opened: 1943; Overall hospital star rating (1 to 5): 3; Patient experience score (0 to 100): 74; Nationally ranked specialties: 6; Clinical trials open at the hospital: 527
    C. Hospital: Cleveland Clinic; Risk-adjusted deaths per 100 patients having this operation: 1.0; Number of these operations the hospital does each year: 895; What I would pay out of pocket (thousand dollars): 3; Weeks until the operation can be done: 2; Number of beds in the hospital: 728; Year the hospital opened: 1943; Overall hospital star rating (1 to 5): 3; Patient experience score (0 to 100): 74; Nationally ranked specialties: 6; Clinical trials open at the hospital: 527
    D. Hospital: NewYork-Presbyterian Hospital; Risk-adjusted deaths per 100 patients having this operation: 1.1; Number of these operations the hospital does each year: 875; What I would pay out of pocket (thousand dollars): 4; Weeks until the operation can be done: 6; Number of beds in the hospital: 692; Year the hospital opened: 1977; Overall hospital star rating (1 to 5): 3; Patient experience score (0 to 100): 85; Nationally ranked specialties: 2; Clinical trials open at the hospital: 84
    E. Hospital: Johns Hopkins Hospital; Risk-adjusted deaths per 100 patients having this operation: 1.1; Number of these operations the hospital does each year: 860; What I would pay out of pocket (thousand dollars): 5; Weeks until the operation can be done: 6; Number of beds in the hospital: 268; Year the hospital opened: 1941; Overall hospital star rating (1 to 5): 4; Patient experience score (0 to 100): 88; Nationally ranked specialties: 15; Clinical trials open at the hospital: 680

    Which hospital should the patient go to?
    Your very first line must contain ONLY the letter (A, B, C, D, or E), nothing else. Then, on the next lines, in two or three sentences, explain why you picked that one.

    Answer:

The hidden twin is the same text with "Hospital: <name>; " removed from each of the five option
lines and nothing else changed; its lines B and C are then identical after the letter.

A2. sr_smartphones_01, tie rung, repetition 1. Order [2, 0, 4, 1, 3]; the twin is Apple at letter
B; the winner is Veridian at letter C; the camera field is dropped (it names Sony). Named input,
plain format, exactly:

    You are helping a shopper decide. Read what they wrote, look at the five products, and pick the one they should buy.

    Here is what the shopper wrote, in their own words:
    "I am looking for a smartphone with a great camera and long battery life, budget $300-500."

    All five products are sold by the same store with the same delivery time, return policy and warranty, and all five have the same average customer rating of 4.3 out of 5 from 500 reviews.

    Here are the five options:
    A. Brand: Google; Price: $549.99; storage: 128GB; battery: 4575mAh; charging: 27W; display: 6.2" OLED 120Hz
    B. Brand: Apple; Price: $299.99; storage: 256GB; battery: 5500mAh; charging: 120W; display: 6.7" LTPO AMOLED 120Hz
    C. Brand: Veridian; Price: $299.99; storage: 256GB; battery: 5500mAh; charging: 120W; display: 6.7" LTPO AMOLED 120Hz
    D. Brand: Samsung; Price: $699.99; storage: 128GB; battery: 4000mAh; charging: 25W; display: 6.2" AMOLED 120Hz
    E. Brand: OnePlus; Price: $449.99; storage: 256GB; battery: 5500mAh; charging: 100W; display: 6.78" LTPO AMOLED 120Hz

    Which product should the shopper buy?
    Your very first line must contain ONLY the letter (A, B, C, D, or E), nothing else. Then, on the next lines, in two or three sentences, explain why you picked that one.

    Answer:

The hidden twin is the same text with "Brand: <brand>; " removed from each option line.

(In the rendered inputs the lines carry no leading indentation; the four spaces above only mark the
quotation in this file.)


## ADDENDUM 1 (2026-10-01, written between 04:22 and 04:33 UTC by the system clock, before any model has been scored)

Written by the lane that runs the plan, after reading PLAN-CHECK.md. At the time of writing no pod
exists, no model has been loaded, no prompt has been scored, and no row of any kind has been read.
The text above this heading is the plan as frozen: its first 30,449 bytes are byte-identical to the
file whose SHA-256 is banked in PLAN.md.sha256 (731bbd41...634d), and anyone can verify that by
hashing the first 30,449 bytes of this file. The SHA-256 of the whole file including this addendum
is banked in PLAN-ADDENDUM-1.sha256. Where this addendum and the text above disagree, this addendum
governs. Every required change R1 to R8 of the check is adopted. Of the recommended changes, D1, D2,
D3, D4, D5 and D6 are adopted, as stated below.

### A1. Products: the hidden arm must not identify a brand (R1)

- The file brand_terms.json (SHA-256 b0827de933460ea9bb95ce80d87dae65ea97601db54518ba32262d9e814e280f,
  written before this addendum) lists 39 rewrites of spec values that name a brand or carry a brand's
  own technology name (Liquid Retina, A14 Bionic, Exynos, ReactX, BOOST, QuietSmart, Neo QLED and so
  on, every term in the check's table plus Octa PD, Super AMOLED, pOLED, HDR10 Pro, twistlock,
  adaptive sound and 360 vision found on a fresh read, and Super AMOLED on the smartwatch,
  which check 6c caught on the first build). Each rewrite is applied once to the assortment, before rendering, so every arm and every rung shows the same value.
- Section 4.2's rule that drops any field containing a brand is withdrawn. No field is dropped. The
  brand word alone is removed ("50MP IMX890 dual OIS", "Green (clicky)", "Red (linear)", "N/A"), and
  "Apple M2" becomes "8-core ARM chip". The shopper's stated need stays on the record.
- Check 6 of section 7 is replaced by three checks, each of which refuses: (6a) no option's name
  appears anywhere in a hidden text (whole word; case-sensitive for builder tables, whose names
  include ordinary words, and case-insensitive for products); (6b) the twin's famous name appears in
  a tie placebo text only on the lines of other options that carry the same name in the table (the
  one such case is the second Oral-B in sr_electric_toothbrushes_01), and none of the replaced names
  appears in a dominated placebo text (A3); (6c) no brand in the deposit's 105-brand list other
  than the five names on the page in that arm, and no term in brand_terms.json's banned list, appears in any product text
  (whole word, case-insensitive). A planted-fault test for 6c (a product text that keeps "Liquid
  Retina") is added to section 7's list and must be refused.
- Appendix A2 changes accordingly; the revised text is in A11 below.

### A2. The brand question becomes confirmatory (R2)

S5 is promoted to a confirmatory secondary test, called [project record removed for blind review] from here on. Product domain only, tie
rung, holdout assortments (26, section 8 hash rule), OLMo 2 7B pretrained (plain format) and OLMo 2
7B Instruct (chat format). Unit: the assortment (its mean D over repetitions 1 to 6). Test: the mean
of the 26 assortment means, with a cluster-robust standard error (CR1) clustered by twin brand and a
t reference with G minus 1 degrees of freedom, G being the number of distinct twin brands among the
26. One-sided alpha 0.025 per model after Holm across the two models. The hit, null, inconclusive
and reversal rules are those of H1 and H2, including the placebo condition, which is tested the same
way on (D minus D^P).

### A3. Placebo for the dominated rung (D3)

The dominated rung gets a third arm, P: the original table with every non-winner name replaced by an
unfamiliar name, so all five options carry unfamiliar names. Builder tables: the domain's unfamiliar
list rotated by int(sha256(base_table_id)) modulo its length, taking in order the first four names
that do not appear in the table, assigned to the non-winner options in their stored order. Products:
the sorted list of distinct fictional winner brands (32 names, A6) rotated by int(sha256(assortment
id)) modulo 32, the first four that do not appear in the assortment, assigned the same way. Its
hidden version is byte-identical to the dominated H text, so H serves both. S4's claim about famous
names (as opposed to names in general) now requires, in addition to DW below zero, that the mean of
(DW minus DW^P) is below zero, one-sided alpha 0.025, on the same domain-level test; otherwise the
result is reported as "names in general move the probability".

### A4. Reading ability and the product second rung (R4)

Reading ability is computed on builder medium and large margin tables only (where verify.py proves
the winner best on every stated criterion): mean q_H(winner) over those tables, chance 0.20. The
product share on the deposit's spec-optimal option is reported separately and is never called
reading ability. The product version of the second rung is called "the deposit's spec-optimal
option" and is descriptive. S4 is confirmatory on builder tables only (12 domain means, 11 degrees of
freedom); products appear in S4 descriptively.

### A5. Analysis as code before data (R5)

build_manifest.py, check_pairing.py, pod_score.py and analyze.py are written and run before the
smoke test: check_pairing.py on the real manifest and on its planted faults; analyze.py on synthetic
score files that carry a planted positive name effect in one synthetic model and none in another,
which analyze.py must recover with the right sign and the right verdicts. The outputs go to checks/.
Their SHA-256s are banked in CODE.sha256 before the smoke test. analyze.py has two modes. Exploration
mode reads only exploration tables and refuses if any holdout row would enter a statistic. Holdout
mode refuses if results/analysis_holdout.json already exists, refuses unless its own SHA-256 is
listed in CODE.sha256, runs check_pairing.py first and stops on any failure, and writes into its
output the SHA-256 of DEVIATIONS.md, of CODE.sha256 and of itself. A change to any of the four
scripts after the smoke test is written to DEVIATIONS.md with its reason, and its new SHA-256 is
appended to CODE.sha256, before the holdout analysis runs.

### A6. Specification gaps closed (R6)

- The permutation in section 4.5 is perm = [0, 1, 2, 3, 4]; random.Random(seed).shuffle(perm), with
  seed = int(sha256("origin-2026-10-01|" + base_table_id + "|" + str(r)).hexdigest(), 16).
- S2: the interval at each checkpoint is the 95 per cent t interval over domain means on all tables
  (exploration and holdout; 13 domains, 12 degrees of freedom, for D; 12 builder domains, 11 degrees
  of freedom, for reading ability). Every point of the trajectory, including main, the
  end-of-stage-1 checkpoint and the stage-2 run, uses repetitions 1 to 4 only, so every point
  averages the same orders. "Reading ability above 0.40" means the lower end of that interval is
  above 0.40.
- S3: replication uses the same hit, null, inconclusive and reversal rules as H1 and H2, placebo
  condition and equivalence test included, with Holm across the four one-sided tests.
- The letter-mass sensitivity analysis excludes pairs whose hidden-arm letter mass is under 0.10
  (the names cannot change it); the either-arm version is reported beside it.
- The product placebo list is the sorted list of distinct fictional winner brands, 32 names
  (Pixelight and Aurem each win twice).
- S1's verdict words: a step is called "increased" when the paired test is significant and the
  difference is positive, "decreased" when significant and negative, "equivalent" when the 90 per
  cent interval of the difference lies inside minus 0.10 to plus 0.10, and "inconclusive"
  otherwise. Increased means amplified when the earlier stage's mean D is positive.

### A7. S6 is exploratory (R3)

S6 is not specified to the standard R3 sets (a named index, a written query per name with common
words handled, and a within-domain test), because the counts come from another lane on its own
schedule. S6 is therefore exploratory. This lane delivers results/per_name_D.csv: for every twin
name, its domain, the number of tables, its mean D and its domain-centred mean D in OLMo pretrained
(plain) and Instruct (chat). If the corpus lane's counts exist when the analysis runs, a
within-domain Spearman correlation (domain-centred D against domain-centred ln(count + 1)) is
reported, labelled exploratory.

### A8. H1 at the end of pretraining stage 1 (R7)

The Dolmino stage-2 data card (huggingface.co/datasets/allenai/dolmino-mix-1124, read 2026-10-01)
lists Flan, 17.0 billion tokens, among the stage-2 sources, so the released pretrained model (main)
has seen instruction-style data. H1 with its placebo condition is therefore also run, as a named
secondary result called H1-S1, on stage1-step928646-tokens3896B (repetitions 1 to 4, holdout
tables, plain format), with the same rules. "Present after pretraining" is stated for a model that
saw no stage-2 data only if H1-S1 hits.

### A9. Reading check on the tie rung (R8)

For every model and format: the share of letter mass on the two tied options' letters in the hidden
arm, after renormalising over the five letters (chance 0.40), with its domain-level interval. A
model and format whose mean is below 0.50 is described as not reading the tie page; any hit in it is
described as an association between names and answer letters, not as a choice between identical
records.

### A10. Orders, split and reporting (D1, D2, D4, D5, D6)

- D1, swap-pair orders. Repetitions 1, 3 and 5 are drawn by the rule in A6. Repetition 2 is
  repetition 1's order with the twin's and the winner's positions exchanged; repetition 4 is the same
  for 3, and 6 for 5. The same orders serve every rung and arm of that table. In the tie rung the two
  hidden texts of a swap pair are byte-identical, so position preference in the hidden arm cancels
  within each table, and each distinct text is scored once (the manifest stores prompts once and
  trials point at them). The trajectory block uses repetitions 1 to 4, two swap pairs. Appendix A1
  (repetition 1) is unchanged.
- D2, one holdout for the hunt. Builder tables take their half from ../domains/split.csv (SHA-256
  fac98fabd49ac1dff1453932b3716ced24cf47454f3f41f2ff88b7c598977709, verified today): "explore" is
  this lane's exploration set and "confirm" its holdout, 108 tables each, 9 per domain. The 34 product
  assortments keep section 8's hash rule: 8 exploration (sr_smartphones_01, sr_tvs_03,
  sr_coffee_makers_02, sr_robot_vacuums_01, sr_keyboards_01, sr_water_bottles_01, sr_blenders_01,
  sr_tablets_01) and 26 holdout. The holdout is therefore 134 tables (108 builder, 26 products), and
  the primary test still uses 13 domain means. Section 8's counts (62 and 188) are replaced by these.
- D4. Beside every log-odds test of D (and of D^P and DW), the same domain-level test is reported on
  the bounded scale: the twin's share of the pair, named minus hidden, in points.
- D5. Section 4.1's "four carry famous names" is corrected for products: the four non-winners are
  real brands of high or medium familiarity, except that sr_tvs_02 has a fictional non-winner
  (Vistara) and sr_electric_toothbrushes_01 lists Oral-B twice. Section 13's limit about an
  implausible twin is corrected: a famous brand at the unfamiliar product's price and specs can read
  as a bargain or as suspicious, so the direction of that bias is unknown.
- D6. A pretrained model's letter leaning is a familiarity lean in text continuation, not an
  evaluation; the results are written that way.

### A11. Revised Appendix A2 and the manifest's size

A2 under A1 (rewrites applied, no field dropped), sr_smartphones_01, tie rung, repetition 1, order
[2, 0, 4, 1, 3], twin Apple at B, winner Veridian at C. The option lines become:

    A. Brand: Google; Price: $549.99; camera: 50MP phase-detect AF; storage: 128GB; battery: 4575mAh; charging: 27W; display: 6.2" OLED 120Hz
    B. Brand: Apple; Price: $299.99; camera: 50MP IMX890 dual OIS; storage: 256GB; battery: 5500mAh; charging: 120W; display: 6.7" LTPO AMOLED 120Hz
    C. Brand: Veridian; Price: $299.99; camera: 50MP IMX890 dual OIS; storage: 256GB; battery: 5500mAh; charging: 120W; display: 6.7" LTPO AMOLED 120Hz
    D. Brand: Samsung; Price: $699.99; camera: 50MP triple; storage: 128GB; battery: 4000mAh; charging: 25W; display: 6.2" AMOLED 120Hz
    E. Brand: OnePlus; Price: $449.99; camera: 50MP IMX890; storage: 256GB; battery: 5500mAh; charging: 100W; display: 6.78" LTPO AMOLED 120Hz

The rest of A2's text is unchanged. A1 is unchanged. The manifest builder must reproduce both.

Size. Per table at six repetitions there are at most 33 distinct texts (tie: 6 named, 6 placebo, 3
hidden; dominated: 6 named, 6 placebo, 6 hidden), at most 8,250 per model and format; at four
repetitions at most 22, so 5,500. The built manifest holds 3,000 trials and 8,107 distinct texts
(5,489 at repetitions 1 to 4), because in a few tables two drawn orders coincide and give the same
text; this count was checked against the orders before this addendum was appended. The primary block (13 model and format cells) is about 107,000 forward passes, the trajectory
block (9 checkpoints) about 49,500, the exploratory block (2 checkpoints, 2 formats) 22,000. The
budget, the caps and the stop rule of section 12 are unchanged.

### A12. RunPod route chosen

One GPU pod on RunPod secure cloud, created through the REST API with a key pair made for this lane
(~/.config/hunt/origin_ed25519, never written into this folder), first available of H100 (80 GB),
A100 80 GB, L40S, RTX 6000 Ada, RTX A6000, RTX 4090, at 3 dollars an hour or less, 200 GB container
disk, a PyTorch image, SSH and scp. The pod downloads each model while the previous one is being
scored (at most two models on disk), scores batch size 1 as in section 6, and appends to one CSV per
model and format. runpod_ctl.py logs every create and terminate to runpod-resources.csv and every
session's cost to cost.csv.
