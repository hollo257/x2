# -*- coding: utf-8 -*-
"""
米什金货币金融学 Obsidian 知识库核对脚本
1) 收集 L1-L4 全部 .md：basename -> 路径
2) 提取 [[...]] 链接，报告悬空链接（目标不存在）
3) 报告单向链接 A->B 且 B 未回链 A，并自动幂等回补（B 文件末尾追加 🔁 回链区块）
4) 出链数 <3 的文件告警
5) 按 L1-L4 生成 00-总索引.md
"""
import os, re, sys, io

ROOT = r"D:\X2\书籍\经济"
LAYERS = ["L1", "L2", "L3", "L4"]
LINK_RE = re.compile(r"\[\[([^\[\]|#]+)(?:[#|][^\[\]]*)?\]\]")

def collect_files():
    names = {}
    for layer in LAYERS:
        d = os.path.join(ROOT, layer)
        for fn in os.listdir(d):
            if fn.endswith(".md"):
                names[fn[:-3]] = os.path.join(d, fn)
    return names

def read(p):
    with io.open(p, encoding="utf-8") as f:
        return f.read()

def extract_links(text):
    out = []
    for m in LINK_RE.findall(text):
        n = m.strip().rstrip("\\").strip()  # 去掉表格转义残留的反斜杠
        if n:
            out.append(n)
    return out

def main():
    names = collect_files()
    print(f"== 共 {len(names)} 张卡 ==")
    links = {}   # basename -> set(targets)
    for n, p in names.items():
        links[n] = set(extract_links(read(p)))

    # 1) 悬空链接
    dangling = []
    for n, tgts in links.items():
        for t in tgts:
            if t not in names:
                dangling.append((n, t))
    print("\n== 悬空链接 ==")
    for n, t in sorted(dangling):
        print(f"  {n} -> [[{t}]]")

    # 2) 单向链接 + 自动回补
    one_way = []
    fixed = 0
    for n, tgts in links.items():
        for t in tgts:
            if t in names and n not in links[t]:
                one_way.append((n, t))
                # 回补：把 [[n]] 追加到 t 文件
                p = names[t]
                content = read(p)
                if f"[[{n}]]" in content:
                    continue
                block = f"\n## 🔁 回链\n- [[{n}]]（由 [[{t}]] 引出，自动回补）\n"
                with io.open(p, "a", encoding="utf-8") as f:
                    f.write(block)
                fixed += 1
    print(f"\n== 单向链接 {len(one_way)} 条，已自动回补 {fixed} 条 ==")
    for n, t in sorted(one_way):
        print(f"  {n} -> {t}")

    # 3) 出链数 <3
    print("\n== 出链数 <3 的卡 ==")
    for n in sorted(names):
        c = len(links[n])
        if c < 3:
            print(f"  {n}: {c} 个出链")

    # 4) 生成总索引
    layer_titles = {
        "L1": "🧭 L1 入口层（导航与自测）",
        "L2": "📖 L2 章节层（6 篇 25 章）",
        "L3": "💡 L3 概念层（知识库心脏）",
        "L4": "🌍 L4 案例层（真实事件）",
    }
    lines = ["# 📚 《货币金融学》第9版 · 总索引\n",
             "> 🏠 Obsidian 知识库主页 | 主线：金融市场 → 金融机构 → 中央银行 → 国际金融 → 货币理论\n",
             "> 🧠 一句话：金融的核心是跨时空配置资源，货币的核心是信任与预期。\n"]
    for layer in LAYERS:
        lines.append(f"\n## {layer_titles[layer]}\n")
        d = os.path.join(ROOT, layer)
        fns = sorted(f[:-3] for f in os.listdir(d) if f.endswith(".md"))
        for fn in fns:
            lines.append(f"- [[{fn}]]")
    idx_path = os.path.join(ROOT, "00-总索引.md")
    with io.open(idx_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"\n== 总索引已生成: {idx_path} ==")

if __name__ == "__main__":
    main()
