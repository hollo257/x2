# -*- coding: utf-8 -*-
"""把每张卡分散的多个 ## 🔁 回链 区块合并成一个，去重。"""
import os, re, io

ROOT = r"D:\X2\书籍\经济"
LAYERS = ["L1", "L2", "L3", "L4"]
BACK_RE = re.compile(r"^- \[\[([^\[\]|#]+)\]\]（由 \[\[[^\[\]]+\]\] 引出，自动回补）\s*$")
HEAD = re.compile(r"^## 🔁 回链\s*$")

def process(path):
    with io.open(path, encoding="utf-8") as f:
        lines = f.read().split("\n")
    keep, backs = [], []
    skip_head = False
    for ln in lines:
        if HEAD.match(ln.strip()):
            skip_head = True
            continue
        if skip_head:
            m = BACK_RE.match(ln.strip())
            if m:
                backs.append(m.group(1))
                continue
            elif ln.strip() == "":
                continue
            else:
                skip_head = False
        keep.append(ln)
    backs = list(dict.fromkeys(backs))
    if not backs:
        return 0
    out = [l.rstrip() for l in keep]
    while out and out[-1] == "":
        out.pop()
    out.append("")
    out.append("## 🔁 回链")
    for b in backs:
        out.append(f"- [[{b}]]")
    out.append("")
    with io.open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(out))
    return len(backs)

total = 0
for layer in LAYERS:
    d = os.path.join(ROOT, layer)
    for fn in os.listdir(d):
        if fn.endswith(".md"):
            n = process(os.path.join(d, fn))
            total += n
print(f"合并完成，共整理回链条目 {total} 条")
