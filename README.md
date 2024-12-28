# CRKT

2024年已经存在了相当多的翻译工具，它们足够便捷，例如知云、沉浸式翻译、各类划词翻译。

但仍需一个不占用电脑运行资源、随时可以呼出、给出高质量地道翻译的小工具，补充其它软件翻译质量一般、只能在浏览器/应用内使用的缺点。

**它是一个轻量简单、全局使用、翻译质量高的备用/补充翻译工具。**


## 1. 安装

下载 [CRKT.zip](https://github.com/churuikai/CRKT/releases) ，在合适位置解压。启动入口为`crkt.exe`，启动后右下角托盘出现图标。

## 2. 配置

### 基础配置

右键单击图标配置`api` (`openai`格式)

例如：`api-key: xx-xxxxxxxxxxxxxxxx`   `base-url: https://api.openai.com/v1/` 

> 推荐一个免费的api项目 [https://github.com/popjane/free_chatgpt_api](https://github.com/popjane/free_chatgpt_api) （申请到的base_url后需要附加`/v1/`）

模型推荐使用 `gpt-4o-mini`

配置文件会保存在`config.ini`

数据缓存会保存到`cache.pkl`，缓存加速重复内容翻译速度，删除不影响使用。

### 技能

可以根据自己需求灵活调整`技能`，不同技能能够提示大模型产生不同输出。各类 pdf 文档、网页产生了非常异构的文本格式和公式格式，较难处理，默认的通用翻译提示词如下：
```
                        "你将作为一个专业的翻译助手，任务是将文本从英文翻译成中文。\n"
                        "翻译时需要遵循以下要求：\n"
                        "1. 准确性：确保翻译内容的准确性，保留专业术语和专有名词，用反引号`标出。\n"
                        "2. 格式要求：使用 Markdown 语法输出内容。\n"
                        "3. 公式格式：任何时候所有公式、数学字母都必须使用四个$$$$包围，忽略任何tag和序号。\n"
                        "4. 使用常见字符: 任何公式中不常见的字符替换成常见标准的字符，输出latex代码，确保katex可以解析，例如:\n"
                        "   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i\n"
                        "   - '...' 换成 '\\cdots', '.'换成 '\\cdot'\n"
                        "5. 注意，如果是单个单词或短语，你可以精炼地道的解释该单词/短语的含义，给出音标和简单例证。\n"
                        "6. 如果是代码或注释，解释代码含义或补全代码\n\n"
                        "下面是需要翻译的内容：{selected_text}"
```
自定义提示词时，{selected_text} 代表被选中的内容。

**如果有更好的提示词，非常欢迎提出。**

## 3. 使用

##### 基础

选中文本后双击`ctrl`，弹出翻译框。

双击`shift`暂存选中文本，暂存区内可二次编辑。这种情况下双击`ctrl`会合并暂存区文本一同翻译。

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


