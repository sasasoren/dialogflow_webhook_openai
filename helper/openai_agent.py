import os
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')


def get_completion(prompt, model='gpt-3.5-turbo'):
    messages = [{"role": "system", "content": "You are a helpful real state agent from DOSS that "
                                              "you are getting information."},
                {"role": 'user', 'content': prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0
    )
    return response.choices[0].message['content']


def create_prompt(x):
    prompt = f"""
    Your task is to extract the following information from text delimited by triple backticks into a JSON format with the
    following keys: Customer respond, City, State, zip code, minimum prince, maximum price, minimum bed, maximum bed,
    minimum bath, maximum bath.

    Please do not respond anything outside of the JSON format.

    0 - customer respond: respond to the text as a helpful real state agent that you are getting information. If the text is not
    related to real state, make an excuse and respond with something as a real state agent.
    1 - City: the city that the customer is looking for a property. If it is not mentioned set it empty
    2 - State: the state that the customer is looking for a property. If it is not mentioned try to find out from the name
    of the city. If the city was not mentioned too, set it empty
    3 - zip code: if zip code of the neighborhood was mentioned return it, otherwise if an area of the city was mentioned try
     to guess the zip code for that neighborhood, otherwise set it empty.
    4 - minimum price: if the minimum price was mention return it in integer, otherwise set it empty.
    5 - maximum price: if the maximum price was mention return it in integer, otherwise set it empty.
    6 - minimum bed: if the minimum number of bed was mention return it in integer, otherwise set it empty.
    7 - maximum bed: if the maximum number of bed was mention return it in integer, otherwise set it empty.
    8 - minimum bath: if the minimum number of bath was mention return it in integer, otherwise set it empty.
    9 - maximum bath: if the maximum number of bath was mention return it in integer, otherwise set it empty.

    '''{x}'''
    """
    return prompt


class UserChat:
    def __init__(self, user_name):
        self.username = user_name

    def get_prompt(self, message):
        response = get_completion(create_prompt(message),
                                  # model='gpt-4'
                                  )
        # print('get prompt response: ', response)
        try:
            return {
                'status': 1,
                'response': eval(response)
            }

        except:
            return {
                'status': 0,
                'response': response
            }


def clean_params(initial_param):
    param = initial_param.copy()
    param['geo-city'] = param['City']
    param['geo-state'] = param['State']
    param['bathroom_count'] = param['minimum bath'] if not param['minimum bath'] == '' else param['maximum bath']
    param['bedroom_count'] = param['minimum bed'] if not param['minimum bed'] == '' else param['maximum bed']

    return param


def clean_params_with_params(initial_param, webhook_params):
    # for param in webhook_params
    pass


if __name__ == "__main__":
    temp_response = UserChat('temp').get_prompt("Apartments in New York near empire state with more than 2 and less"
                                                " than 4 beds, more than 3 bath and less than 6 ")
