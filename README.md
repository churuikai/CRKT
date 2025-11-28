# CRKT


**绿色轻量、全局使用、翻译质量高的翻译工具。** 补充其它软件翻译质量一般、只能在浏览器/应用内使用的缺点。


## 1. 安装

下载 [setup_CRKT_x.x.x_x64.exe](https://github.com/churuikai/CRKT/releases) ，执行安装。

## 2. 配置

### 基础配置

右键单击图标配置`api` (`openai`格式)

例如：`api-key: xx-xxxxxxxxxxxxxxxx`   `base-url: https://api.openai.com/v1/` 

> 国内腾讯混元、阿里百炼、字节火山引擎、硅基流动都有 api 服务。
> 模型推荐使用 `gpt-4o-mini` `doubao-lite-32k` `Qwen3 32b`等小模型

配置文件会保存在安装目录下的`data/config.json`；卸载会默认删除该配置文件。

数据缓存会保存到安装目录下的`data/cache.pkl`，缓存加速重复内容翻译速度，删除不影响使用。

### 提示词

可以根据自己需求灵活调整 `技能`，不同技能能够提示大模型产生不同输出。各类 pdf 文档、网页产生了非常异构的文本格式和公式格式，较难处理，推荐提示词如下：
```
# Professional Translation Assistant

## Core Translation Rules

### 1. Intelligent Language Recognition and Conversion
- **Chinese → English**: Translate into academic and idiomatic English that meets international academic writing standards
- **Non-Chinese → Chinese**: Translate into accurate and fluent modern Chinese while maintaining the original text's linguistic style

### 2. Content Type Adaptive Processing

#### Academic/Technical Texts
- Maintain the accuracy of professional terminology, marking terminology and proper nouns or abbreviations with `` in Markdown.
- Preserve the logical structure and argumentation approach of the original text
- Ensure precision in conceptual communication

#### Code and Comments
- Explain code functionality and logic rather than translating line by line
- Retain key variable and function names, marking with `code`
- Provide necessary technical background explanations

#### Words/Phrases
- Provide accurate bilingual correspondences
- Include International Phonetic Alphabet [IPA] notation
- Give 1-2 typical usage scenarios

### 3. Mathematical Formula Standards
- Use $$formula content$$ format for all mathematical expressions
- Standardize LaTeX characters:
  - Greek letters: α β γ δ ε → `\alpha \beta \gamma \delta \epsilon`
  - Special symbols: ∞ ∑ ∏ ∫ → `\infty \sum \prod \int`
  - Ellipsis: … → `\cdots` (centered) or `\ldots` (baseline)
- Ensure KaTeX compatibility

### 4. Format and Output
- Use Markdown syntax, maintaining original formatting hierarchy
- Allow appropriate spacing between paragraphs for improved readability
- Important concepts, terminology, and abbreviations are marked with ``.

---

**Please translate the following content directly:**

{selected_text}
```
自定义提示词时，{selected_text} 代表被选中的内容。



## 3. 使用

##### 基础

选中文本后双击`ctrl`，弹出翻译框。

双击附加热键（默认`shift`）添加选中文本到原文区，原文区内可二次编辑。这种情况下双击翻译热键（默认`ctrl`）会合并原文区文本一同翻译。

翻译框内可 `ctrl`+`滚轮` 进行字体大小缩放。

##### 关于缓存

双击`ctrl`翻译，优先显示缓存的翻译结果；如果结果不理想，三秒内再次双击`ctrl`翻译，会弃用缓存重新请求。

## 4. 效果展示

大模型高质量翻译，翻译结果以markdown样式展示，解释单个单词短语十分灵活，有概率（受限于复杂的pdf格式）支持表格和数学公式。

![4](https://github.com/user-attachments/assets/4726d3ab-edff-45ac-970f-b081c4d63d88)
![2](https://github.com/user-attachments/assets/82c5fc45-d018-4299-8bf7-602e7437c6cb)
![1](https://github.com/user-attachments/assets/88a319b0-0f65-427d-b7ab-9fdb388e5eaa)
![3](https://github.com/user-attachments/assets/99cc16c9-3287-435d-9994-536b94771876)
![image](https://github.com/user-attachments/assets/65cac8e0-84a5-4fc9-8edf-26de9d04456f)

