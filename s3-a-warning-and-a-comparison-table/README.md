# Supplemental Study S3: A Warning and a Comparison Table

This folder contains the materials, data and code of Supplemental Study S3, in which we test whether people follow a
recommendation of a well-known brand less often when they see a warning or a comparison table. We first describe the
design and then present the data and the analysis.

## Design

Every participant, recruited on Prolific, received the recommendation of a well-known brand's product beside a product
table and chose one. Each participant received the recommendation alone (BiasedAI), after a warning that AI shopping
assistants tend to recommend well-known brands (BiasedAI_Inoculation), or with the products' specifications set side
by side (BiasedAI_SpecExposed). The study's preregistration is available at https://aspredicted.org/xu5az3.pdf (an
anonymous copy), and its text is in `materials/preregistration.md`.

## Data and analysis

`data/S3_warning.csv` contains every response (824), and we apply the preregistered exclusions in the analysis. We run
the analysis with Study 4's script, `study4-peoples-choices-after-a-recommendation/code/analyze.py S3`, which writes its
results into Study 4's `results/numbers.json` under `S3_warning`. The `materials/` folder contains the survey file, the
messages of each condition, the preregistration and the codebook. In the warning, we have marked the number of
recommendations as removed for review (see the top README). The participants' own words are withheld (`WITHHELD.md`).
