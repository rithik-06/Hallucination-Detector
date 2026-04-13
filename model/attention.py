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


        # Step 3: softmax — weights bano
        # (batch, heads, seq, seq)
        weights = torch.softmax(scores, dim=-1)

        if dropout is not None:
            weights = dropout(weights)

        # Step 4: values se multiply karo
        # (batch, heads, seq, seq) × (batch, heads, seq, 64)
        # = (batch, heads, seq, 64)
        output = weights @ value

        return output, weights

     def forward(self, q, k, v, mask):
        # Step 1: Q K V banao — linear layers se
        # (batch, seq, 512) → (batch, seq, 512)
        query = self.w_q(q)
        key   = self.w_k(k)
        value = self.w_v(v)

        # Step 2: 8 heads mein split karo
        # (batch, seq, 512) → (batch, seq, 8, 64) → (batch, 8, seq, 64)
        batch = query.shape[0]
        seq   = query.shape[1]

        query = query.view(batch, seq, self.n_heads, self.d_k).transpose(1, 2)
        key   = key.view(batch, seq, self.n_heads, self.d_k).transpose(1, 2)
        value = value.view(batch, seq, self.n_heads, self.d_k).transpose(1, 2)

        # Step 3: har head mein attention compute karo
        # (batch, 8, seq, 64)
        x, self.weights = MultiHeadAttention.attention(
            query, key, value, mask, self.dropout
        )

        # Step 4: heads ko wapas jodo
        # (batch, 8, seq, 64) → (batch, seq, 8, 64) → (batch, seq, 512)
        x = x.transpose(1, 2).contiguous().view(batch, seq, self.d_model)

        # Step 5: output projection
        # (batch, seq, 512) → (batch, seq, 512)
        return self.w_o(x)        
    


         
        

