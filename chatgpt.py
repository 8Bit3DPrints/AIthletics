#chatgpt.py

import requests
import logging

class ChatGPT:
    def __init__(self, api_key):
        self.api_key = api_key

    def get_response(self, prompt):
        try:
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': 'text-davinci-003',
                    'messages': [{'role': 'system', 'content': 'Y'}, {'role': 'user', 'content': prompt}]
                }
            )
            response.raise_for_status()
            data = response.json()
            choices = data.get('choices', [])
            if choices and 'message' in choices[0]:
                return choices[0]['message']['content'].strip()
            else:
                logging.error('No message content in response from OpenAI API: %s', data)
                return "Failed to generate a fitness plan."
        except requests.HTTPError as http_err:
            logging.error('HTTP error occurred: %s', http_err)
            return "Failed to generate a fitness plan. HTTP error occurred."
        except requests.RequestException as err:
            logging.error('Request exception occurred: %s', err)
            return "Failed to generate a fitness plan. Request exception occurred."
        except Exception as err:
            logging.error('Error occurred: %s', err)
            return "Failed to generate a fitness plan. An error occurred."
