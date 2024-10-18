# CRKT

## 1. 安装

下载 [CRKT.zip](https://github.com/churuikai/CRKT/releases/tag/v2) ，在合适位置解压。启动入口为`crkt.exe`，启动后右下角托盘出现图标。

## 2. 配置

### 基础配置

右键单击图标配置`api-key`、`base-url` (`openai`格式)

例如：`api-key: xx-xxxxxxxxxxxxxxxx`   `base-url: https://api.openai.com/v1/` 

模型推荐使用 `gpt-4o-mini`

配置文件会保存在`config.ini`

### 提示词

可以根据自己需求灵活调整`prompt`（记得提示以`markdown`格式输出），各类 pdf 文档、网页产生了非常异构的文本格式和公式格式，较难处理，推荐提示词如下：
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

选中文本后双击`ctrl`，弹出翻译框。翻译框内可 `ctrl`+`滚轮` 进行字体大小缩放。

## 4. 效果展示

大模型高质量翻译，翻译结果以markdown样式展示，支持数学公式。

![2](https://github.com/user-attachments/assets/82c5fc45-d018-4299-8bf7-602e7437c6cb)
![1](https://github.com/user-attachments/assets/88a319b0-0f65-427d-b7ab-9fdb388e5eaa)
![3](https://github.com/user-attachments/assets/99cc16c9-3287-435d-9994-536b94771876)

