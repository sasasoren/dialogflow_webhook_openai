from flask import Flask, request, jsonify
from helper.openai_agent import UserChat

app = Flask(__name__)

@app.route('/')
def home():
    return 'So far everything is running well...'

@app.route('/dialogflow/cx/receiveMessage', methods=['POST'])
def cxReceiveMessage():
    try:
        data = request.get_json(force=True)
        query_text = data.get('text', '')

        user_chat = UserChat('temp')
        result = user_chat.get_prompt(query_text)
        response = result['response']

        if isinstance(response, dict):
            res_param = user_chat.clean_params({key: val for key, val in response.items() if key != 'Customer respond'})
            print(f"This is the response: {response.get('Customer respond', 'Sure thing, let me look up the best possible match')}")
            messages = [{
                'text': {
                    'text': [response.get('Customer respond', 'Sure thing, let me look up the best possible match')],
                    'redactedText': [response.get('Customer respond', 'Sure thing, let me look up the best possible match')]
                },
                'responseType': 'HANDLER_PROMPT',
                'source': 'VIRTUAL_AGENT'
            }]
        else:
            res_param = {}
            messages = [{
                'text': {
                    'text': [response],
                    'redactedText': [response]
                },
                'responseType': 'HANDLER_PROMPT',
                'source': 'VIRTUAL_AGENT'
            }]

        fulfillment_response = {
            'fulfillmentResponse': {
                'messages': messages
            }
        }

        if res_param:
            fulfillment_response['sessionInfo'] = {'parameters': res_param}

        return jsonify(fulfillment_response)

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return jsonify({
            'fulfillment_response': {
                'messages': [{
                    'text': {
                        'text': ['Something went wrong.'],
                        'redactedText': ['Something went wrong.']
                    },
                    'responseType': 'HANDLER_PROMPT',
                    'source': 'VIRTUAL_AGENT'
                }]
            }
        })


if __name__ == '__main__':
    app.run()
