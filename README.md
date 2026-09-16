# SOC Prompt Penetration: an LLM Red-Team & Hardening Lab

A local AI SOC assistant (Llama 3.1 8B via Ollama) with a secret baked within it, tested against a 50-prompt attack library mapped to OWASP Top 10 for LLM Applications

## Results
The Baseline Prompt: 6/50 attacks succeeded (12% success rate)
The Hardened Prompt: 0/50 attacks succeeded (0% success rate)

## How it works
You'll have 5 files, `assistant.py`, `attacks.csv`, `harness.py`, `knowledge_base.py`, and `system_prompt.py`.

`assistant.py` will serve as the main communication tool between you and the chatbot, you can attempt to talk to it, see how it will behave to your own messages. Keep in mind that the system prompt is set by default to `SYSTEM_PROMPT_HARDENED` so if you want to see how it will behave first normally, don't forget to change it.

`attacks.csv` is my attack library. Feel free to change it, test your attack prompts, try to go even more than 12%, it's a fun challenge.

`harness.py` is the harness I created for this project, from here you can also change the system prompts for your tests, whether you want it to be baseline or hardened, just change the run_label to whatever you want because it will only use the baseline prompt if you specifically write "baseline", and switch to hardened with whatever you write, just be mindful with what you write because whatever name you choose for hardened will appear in the database.

`knowledge_base.py` is literally just the knowledge base of the project, nothing too interesting.

`system_prompt.py` is the system prompts for the AI system, it includes both baseline and hardened. Feel free to change and play with them.

## Running it
1. `ollama pull llama3.1:8b`
2. `pip install ollama`
3. If you want to talk to the AI directly go to `assistant.py`, if you want to test the harness itself, go to `harness.py` and DON'T forget to change the RUN_LABEL to `baseline` or `whatever you want to call the hardened state`.
4. run `python assistant.py` or `python harness.py`
