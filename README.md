# html-review-tool

> 给任意 HTML demo 注入一套轻量评审工具条，让评审人在浏览器里直接点元素留评论。
> 全程零服务器、零账号、零付费，评论存在 HTML 文件本身。

**[English](#english) | [中文](#中文)**

---

## 中文

### 解决什么问题

你做了一个 HTML demo 想发给同事评审？
- ❌ 发截图 → 评审人只能在聊天里描述"第三张图红色那个按钮"，难定位
- ❌ 部署到 Vercel → 要公开链接或者付费密码保护
- ❌ 上传到 Figma → HTML 交互丢失，变成静态图
- ✅ **html-review-tool** → HTML 文件互传，点元素留评论，完全离线

### 完整闭环

```
[作者]
  你的HTML → python3 inject_comments.py your_demo.html
          → your_demo_review.html（注入了评审工具条）
          ↓ 微信 / 飞书 / 邮件发给评审人
[评审人]
  双击打开 → 点"开启评审" → 点元素留评论
         → 点"💾 保存" → 下载 your_demo_review_张三.html
         ↓ 回传
[作者]
  方式 A：双击打开 → 浏览器里看所有评论标注
  方式 B：python3 extract_comments.py your_demo_review_张三.html
        → 生成结构化 Markdown 报告（按必改/建议/疑问分组）
        → 扔给 AI 读 → 直接修改源项目
```

**两个脚本分别做什么**：
| 脚本 | 作用 | 触发时机 |
|------|------|---------|
| `inject_comments.py` | 给 HTML 加评审工具条 | 你做完 demo，要发评审之前 |
| `extract_comments.py` | 从回传的 HTML 里抽取评论，生成 Markdown 报告 | 评审人回传之后，你要改项目之前 |

### 快速开始

```bash
# 1. Clone
git clone https://github.com/klook-tech-bella/html-review-tool.git
cd html-review-tool

# 2. 试一下示例
python3 inject_comments.py examples/sample.html
open examples/sample_review.html

# 3. 给自己的 HTML 用
python3 inject_comments.py /path/to/your_demo.html

# 4. 收到评审回传后，提取评论成 Markdown 报告
python3 extract_comments.py your_demo_review_张三.html -o report.md

# 多份评审合并
python3 extract_comments.py *_review_*.html -o report.md
```

### 评审工具条功能

| 按钮 | 作用 |
|------|------|
| 名字输入框 | 填你的名字（会记住） |
| 开启评审 | 进入评审模式，工具条变红 |
| 💬 N | 查看所有评论列表，点击定位到元素 |
| 💾 保存 | 下载包含评论的新 HTML 文件 |

评审模式下：
- 鼠标悬停元素 → 红色虚线高亮
- 点击元素 → 弹出评论框（必改 / 建议 / 疑问）
- 元素右上角显示红色数字标记，点标记看评论

### 配合 AI 使用

#### Claude Code（最流畅）
把 `SKILL.md`、`inject_comments.py`、`extract_comments.py` 复制到 `~/.claude/skills/inject-review/`：

```bash
mkdir -p ~/.claude/skills/inject-review
cp SKILL.md inject_comments.py extract_comments.py ~/.claude/skills/inject-review/
```

之后直接跟 Claude 说：
- `/inject-review` 或 "帮我给这个 HTML 加评论功能" → 自动注入
- `/extract-review` 或 "帮我看下这份评审" / "提取评论" → 自动跑 extract + 展示报告 + 问你要不要改

#### Claude.ai 网页版 / Claude Desktop
也能用，只是没有 Skill 自动触发。上传 HTML 后直接说：
- "跑一下这个仓库里的 `inject_comments.py` 给这个 HTML 注入评论功能" → 下载结果
- "跑一下 `extract_comments.py` 提取评论成 Markdown" → 读报告再改源项目

#### 其他 AI（Cursor / Cline / ChatGPT 代码沙箱）
一样，只要能跑 Python 就能用，脚本纯标准库，无依赖。

### 多人评审

- **串行**：A 评完 → 回传 → B 基于 A 的版本继续评（评论累积）
- **并行**：原始版本同时发 A 和 B → 各自评完 → 作者手动合并

### 限制

- HTML 必须有 `</body>` 标签
- 元素定位基于 CSS nth-child 选择器；如果作者重新编辑了 HTML 的 DOM 结构，旧评论的标记可能错位
- 评论存 DOM 状态，评审人没点"保存"就关浏览器会丢

### License

MIT

---

## English

### What it does

Inject a lightweight review toolbar into any HTML demo. Reviewers double-click the HTML, click on any element to leave comments (must-fix / suggestion / question), and export a new HTML with all comments embedded. Zero server, zero account, zero cost — the comments live inside the HTML file itself.

### Quick start

```bash
git clone https://github.com/<your-username>/html-review-tool.git
cd html-review-tool
python3 inject_comments.py examples/sample.html
open examples/sample_review.html
```

### Workflow

1. Author runs `python3 inject_comments.py my_demo.html` → gets `my_demo_review.html`
2. Author sends the file to reviewers (WeChat, email, anything)
3. Reviewer opens in browser, enters name, clicks "开启评审" (Start Review), clicks elements to comment
4. Reviewer clicks "💾 保存" to download `my_demo_review_<name>.html`
5. Reviewer sends it back; author either:
   - Double-clicks to see annotations in browser, OR
   - Runs `python3 extract_comments.py my_demo_review_<name>.html -o report.md` → gets a structured Markdown report (grouped by severity) → feed to AI to fix the source project

### Two scripts, two phases

| Script | Phase |
|--------|-------|
| `inject_comments.py` | Before review — add toolbar to HTML |
| `extract_comments.py` | After review — extract comments to Markdown report |

### Works with AI

**Claude Code** — install as a skill, then use `/inject-review` or `/extract-review`:
```bash
mkdir -p ~/.claude/skills/inject-review
cp SKILL.md inject_comments.py extract_comments.py ~/.claude/skills/inject-review/
```

**Claude.ai / ChatGPT / Cursor / any AI with Python sandbox** — upload the HTML and ask the AI to run the scripts. Pure stdlib, zero dependencies.

### License

MIT
