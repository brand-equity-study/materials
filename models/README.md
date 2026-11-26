# The models

In this folder, we describe every model that answered in the studies. We first list the folder's files and then explain
how each model was reached.

## The files

| File | Contents |
|---|---|
| `models.csv` | for every model and set of prompts: the model's identifier, how it was reached, its decoding settings and the dates of its responses |
| `model_characteristics.csv` | for every model: its developer, whether its weights are open, whether it thinks before answering, its size and its release date, with the source of each |
| `open-models.tsv` | each model with open weights: its repository, revision and settings |
| `open_models_plan.md` | the analysis plan for the models with open weights: their settings and the rule that reports a model apart |

## How each model was reached

The Claude models answered through Anthropic's Messages API (and, where a study says so, the Claude command line),
the GPT-6 models through OpenAI's Codex command line, and the models with open weights on a university computing
cluster, where they were served with vLLM. `computing/gpu_jobs.csv` lists every run on the cluster with its GPU type and
hours.
