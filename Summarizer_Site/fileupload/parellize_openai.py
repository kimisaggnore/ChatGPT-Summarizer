import openai
import asyncio

openai_api_key_1 = ""
openai_api_key_2 = ""

async def call_openai_api(api_key, index, txt, prompt):
    try:
        openai.api_key = api_key
        print(f"text: {txt}")
        messages = [ {"role": "user", "content": txt}, {"role": "user", "content": f"{prompt}"}]
        response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
        return index, response.choices[0].message.content
    except Exception as e:
        print(f"Error: {e}")
        return index, None

async def main():
    txt = ["Once upon a time", "In a galaxy far, far away"]
    prompts = "Summarize for me"
    api_key_prompt_pairs = [(openai_api_key_1, 0, txt[0], prompts), (openai_api_key_2, 1, txt[1], prompts)]
    tasks = [loop.create_task(call_openai_api(api_key, index, txt, prompt)) for api_key, index, txt, prompt in api_key_prompt_pairs]
    results = await asyncio.gather(*tasks)
    sorted_results = sorted(results, key=lambda x: x[0])  # Sort results based on the original order
    for _, result in sorted_results:
        print(f"Result: {result}")
        print()

loop = asyncio.new_event_loop()
# loop = asyncio.get_event_loop()
loop.run_until_complete(main())