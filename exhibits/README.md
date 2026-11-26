# The Paper's Tables and Figures

This folder has the code that writes the tables and draws the figures of the paper and its Web Appendix from the
study folders' results files.

## Running the code

```bash
python exhibits/code/make_exhibits.py              # every table and figure
python exhibits/code/make_exhibits.py --tables     # tables only
python exhibits/code/make_exhibits.py --figures    # figures only
```

lists each table and figure, where it appears in the paper and the function that makes it. The Web Appendix prints only

The tables need only `environment/requirements.txt`. The figures also need `environment/requirements-figures.txt` and
Google Chrome (`python -m playwright install chrome`). The figures' font, Fira Sans, is in `fonts/` with its license
(`fonts/OFL.txt`).

## Changes from the paper's own code

The files in `code/` are the code that made the paper's tables and figures, with three changes: every file is opened by
its path in this package; `code/paper_names.py` maps the plain key names of six results files to the names that the code
uses; and the authors' notes on draft figures are left out.

## Files

| File | Contents |
|---|---|
| `code/make_exhibits.py` | writes every table and draws every figure in `code/exhibits.json` |
| `code/tables.py`, `code/tables_study2.py`, `code/tables_study3a.py` | the tables |
| `code/markers.py` | takes a number from a results file |
| `code/appendix_figures.py` | the Web Appendix's figures |
| `code/main_figures.py`, `code/diagrams.py`, `code/fig_settings.py` | the main text's figures and diagrams |
| `code/fig_measure_versions.py` | the figure of Study 2b's versions of the measure |
| `fonts/` | the font and its license (`OFL.txt`) |
| `materials/settings_sources.json` | the two model outputs quoted in the figures of the settings |
| `code/paper_names.py` | the key names, and the functions that open the gzipped files |
| `code/appendix_sections.json` | the letter of each Web Appendix section |
| `code/model_names.json` | the printed name of each model |
| `materials/` | the texts that the Web Appendix prints |
