---
name: inject-review
description: HTML demo 评审闭环工具。两个动作：(1) 注入评论功能 —— 用户说"注入评审"、"inject review"、"给这个 HTML 加评论功能"、"/inject-review"；(2) 提取评论 —— 用户说"帮我看下这份评审"、"提取评论"、"把评论整理一下"、"读一下这份 review"、"/extract-review"。评论存在 HTML 文件内，无服务器、无外网。
---

# inject-review — HTML Demo 评审闭环工具

## 用途

两个核心动作，构成完整评审闭环：

1. **注入（inject）**：给任意 HTML 加评论工具条 → 发给评审人 → 评审人点元素留评论 → 保存回传
2. **提取（extract）**：从收回的 review HTML 里提取所有评论 → 输出结构化 Markdown 报告 → Claude 读报告去改项目

**核心特性**：零服务器、零账号、零付费、评论存在 HTML 文件本身。

## 何时触发

### 注入（inject_comments.py）
- 用户直接喊：`/inject-review`、"注入评审"、"inject review"
- 用户刚生成完一个 HTML demo，说"发给同事评审" / "收集评论" / "让别人 review"
- 用户收到别人发来的 HTML，说"帮我改成可评论的" / "加个评论功能"

### 提取（extract_comments.py）
- 用户喊：`/extract-review`、"提取评论"、"把评论整理一下"
- 用户说"帮我看下这份评审" / "读一下这份 review" / "评论有哪些"
- 用户扔一个 `_review_<名字>.html` 过来（典型是评审人回传的版本）

## 使用方式

### 注入评论功能

```bash
python3 ~/.claude/skills/inject-review/inject_comments.py <输入HTML路径> [输出路径]
```

### 提取评论报告

```bash
# 单个文件
python3 ~/.claude/skills/inject-review/extract_comments.py <review.html>

# 多个评审回传合并
python3 ~/.claude/skills/inject-review/extract_comments.py *.html

# 输出到文件
python3 ~/.claude/skills/inject-review/extract_comments.py review.html -o report.md
```

输出 Markdown 报告结构：总览（评审人/数量/时间）→ 按必改/建议/疑问分组 → 评审人统计表。

### Claude 执行 extract 时的行为

1. 找用户指定的 review HTML（可 Glob `*_review_*.html` 定位评审回传版本）
2. 跑 `extract_comments.py`，拿到 Markdown 报告
3. 把报告直接展示给用户
4. 主动问："哪些要改，我来改？" 然后根据确认去修改源 PRD / 代码 / Demo

不指定输出路径时，默认生成同目录下的 `<原文件名>_review.html`。

### 典型工作流

1. **作者侧（Bella 或同事）** — 生成完 HTML demo 后：
   ```bash
   python3 ~/.claude/skills/inject-review/inject_comments.py ./my_demo.html
   # → 生成 my_demo_review.html
   ```
   把 `my_demo_review.html` 通过微信 / 飞书 / 邮件发给评审人。

2. **评审人侧** — 收到 HTML 文件：
   - 双击打开（任何浏览器、离线可用）
   - 右上角工具条：填名字 → 点"开启评审" → 点元素留评论
   - 评审完点 "💾 保存" → 下载 `<原名>_review_<评审人>.html`
   - 把这个文件回传给作者

3. **作者侧** — 收到评审后的 HTML：
   - 双击打开 → 自动看到所有评论标注（右上红色数字）
   - 点数字查看具体评论，点 💬 看评论列表
   - 可以继续评审或交给下一位评审人

### 同一份 demo 多人评审

支持两种模式：
- **串行**：A 评完 → 回传 → B 基于 A 的评审版再评 → 回传（评论累积）
- **并行**：原始版本同时发给 A 和 B → 各自评完 → 作者收到两份 → 手动 / 脚本合并（后续可扩展聚合工具）

## 执行步骤（Claude 的行为）

当用户触发这个 skill 时：

1. **确认输入文件**：
   - 如果用户指定了 HTML 路径，直接用
   - 如果用户说"刚才那个 demo" / 没指定，用 Glob 找最近修改的 `*.html`，跟用户确认
   - 如果找不到，问用户路径

2. **运行注入**：
   ```bash
   python3 ~/.claude/skills/inject-review/inject_comments.py <路径>
   ```

3. **自动打开浏览器预览**（可选，用户没反对就默认打开）：
   ```bash
   open <输出路径>
   ```

4. **告诉用户**：
   - 输出文件路径
   - 简短的评审人使用说明（一两句话：填名字 → 开启评审 → 点元素留评论 → 保存）
   - 可以直接把这个文件发给评审人

## 注入的工具条功能

评审人打开 HTML 后看到的 UI：

- **右上角深紫工具条**：
  - 名字输入框（记住在 localStorage）
  - `开启评审 / 关闭评审` 按钮
  - `💬 N` 评论计数 + 列表
  - `💾 保存` 导出

- **评审模式下**：
  - 鼠标悬停元素 → 红色虚线高亮
  - 点击元素 → 弹出评论对话框
  - 对话框：文本框 + 必改 / 建议 / 疑问 三选一 + 提交 / 取消

- **已有评论**：
  - 被评论元素右上角显示红色数字标记
  - 点标记弹出该元素所有评论
  - 点列表中的评论会滚动定位 + 闪烁高亮元素

## 幂等性

脚本自带幂等处理：对已经注入过的 HTML 再次运行，会自动剥离旧注入再重新注入，不会重复。

## 数据安全

- 评论只存在 HTML 文件本身（`<script id="rv-data">` JSON 块）
- 不上传任何服务器
- localStorage 仅用于记住评审人名字，不存评论（评论直接写入 DOM state）
- 文件传输完全由用户掌控（微信 / 飞书 / 邮件等）

## 限制

- HTML 必须包含 `</body>` 标签（99% 都有）
- 元素定位基于 CSS nth-child 选择器，如果原 HTML 的 DOM 结构被二次编辑（不是作者重新生成），可能有少量标记错位
- 跨不同浏览器 localStorage 不同步（但评论都在 HTML 文件里，不影响使用）

## 典型问答

**Q: 评审人需要装什么？**
A: 什么都不用。任何浏览器双击 HTML 就能用。

**Q: 需要联网吗？**
A: 不需要。完全离线。

**Q: 评论会不会丢？**
A: 评论存在 HTML 文件本身（`<script>` 标签内）。评审人点 "💾 保存" 下载新文件后，评论就固化在文件里了。如果评审人没点保存就关了浏览器，会丢（只在内存里）。UI 可以后续加个"未保存警告"。

**Q: 同事是评审人时要装这个 skill 吗？**
A: 不用。只有"生成 demo 并发起评审"的那方需要这个 skill。评审人只要有浏览器。
