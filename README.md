# gradual
This a command-line ChatGPT client that stores dialog histories in BigQuery.
Almost all code (except db structure and some SQL) is written by ChatGPT, orchestrated by me. I'm not a programmer.

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
Create a service account for this project with a BQ admin role, and generate a JSON key for it.
Encrypt it with `keys-util.py -encrypt key-json-file > bq-key-encrypted.txt` and add a path to the encrypted file into bqconfig.yml
This is done to avoid plain text keys lying on your drive.
Note: currently you need to use debugger to see the generated key (TBD), put it into environment variable PY_ENCRYPTION_KEY

Do the same with your OpenAI API key.

