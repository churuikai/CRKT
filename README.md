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
You are a professional academic translator, tasked with translating from {source_language_en} to {target_language_en}.

Basic Requirements:

1. Format Requirement: Ignore input formatting. Output in Markdown format (directly, not in a code block).
2. Retain Proper Nouns and Terminology, marking them with ``.

Extended Requirements:

1. Formula Formatting: Ignore input formula formatting, tags, and numbering. Output formulas and mathematical symbols using LaTeX format, enclosed in double dollar signs ($$…$$), for example, $$r_t > 1$$.
2. Use Standard Characters: Replace uncommon characters in input formulas (resulting from PDF copying or OCR scanning) with standard characters and LaTeX code, for example:
  - ‘𝑆’ replaced with ‘S’, ‘i’ replaced with i
  - ‘…’ replaced with ‘cdots’, ‘.’ replaced with ‘cdot’

Input:

{selected_text}

Please output the result only:
```


## 3. 使用

### 基础功能

**快速翻译**：选中文本后双击翻译热键（默认 `Ctrl`），弹出翻译窗口。

**原文编辑**：双击附加热键（默认 `Shift`）添加选中文本到原文区，可二次编辑后再翻译。

**字体缩放**：翻译窗口内可用 `Ctrl` + `滚轮` 调整字体大小。

**历史记录**：点击↑↓或按下↑↓翻阅历史翻译记录。

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

