import traceback
import yaml
import os
import json
from google.cloud import bigquery
from google.api_core.exceptions import GoogleAPIError
from google.auth import exceptions
from google.oauth2 import service_account
from datetime import datetime

from keys_lib import decrypt_data

def load_bq_config():
    with open('bqconfig.yml') as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)
        enc_key_file = os.path.expanduser(config.get('enc_json_key_file'))
        with open(enc_key_file, 'rb') as encrypted_file:
            encrypted_data = encrypted_file.read()
        decrypted_data = decrypt_data(encrypted_data)
        decrypted_key = decrypted_data.decode("utf-8")
        credentials = service_account.Credentials.from_service_account_info(json.loads(decrypted_key))
        return config.get('project_id'), config.get('dataset'), credentials

def db(action, *args, **kwargs):
    try:
        project_id, dataset, credentials = load_bq_config()
        client = bigquery.Client(project=project_id, credentials=credentials)

        if action == "get_new_stacked_ids_array":
            response_id = kwargs["previous_response_id"]
            query = f"""
            SELECT ARRAY_CONCAT(stacked_message_ids, ARRAY<INT64>[user_message_id],ARRAY<INT64>[response_id])
            FROM `{project_id}.{dataset}.request_log`
            WHERE response_id = @response_id
            """

            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("response_id", "INT64", response_id)
                ]
            )
            result = list(client.query(query, job_config=job_config))
            re = result[0][0]

        elif action == "get_threads":
            query = f"""SELECT response_id FROM `{project_id}.{dataset}.request_log` WHERE response_id NOT IN (SELECT DISTINCT id FROM `{project_id}.{dataset}.request_log` AS db
CROSS JOIN UNNEST(db.stacked_message_ids) as id) ORDER by response_id DESC LIMIT 1000"""
            result = client.query(query)
            threads = [row['response_id'] for row in result]
            re = threads
        
        elif action == "record_message":
            role = kwargs["role"]
            message = kwargs["message"]
            query = f"""
            SELECT IFNULL(MAX(id),0) AS max_id
            FROM `{project_id}.{dataset}.messages`
            """
            result = list(client.query(query))
            max_id = result[0].max_id
            new_id = max_id + 1

            query = f"""
            INSERT INTO `{project_id}.{dataset}.messages` (id, role, content)
            VALUES (@new_id, @role, @message)
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("new_id", "INT64", new_id),
                    bigquery.ScalarQueryParameter("role", "STRING", role),
                    bigquery.ScalarQueryParameter("message", "STRING", message),
                ]
            )
            result = list(client.query(query, job_config=job_config))
            re = new_id

        elif action == "get_stacked_message_texts":
            if len(args) > 0:
                stacked_message_ids = args[0]
            else: return []  # Return an empty list if the stacked_message_ids are empty

            query = f"""
            SELECT role, content
            FROM `{project_id}.{dataset}.messages`
            WHERE id IN UNNEST(@stacked_message_ids)
            ORDER BY id ASC
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                bigquery.ArrayQueryParameter("stacked_message_ids", "INT64", stacked_message_ids)
                ]
            )
            result = client.query(query, job_config=job_config)
            stacked_messages = [[row["role"], row["content"]] for row in result]

            re = stacked_messages

        elif action == "log_request":
            timestamp = datetime.utcnow()

            query = f"""
                INSERT INTO `{project_id}.{dataset}.request_log` (
                completion_id,
                user_message_id,
                stacked_message_ids,
                response_id,
                model_requested,
                finish_reason,
                created,
                model_used,
                usage_completion_tokens,
                usage_prompt_tokens,
                usage_total_tokens,
                stampUTC
                )
                VALUES (
                @completion_id,
                @user_message_id,
                @stacked_message_ids,
                @response_id,
                @model_requested,
                @finish_reason,
                @created,
                @model_used,
                @usage_completion_tokens,
                @usage_prompt_tokens,
                @usage_total_tokens,
                @timestamp
                )
            """
            job_config = bigquery.QueryJobConfig(
                query_parameters=[
                    bigquery.ScalarQueryParameter("completion_id", "STRING", kwargs["completion_id"]),
                    bigquery.ScalarQueryParameter("user_message_id", "INT64", kwargs["user_message_id"]),
                    bigquery.ArrayQueryParameter("stacked_message_ids", "INT64", kwargs["stacked_message_ids"]),
                    bigquery.ScalarQueryParameter("response_id", "INT64", kwargs["response_id"]),
                    bigquery.ScalarQueryParameter("model_requested", "STRING", kwargs["model_requested"]),
                    bigquery.ScalarQueryParameter("finish_reason", "STRING", kwargs["finish_reason"]),
                    bigquery.ScalarQueryParameter("created", "INT64", kwargs["created"]),
                    bigquery.ScalarQueryParameter("model_used", "STRING", kwargs["model_used"]),
                    bigquery.ScalarQueryParameter("usage_completion_tokens", "INT64", kwargs["usage_completion_tokens"]),
                    bigquery.ScalarQueryParameter("usage_prompt_tokens", "INT64", kwargs["usage_prompt_tokens"]),
                    bigquery.ScalarQueryParameter("usage_total_tokens", "INT64", kwargs["usage_total_tokens"]),
                    bigquery.ScalarQueryParameter("timestamp", "TIMESTAMP", timestamp)
                ]
            )
            result = list(client.query(query, job_config=job_config))
            re = result

    except exceptions.GoogleAuthError as auth_error:
        print(f"Authentication failed: {str(auth_error)}")
        traceback.print_exc()  # Print full traceback

    except GoogleAPIError as bq_error:
        print(f"BigQuery error: {str(bq_error)}")
        traceback.print_exc()  # Print full traceback

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        traceback.print_exc()  # Print full traceback

    return re