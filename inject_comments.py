#!/usr/bin/env python3
"""
给任意 HTML 注入评论评审功能。
用法:
    python inject_comments.py <input.html> [output.html]
    默认输出: <input>_review.html
"""
import sys
import os

INJECT = r"""
<!-- ===== Review Tool (auto-injected) ===== -->
<style>
  #rv-toolbar { position: fixed; top: 10px; right: 10px; z-index: 99999;
    background: #2D2040; color: #fff; border-radius: 8px; padding: 8px 12px;
    display: flex; gap: 8px; align-items: center;
    font-family: -apple-system, sans-serif; font-size: 12px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25); }
  #rv-toolbar button { background: #7B5EA7; color: #fff; border: 0;
    padding: 5px 10px; border-radius: 4px; cursor: pointer; font-size: 12px; }
  #rv-toolbar button:hover { background: #5B3E8A; }
  #rv-toolbar input { border: 0; padding: 5px 8px; border-radius: 4px;
    font-size: 12px; width: 90px; }
  #rv-toolbar.active { background: #c0392b; }
  #rv-toolbar.active button { background: #fff; color: #c0392b; }
  .rv-hover { outline: 2px dashed #c0392b !important; cursor: pointer !important; }
  .rv-marker { position: absolute; background: #c0392b; color: #fff;
    font-size: 10px; font-weight: 700; border-radius: 10px; padding: 1px 6px;
    z-index: 99998; cursor: pointer; box-shadow: 0 2px 4px rgba(0,0,0,0.3); }
  #rv-dialog { position: fixed; background: #fff; border: 1px solid #ddd;
    border-radius: 8px; padding: 14px; box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    z-index: 99999; width: 300px;
    font-family: -apple-system, sans-serif; font-size: 13px; }
  #rv-dialog textarea { width: 100%; min-height: 70px; border: 1px solid #ddd;
    border-radius: 4px; padding: 6px; font-size: 13px; box-sizing: border-box;
    font-family: inherit; }
  #rv-dialog .rv-sev { display: flex; gap: 8px; margin: 8px 0; font-size: 12px; }
  #rv-dialog .rv-sev label { cursor: pointer; }
  #rv-dialog .rv-actions { display: flex; gap: 8px; justify-content: flex-end; margin-top: 8px; }
  #rv-dialog button { padding: 5px 12px; border-radius: 4px; cursor: pointer;
    border: 1px solid #ddd; background: #fff; font-size: 12px; }
  #rv-dialog button.primary { background: #7B5EA7; color: #fff; border-color: #7B5EA7; }
  #rv-list { position: fixed; bottom: 10px; right: 10px; width: 340px;
    max-height: 50vh; background: #fff; border-radius: 8px;
    box-shadow: 0 4px 16px rgba(0,0,0,0.2); z-index: 99998;
    display: none; font-family: -apple-system, sans-serif; }
  #rv-list.open { display: flex; flex-direction: column; }
  #rv-list .rv-list-header { background: #2D2040; color: #fff;
    padding: 10px 12px; font-size: 13px; display: flex;
    justify-content: space-between; align-items: center; border-radius: 8px 8px 0 0; }
  #rv-list .rv-list-body { overflow-y: auto; flex: 1; max-height: 40vh; }
  #rv-list .rv-item { padding: 10px 12px; border-bottom: 1px solid #f0f0f0;
    font-size: 12px; cursor: pointer; }
  #rv-list .rv-item:hover { background: #faf8fc; }
  .rv-sev-tag { display: inline-block; padding: 1px 6px; border-radius: 3px;
    font-size: 10px; font-weight: 700; margin-right: 4px; }
  .rv-sev-must { background: #fde8e8; color: #c0392b; }
  .rv-sev-suggest { background: #fef9e7; color: #d4a017; }
  .rv-sev-question { background: #e3f2fd; color: #1565c0; }
  .rv-close-x { cursor: pointer; font-size: 16px; }
</style>

<div id="rv-toolbar">
  <span>📝</span>
  <input id="rv-reviewer" placeholder="你的名字" />
  <button id="rv-toggle">开启评审</button>
  <button id="rv-show-list">💬 <span id="rv-count">0</span></button>
  <button id="rv-save">💾 保存</button>
</div>

<script id="rv-data" type="application/json">{"comments":[]}</script>

<script>
(function(){
  var state = { active: false, reviewer: '', comments: [] };

  try {
    var raw = document.getElementById('rv-data').textContent;
    var data = JSON.parse(raw || '{}');
    state.comments = data.comments || [];
  } catch(e) { state.comments = []; }

  state.reviewer = localStorage.getItem('rv-reviewer') || '';
  document.getElementById('rv-reviewer').value = state.reviewer;

  function getSelector(el) {
    if (el.id) return '#' + el.id;
    var path = [];
    while (el && el.nodeType === 1 && el.tagName !== 'BODY' && el.tagName !== 'HTML') {
      var sib = el, nth = 1;
      while (sib.previousElementSibling) { sib = sib.previousElementSibling; nth++; }
      path.unshift(el.tagName.toLowerCase() + ':nth-child(' + nth + ')');
      el = el.parentElement;
    }
    return path.join(' > ');
  }

  function queryEl(sel) {
    try { return document.querySelector(sel); } catch(e) { return null; }
  }

  function renderMarkers() {
    var old = document.querySelectorAll('.rv-marker');
    for (var i = 0; i < old.length; i++) old[i].remove();
    var grouped = {};
    state.comments.forEach(function(c) {
      grouped[c.selector] = (grouped[c.selector] || 0) + 1;
    });
    Object.keys(grouped).forEach(function(sel) {
      var el = queryEl(sel);
      if (!el) return;
      var rect = el.getBoundingClientRect();
      var marker = document.createElement('div');
      marker.className = 'rv-marker';
      marker.style.top = (rect.top + window.scrollY - 8) + 'px';
      marker.style.left = (rect.right + window.scrollX - 20) + 'px';
      marker.textContent = grouped[sel];
      marker.addEventListener('click', function(e) {
        e.stopPropagation();
        showCommentsFor(sel);
      });
      document.body.appendChild(marker);
    });
    document.getElementById('rv-count').textContent = state.comments.length;
  }

  function showCommentsFor(sel) {
    var items = state.comments.filter(function(c) { return c.selector === sel; });
    var labelMap = { must: '必改', suggest: '建议', question: '疑问' };
    var texts = items.map(function(c) {
      return '[' + (labelMap[c.severity] || c.severity) + '] '
             + (c.reviewer || '匿名') + ': ' + c.text;
    }).join('\n\n');
    alert(texts);
  }

  var hoverEl = null;

  document.addEventListener('mouseover', function(e) {
    if (!state.active) return;
    if (e.target.closest('#rv-toolbar, #rv-dialog, #rv-list, .rv-marker')) return;
    if (hoverEl) hoverEl.classList.remove('rv-hover');
    hoverEl = e.target;
    hoverEl.classList.add('rv-hover');
  });

  document.addEventListener('click', function(e) {
    if (!state.active) return;
    if (e.target.closest('#rv-toolbar, #rv-dialog, #rv-list, .rv-marker')) return;
    e.preventDefault();
    e.stopPropagation();
    var sel = getSelector(e.target);
    openDialog(sel, e.clientX, e.clientY);
  }, true);

  function openDialog(sel, x, y) {
    var existing = document.getElementById('rv-dialog');
    if (existing) existing.remove();
    var dlg = document.createElement('div');
    dlg.id = 'rv-dialog';
    dlg.style.left = Math.min(x, window.innerWidth - 320) + 'px';
    dlg.style.top = Math.min(y + 10, window.innerHeight - 240) + 'px';
    dlg.innerHTML =
      '<div style="font-size:11px;color:#999;margin-bottom:6px;word-break:break-all;">'
      + sel + '</div>'
      + '<textarea id="rv-text" placeholder="写下你的评论..."></textarea>'
      + '<div class="rv-sev">'
      + '<label><input type="radio" name="rv-sev" value="must" checked> 必改</label>'
      + '<label><input type="radio" name="rv-sev" value="suggest"> 建议</label>'
      + '<label><input type="radio" name="rv-sev" value="question"> 疑问</label>'
      + '</div>'
      + '<div class="rv-actions">'
      + '<button id="rv-cancel">取消</button>'
      + '<button id="rv-submit" class="primary">提交</button>'
      + '</div>';
    document.body.appendChild(dlg);
    document.getElementById('rv-text').focus();
    document.getElementById('rv-cancel').onclick = function() { dlg.remove(); };
    document.getElementById('rv-submit').onclick = function() {
      var text = document.getElementById('rv-text').value.trim();
      if (!text) return;
      var sev = document.querySelector('input[name="rv-sev"]:checked').value;
      state.reviewer = document.getElementById('rv-reviewer').value.trim() || '匿名';
      localStorage.setItem('rv-reviewer', state.reviewer);
      state.comments.push({
        id: 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2,6),
        selector: sel,
        text: text,
        severity: sev,
        reviewer: state.reviewer,
        created_at: new Date().toISOString()
      });
      dlg.remove();
      renderMarkers();
    };
  }

  document.getElementById('rv-toggle').onclick = function() {
    state.active = !state.active;
    this.textContent = state.active ? '关闭评审' : '开启评审';
    document.getElementById('rv-toolbar').classList.toggle('active', state.active);
    if (!state.active && hoverEl) {
      hoverEl.classList.remove('rv-hover');
      hoverEl = null;
    }
  };

  document.getElementById('rv-show-list').onclick = function() {
    var list = document.getElementById('rv-list');
    if (list && list.classList.contains('open')) {
      list.classList.remove('open');
      return;
    }
    if (list) list.remove();
    list = document.createElement('div');
    list.id = 'rv-list';
    list.classList.add('open');
    var labelMap = { must: '必改', suggest: '建议', question: '疑问' };
    list.innerHTML =
      '<div class="rv-list-header">'
      + '<span>评论列表 (' + state.comments.length + ')</span>'
      + '<span class="rv-close-x" id="rv-list-close">✕</span>'
      + '</div>'
      + '<div class="rv-list-body" id="rv-list-body"></div>';
    document.body.appendChild(list);
    document.getElementById('rv-list-close').onclick = function() {
      list.classList.remove('open');
    };
    var body = document.getElementById('rv-list-body');
    if (state.comments.length === 0) {
      body.innerHTML = '<div style="padding:16px;text-align:center;color:#999">暂无评论</div>';
    } else {
      state.comments.forEach(function(c) {
        var item = document.createElement('div');
        item.className = 'rv-item';
        item.innerHTML =
          '<span class="rv-sev-tag rv-sev-' + c.severity + '">'
          + (labelMap[c.severity] || c.severity) + '</span>'
          + '<b>' + (c.reviewer || '匿名') + '</b>: ' + c.text
          + '<div style="color:#999;font-size:10px;margin-top:2px">' + c.selector + '</div>';
        item.onclick = function() {
          var el = queryEl(c.selector);
          if (el) {
            el.scrollIntoView({ behavior: 'smooth', block: 'center' });
            var prev = el.style.outline;
            el.style.transition = 'outline 0.3s';
            el.style.outline = '3px solid #c0392b';
            setTimeout(function() { el.style.outline = prev || ''; }, 1800);
          }
        };
        body.appendChild(item);
      });
    }
  };

  document.getElementById('rv-save').onclick = function() {
    var dataScript = document.getElementById('rv-data');
    dataScript.textContent = JSON.stringify({ comments: state.comments }, null, 2);
    var html = '<!DOCTYPE html>\n' + document.documentElement.outerHTML;
    var reviewer = state.reviewer || '匿名';
    var originalName = (location.pathname.split('/').pop() || 'review.html')
                       .replace(/\.html?$/, '')
                       .replace(/_review(_[^_]+)?$/, '');
    var filename = originalName + '_review_' + reviewer + '.html';
    var blob = new Blob([html], { type: 'text/html' });
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.click();
    URL.revokeObjectURL(url);
  };

  window.addEventListener('scroll', renderMarkers);
  window.addEventListener('resize', renderMarkers);
  setTimeout(renderMarkers, 100);
})();
</script>
<!-- ===== /Review Tool ===== -->
"""

def inject(input_path, output_path=None):
    with open(input_path, 'r', encoding='utf-8') as f:
        html = f.read()
    if '</body>' not in html:
        raise ValueError('HTML 缺少 </body> 标签，无法注入')
    # 幂等：如果已经注入过，先剥离旧版本
    start_marker = '<!-- ===== Review Tool (auto-injected) ===== -->'
    end_marker = '<!-- ===== /Review Tool ===== -->'
    if start_marker in html and end_marker in html:
        s = html.index(start_marker)
        e = html.index(end_marker) + len(end_marker)
        html = html[:s] + html[e:]
    new_html = html.replace('</body>', INJECT + '\n</body>', 1)
    if output_path is None:
        base, ext = os.path.splitext(input_path)
        output_path = f'{base}_review{ext}'
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(new_html)
    size_kb = os.path.getsize(output_path) / 1024
    print(f'✅ 已生成: {output_path}  ({size_kb:.1f} KB)')
    return output_path

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    inject(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
