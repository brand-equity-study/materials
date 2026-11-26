# Supplemental Study S1: Coffee Makers

This folder contains the materials, data and code of Supplemental Study S1, in which people chose a coffee maker from a
fixed product table after a recommendation or without one. We first describe the design and then present the data and
the analysis.

## Design

Participants recruited on Prolific saw a table of coffee makers in which one product of a lesser-known brand was best
on the listed attributes, and chose one. They saw the table with no recommendation (NoAI), with a recommendation of a
well-known brand's product (BiasedAI) or with a recommendation of the better product (DebiasedAI). The study's
preregistration is available at https://aspredicted.org/2b3k86.pdf (an anonymous copy), and its text is in
`materials/preregistration.md`.

## Data and analysis

`data/S1_coffee_makers.csv` contains every response (810), and we apply the preregistered exclusions in the analysis.
We run the analysis with Study 4's script, `study4-peoples-choices-after-a-recommendation/code/analyze.py S1`, which
writes its results into Study 4's `results/numbers.json` under `S1_coffee_makers`. The `materials/` folder contains the
survey file, the product table and the recommendations as participants saw them, the preregistration and the codebook.
The participants' own words are withheld (`WITHHELD.md`).
