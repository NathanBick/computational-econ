import torch
a = torch.zeros(300000000, dtype = torch.int8, device = 'cuda')
del a
torch.cuda.empty_cache()