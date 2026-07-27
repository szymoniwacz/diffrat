# Stack Profiles

## Purpose

Stack profiles provide technology-specific guidance without polluting global workflow rules in `.ai/conventions/` or tool adapters.

## Selecting active profiles

During bootstrap:

1. Select one or more active stack profiles for the project.
2. Record the selection in `.ai/docs/project-requirements.md`.
3. Read the selected profile(s) before AI-assisted implementation.
4. Treat unselected profiles as reusable examples, not active project rules.
5. Add project-specific commands to the selected profile or a project doc—do not invent global commands here.
6. Do not delete unused profiles automatically.

## Available profiles

| Profile | Use when |
|---|---|
| [ruby-rails.md](ruby-rails.md) | Ruby or Rails application |
| [typescript-web.md](typescript-web.md) | TypeScript web frontend or full-stack JS |
| [python-cli.md](python-cli.md) | Python CLI or library project |

## Relationship to global workflow

| Layer | Owns |
|---|---|
| `.ai/docs/template-flow.md` | Universal flow |
| `.ai/quality/quality-gates.md` | Universal gates |
| Stack profiles | Stack-specific structure, commands, risks |

## Rule

If guidance applies to all projects, it belongs in `.ai/conventions/` or `.ai/policies/`—not in a stack profile.
