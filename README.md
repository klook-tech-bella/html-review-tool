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

### 工作流

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
  双击打开 → 看到所有评论标注
```

### 快速开始

```bash
# 1. Clone
git clone https://github.com/<your-username>/html-review-tool.git
cd html-review-tool

# 2. 试一下示例
python3 inject_comments.py examples/sample.html
open examples/sample_review.html

# 3. 给自己的 HTML 用
python3 inject_comments.py /path/to/your_demo.html
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

### 作为 Claude Code Skill 使用

如果你用 Claude Code，可以把 `SKILL.md` 和 `inject_comments.py` 复制到 `~/.claude/skills/inject-review/`，之后跟 Claude 说 `/inject-review` 或 "帮我给这个 HTML 加评论功能"，它会自动跑。

```bash
mkdir -p ~/.claude/skills/inject-review
cp SKILL.md inject_comments.py ~/.claude/skills/inject-review/
```

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
5. Reviewer sends it back; author double-clicks to see all annotations

### Claude Code Skill

This repo ships with a `SKILL.md` compatible with Claude Code's skills system. Install it:

```bash
mkdir -p ~/.claude/skills/inject-review
cp SKILL.md inject_comments.py ~/.claude/skills/inject-review/
```

Then in Claude Code: `/inject-review` or just say "add review comments to this HTML".

### License

MIT
