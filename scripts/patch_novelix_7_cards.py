#!/usr/bin/env python3
with open("scripts/generate_4.py", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Real rating and read count in Featured Card
old_featured = """      <div class="flex items-center justify-between text-[10px] text-app-secondary">
        <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
        <span>${formatCompactNum(book.viewCount || 0)} reads</span>
      </div>"""

new_featured = """      <div class="flex items-center justify-between text-[10px] text-app-secondary">
        <span>${(book.avgRating && book.avgRating > 0) ? `★ ${book.avgRating.toFixed(1)}` : 'New'}</span>
        <span>${formatCompactNum(book.viewCount || 0)} reads</span>
      </div>"""

if old_featured in content:
    content = content.replace(old_featured, new_featured, 1)
    print("OK: Replaced hardcoded rating in Featured Card")
else:
    print("WARN: Featured card rating pattern not found")

# 2. Real rating in Standard Book Card
old_card = """      <div class="flex items-center justify-between text-[10px] text-app-secondary pt-1 border-t border-app-border/40">
        <span>★ ${book.avgRating ? book.avgRating.toFixed(1) : '4.8'}</span>
        <span>${formatCompactNum(book.viewCount || 0)}</span>
      </div>"""

new_card = """      <div class="flex items-center justify-between text-[10px] text-app-secondary pt-1 border-t border-app-border/40">
        <span>${(book.avgRating && book.avgRating > 0) ? `★ ${book.avgRating.toFixed(1)}` : 'New'}</span>
        <span>${formatCompactNum(book.viewCount || 0)} reads</span>
      </div>"""

if old_card in content:
    content = content.replace(old_card, new_card, 1)
    print("OK: Replaced hardcoded rating in Standard Book Card")
else:
    print("WARN: Standard card rating pattern not found")

# 3. Direct resume button in Library Continue Reading Card
old_btn = '<button class="btn-primary text-[11px] px-3 py-1.5 flex-shrink-0 font-medium">Resume</button>'
new_btn = '<button onclick="directResumeBook(\'${escapeHtml(item.id)}\', ${item.page || 1}, \'${escapeHtml(item.selectedEditionLanguage || \\\'\\\')}\', event)" class="btn-primary text-[11px] px-3 py-1.5 flex-shrink-0 font-medium">Resume</button>'

if old_btn in content:
    content = content.replace(old_btn, new_btn, 1)
    print("OK: Added directResumeBook to Library Continue Reading Resume button")
else:
    print("WARN: Library Resume button pattern not found")

with open("scripts/generate_4.py", "w", encoding="utf-8") as f:
    f.write(content)

import py_compile
py_compile.compile("scripts/generate_4.py", doraise=True)
print("generate_4.py syntax check OK.")
