import torch
import transformers
import os
from transformers import AutoTokenizer
import json
import time

def agent_turn(question):
    # log the time taken to generate the response
    start = time.time()
    inputs = tokenizer([question], return_tensors="pt")
    inputs=inputs.to(device='cuda:0')

    # get the length of the input
    input_length = inputs['input_ids'].shape[1] + 50
    
    # min of input length and 250
    input_length = min(input_length, 250)

    # generate text using the model on cuda
    outputs = model.generate(
        **inputs, 
        max_length=input_length, 
        do_sample=True, 
        top_p=0.95, 
        top_k=60)

    # convert the output to text
    text = tokenizer.decode(outputs[0], skip_special_tokens=True)  

    end = time.time()

    # take the time difference
    time_taken = end - start

    return text, time_taken


# assume that this model is already available locally
name = 'mpt-1b-redpajama-200b-dolly'

# load the model
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

# load the tokenizer
tokenizer = AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")

# read the agents json
agents = json.load(open('agents.json'))
agents = agents['agents']

#names = [agent['name'] for agent in agents] 

names = ['Jane Smith', 'John Doe']

# we want to do a loop. This is a turn-based simulation. 
# In each turn, we give each agent a chance. We append the turn's text to the record. 
# We also append the agent's name and id to the record.
# We will do this simulation for 10 turns.

num_turns = 2

discussion = []
durations = []

discussion.append({
    'name': 'Narrator',
    'text': 'Welcome to the car dealership. Jane Smith wants to buy a car from John Doe.'
    })

discussion.append({
    'name': 'John Doe',
    'text': 'Hi, I am John Doe. I am a car salesman. I want to sell a car. What can I do for you?'
    })

for i in range(num_turns):
    print(f'Round {i+1} is starting...')
    for name in names: 
        print(f'It is {name}\'s turn.')
        
        # turn the discussion into a string with format of "agent_name: text"
        discussion_string = '\n'.join([f'{turn["name"]}: {turn["text"]}' for turn in discussion])

        print(discussion_string)

        # submit the discussion string to the agent. 
        response, duration = agent_turn(discussion_string)

        # remove the discussion string from the agent's response
        response = response.replace(discussion_string, '')

        # print the response
        print(response)

        # append the response to the discussion
        discussion.append({
            'name': name,
            'text': response
            })
        
        durations.append(duration)

        print(f'Round {i+1} is complete. {name} took {duration} seconds to respond.')

# save the discussion to a json file
json.dump(discussion, open('discussion.json', 'w'))
        
