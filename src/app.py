from flask import Flask, request, jsonify

from helper.openai_agent import UserChat, clean_params, clean_params_with_params

app = Flask(__name__)


@app.route('/')
def home():
    return 'So far everything is running well...'


@app.route('/dialogflow/cx/receiveMessage', methods=['POST'])
def cxReceiveMessage():
    try:
        data = request.get_json(force=True)

        query_text = data['text']

        result = UserChat('temp').get_prompt(query_text)

        if isinstance(result['response'], str):
            res_param = {}
        else:
            res_param = {key: val for key, val in result['response'].items() if not key == 'Customer respond'}

        if res_param:
            res_param = clean_params(res_param)

        if result['status'] == 1:
            return jsonify(
                {
                    'fulfillmentResponse': {
                        'messages': [
                            {
                                'text': {
                                    'text': [result['response']['Customer respond']],
                                    'redactedText': [result['response']['Customer respond']]
                                },
                                'responseType': 'HANDLER_PROMPT',
                                'source': 'VIRTUAL_AGENT'
                            }
                        ]
                    },
                    'sessionInfo': {
                        "parameters": res_param
                    },

                }
            )
        else:
            return jsonify(
                {
                    'fulfillmentResponse': {
                        'messages': [
                            {
                                'text': {
                                    'text': [result['response']],
                                    'redactedText': [result['response']]
                                },
                                'responseType': 'HANDLER_PROMPT',
                                'source': 'VIRTUAL_AGENT'
                            }
                        ]
                    }
                }
            )

    except:
        pass
    return jsonify(
        {
            'fulfillment_response': {
                'messages': [
                    {
                        'text': {
                            'text': ['Something went wrong.'],
                            'redactedText': ['Something went wrong.']
                        },
                        'responseType': 'HANDLER_PROMPT',
                        'source': 'VIRTUAL_AGENT'
                    }
                ]
            }
        }
    )
