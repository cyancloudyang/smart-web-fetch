# Smart-Web-Fetch

**Multi-node Bilingual Search Engine for AI Agents.**

[English](#english) | [中文](#中文)

---

<a name="english"></a>
## English

Smart-Web-Fetch is an advanced search skill designed for AI agents (like Claude Code, Gemini CLI, or any LLM with tool-use capabilities). It leverages multiple distributed SearXNG instances and Jina Proxy to provide high-quality, noise-free, and bilingual (ZH/EN) search results.

### Key Features

- **Bilingual Alignment**: Searches in both Chinese and English to capture the best information from global sources.
- **Multi-node Redundancy**: Automatically selects the fastest and most reliable SearXNG nodes.
- **Consensus Ranking**: Ranks results based on hits across different nodes for higher authority.
- **Noiseless Reading**: Integrated with Jina Proxy (`r.jina.ai`) for clean Markdown full-text extraction.
- **Multi-round Escalation**: Supports R1 (Core), R2 (Expand), and R3 (Fallback) query logic with early termination.

### Structure

```text
.
├── scripts/
│   └── searx_pro_engine.py    # The core Python search engine
├── skills/
│   └── smart-web-fetch/
│       └── SKILL.md           # Instructions for AI agents
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/cyancloudyang/smart-web-fetch.git
cd smart-web-fetch
```

2. **Dependencies**: Requires Python 3.x and the `requests` library.
```bash
pip install requests
```

3. **Skill Setup**: Copy the `skills/smart-web-fetch` directory to your agent's skill directory (e.g., `~/.agents/skills/` or `~/.claude/skills/`).

### Usage for Humans

Run the engine directly from the command line:

```bash
python3 scripts/searx_pro_engine.py "关键词" "English Keywords"
```

For multi-round search:
```bash
python3 scripts/searx_pro_engine.py "核心关键词;扩展关键词" "Core Keywords;Expanded Keywords"
```

### Usage for Agents

Once the skill is installed, instruct your agent to:
```
activate_skill(name='smart-web-fetch')
```

The agent will then follow the operational guide in `SKILL.md` to perform intelligent keyword engineering and execute the search.

---

<a name="中文"></a>
## 中文

Smart-Web-Fetch 是一款专为 AI Agent 设计的先进搜索技能。它利用多个分布式 SearXNG 实例和 Jina Proxy，提供高质量、无噪音的双语（中/英）搜索结果。

### 核心特性

- **双语对齐**：同时搜索中英文，获取全球范围内的最佳信息
- **多节点冗余**：自动选择最快、最可靠的 SearXNG 节点
- **共识排名**：基于多节点命中次数排名，结果更权威
- **纯净阅读**：集成 Jina Proxy (`r.jina.ai`)，提取干净的 Markdown 全文
- **多级递进**：支持 R1（核心）、R2（扩展）、R3（回退）查询策略，自动终止

### 项目结构

```text
.
├── scripts/
│   └── searx_pro_engine.py    # Python 核心搜索引擎
├── skills/
│   └── smart-web-fetch/
│       └── SKILL.md           # AI Agent 使用指南
├── .gitignore
├── CHANGELOG.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

### 安装

1. **克隆仓库**：
```bash
git clone https://github.com/cyancloudyang/smart-web-fetch.git
cd smart-web-fetch
```

2. **安装依赖**：需要 Python 3.x 和 `requests` 库
```bash
pip install requests
```

3. **配置 Skill**：将 `skills/smart-web-fetch` 目录复制到你的 Agent skill 目录（如 `~/.agents/skills/` 或 `~/.claude/skills/`）

### 人类使用方法

直接从命令行运行搜索引擎：

```bash
python3 scripts/searx_pro_engine.py "关键词" "English Keywords"
```

多级搜索示例：
```bash
python3 scripts/searx_pro_engine.py "核心关键词;扩展关键词" "Core Keywords;Expanded Keywords"
```

### Agent 使用方法

安装 skill 后，指示你的 Agent：
```
activate_skill(name='smart-web-fetch')
```

Agent 将遵循 `SKILL.md` 中的操作指南，执行智能关键词工程并返回搜索结果。

---

## License / 许可证

MIT
