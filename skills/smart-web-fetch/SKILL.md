---
name: smart-web-fetch
version: 4
description: '[INSTRUCTIONAL] Multi-node Bilingual Search. READ ONLY. Do NOT call as a function.'
---

# Smart-Web-Fetch: Agent Operational Guide

**WARNING**: This is an **INSTRUCTIONAL SKILL**, not a TOOL.
- ❌ DO NOT call `<smart-web-fetch>` as a tool name.
- ✅ ALWAYS use `activate_skill(name='smart-web-fetch')` first to read these instructions.

## Workflow

### 1. Intelligence — Keyword Engineering

**NEVER copy-paste raw user text into queries.** Apply 3-step transformation:

#### 1.1 Query Decomposition
Split the user's question into 2-3 independent information dimensions. Each dimension targets a different aspect (e.g., definition, market data, comparison, technical specs).

#### 1.2 Searchability Filter
Remove terms SearX cannot reach:
- Platform-exclusive brands (Taobao/Xiaohongshu/Douyin shops, WeChat accounts)
- Social buzzwords (网红, 种草, 打卡, 出片)
- Login/paywalled content (CNKI full-text, member areas)

Convert to searchable equivalents:
- Platform brand → category/industry term
- Colloquial description → standard terminology
- Add bilingual synonyms for each dimension

#### 1.3 Keyword Grouping
Generate up to 3 ranked groups for both ZH and EN. Semicolon `;` separated.

| Group | Purpose | Example (consumer electronics) |
|-------|---------|-------------------------------|
| **R1** Core | Most precise, highest expected hit rate | `"iPhone vs Samsung benchmark"` |
| **R2** Expand | Adjacent domains, alternative terms | `"smartphone camera comparison review"` |
| **R3** Fallback | Broader industry/category terms | `"mobile phone market share 2024"` |

- If R1 is likely sufficient (simple factual query), R2/R3 can be empty.
- Keep each group concise: 3-6 keywords, no filler words.

### 2. Execution

```bash
# Path should be adapted to the local installation directory
python3 scripts/searx_pro_engine.py "<ZH_R1>;<ZH_R2>;<ZH_R3>" "<EN_R1>;<EN_R2>;<EN_R3>"
```

- Semicolons separate rounds. Unused rounds can be omitted (backward compatible).
- Groups are searched in order; later rounds auto-skip if enough results found.

### 3. Processing

The script returns a JSON list of consensus-ranked results (up to 15).
- **hits**: Number of nodes that found this link (higher = more authoritative).
- **jina_url**: Jina-proxy link for full-text Markdown extraction.
- Pre-filtered for noise (error pages, SearX internal links, static resources, off-topic hits).

**Known limitation**: SearX cannot index Chinese social platforms (Xiaohongshu, WeChat, Douyin, Taobao). Acknowledge this explicitly when relevant.

### 4. Verification

Select top 3-8 results by `hits`/`score`, fetch their `jina_url` for deep reading, then synthesize the final answer.
