import openai

from config import OPENAI_API_TOKEN

openai.api_key = OPENAI_API_TOKEN


def generate_response_from_chat_gpt(text: str) -> str:
    request_text = text
    if request_text[-1] != '?':
        request_text = text + '?'
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=request_text,
        max_tokens=340,
        n=1,
        top_p=1.0,
        stop=None,
        temperature=0.5,
        presence_penalty=0.0,
        frequency_penalty=0.5,
    )
    return response['choices'][0]['text'].strip()
