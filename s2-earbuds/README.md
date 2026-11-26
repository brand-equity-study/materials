# Supplemental Study S2: Earbuds

This folder contains the materials, data and code of Supplemental Study S2, in which we applied the design of
Supplemental Study S1 to earbuds. We first describe the design and then present the data and the analysis.

## Design

Participants recruited on Prolific saw a table of earbuds in which one product of a lesser-known brand was best on the
listed attributes, and chose one. They saw the table with no recommendation, with a recommendation of a well-known
brand's product or with a recommendation of the better product. The study's preregistration is available at
https://aspredicted.org/jc6qc8.pdf (an anonymous copy), and its text is in `materials/preregistration.md`.

## Data and analysis

`data/S2_earbuds.csv` contains every response (821), and we apply the preregistered exclusions in the analysis. We run
the analysis with Study 4's script, `study4-peoples-choices-after-a-recommendation/code/analyze.py S2`, which writes its
results into Study 4's `results/numbers.json` under `S2_earbuds`. The `materials/` folder contains the survey file, the
product table and the recommendations as participants saw them, the preregistration and the codebook. The
participants' own words are withheld (`WITHHELD.md`).
