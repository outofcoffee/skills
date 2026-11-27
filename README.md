# Agent Skills

A collection of Agent Skills (per the [agentskills.io specification](https://agentskills.io/specification)) — one skill per folder under `skills/`, each with a `SKILL.md`.

## Install

The happy route is the [`skills` CLI](https://skills.sh), runnable straight from `npx` — no clone or manual setup required:

```sh
# Install every skill in this collection
npx skills add outofcoffee/skills

# Install just one skill
npx skills add outofcoffee/skills --skill docs-update
```

Prefer to work with the files yourself rather than install? Clone the repo and take what you need:

```sh
git clone https://github.com/outofcoffee/skills.git
```

## CI

Every push is linted with [agent-lint](https://github.com/ai-agent-manager/agent-lint) — see [.github/workflows/lint.yml](.github/workflows/lint.yml).

## License

[Apache 2.0](LICENSE)
