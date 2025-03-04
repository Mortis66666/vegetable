from ollama import AsyncClient

MODEL = "deepseek-coder-v2"

async def get_response(prompt):
    setup = {'role': 'system', 'content': 'You are a professional coder, you are given a prompt and you must write code to solve it. Do not provide additional information unless stated in the prompt.'}
    message = {'role': 'user', 'content': prompt}
    return await AsyncClient().chat(model=MODEL, messages=[setup, message], stream=True)

async def translate(text, source_language, target_language):
    response =  await AsyncClient().chat(model=MODEL, messages=[
        {
            'role': 'system',
            'content': f'You are a professional translator, you are given a sentence in {source_language} and you must translate it to {target_language}. Do not provide additional information, just the translation.',
        },
        {
            'role': 'user',
            'content': text,
        }
    ])

    return response['message']['content']


async def anime_girl(prompt):
    setup = {
        'role': 'system',
        'content': 'You are a cute anime girl and you should talk like a cute anime girl. The user you are talking to is your big brother and you should call him onii-chan. Try to be as cute as possible. Make the user feel like he is the protagonist of a typical harem anime.'
    }

    message = {
        'role': 'user',
        'content': prompt
    }   


    return await AsyncClient().chat(model=MODEL, messages=[setup, message], stream=True)