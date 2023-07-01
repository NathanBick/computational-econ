import torch
import transformers
import os
from transformers import AutoTokenizer
#import gc

# check if the model is available locally first
name = 'mpt-1b-redpajama-200b-dolly'

if not os.path.exists(name):
    print(f'Downloading {name} from the hub')
    model = transformers.AutoModelForCausalLM.from_pretrained(
        f'mosaicml/{name}',
        trust_remote_code=True, 
        torch_dtype=torch.float16
        )
    # save the model to disk locally
    model.save_pretrained(name)


config = transformers.AutoConfig.from_pretrained(name, trust_remote_code=True)
config.init_device = 'cuda:0' # For fast initialization directly on GPU! 
# load the model from disk to cuda
# convert the model to fp16
model = transformers.AutoModelForCausalLM.from_pretrained(
    name,
    config=config,
    trust_remote_code=True,
    torch_dtype=torch.float16
    ).half()

model.to(device='cuda:0', dtype=torch.bfloat16)

# use the model
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")

question = "What do you think about AI rights?"

inputs = tokenizer([question], return_tensors="pt")
inputs=inputs.to(device='cuda:0')

# generate text using the model on cuda
outputs = model.generate(
    **inputs, 
    max_length=250, 
    do_sample=True, 
    top_p=0.95, 
    top_k=60)

# convert the output to text
text = tokenizer.decode(outputs[0], skip_special_tokens=True)
print(text)
