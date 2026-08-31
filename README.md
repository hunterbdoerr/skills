# Agent Orchestration Skills

Reusable [Agent Skills](https://agentskills.io/) for coding agents.

## Available skills

- `build-spec-context`: Investigate an early idea with an engineer and prepare a repository-grounded context packet for specification writing.
- `write-spec`: Research a repository and create, revise, or review an implementation-ready specification.

## Cross-agent layout

The canonical skill source lives in `.agents/skills`. Tool-specific directories contain relative symlinks to the same skill so all agents use one maintained copy.

| Agent | Discovery path |
|---|---|
| Codex | `.agents/skills/<skill-name>` |
| Claude Code | `.claude/skills/<skill-name>` |
| GitHub Copilot | `.github/skills/<skill-name>` |

Start with `$build-spec-context` in Codex or `/build-spec-context` in Claude Code and Copilot when an idea still needs discovery. Then invoke `$write-spec` or `/write-spec` to turn the resulting context packet into a specification. Natural-language requests can also match either skill automatically.
