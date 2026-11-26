"""Brand-blind weights (step B6, WEIGHTS-IDEAS.md W18; the plan amendment that runs it is written before its jobs): a
direction r is removed from the residual stream of a Gemma 4 model by editing the weights, with no training, so that no
layer can write any component along r.

Arditi et al. (2024) replace every matrix W that writes to the residual stream by W - r r^T W. Gemma 4 does not add a
matrix's output to the residual stream directly: each attention output and each MLP output first passes through an
RMSNorm with an elementwise weight (and in the expert model the dense MLP and the experts each pass through their own
norm before the norm of their sum). An RMSNorm divides by a number and multiplies elementwise by its weight g, so its
output y satisfies y . r = (z . (g * r)) / rms(z): y has no component along r exactly when its input z has none along
g * r. So each writing matrix is edited with its own direction, r multiplied elementwise by the weights of every norm
between that matrix and the residual stream, and normalized. The embedding rows are edited with r itself (Gemma
multiplies them by a number). Every layer's output is then orthogonal to r, by induction from the embedding; the
test in test_weights_edit.py checks this on tiny models of both kinds. The edit is not the same as removing r from
the activations, because a norm then divides by the rms of an edited input.

    edit(model, r) -> a list of the edited parameters and the direction used for each
"""
import torch


def norm_scale(norm):
    """The elementwise factor of a Gemma 4 RMSNorm (its weight; ones when it has none)."""
    w = getattr(norm, "weight", None)
    if w is None or not getattr(norm, "with_scale", True):
        return None
    return w.detach().float()


def chain(r, *norms):
    """r multiplied by the elementwise factor of each norm in turn, normalized; computed on the norms' device (job
    12089 failed when r was on the CPU and the model on the GPU, which the CPU tests could not show)."""
    v = r.float().clone()
    for n in norms:
        g = norm_scale(n)
        if g is not None:
            v = v.to(g.device) * g
    return v / v.norm()


def project_out(W, u, dim):
    """W minus u u^T W along its output dimension dim (0 for nn.Linear [out, in], 1 for experts [E, out, in])."""
    u = u.to(W.device, torch.float32)
    if dim == 0:
        Wf = W.data.float()
        W.data.copy_((Wf - torch.outer(u, u @ Wf)).to(W.dtype))
    else:                                        # experts [E, out, in]: one expert at a time
        for e in range(W.shape[0]):
            We = W.data[e].float()
            W.data[e] = (We - torch.outer(u, u @ We)).to(W.dtype)


def text_model(model):
    lm = getattr(getattr(model, "model", model), "language_model", None)
    return lm if lm is not None else getattr(model, "model", model)


@torch.no_grad()
def edit(model, r):
    """Edits the model in place; returns [(parameter name, direction used)] for the record."""
    tm = text_model(model)
    r = r.float() / r.float().norm()
    done = []
    emb = tm.embed_tokens.weight
    rr = r.to(emb.device)
    for i in range(0, emb.shape[0], 16384):     # in chunks: a float32 copy of the 31B's embedding is 5.6 GB
        rows = emb.data[i:i + 16384].float()
        emb.data[i:i + 16384] = (rows - torch.outer(rows @ rr, rr)).to(emb.dtype)
    done.append(("embed_tokens.weight", "r"))
    for i, layer in enumerate(tm.layers):
        if getattr(layer, "hidden_size_per_layer_input", 0):
            raise NotImplementedError("per-layer inputs (Gemma 4 E models) also write to the residual stream")
        project_out(layer.self_attn.o_proj.weight, chain(r, layer.post_attention_layernorm), 0)
        done.append((f"layers.{i}.self_attn.o_proj.weight", "r * post_attention_layernorm"))
        if getattr(layer, "enable_moe_block", False):
            project_out(layer.mlp.down_proj.weight,
                        chain(r, layer.post_feedforward_layernorm_1, layer.post_feedforward_layernorm), 0)
            project_out(layer.experts.down_proj,
                        chain(r, layer.post_feedforward_layernorm_2, layer.post_feedforward_layernorm), 1)
            done += [(f"layers.{i}.mlp.down_proj.weight", "r * post_feedforward_layernorm_1 * post_feedforward_layernorm"),
                     (f"layers.{i}.experts.down_proj", "r * post_feedforward_layernorm_2 * post_feedforward_layernorm")]
        else:
            project_out(layer.mlp.down_proj.weight, chain(r, layer.post_feedforward_layernorm), 0)
            done.append((f"layers.{i}.mlp.down_proj.weight", "r * post_feedforward_layernorm"))
    return done
