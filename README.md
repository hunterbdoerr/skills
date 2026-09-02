# Agent Orchestration Skills

Reusable [Agent Skills](https://agentskills.io/) for coding agents.

## Available skills

- `build-spec-context`: Investigate an early idea with an engineer and prepare a repository-grounded context packet for specification writing.
- `write-spec`: Research a repository and create, revise, or review an implementation-ready specification.
- `implement-spec` (Codex only): Implement a Markdown spec through a user-approved task list and sequential independent review.

## Cross-agent layout

The canonical skill source lives in `.agents/skills`. The portable `build-spec-context` and `write-spec` skills also have relative symlinks in tool-specific directories so supported agents use one maintained copy.

| Agent | Discovery path |
|---|---|
| Codex | `.agents/skills/<skill-name>` |
| Claude Code | `.claude/skills/<skill-name>` |
| GitHub Copilot | `.github/skills/<skill-name>` |

Start with `$build-spec-context` in Codex or `/build-spec-context` in Claude Code and Copilot when an idea still needs discovery. Then invoke `$write-spec` or `/write-spec` to turn the resulting context packet into a specification. Natural-language requests can also match either skill automatically.

`implement-spec` is Codex-only and is discovered directly at `.agents/skills/implement-spec`; it has no Claude Code or GitHub Copilot symlink. It accepts any implementation-ready Markdown spec and uses Codex's current plan and conversation instead of creating repository workflow state.
