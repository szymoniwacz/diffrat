# Skill — Project Intake

## Command

`/project-intake`

## Purpose

Guide the user through questions needed to define a new project before implementation starts.

Use this skill when the user wants one prompt-driven flow that gathers everything needed to fill project context and documentation files.

This skill is different from `/define-project`:

| Skill | Purpose |
|---|---|
| `/define-project` | Organize an existing rough project description. |
| `/project-intake` | Actively interview the user and gather missing requirements step by step. |

## Trigger

Run this skill when the user writes:

`/project-intake`

Also use it when the user asks to:

- define everything about a new project through questions
- be interviewed about project requirements
- fill all AI project context files
- prepare documentation before implementation
- create a complete project brief from scratch

## Input

Required:

- project idea, even if rough

Optional:

- project name
- preferred technology stack
- similar projects
- known constraints
- things to avoid

## Related files

Read:

- `.ai/README.md`
- `.ai/project/vision.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/roadmap.md`
- `.ai/project/glossary.md`
- `.ai/project/decisions.md`
- `.ai/docs/project-requirements.md`
- `.ai/contracts/project-definition-contract.md`
- `.ai/conventions/ai-working-mode.md`
- `.ai/conventions/documentation-rules.md`

Update:

- `.ai/project/vision.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/roadmap.md`
- `.ai/project/glossary.md`
- `.ai/docs/project-requirements.md`
- `.ai/project/decisions.md` only when a meaningful decision is made

## Intake areas

Use `.ai/contracts/project-definition-contract.md` as the canonical list of
decision areas and statuses.

During intake:

1. gather enough information to fill project context and requirements,
2. assign an explicit status and required metadata to every contract area in
   `.ai/docs/project-requirements.md`,
3. record assumptions separately from confirmed requirements,
4. record confirmed meaningful choices in `.ai/project/decisions.md` when
   appropriate.

Do not duplicate the full decision-area list here. The contract owns the
areas, statuses, and gates; this skill owns the interview procedure.

## Question strategy

Do not ask all questions at once.

Ask questions in short rounds.
Each round should have at most 5 questions.

After each round:

1. Summarize what is already known.
2. List assumptions separately.
3. List open questions separately.
4. Ask the next most important questions.

Prioritize questions in this order:

1. purpose and problem
2. users and workflows
3. first useful version
4. scope and non-goals
5. inputs and outputs
6. constraints and technical direction
7. quality, security, and privacy
8. risks and roadmap

## First question round

When starting from a rough project idea, ask:

1. What should this project do in one or two sentences?
2. Who is the main user?
3. What problem or repeated pain should it solve?
4. What should the first useful version include?
5. What should be explicitly out of scope for now?

If the user already answered some of these, do not ask them again.
Ask the next missing questions instead.

## Completion rule

Definition coverage is complete when the assistant can fill these files with
useful, honest content:

- `.ai/project/vision.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/roadmap.md`
- `.ai/project/glossary.md`
- `.ai/docs/project-requirements.md`

and when:

- every contract area has an explicit status with required metadata,
- assumptions are recorded separately from confirmed requirements,
- no area remains implicitly unset.

Definition coverage does not mean the project is ready for product
implementation. Project readiness is a separate gate in
`.ai/onboarding/bootstrap-checklist.md`.

Do not recommend product implementation until project readiness passes.

## Steps

1. Read the related files.
2. Extract any requirements already provided by the user.
3. Ask the first missing question round.
4. After the user answers, update the known facts, assumptions, and open questions.
5. Continue with short question rounds until the minimum useful context is known.
6. Fill `.ai/project/*` files with stable project context.
7. Fill `.ai/docs/project-requirements.md` with detailed requirements.
8. Fill the project decision status table with an explicit status and required
   metadata for every contract area.
9. Record assumptions in the assumptions section.
10. Record decisions only when the user confirms meaningful choices.
11. Stop before implementation and before declaring project readiness.

## Output

During intake:

- short summary of known facts
- assumptions
- open questions
- next question round

After intake:

- updated project context files
- updated project requirements document
- explicit decision status for every contract area
- recorded assumptions
- explicit scope and non-goals
- first useful version
- risks and open questions
- recommended next step: complete template customization and the project
  readiness gate in `.ai/onboarding/bootstrap-checklist.md`

## Stop conditions

Stop and ask for clarification if:

- the project purpose cannot be identified
- the user gives conflicting goals
- the first useful version cannot be separated from later ideas
- definition coverage cannot be completed honestly
- a `blocking-question` remains unresolved

Do not write application code as part of this skill.
Do not invent confirmed requirements.
Do not declare project readiness before bootstrap checks pass.
Mark uncertain details as assumptions or open questions.
