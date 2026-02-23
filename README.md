# Airbyte Claude Skills

Curated [Claude Code skills](https://code.claude.com/docs/en/skills) for document workflows. Built on the [Agent Skills open standard](https://agentskills.io) — compatible with Claude Code, Codex CLI, Gemini CLI, Cursor, and other tools that support the spec.

## Skills

| Skill | Description |
|-------|-------------|
| [`md2gdoc`](./md2gdoc/) | Convert markdown to a styled Google Doc using any template |

## Installation

Copy any skill folder into your Claude Code skills directory:

```bash
# Global (available in all projects)
cp -r md2gdoc ~/.claude/skills/md2gdoc

# Project-scoped (available only in that project)
cp -r md2gdoc .claude/skills/md2gdoc
```

Then invoke with `/md2gdoc` in Claude Code.

## How md2gdoc works

Agents are great at helping build knowledge — spinning up research across multiple repos in parallel, following up with targeted questions, and accumulating findings into structured markdown. But sharing that knowledge through Google Docs meant copy-pasting sections, fixing table borders, reformatting code blocks, and manually fitting content into templates.

`/md2gdoc` converts any markdown file into a professionally styled Google Doc using your company's own template:

1. Provide a Google Doc URL as your template (once — it gets cached)
2. The skill auto-generates a template skeleton from the document's heading structure
3. Your markdown content gets mapped to the template sections via fuzzy heading matching
4. Output: a styled Google Doc with proper table borders, code blocks, heading hierarchy, and spacing

```
/md2gdoc /path/to/my-spec.md
```

### Prerequisites

- `pandoc`: `brew install pandoc`
- `python-docx`: `pip3 install python-docx`
- `rclone` configured with a `gdrive:` remote

See the [SKILL.md](./md2gdoc/SKILL.md) for full details.

## Contributing

Add a new skill by creating a folder with a `SKILL.md` file:

```
your-skill/
  SKILL.md          # Skill definition (required)
  scripts/          # Supporting scripts (optional)
```

See the [Agent Skills spec](https://agentskills.io) for the `SKILL.md` format.
