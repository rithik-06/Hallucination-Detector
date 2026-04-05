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
        

