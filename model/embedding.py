# the first part is building input embedding
import torch
import torch.nn as nn 
import math

class InputEmbedding(nn.Module):

    def __init__(self, d_model: int , vocab_size: int):
        super().__init__()
        self.d_model = d_model
        self.vocab_size = vocab_size 
        self.embedding = nn.Embedding(vocab_size, d_model)

    def forward(self, x):
            return self.embedding(x) * math.sqrt(self.d_model)
    

class PositionalEncoding(nn.Module):
     def __init__(self, d_models: int, seq_len: int, dropout:float)->None:
          super().__init__()
          self.d_models = d_models    
          self.seq_len = seq_len
          self.dropout = nn.Dropout(dropout)

          # create a matrix of a shape(seq_len, d_models)
          pe = torch.zeros(seq_len, d_models)

          #create a vector of shape (seq_len)
          position = torch.arange(0, seq_len, dtype=torch.float).unsqueeze(1)

          div_term = torch.exp(torch.arange(0, d_models, 2).float()* (-math.log(10000.0) / d_models))

          # even dimensions -> sin
          pe[:, 0::2] = torch.sin(position * div_term)

            # odd dimensions -> cos
          pe[:, 1::2] = torch.cos(position * div_term)  

          # unsqueeze to add batch dimension
          pe = pe.unsqueeze(0)

          self.register_buffer('pe', pe)

     def forward(self, x):
         # x shape: (batch, seq_len, d_model)
        # pe add karo — position info daal do
        x = x + self.pe[:, :x.shape[1], :]
        return self.dropout(x)