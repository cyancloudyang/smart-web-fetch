# Smart-Web-Fetch

**Multi-node Bilingual Search Engine for AI Agents.**

Smart-Web-Fetch is an advanced search skill designed for AI agents (like Claude Code, Gemini CLI, or any LLM with tool-use capabilities). It leverages multiple distributed SearXNG instances and Jina Proxy to provide high-quality, noise-free, and bilingual (ZH/EN) search results.

## Key Features

- **Bilingual Alignment**: Searches in both Chinese and English to capture the best information from global sources.
- **Multi-node Redundancy**: Automatically selects the fastest and most reliable SearXNG nodes.
- **Consensus Ranking**: Ranks results based on hits across different nodes for higher authority.
- **Noiseless Reading**: Integrated with Jina Proxy (`r.jina.ai`) for clean Markdown full-text extraction.
- **Multi-round Escalation**: Supports R1 (Core), R2 (Expand), and R3 (Fallback) query logic with early termination.

## Structure

```text
.
├── scripts/
│   └── searx_pro_engine.py    # The core Python search engine
├── skills/
│   └── smart-web-fetch/
│       └── SKILL.md           # Instructions for AI agents
└── README.md
```

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/cyancloudyang/smart-web-fetch.git
   cd smart-web-fetch
   ```

2. **Dependencies**:
   Requires Python 3.x and the `requests` library.
   ```bash
   pip install requests
   ```

3. **Skill Setup**:
   Copy the `skills/smart-web-fetch` directory to your agent's skill directory (e.g., `~/.agents/skills/` or `~/.claude/skills/`).

## Usage for Humans

You can run the engine directly from the command line:

```bash
python3 scripts/searx_pro_engine.py "关键词" "English Keywords"
```

For multi-round search:
```bash
python3 scripts/searx_pro_engine.py "核心关键词;扩展关键词" "Core Keywords;Expanded Keywords"
```

## Usage for Agents

Once the skill is installed, instruct your agent to:
`activate_skill(name='smart-web-fetch')`

The agent will then follow the operational guide in `SKILL.md` to perform intelligent keyword engineering and execute the search.

## License

MIT
