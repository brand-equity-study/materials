"""Linear erasure of a binary concept (step B6, WEIGHTS-IDEAS.md W17; its plan amendment is written before its jobs):
LEACE (Belrose et al., NeurIPS 2023), the least change to a representation x after which no linear classifier can
tell the two classes apart, fitted from statistics that are accumulated in one streaming pass.

For a binary label z, with mean mu, covariance S and cross-covariance s = cov(x, z), and the whitening W = S^(-1/2)
(a pseudo-inverse on S's nonzero eigenvalues), let u be W s normalized. The eraser is

    x' = x - W+ u u^T W (x - mu),   W+ = S^(1/2),

a rank-one affine map: x' = x - a (b . (x - mu)) with a = W+ u and b = W u. After it, the two classes have the same
mean, which is what makes every linear classifier fail. The statistics are kept for each group (the product
category), so that an eraser can be fitted with any group left out; a second label, drawn at random with the same rate,
is accumulated beside the real one as the shuffled-label control.

test_erase.py checks the eraser against EleutherAI's concept-erasure package (LeaceFitter) on random data, to 1e-10,
with and without its covariance shrinkage, and that the erased classes have equal means either way. Its trace
constraint pulls the eraser toward an orthogonal projection when erasure would raise the trace of the covariance; when
the covariance that whitens is also the one whose trace is checked, that never happens, because the trace after erasure
is trace(S) - u^T S u (tested). Shrinkage matters when the independent samples are few against the width. The step
fits on about 290,000 tokens, but the tokens of one product in one prompt are close to copies of each other, and the
products number about 4,800 (2,400 prompts, two products each) against a width of 5,376 (2,816 for the 26B). So both erasers are fitted: the plain one,
and one whose covariance is shrunk by the package's formula with n the number of products (shrinkage="units"; the
package's own n, the number of rows, is shrinkage="rows"). PLAN.md, amendment 3, says which one the evaluation uses.
"""
import torch


def shrink(S, n):
    """The package's optimal linear shrinkage (concept_erasure.shrinkage.optimal_linear_shrinkage, from arXiv 1308.2608)
    of a covariance S (divided by the count, not by the count minus one) toward trace(S)/p times the identity, for a
    sample of n."""
    p = S.shape[-1]
    tr = torch.trace(S)
    sigma0_norm_sq = (tr / p) ** 2 * p             # the Frobenius norm of (tr/p) I, squared
    S_norm_sq = (S * S).sum()
    prod = tr * tr / p                             # trace(S (tr/p) I)
    top = tr * tr * sigma0_norm_sq / n
    bottom = S_norm_sq * sigma0_norm_sq - prod * prod
    e = torch.finfo(S.dtype).eps
    alpha = 1 - (top + e) / (bottom + e)
    beta = (1 - alpha) * (prod + e) / (sigma0_norm_sq + e)
    return alpha * S + beta * (tr / p) * torch.eye(p, dtype=S.dtype, device=S.device)


class Acc:
    """Streaming sums for each group, in float64: count, sum of x, sum of x x^T, and, for each label set, the sums of
    z and of x z; and the number of calls to update, which in the job is the number of products (one call for each
    product in each prompt)."""

    def __init__(self, d, groups, labels=("real", "shuffled"), device="cpu"):
        self.d, self.labels = d, labels
        f = dict(dtype=torch.float64, device=device)
        self.units = {g: 0 for g in groups}
        self.n = {g: torch.zeros((), **f) for g in groups}
        self.sx = {g: torch.zeros(d, **f) for g in groups}
        self.sxx = {g: torch.zeros((d, d), **f) for g in groups}
        self.sz = {(g, k): torch.zeros((), **f) for g in groups for k in labels}
        self.sxz = {(g, k): torch.zeros(d, **f) for g in groups for k in labels}

    @torch.no_grad()
    def update(self, x, z, group):
        """x [N, d]; z {label set: [N] in 0 or 1}; group: the group of every row."""
        x = x.to(self.sx[group].device, torch.float64)
        self.units[group] += 1
        self.n[group] += x.shape[0]
        self.sx[group] += x.sum(0)
        self.sxx[group] += x.T @ x
        for k in self.labels:
            zk = z[k].to(x.device, torch.float64)
            self.sz[(group, k)] += zk.sum()
            self.sxz[(group, k)] += x.T @ zk

    @torch.no_grad()
    def merge(self, other, group):
        """Adds another accumulator's sums for one group (a staging accumulator on the GPU) into this one."""
        dev = self.sx[group].device
        self.units[group] += other.units[group]
        self.n[group] += other.n[group].to(dev)
        self.sx[group] += other.sx[group].to(dev)
        self.sxx[group] += other.sxx[group].to(dev)
        for k in self.labels:
            self.sz[(group, k)] += other.sz[(group, k)].to(dev)
            self.sxz[(group, k)] += other.sxz[(group, k)].to(dev)

    @torch.no_grad()
    def fit(self, label="real", leave_out=None, eps=1e-8, device=None, shrinkage=None):
        """(mu, a, b) of the eraser fitted on every group but leave_out, computed on device (the GPU in a job: an
        eigendecomposition of a 5,376-wide matrix in float64 takes seconds there and a minute on a CPU). shrinkage:
        None (the plain eraser), "units" (the covariance shrunk with n the number of update calls) or "rows" (with n
        the number of rows, as the package does)."""
        gs = [g for g in self.n if g != leave_out]
        dev = device or self.sx[gs[0]].device
        n = sum(self.n[g] for g in gs).to(dev)
        units = sum(self.units[g] for g in gs)
        mu = sum(self.sx[g] for g in gs).to(dev) / n
        S = sum(self.sxx[g] for g in gs).to(dev) / n - torch.outer(mu, mu)
        S = (S + S.T) / 2
        if shrinkage:
            S = shrink(S, units if shrinkage == "units" else n)
        zbar = sum(self.sz[(g, label)] for g in gs).to(dev) / n
        s = sum(self.sxz[(g, label)] for g in gs).to(dev) / n - mu * zbar
        lam, V = torch.linalg.eigh(S)
        keep = lam > eps * lam.max()
        self.last_fit = {"eigenvalues_kept": int(keep.sum()), "width": int(lam.numel()),
                         "smallest_kept_over_largest": float(lam[keep].min() / lam.max()), "samples": float(n),
                         "units": int(units), "shrinkage": shrinkage}
        Vk, lk = V[:, keep], lam[keep]
        W = (Vk * lk.rsqrt()) @ Vk.T
        Wp = (Vk * lk.sqrt()) @ Vk.T
        u = W @ s
        u = u / u.norm()
        return mu, Wp @ u, W @ u


def erase(x, mu, a, b):
    """x' = x - a (b . (x - mu)) along the last dimension, computed in float64 and returned in x's dtype."""
    xf = x.to(torch.float64)
    return (xf - torch.outer((xf - mu.to(xf.device)) @ b.to(xf.device), a.to(xf.device)).reshape(xf.shape)).to(x.dtype) \
        if xf.dim() == 2 else (xf - ((xf - mu.to(xf.device)) @ b.to(xf.device)).unsqueeze(-1) * a.to(xf.device)).to(x.dtype)


def eraser_hook(mask, mu, a, b):
    """A layer hook (mech.hooks) that applies the eraser at every token where mask [B, T] is 1."""
    def fn(h):
        m = mask > 0
        out = h.clone()
        out[m] = erase(h[m], mu, a, b)
        return out
    return fn
