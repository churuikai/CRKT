# CRKT

> 优势：
> 1. 翻译质量高，特别是对单词/短语/名词术语/缩写的灵活解释。
> 2. 显示美观，能识别复杂格式如表格/公式。
> 3. 使用方便，全局可用，双击ctrl召出。
> 4. 低消耗，后台运行对系统资源占用忽略不计，可日常挂在托盘，作为主力/备用翻译。
> 
> 劣势：
> 1. 长文本速度稍慢。
> 2. 功能单一，仅翻译和解释。
> 3. 免费但需自己准备api。
>
> 后续优化方向：
> 1. 提示词优化。
> 2. 输入和输出做进一步格式化处理，翻译更准确、显示更美观。
> 3. 设计缓存，相同相似文本二次翻译响应更快。
> 4. 多模型协同，识别输入文本所在领域和翻译难度，动态选择不同提示词/大模型高质量翻译/传统模型快速翻译。
> 5. 不提高系统资源占用和使用难度的情况下增加实用功能。

## 1. 安装

下载 [CRKT.zip](https://github.com/churuikai/CRKT/releases/tag/v2) ，在合适位置解压。启动入口为`crkt.exe`，启动后右下角托盘出现图标。

## 2. 配置

### 基础配置

右键单击图标配置`api-key`、`base-url` (`openai`格式)

例如：`api-key: xx-xxxxxxxxxxxxxxxx`   `base-url: https://api.openai.com/v1/` 

> 推荐一个免费的api项目 [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api) （申请到的base_url后需要附加`/v1/`）

模型推荐使用 `gpt-4o-mini`

配置文件会保存在`config.ini`

数据缓存会保存到`cache.pkl`，缓存加速重复内容翻译速度，删除不影响使用。

### 提示词

可以根据自己需求灵活调整`prompt`（记得提示以`markdown`格式输出），各类 pdf 文档、网页产生了非常异构的文本格式和公式格式，较难处理，推荐提示词如下：
```
你将作为一个专业的翻译助手，任务是将文本从英文翻译成中文。翻译时需要遵循以下要求：
1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。
2. 格式要求：使用 Markdown 语法输出内容。
3. 使用双$$：任何时候所有公式、数学字母都必须使用四个$$$$包围。
4. 公式格式: katex格式输出，例如：$$E = mc^2$$, 忽略任何tag和序号。
4. 使用常见字符: 任何公式中不常见的字符替换成常见标准的字符，输出latex代码，确保katex可以解析，例如:
   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i
   - '...' 换成 '\cdots', '.'换成 '\cdot'
5. 注意，如果是单个单词或短语，你可以精炼地道的解释该单词/短语的含义，给出音标和简单例证。
6. 如果是代码或注释，解释代码含义或补全代码
```
下方英文提示词效果不如上述中文提示词，有待优化。
```
You are a professional translator whose task is to translate English text into Chinese. Please follow the rules below when translating:

1. **Accuracy**: Ensure the accuracy and professionalism of the translation. Retain technical terms, proper nouns, and abbreviations, marking them with backticks `` ` ``.

2. **Formatting Requirements**: Use Markdown syntax to output the content. All mathematical expressions and formulas should be in LaTeX syntax, enclosed by four dollar signs `$$`. For example:
   - $$E = mc^2$$
   - $$x_1$$

3. **Formula Handling**:
   - Ignore labels, numbering, and unnecessary HTML tags in formulas, and ensure only the essential content of the formulas is translated.
   - Standardize uncommon characters, special symbols, or HTML language in the formulas. For example:
     - Replace '𝑆' with 'S', '𝐹' with 'F', and '𝑛' with 'n'.
     - Use `\cdots` instead of '...', and `\cdot` instead of '.'.
     - Replace `X<em>k,NSTS</em>` with `X_{k,NSTS}`.

4. **Vocabulary Translation**:
   - For single words or short phrases, provide a concise translation or refined, idiomatic explanation. Also include the International Phonetic Alphabet (IPA) pronunciation and simple examples to aid understanding.
```
**如果有更好的提示词，非常欢迎提出。**

## 3. 使用

##### 基础

选中文本后双击`ctrl`，弹出翻译框。

翻译框内可 `ctrl`+`滚轮` 进行字体大小缩放。

##### 关于缓存

双击`ctrl`翻译，优先显示缓存的翻译结果；如果结果不理想，三秒内再次双击`ctrl`翻译，会弃用缓存重新请求。

## 4. 效果展示

大模型高质量翻译，翻译结果以markdown样式展示，解释单个单词短语十分灵活，有概率（受限于复杂的pdf格式）支持表格和数学公式。

![4](https://github.com/user-attachments/assets/4726d3ab-edff-45ac-970f-b081c4d63d88)
![2](https://github.com/user-attachments/assets/82c5fc45-d018-4299-8bf7-602e7437c6cb)
![1](https://github.com/user-attachments/assets/88a319b0-0f65-427d-b7ab-9fdb388e5eaa)
![3](https://github.com/user-attachments/assets/99cc16c9-3287-435d-9994-536b94771876)

