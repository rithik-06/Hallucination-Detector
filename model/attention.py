import torch
import torch.nn as nn   

class MultiHeadAttention(nn.Module):

    def __init__(self, d_model:int , num_heads:int , dropout:float):
        super().__init__()
        self.d_model = d_model
        self.num_heads = num_heads

        # 512 / 8 = 64 — har head itna dekhega
        assert d_model % num_heads ==0 # d_model should be divisible by num_heads
        self.d_k = d_model // num_heads


        # 4 linear layers — W_Q, W_K, W_V, W_O
        self.w_q = nn.Linear(d_model, d_model, bias=False)  # (512 → 512)
        self.w_k = nn.Linear(d_model, d_model, bias=False)  # (512 → 512)
        self.w_v = nn.Linear(d_model, d_model, bias=False)  # (512 → 512)
        self.w_o = nn.Linear(d_model, d_model, bias=False)  # (512 → 512)

        self.dropout = nn.Dropout(dropout)

    @staticmethod
    def attention(query, key, value, mask, dropout):
        d_k = query.shape[-1]  # 64

        # Step 1: Q aur K multiply karo
        # (batch, heads, seq, 64) × (batch, heads, 64, seq)
        # = (batch, heads, seq, seq)
        scores = query @ key.transpose(-2, -1) / math.sqrt(d_k)

        # Step 2: mask lagao (padding tokens ignore karne ke liye)
        if mask is not None:
            scores = scores.masked_fill(mask == 0, -1e9)
    


         
        

