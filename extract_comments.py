#!/usr/bin/env python3
"""
从一个或多个 review HTML 中提取评论，生成 Markdown 报告。
用法:
    python3 extract_comments.py <review.html> [more.html ...]
    python3 extract_comments.py *.html -o report.md
"""
import sys
import re
import json
import os
import argparse
from datetime import datetime
from collections import defaultdict

SEV_LABEL = {'must': '必改', 'suggest': '建议', 'question': '疑问'}
SEV_ICON = {'must': '🔴', 'suggest': '🟡', 'question': '💭'}
SEV_ORDER = ['must', 'suggest', 'question']


def parse_review_html(path):
    """返回 list of comment dicts, 并附加 _source 字段。"""
    with open(path, 'r', encoding='utf-8') as f:
        html = f.read()
    m = re.search(r'<script id="rv-data"[^>]*>([\s\S]*?)</script>', html)
    if not m:
        return []
    try:
        data = json.loads(m.group(1).strip())
    except json.JSONDecodeError:
        return []
    comments = data.get('comments', [])
    basename = os.path.basename(path)
    for c in comments:
        c['_source'] = basename
    return comments


def get_location(c):
    """评论的可读位置：优先 label，fallback selector。"""
    return c.get('label') or c.get('selector') or '<未知位置>'


def build_report(all_comments, sources):
    """生成 Markdown 报告。"""
    if not all_comments:
        return '# 评审报告\n\n❌ 没有找到任何评论。'

    reviewers = sorted({c.get('reviewer', '匿名') for c in all_comments})
    total = len(all_comments)

    lines = []
    lines.append('# 评审报告')
    lines.append('')
    lines.append(f'**评审人**: {", ".join(reviewers)}  ')
    lines.append(f'**总评论数**: {total}  ')
    lines.append(f'**来源文件**: {", ".join(sources)}  ')
    lines.append(f'**生成时间**: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    lines.append('')
    lines.append('---')
    lines.append('')

    # 按严重程度分组
    by_sev = defaultdict(list)
    for c in all_comments:
        by_sev[c.get('severity', 'suggest')].append(c)

    for sev in SEV_ORDER:
        items = by_sev.get(sev, [])
        if not items:
            continue
        icon = SEV_ICON.get(sev, '•')
        label = SEV_LABEL.get(sev, sev)
        lines.append(f'## {icon} {label} ({len(items)})')
        lines.append('')
        for i, c in enumerate(items, 1):
            loc = get_location(c)
            reviewer = c.get('reviewer', '匿名')
            text = c.get('text', '').strip()
            created = c.get('created_at', '')[:10]
            src = c.get('_source', '')
            lines.append(f'### {i}. 📍 {loc}')
            lines.append(f'**[{reviewer}]** {text}')
            meta = []
            if created:
                meta.append(created)
            if len(sources) > 1 and src:
                meta.append(f'来自 {src}')
            if meta:
                lines.append(f'<sub>{" · ".join(meta)}</sub>')
            lines.append('')
        lines.append('---')
        lines.append('')

    # 评审人统计
    if len(reviewers) > 1:
        lines.append('## 评审人统计')
        lines.append('')
        lines.append('| 评审人 | 必改 | 建议 | 疑问 | 总数 |')
        lines.append('|--------|------|------|------|------|')
        for r in reviewers:
            mine = [c for c in all_comments if c.get('reviewer') == r]
            must = sum(1 for c in mine if c.get('severity') == 'must')
            suggest = sum(1 for c in mine if c.get('severity') == 'suggest')
            question = sum(1 for c in mine if c.get('severity') == 'question')
            lines.append(f'| {r} | {must} | {suggest} | {question} | {len(mine)} |')
        lines.append('')

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(description='提取 review HTML 里的评论生成 Markdown 报告。')
    parser.add_argument('files', nargs='+', help='一个或多个 review HTML 文件路径')
    parser.add_argument('-o', '--output', help='输出 Markdown 文件路径（默认打印到 stdout）')
    args = parser.parse_args()

    all_comments = []
    sources = []
    for path in args.files:
        if not os.path.exists(path):
            print(f'⚠️ 跳过不存在的文件: {path}', file=sys.stderr)
            continue
        comments = parse_review_html(path)
        if comments:
            all_comments.extend(comments)
            sources.append(os.path.basename(path))
        else:
            print(f'⚠️ {path} 里没有找到评论', file=sys.stderr)

    report = build_report(all_comments, sources)

    if args.output:
        with open(args.output, 'w', encoding='utf-8') as f:
            f.write(report)
        print(f'✅ 报告已保存: {args.output}  ({len(all_comments)} 条评论)')
    else:
        print(report)


if __name__ == '__main__':
    main()
