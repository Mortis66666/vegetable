from ollama import AsyncClient

async def get_response(prompt):
    message = {'role': 'user', 'content': prompt}
    return await AsyncClient().chat(model='deepseek-r1:7b', messages=[message], stream=True)

async def translate(text, source_language, target_language):
    response =  await AsyncClient().chat(model='deepseek-r1:7b', messages=[
        {
            'role': 'system',
            'content': f'You are a professional translator, you are given a sentence in {source_language} and you must translate it to {target_language}. Do not provide additional information, just the translation. You are also not allowed to think.',
        },
        {
            'role': 'user',
            'content': text,
        }
    ])

    return response['messages']['content']


