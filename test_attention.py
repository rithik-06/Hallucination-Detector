import torch
from model.attention import MultiHeadAttention

# model banao
mha = MultiHeadAttention(d_model=512, n_heads=8, dropout=0.1)

# fake input — batch=2, seq=10, d_model=512
x = torch.randn(2, 10, 512)

# forward pass
out = mha(x, x, x, mask=None)

print(f"Input shape:  {x.shape}")    # (2, 10, 512)
print(f"Output shape: {out.shape}")  # (2, 10, 512) — same!