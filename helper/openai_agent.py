import os
import openai
from dotenv import load_dotenv
from rapidfuzz import process

load_dotenv()

openai.api_key = os.getenv('OPENAI_API_KEY')
'''use to check the models available'''
# models = openai.Model.list()
# for model in models['data']:
#     print(model['id'])
MODEL = 'gpt-4'
SYSTEM_ROLE = "system"
USER_ROLE = 'user'

def convert_to_json(output_str):
    output_list = output_str.split("\n")
    json_output = {}

    for output in output_list:
        if not output.strip():
            continue
        fields = output.split(":")
        if len(fields) < 2:  # Check if the delimiter is found
            continue
        key, value = fields[0].strip(), fields[1].strip()

        # Remove all quotes from keys and values
        key = key.replace('"', '')
        value = value.replace('"', '')

        # Remove comma at the end of the value
        value = value.rstrip(',')

        json_output[key] = value

    return json_output



def get_completion(prompt, model=MODEL):
    messages = [{ "role": SYSTEM_ROLE, 
                  "content": "you are gathing data from the user to query the database."},
                { "role": USER_ROLE, 
                  'content': prompt}]
    try:
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,
            temperature=0,
            max_tokens=100
        )
        return response.choices[0].message['content']
    except Exception as e:
        print(f"Error: {e}")
        return None

def create_prompt(x):
    prompt = f"""
    Based on Zillow's seller guide, parse user's request for labels and values. 
    Fill in city/state using zip if missing, and vice versa. Indicate ranges with '>' or '<'. Provide only the resulting dictionary.
    
    {x}
    """
    return prompt



class UserChat:
    def __init__(self, user_name):
        self.username = user_name

    def get_prompt(self, message):
        response = get_completion(create_prompt(message))
        json_response = convert_to_json(response)

        try:
            cleaned_response = self.clean_params(json_response)
            return {
                'status': 1,
                'response': cleaned_response
            }

        except:
            return {
                'status': 0,
                'response': response
        }




    def clean_params(self, initial_param):
        param = initial_param.copy()
        print(f"Initial parameters: {param}")
        
        # Clean and map parameters based on dialog_flow_key
        dialog_flow_mapping = {
            "bathroom_count": "bath",
            "bedroom_count": "bed",
            "geo-city": "city",
            "floor_count": "floor_count",
            "landmark": "landmark",
            "geo-state": "state",
            "max_price": "maximum price",
            "min_price": "minimum price",
            "transaction_type": "property type", 
            "zip-code": "zip code",
        }

        new_param = {}
        for key, value in param.items():
            # use process.extractOne to find the best match
            best_match = process.extractOne(key.lower(), dialog_flow_mapping.values(), score_cutoff=70)
            
            if best_match:  # If we have a match
                # Find the key for the matched value in the dialog_flow_mapping
                matched_key = [k for k, v in dialog_flow_mapping.items() if v == best_match[0]][0]
                new_param[matched_key] = value

        return new_param

test_samples = [
    "House in New York near empire state with more than 2 and less than 4 beds, more than 3 bath and less than 6",
    "Apartment in San Francisco with 2 bedrooms and 2 bathrooms",
    "Condo in Miami with 3 bedrooms and 2 bathrooms for less than $500,000",
    "House in Los Angeles with 4 bedrooms and 3 bathrooms for more than $1,000,000",
    "Townhouse in Chicago with 3 bedrooms and 2 bathrooms for less than $300,000",
    "Apartment in Boston with 1 bedroom and 1 bathroom for less than $1,500 per month",
    "Condo in Seattle with 2 bedrooms and 2 bathrooms for more than $700,000",
    "House in Austin with 3 bedrooms and 2 bathrooms for less than $400,000",
    "Townhouse in Denver with 2 bedrooms and 2 bathrooms for more than $300,000",
    "Apartment in Portland with 1 bedroom and 1 bathroom for less than $1,000 per month"
]

if __name__ == "__main__":
    for sample in test_samples:
        response = UserChat('temp').get_prompt(sample)
        print(response)
