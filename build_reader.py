#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import re
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def load_chapters():
    chapters = []
    for fname in sorted(os.listdir(BASE_DIR)):
        if re.match(r"^\d{2}_.*\.md$", fname):
            fpath = os.path.join(BASE_DIR, fname)
            with open(fpath, "r", encoding="utf-8") as f:
                content = f.read()
            chapters.append({
                "filename": fname,
                "content": content,
                "mtime": os.path.getmtime(fpath),
            })
    return chapters


READONLY_HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>《我不是勇者》第一卷：無風迴廊盡頭的少女</title>
<style>
  :root {
    --bg-primary: #f7f3e8;
    --bg-secondary: #efe9d8;
    --bg-elevated: #fdfbf6;
    --text-primary: #26221e;
    --text-secondary: #6e655c;
    --text-muted: #9c9286;
    --border-color: #dfd6c3;
    --accent-color: #8c3f2b;
    --accent-hover: #702f1e;
    --accent-soft: rgba(140, 63, 43, 0.08);
    --shadow-sm: 0 2px 8px rgba(38, 34, 30, 0.06);
    --shadow-md: 0 8px 28px rgba(38, 34, 30, 0.1);
    --reader-font: "Songti TC", "Noto Serif TC", "PMingLiU", "SimSun", serif;
    --ui-font: -apple-system, BlinkMacSystemFont, "Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif;
    --font-size: 19px;
    --line-height: 2.05;
    --page-max-width: 760px;
    --para-indent: 2em;
  }

  [data-theme="light"] {
    --bg-primary: #f8f9fa;
    --bg-secondary: #eef0f3;
    --bg-elevated: #ffffff;
    --text-primary: #1e2125;
    --text-secondary: #5c6470;
    --text-muted: #8c95a2;
    --border-color: #e1e4e8;
    --accent-color: #2b579a;
    --accent-hover: #1e3f73;
    --accent-soft: rgba(43, 87, 154, 0.08);
  }

  [data-theme="dark"] {
    --bg-primary: #14161a;
    --bg-secondary: #1c1f26;
    --bg-elevated: #22262f;
    --text-primary: #d9d6cf;
    --text-secondary: #98948c;
    --text-muted: #66635d;
    --border-color: #2e333d;
    --accent-color: #d4845a;
    --accent-hover: #e3966e;
    --accent-soft: rgba(212, 132, 90, 0.12);
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 8px 28px rgba(0, 0, 0, 0.45);
  }

  [data-theme="green"] {
    --bg-primary: #e8f0e6;
    --bg-secondary: #dbe6d8;
    --bg-elevated: #f2f7f1;
    --text-primary: #1f2b21;
    --text-secondary: #526354;
    --text-muted: #7b8e7d;
    --border-color: #c8d8c5;
    --accent-color: #2d6a4f;
    --accent-hover: #1b4332;
    --accent-soft: rgba(45, 106, 79, 0.1);
  }

  * {
    box-sizing: border-box;
  }

  html, body {
    margin: 0;
    padding: 0;
    height: 100%;
    background: var(--bg-primary);
    color: var(--text-primary);
    font-family: var(--ui-font);
    overflow: hidden;
    transition: background-color 0.25s ease, color 0.25s ease;
  }

  #progress-bar {
    position: fixed;
    top: 0;
    left: 0;
    height: 3px;
    background: var(--accent-color);
    width: 0%;
    z-index: 1000;
    transition: width 0.1s ease;
  }

  .app-shell {
    display: flex;
    flex-direction: column;
    height: 100vh;
    width: 100vw;
  }

  .topbar {
    height: 54px;
    background: var(--bg-elevated);
    border-bottom: 1px solid var(--border-color);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 18px;
    gap: 12px;
    z-index: 100;
    box-shadow: var(--shadow-sm);
    flex-shrink: 0;
  }

  .topbar-left, .topbar-right {
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: var(--bg-elevated);
    color: var(--text-primary);
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.15s ease;
    user-select: none;
    white-space: nowrap;
  }

  .btn:hover {
    background: var(--bg-secondary);
    border-color: var(--text-muted);
  }

  .chapter-badge {
    font-family: var(--reader-font);
    font-size: 15px;
    font-weight: 700;
    color: var(--text-primary);
    max-width: 420px;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .word-count-pill {
    font-size: 12px;
    color: var(--text-secondary);
    background: var(--bg-secondary);
    padding: 4px 10px;
    border-radius: 999px;
    border: 1px solid var(--border-color);
    white-space: nowrap;
  }

  .workspace {
    display: flex;
    flex: 1;
    overflow: hidden;
    position: relative;
  }

  .sidebar {
    width: 290px;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: margin-left 0.25s ease;
    flex-shrink: 0;
    z-index: 50;
  }

  .sidebar.collapsed {
    margin-left: -290px;
  }

  .sidebar-header {
    padding: 18px 16px 14px 16px;
    border-bottom: 1px solid var(--border-color);
  }

  .book-title {
    font-family: var(--reader-font);
    font-size: 18px;
    font-weight: 700;
    margin: 0 0 4px 0;
    color: var(--text-primary);
  }

  .book-subtitle {
    font-size: 12px;
    color: var(--text-secondary);
    margin: 0 0 12px 0;
  }

  .search-box {
    width: 100%;
    padding: 8px 10px;
    border-radius: 6px;
    border: 1px solid var(--border-color);
    background: var(--bg-elevated);
    color: var(--text-primary);
    font-size: 13px;
    outline: none;
  }

  .search-box:focus {
    border-color: var(--accent-color);
  }

  .chapter-list {
    flex: 1;
    overflow-y: auto;
    padding: 8px;
  }

  .chapter-item {
    padding: 11px 12px;
    border-radius: 8px;
    cursor: pointer;
    margin-bottom: 4px;
    transition: all 0.15s ease;
    border: 1px solid transparent;
  }

  .chapter-item:hover {
    background: var(--bg-elevated);
  }

  .chapter-item.active {
    background: var(--bg-elevated);
    border-color: var(--accent-color);
    box-shadow: var(--shadow-sm);
  }

  .chapter-item-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 4px;
  }

  .chapter-item.active .chapter-item-title {
    color: var(--accent-color);
  }

  .chapter-item-meta {
    font-size: 11px;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
  }

  .section-anchors {
    margin-top: 6px;
    padding-left: 8px;
    border-left: 2px solid var(--border-color);
    display: none;
    flex-wrap: wrap;
    gap: 4px;
  }

  .chapter-item.active .section-anchors {
    display: flex;
  }

  .sec-pill {
    font-size: 11px;
    padding: 2px 8px;
    border-radius: 4px;
    background: var(--bg-secondary);
    color: var(--text-secondary);
    cursor: pointer;
  }

  .sec-pill:hover {
    background: var(--accent-soft);
    color: var(--accent-color);
  }

  .sidebar-footer {
    padding: 12px 16px;
    border-top: 1px solid var(--border-color);
    font-size: 12px;
    color: var(--text-secondary);
  }

  .reader-pane {
    flex: 1;
    overflow-y: auto;
    padding: 40px 24px 120px 24px;
    scroll-behavior: smooth;
    height: 100%;
  }

  .reader-paper {
    max-width: var(--page-max-width);
    margin: 0 auto;
    background: var(--bg-elevated);
    padding: 58px 68px;
    border-radius: 12px;
    border: 1px solid var(--border-color);
    box-shadow: var(--shadow-md);
    font-family: var(--reader-font);
    font-size: var(--font-size);
    line-height: var(--line-height);
    letter-spacing: 0.03em;
    transition: all 0.2s ease;
  }

  @media (max-width: 768px) {
    .sidebar {
      position: absolute;
      height: 100%;
    }
    .reader-pane {
      padding: 18px 10px 90px 10px;
    }
    .reader-paper {
      padding: 28px 20px;
    }
    .word-count-pill {
      display: none;
    }
  }

  .reader-paper h1 {
    font-size: 1.65em;
    font-weight: 700;
    margin: 0.2em 0 1.3em 0;
    padding-bottom: 0.6em;
    border-bottom: 2px solid var(--accent-color);
    color: var(--text-primary);
    line-height: 1.35;
    letter-spacing: 0.05em;
  }

  .reader-paper h2 {
    font-size: 1.25em;
    font-weight: 700;
    margin: 2.2em 0 1.2em 0;
    color: var(--accent-color);
    text-align: center;
    letter-spacing: 0.15em;
  }

  .reader-paper p {
    margin: 0 0 1.05em 0;
    text-indent: var(--para-indent);
    text-align: justify;
  }

  .reader-paper hr {
    border: none;
    text-align: center;
    margin: 2.2em 0;
  }

  .reader-paper hr::after {
    content: "＊　　　＊　　　＊";
    color: var(--text-muted);
    font-size: 0.85em;
  }

  .reader-paper strong {
    color: var(--accent-color);
    font-weight: 700;
  }

  .chapter-nav-footer {
    max-width: var(--page-max-width);
    margin: 28px auto 0 auto;
    display: flex;
    justify-content: space-between;
    gap: 16px;
  }

  .nav-card {
    flex: 1;
    padding: 16px 20px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-color);
    border-radius: 10px;
    cursor: pointer;
    transition: all 0.15s ease;
  }

  .nav-card:hover {
    border-color: var(--accent-color);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
  }

  .nav-card-label {
    font-size: 12px;
    color: var(--text-muted);
    margin-bottom: 4px;
  }

  .nav-card-title {
    font-size: 15px;
    font-weight: 600;
    color: var(--text-primary);
  }

  .settings-panel {
    position: fixed;
    top: 62px;
    right: 18px;
    width: 300px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-color);
    border-radius: 12px;
    box-shadow: var(--shadow-md);
    padding: 18px;
    z-index: 200;
    display: none;
  }

  .settings-panel.open {
    display: block;
  }

  .setting-row {
    margin-bottom: 14px;
  }

  .setting-label {
    font-size: 12px;
    font-weight: 600;
    color: var(--text-secondary);
    margin-bottom: 8px;
    display: flex;
    justify-content: space-between;
  }

  .theme-swatches {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 8px;
  }

  .swatch {
    padding: 8px 4px;
    border-radius: 6px;
    border: 2px solid var(--border-color);
    text-align: center;
    font-size: 12px;
    cursor: pointer;
    font-weight: 500;
  }

  .swatch.active {
    border-color: var(--accent-color);
  }

  .search-results-box {
    max-height: 220px;
    overflow-y: auto;
    margin-top: 8px;
    background: var(--bg-elevated);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    display: none;
  }

  .search-hit {
    padding: 8px 10px;
    border-bottom: 1px solid var(--border-color);
    font-size: 12px;
    cursor: pointer;
  }

  .search-hit:hover {
    background: var(--accent-soft);
  }

  .search-hit-chap {
    font-weight: 600;
    color: var(--accent-color);
    margin-bottom: 2px;
  }

  mark {
    background: rgba(235, 180, 40, 0.35);
    color: inherit;
    padding: 0 2px;
    border-radius: 2px;
  }
</style>
</head>
<body data-theme="sepia">

<div id="progress-bar"></div>

<div class="app-shell">
  <header class="topbar">
    <div class="topbar-left">
      <button class="btn" id="btn-toggle-sidebar" title="切換目錄側欄">☰ 目錄</button>
      <span class="chapter-badge" id="current-chapter-title">載入中...</span>
    </div>
    <div class="topbar-right">
      <span class="word-count-pill" id="word-count-display">0 字</span>
      <button class="btn" id="btn-settings" title="字體、主題與版面設定">Aa 閱讀設定</button>
    </div>
  </header>

  <div class="workspace">
    <aside class="sidebar" id="sidebar">
      <div class="sidebar-header">
        <h2 class="book-title">《我不是勇者》</h2>
        <p class="book-subtitle">第一卷：無風迴廊盡頭的少女</p>
        <input type="text" class="search-box" id="global-search" placeholder="🔍 搜尋全卷內文...">
        <div class="search-results-box" id="search-results"></div>
      </div>
      <div class="chapter-list" id="chapter-list"></div>
      <div class="sidebar-footer" id="total-volume-stats"></div>
    </aside>

    <main class="reader-pane" id="reader-pane">
      <div class="reader-paper">
        <article id="reader-article"></article>
      </div>
      <div class="chapter-nav-footer" id="chapter-nav-footer"></div>
    </main>
  </div>
</div>

<div class="settings-panel" id="settings-panel">
  <div class="setting-row">
    <div class="setting-label"><span>閱讀主題</span></div>
    <div class="theme-swatches">
      <div class="swatch active" data-set-theme="sepia" style="background:#f7f3e8; color:#26221e;">文庫紙</div>
      <div class="swatch" data-set-theme="light" style="background:#ffffff; color:#1e2125;">純白</div>
      <div class="swatch" data-set-theme="green" style="background:#e8f0e6; color:#1f2b21;">松綠</div>
      <div class="swatch" data-set-theme="dark" style="background:#1c1f26; color:#d9d6cf;">夜間</div>
    </div>
  </div>

  <div class="setting-row">
    <div class="setting-label"><span>字體風格</span></div>
    <div style="display:flex; gap:6px;">
      <button class="btn" data-set-font="serif" style="flex:1; justify-content:center;">明體 / 宋體</button>
      <button class="btn" data-set-font="sans" style="flex:1; justify-content:center;">黑體</button>
      <button class="btn" data-set-font="kai" style="flex:1; justify-content:center;">楷體</button>
    </div>
  </div>

  <div class="setting-row">
    <div class="setting-label"><span>字級大小</span><span id="lbl-font-size">19px</span></div>
    <input type="range" id="rng-font-size" min="15" max="26" value="19" style="width:100%;">
  </div>

  <div class="setting-row">
    <div class="setting-label"><span>行距寬度</span><span id="lbl-line-height">2.05</span></div>
    <input type="range" id="rng-line-height" min="1.5" max="2.5" step="0.05" value="2.05" style="width:100%;">
  </div>

  <div class="setting-row">
    <div class="setting-label"><span>版面寬度</span></div>
    <div style="display:flex; gap:6px;">
      <button class="btn" data-set-width="640px" style="flex:1; justify-content:center;">窄版</button>
      <button class="btn" data-set-width="760px" style="flex:1; justify-content:center;">標準</button>
      <button class="btn" data-set-width="920px" style="flex:1; justify-content:center;">寬版</button>
    </div>
  </div>

  <div class="setting-row" style="margin-bottom:0;">
    <label style="display:flex; align-items:center; gap:8px; font-size:13px; cursor:pointer;">
      <input type="checkbox" id="chk-indent" checked> 段落首行縮排兩字
    </label>
  </div>
</div>

<script id="chapters-data" type="application/json">
__INITIAL_CHAPTERS_JSON__
</script>

<script>
(() => {
  const chapters = JSON.parse(document.getElementById('chapters-data').textContent);
  let currentIdx = parseInt(localStorage.getItem('readonly_last_chapter') || '0', 10);
  if (isNaN(currentIdx) || currentIdx < 0 || currentIdx >= chapters.length) currentIdx = 0;

  const elSidebar = document.getElementById('sidebar');
  const elChapterList = document.getElementById('chapter-list');
  const elCurrentTitle = document.getElementById('current-chapter-title');
  const elWordCount = document.getElementById('word-count-display');
  const elTotalStats = document.getElementById('total-volume-stats');
  const elArticle = document.getElementById('reader-article');
  const elReaderPane = document.getElementById('reader-pane');
  const elNavFooter = document.getElementById('chapter-nav-footer');
  const elProgressBar = document.getElementById('progress-bar');
  const elSettingsPanel = document.getElementById('settings-panel');

  function countCJK(str) {
    const m = str.match(/[\u4e00-\u9fff]/g);
    return m ? m.length : 0;
  }

  function escapeHtml(s) {
    return s.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
  }

  function getChapterTitle(md, fallbackFilename) {
    const lines = md.split(/\r?\n/);
    for (const line of lines) {
      if (line.startsWith('# ')) {
        const t = line.replace(/^#\s+/, '').trim();
        if (t !== '《我不是勇者》') return t;
      }
    }
    return fallbackFilename.replace(/\.md$/, '');
  }

  function getSections(md) {
    const secs = [];
    const lines = md.split(/\r?\n/);
    lines.forEach((line, idx) => {
      if (line.startsWith('## ')) {
        const title = line.replace(/^##\s+/, '').trim();
        if (!title.startsWith('第一卷')) {
          secs.push({ title, lineIndex: idx });
        }
      }
    });
    return secs;
  }

  function renderMarkdown(md) {
    const lines = md.split(/\r?\n/);
    let html = '';
    lines.forEach((rawLine, lineIdx) => {
      const line = rawLine.trim();
      if (!line) return;
      if (line.startsWith('# ')) {
        const text = escapeHtml(line.replace(/^#\s+/, ''));
        if (text === '《我不是勇者》') return;
        html += `<h1 data-line="${lineIdx}">${text}</h1>`;
      } else if (line.startsWith('## ')) {
        const text = escapeHtml(line.replace(/^##\s+/, ''));
        if (text.startsWith('第一卷')) return;
        html += `<h2 id="sec-line-${lineIdx}" data-line="${lineIdx}">§ ${text}</h2>`;
      } else if (line === '---' || line === '＊　　　＊　　　＊' || line === '* * *') {
        html += `<hr data-line="${lineIdx}">`;
      } else {
        const formatted = escapeHtml(line).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html += `<p data-line="${lineIdx}">${formatted}</p>`;
      }
    });
    return html;
  }

  function renderSidebar() {
    elChapterList.innerHTML = '';
    let totalCJK = 0;
    chapters.forEach((ch, idx) => {
      const cjk = countCJK(ch.content);
      totalCJK += cjk;
      const title = getChapterTitle(ch.content, ch.filename);
      const secs = getSections(ch.content);

      const item = document.createElement('div');
      item.className = 'chapter-item' + (idx === currentIdx ? ' active' : '');
      item.innerHTML = `
        <div class="chapter-item-title">${escapeHtml(title)}</div>
        <div class="chapter-item-meta">
          <span>第 ${idx + 1} 章</span>
          <span>${cjk.toLocaleString()} 字</span>
        </div>
      `;

      if (secs.length > 0) {
        const secWrap = document.createElement('div');
        secWrap.className = 'section-anchors';
        secs.forEach(s => {
          const pill = document.createElement('span');
          pill.className = 'sec-pill';
          pill.textContent = '§ ' + s.title;
          pill.addEventListener('click', (ev) => {
            ev.stopPropagation();
            if (currentIdx !== idx) loadChapter(idx, true);
            const targetEl = document.getElementById('sec-line-' + s.lineIndex);
            if (targetEl) targetEl.scrollIntoView({ behavior: 'smooth', block: 'start' });
          });
          secWrap.appendChild(pill);
        });
        item.appendChild(secWrap);
      }

      item.addEventListener('click', () => {
        loadChapter(idx, true);
        if (window.innerWidth <= 768) elSidebar.classList.add('collapsed');
      });
      elChapterList.appendChild(item);
    });
    elTotalStats.textContent = `全卷共 ${chapters.length} 章 ｜ 總計 ${totalCJK.toLocaleString()} 中文字`;
  }

  function loadChapter(idx, resetScroll = true) {
    currentIdx = idx;
    localStorage.setItem('readonly_last_chapter', String(currentIdx));
    const ch = chapters[currentIdx];
    const title = getChapterTitle(ch.content, ch.filename);
    const cjk = countCJK(ch.content);

    elCurrentTitle.textContent = title;
    elWordCount.textContent = `本章 ${cjk.toLocaleString()} 字`;
    elArticle.innerHTML = renderMarkdown(ch.content);

    Array.from(elChapterList.children).forEach((el, i) => {
      el.classList.toggle('active', i === currentIdx);
    });

    elNavFooter.innerHTML = '';
    if (currentIdx > 0) {
      const prevTitle = getChapterTitle(chapters[currentIdx - 1].content, chapters[currentIdx - 1].filename);
      const prevCard = document.createElement('div');
      prevCard.className = 'nav-card';
      prevCard.innerHTML = `<div class="nav-card-label">← 上一章</div><div class="nav-card-title">${escapeHtml(prevTitle)}</div>`;
      prevCard.onclick = () => loadChapter(currentIdx - 1, true);
      elNavFooter.appendChild(prevCard);
    }
    if (currentIdx < chapters.length - 1) {
      const nextTitle = getChapterTitle(chapters[currentIdx + 1].content, chapters[currentIdx + 1].filename);
      const nextCard = document.createElement('div');
      nextCard.className = 'nav-card';
      nextCard.style.textAlign = 'right';
      nextCard.innerHTML = `<div class="nav-card-label">下一章 →</div><div class="nav-card-title">${escapeHtml(nextTitle)}</div>`;
      nextCard.onclick = () => loadChapter(currentIdx + 1, true);
      elNavFooter.appendChild(nextCard);
    }

    if (resetScroll) elReaderPane.scrollTop = 0;
  }

  document.getElementById('btn-toggle-sidebar').addEventListener('click', () => {
    elSidebar.classList.toggle('collapsed');
  });

  elReaderPane.addEventListener('scroll', () => {
    const maxScroll = elReaderPane.scrollHeight - elReaderPane.clientHeight;
    const pct = maxScroll > 0 ? (elReaderPane.scrollTop / maxScroll) * 100 : 0;
    elProgressBar.style.width = pct.toFixed(1) + '%';
  });

  // Global Search
  const elGlobalSearch = document.getElementById('global-search');
  const elSearchResults = document.getElementById('search-results');
  elGlobalSearch.addEventListener('input', () => {
    const q = elGlobalSearch.value.trim();
    if (!q) {
      elSearchResults.style.display = 'none';
      return;
    }
    elSearchResults.innerHTML = '';
    let hits = 0;
    chapters.forEach((ch, cIdx) => {
      const lines = ch.content.split(/\r?\n/);
      const title = getChapterTitle(ch.content, ch.filename);
      lines.forEach((line, lIdx) => {
        if (line.includes(q) && hits < 50) {
          hits++;
          const div = document.createElement('div');
          div.className = 'search-hit';
          const snippet = escapeHtml(line.length > 60 ? line.slice(0, 60) + '...' : line)
            .replace(new RegExp(escapeHtml(q), 'g'), `<mark>${escapeHtml(q)}</mark>`);
          div.innerHTML = `<div class="search-hit-chap">${escapeHtml(title)}</div><div>${snippet}</div>`;
          div.onclick = () => {
            loadChapter(cIdx, false);
            const targetP = elArticle.querySelector(`[data-line="${lIdx}"]`);
            if (targetP) {
              targetP.scrollIntoView({ behavior: 'smooth', block: 'center' });
              targetP.style.backgroundColor = 'rgba(235, 180, 40, 0.35)';
              setTimeout(() => { targetP.style.backgroundColor = ''; }, 2000);
            }
          };
          elSearchResults.appendChild(div);
        }
      });
    });
    elSearchResults.style.display = hits > 0 ? 'block' : 'none';
  });

  // Settings
  document.getElementById('btn-settings').addEventListener('click', (e) => {
    e.stopPropagation();
    elSettingsPanel.classList.toggle('open');
  });

  document.addEventListener('click', (e) => {
    if (!elSettingsPanel.contains(e.target) && e.target.id !== 'btn-settings') {
      elSettingsPanel.classList.remove('open');
    }
  });

  document.querySelectorAll('[data-set-theme]').forEach(sw => {
    sw.addEventListener('click', () => {
      const t = sw.getAttribute('data-set-theme');
      document.body.setAttribute('data-theme', t);
      document.querySelectorAll('[data-set-theme]').forEach(s => s.classList.toggle('active', s === sw));
    });
  });

  document.querySelectorAll('[data-set-font]').forEach(btn => {
    btn.addEventListener('click', () => {
      const f = btn.getAttribute('data-set-font');
      if (f === 'serif') document.documentElement.style.setProperty('--reader-font', '"Songti TC", "Noto Serif TC", "PMingLiU", "SimSun", serif');
      if (f === 'sans') document.documentElement.style.setProperty('--reader-font', '"Microsoft JhengHei", "PingFang TC", "Noto Sans TC", sans-serif');
      if (f === 'kai') document.documentElement.style.setProperty('--reader-font', '"Kaiti TC", "DFKai-SB", "BiauKai", serif');
    });
  });

  document.getElementById('rng-font-size').addEventListener('input', (e) => {
    const v = e.target.value + 'px';
    document.getElementById('lbl-font-size').textContent = v;
    document.documentElement.style.setProperty('--font-size', v);
  });

  document.getElementById('rng-line-height').addEventListener('input', (e) => {
    const v = e.target.value;
    document.getElementById('lbl-line-height').textContent = v;
    document.documentElement.style.setProperty('--line-height', v);
  });

  document.querySelectorAll('[data-set-width]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.documentElement.style.setProperty('--page-max-width', btn.getAttribute('data-set-width'));
    });
  });

  document.getElementById('chk-indent').addEventListener('change', (e) => {
    document.documentElement.style.setProperty('--para-indent', e.target.checked ? '2em' : '0em');
  });

  renderSidebar();
  loadChapter(currentIdx, true);

  // Real-time auto-update polling when hosted on GitHub Pages / HTTP(S)
  if (location.protocol === 'http:' || location.protocol === 'https:') {
    let currentHash = chapters.map(c => c.content.length + ':' + c.mtime).join('|');
    const toast = document.createElement('div');
    toast.style.cssText = 'position:fixed;bottom:20px;right:20px;background:var(--accent-color);color:#fff;padding:8px 14px;border-radius:999px;font-size:12px;box-shadow:var(--shadow-md);opacity:0;transition:opacity 0.3s ease;pointer-events:none;z-index:9999;';
    toast.textContent = '✨ 已自動同步最新內文';
    document.body.appendChild(toast);

    setInterval(async () => {
      try {
        const res = await fetch('./chapters.json?t=' + Date.now(), { cache: 'no-store' });
        if (!res.ok) return;
        const data = await res.json();
        if (!data || !Array.isArray(data.chapters)) return;
        const newHash = data.chapters.map(c => c.content.length + ':' + c.mtime).join('|');
        if (newHash !== currentHash) {
          currentHash = newHash;
          const savedScroll = elReaderPane.scrollTop;
          chapters.length = 0;
          data.chapters.forEach(c => chapters.push(c));
          if (currentIdx >= chapters.length) currentIdx = chapters.length - 1;
          renderSidebar();
          loadChapter(currentIdx, false);
          elReaderPane.scrollTop = savedScroll;
          toast.style.opacity = '1';
          setTimeout(() => { toast.style.opacity = '0'; }, 3000);
        }
      } catch (_) {}
    }, 15000);
  }
})();
</script>
</body>
</html>
"""

# Reuse the existing HTML_TEMPLATE from before by reading or keeping both
from pathlib import Path


def build_html():
    chapters = load_chapters()
    json_str = json.dumps(chapters, ensure_ascii=False)

    # 1. Build Standalone Read-Only HTML for sharing
    readonly_html = READONLY_HTML_TEMPLATE.replace("__INITIAL_CHAPTERS_JSON__", json_str)
    readonly_path = os.path.join(BASE_DIR, "我不是勇者_第一卷_純閱讀版.html")
    with open(readonly_path, "w", encoding="utf-8") as f:
        f.write(readonly_html)

    # Also copy to G:\ root so it's easy to grab and share
    root_copy = r"G:\我不是勇者_第一卷_純閱讀版.html"
    try:
        shutil.copyfile(readonly_path, root_copy)
    except Exception:
        pass

    # 1b. Build GitHub Pages /docs folder (index.html + chapters.json + .nojekyll)
    docs_dir = os.path.join(BASE_DIR, "docs")
    os.makedirs(docs_dir, exist_ok=True)
    with open(os.path.join(docs_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(readonly_html)
    with open(os.path.join(docs_dir, "chapters.json"), "w", encoding="utf-8") as f:
        json.dump({"updated_at": max((c["mtime"] for c in chapters), default=0), "chapters": chapters}, f, ensure_ascii=False)
    with open(os.path.join(docs_dir, ".nojekyll"), "w", encoding="utf-8") as f:
        f.write("")

    # 2. Update embedded JSON inside reader.html (the sync editor)
    editor_path = os.path.join(BASE_DIR, "reader.html")
    if os.path.exists(editor_path):
        with open(editor_path, "r", encoding="utf-8") as f:
            editor_html = f.read()
        updated_editor_html = re.sub(
            r'(<script id="initial-chapters-data" type="application/json">\s*).*?(\s*</script>)',
            lambda m: m.group(1) + json_str + m.group(2),
            editor_html,
            flags=re.DOTALL,
        )
        with open(editor_path, "w", encoding="utf-8") as f:
            f.write(updated_editor_html)

    print(f"Built read-only HTML: {readonly_path} ({len(readonly_html)} bytes)")
    print(f"Built GitHub Pages docs: {docs_dir}")
    print(f"Updated sync editor HTML: {editor_path}")


if __name__ == "__main__":
    build_html()
