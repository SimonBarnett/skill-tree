# skill-tree

MCP service that resolves a **DAG of agent skills** so a seat loads only
the nodes required for a role (MUD-style skill tree), minimising context
while keeping leaf playbooks single-sourced across skill homes.

See `docs/vision.md` and `docs/functional-spec.md`.

## Phase 0 status

Vision pack LOCKED. Resolver/MCP implementation is the first build FR.

## Skill homes (catalog roots)

Configured locally by the operator (clones/paths). Public list includes
gh-Jeeves, agentic_build, agentic_irc, club-madeira-*, skills-visionary,
agentic_fomprep, open-tts, mud-skill, bob-design-uat, skill-dba, irc-skill,
and related SimonBarnett skill books.

## Honesty box

`.grok/skills/harvest-agent-skills` → PRs back to this repo.
