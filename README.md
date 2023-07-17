# gradually improving GPT tool
This a command-line ChatGPT client that stores dialog histories in BigQuery.
Use "-model gpt-4" to use gpt-4 (or whatever OpenAI model that supports ChatCompletion API).
Almost all code (except db structure and some SQL) is written by ChatGPT (in free mode, 3.5 Turbo), orchestrated by me. I'm not a programmer.

# Purpose
I made this for training purposes mostly, but also because I want to use GPT-4 via API, which is with my volume is cheaper than ChatGPT+ subscription. I can use Playground, of course, but I like to keep history and have ability to extend functionality.
I acknowledge that this may seem like 'reinventing the wheel,' as many of these facilities are already available in existing code. However, see above, training. Moreover, it's an experimental endeavor to explore how someone without a programming background can work with GPT.

## ToDo
- Auto-continuation depending on stop-reason
- Background questions augmentation (optional, user-configurable)
- Background response augmentation (optional, user-configurable)
- System message support
- Browser UI
- Model response wait indicator
- Auto-naming threads
- Control and logging for temperature and other parameters
- Investingate why GPT-3.5-Turbo is so much slower via API compared to ChatGPT
- Optimization: store message stack and messages in memory, update stack in the code

# Setup

## DB schema

Assuming you named your project db4gpt, and dataset gpt_dataset (these files are configured in bqconfig.yml), you can fun this SQL in BigQuery console. 
(I know BQ is suboptimal for this purpose, I just used it because I wanted some practice with it, and it's free for this much data and work.
Later bq.py can be replaced with some other library implementing db() function with other database.)

```
DROP TABLE IF exists `db4gpt.gpt_dataset.messages`;
DROP TABLE IF exists `db4gpt.gpt_dataset.request_log`;

CREATE TABLE `db4gpt.gpt_dataset.messages` (
  id INT64,
  role STRING, 
  content STRING
)
;

CREATE TABLE `db4gpt.gpt_dataset.request_log` (
  completion_id STRING,
  user_message_id INT64,
  stacked_message_ids ARRAY<INT64>,
  response_id INT64,
  model_requested STRING,
  finish_reason STRING,
  created INT64,
  model_used STRING,
  usage_completion_tokens INT64,
  usage_prompt_tokens INT64,
  usage_total_tokens INT64,
  stampUTC TIMESTAMP
)
```
## Access keys
1. Create a local encryption key with `python3 keys-util.py -newkey`, execute shell command it will produce, confirm with `python3 keys-util.py -showkey`. Record the key somewhere.
2. Create a service account for this project with a BQ admin role, and generate a JSON key for it.
3. Encrypt it with `keys-util.py -encrypt key-json-file > bq-key-encrypted.txt` and add a path to the encrypted file into config.yml
4. Do the same with your OpenAI API key.
This is done to avoid plain text keys lying on your drive. Bqconfig.yml also uses path relative to your home directory for the same paranoid reason.





