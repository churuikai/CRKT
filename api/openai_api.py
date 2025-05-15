import openai

def request(text:str, api_key, base_url, model, prompt:str, Structured=False, stream=True):
    assert api_key, "API Key is required."
    assert base_url, "API URL is required."
    assert model, "Model is required."
    assert prompt, "Prompt is required."
    print(f"request")
    client = openai.OpenAI(api_key=api_key, base_url=base_url)

    completion_stream = client.chat.completions.create(
        model=model,
        # messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
        messages=[{"role": "user", "content": prompt.format(selected_text=text)}],
        stream=stream,
    )
    if stream:
        return completion_stream      
    return completion_stream.choices[0].message.content

    

    

    


