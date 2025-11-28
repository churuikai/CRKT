# CRKT


**绿色轻量、全局使用、翻译质量高的翻译工具。** 


## 1. 安装

下载 [setup_CRKT_x.x.x_x64.exe](https://github.com/churuikai/CRKT/releases) ，执行安装。

## 2. 配置

### 基础配置

右键单击图标配置`api` (`openai`格式)

例如：`api-key: xx-xxxxxxxxxxxxxxxx`   `base-url: https://api.openai.com/v1/` 

> 国内腾讯混元、阿里百炼、字节火山引擎、硅基流动都有 api 服务。
> 模型推荐使用 `gpt-4o-mini`等小模型

配置文件会保存在安装目录下的`data/config.json`；卸载会默认删除该配置文件。

数据缓存会保存到安装目录下的`data/cache.pkl`，缓存加速重复内容翻译速度，删除不影响使用。

### 提示词

可以根据自己需求调整，推荐提示词如下：
```
你是一个专业的学术翻译，任务是将{source_language}翻译为{target_language}。

基本要求：

1. 单词短语识别：如果输入不是句子段落而是是单词或短语，则精炼地解释含义，并给出音标和简单例证。
2. 格式要求：忽略输入的格式，输出格式为 Markdown（直接输出而不是以代码块给出）。

拓展要求：

1. 专有名词和术语使用``标出。
2. 公式格式：忽略输入公式的格式、忽略和清除公式中的tag和序号；输出的公式和数学符号使用latex格式，使用$$...$$包围而不是$...$，例如$$r_t > 1$$，而不是$r_t > 1$。
3. 使用正常字符: 将输入的公式中因复制PDF或ocr扫描而产生的不常见字符替换成标准字符，使用latex代码，例如:
   - '𝑆'换成'S', '𝐹'换成'F', '𝑛'换成'n', 'i'换成i
   - '...' 换成 '\cdots', '.'换成 '\cdot'

直接按要求输出翻译结果，不要输出任何其他内容。
输入：
{selected_text}
```


## 3. 使用

### 基础功能

**快速翻译**：选中文本后双击翻译热键（默认 `Ctrl`），弹出翻译窗口。

**原文编辑**：双击附加热键（默认 `Shift`）添加选中文本到原文区，可二次编辑后再翻译。

**字体缩放**：翻译窗口内可用 `Ctrl` + `滚轮` 调整字体大小。

### 双栏对照

右键托盘图标→开启原文对照，启用原文-翻译双栏布局：

### 缓存机制

双击翻译热键优先显示缓存结果；若不满意，3秒内再次双击会弃用缓存重新请求。

## 4. 效果展示

大模型高质量翻译，翻译结果以markdown样式展示，解释单个单词短语十分灵活，有概率（受限于复杂的pdf格式）支持表格和数学公式。

![4](https://github.com/user-attachments/assets/4726d3ab-edff-45ac-970f-b081c4d63d88)
![2](https://github.com/user-attachments/assets/82c5fc45-d018-4299-8bf7-602e7437c6cb)
![1](https://github.com/user-attachments/assets/88a319b0-0f65-427d-b7ab-9fdb388e5eaa)
![3](https://github.com/user-attachments/assets/99cc16c9-3287-435d-9994-536b94771876)
![image](https://github.com/user-attachments/assets/65cac8e0-84a5-4fc9-8edf-26de9d04456f)

