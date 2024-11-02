from enum import Enum
from typing import List, Optional, Literal
from pydantic import BaseModel
import openai

# 定义Markdown元素类型的枚举
class MarkdownElementType(str, Enum):
    paragraph = "paragraph"
    heading = "heading"
    list = "list"
    table = "table"
    block_formula_latex = "block_formula_latex"
    block_quote = "block_quote"
    block_code = "block_code"

class TextElementType(str, Enum):
    text = "text"
    inline_code = "inline_code"
    inline_formula_latex = "inline_formula_latex"

class TextElement(BaseModel):
    type: TextElementType
    content: str

class Paragraph(BaseModel):
    elements: List[TextElement]

class Heading(BaseModel):
    level: Literal['##', '###', '####', '#####']
    content: str
    
# Markdown元素模型
class MarkdownElement(BaseModel):
    type: MarkdownElementType
    content: Optional[str]
    paragraph: Optional[Paragraph]
    heading: Optional[Heading]

# 响应模型
class Response(BaseModel):
    elements: List[MarkdownElement]
    

def parse_response(response: Response):
    print(f"parse_response")
    print(response)
    print('----------------')
    markdown = ""
    for element in response.elements:
        try:
            markdown += parse_element(element)
        except Exception as e:
            markdown += ""
    return markdown.strip()

def parse_element(element: MarkdownElement):
    try:
        if element.type == MarkdownElementType.paragraph:
            return parse_paragraph(element)
        elif element.type == MarkdownElementType.heading:
            return parse_heading(element)
        elif element.type == MarkdownElementType.list:
            return parse_list(element)
        elif element.type == MarkdownElementType.table:
            return parse_table(element)
        elif element.type == MarkdownElementType.block_formula_latex:
            return parse_block_formula_latex(element)
        elif element.type == MarkdownElementType.block_quote:
            return parse_block_quote(element)
        elif element.type == MarkdownElementType.block_code:
            return parse_block_code(element)
        else:
            return ""
    except Exception as e:
        print(e)
        return ""

def parse_paragraph(element: MarkdownElement):
    res = ""
    for text_element in element.paragraph.elements:
        try:
            if text_element.type == TextElementType.text:
                res += text_element.content
            elif text_element.type == TextElementType.inline_code:
                res += f"`{text_element.content.strip('`')}`"
            elif text_element.type == TextElementType.inline_formula_latex:
                res += f"$ {text_element.content.strip('$').strip()} $"
        except Exception as e:
            res += ""
            print(e)
    return res.strip()+"\n\n"

def parse_heading(element: MarkdownElement):
    return f"{element.heading.level} {element.heading.content.strip('#').strip()}\n\n"
    
def parse_list(element: MarkdownElement):
    return element.content.strip()+"\n\n"

def parse_table(element: MarkdownElement):
    return element.content.strip()+"\n\n"

def parse_block_formula_latex(element: MarkdownElement):
    return f"$$ {element.content.strip('$').strip()} $$\n\n"

def parse_block_quote(element: MarkdownElement):
    return f"> {element.content.strip('>').strip()}\n\n"

def parse_block_code(element: MarkdownElement):
    return f"```\n{element.content.strip('```').strip()}\n```\n\n"


def request(text:str, api_key, base_url, default_headers, model, prompt, Structured=False, stream=True):
    assert api_key, "API Key is required."
    assert base_url, "API URL is required."
    assert default_headers, "API Headers is required."
    assert model, "Model is required."
    assert prompt, "Prompt is required."
    print(f"request")
    client = openai.OpenAI(api_key=api_key, base_url=base_url, default_headers=default_headers)
    if not Structured:
        completion_stream = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
            stream=stream,
        )
        if stream:
            return completion_stream      
        return completion_stream.choices[0].message.content
    else:
        completion = client.beta.chat.completions.parse(
            model=model,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
            response_format=Response,
        )
        res = parse_response(completion.choices[0].message.parsed)
        return res
    

    

    


