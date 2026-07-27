# Skill — Add Idea

## Command

`/add-idea`

## Purpose

Add a new project idea without starting implementation.

Use this skill to capture rough ideas in a structured, reviewable format.

## Trigger

Run this skill when the user writes:

`/add-idea`

Also use it when the user clearly asks to:

- add a new idea
- capture a rough project idea
- save an idea for later
- add something to the project backlog

## Input

Required:

- idea title or rough description

Optional:

- problem
- goal
- motivation
- constraints
- expected outcome
- priority
- known non-goals

## Related files

Read:

- `.ai/conventions/idea-rules.md`
- `.ai/templates/idea.md`
- `.ai/ideas/README.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`

Update:

- `.ai/ideas/README.md`
- one new file in `.ai/ideas/active/`

## Steps

1. Read the related files.
2. Check existing idea files and the idea index for duplicates.
3. If a similar idea exists, update or reference the existing idea instead of creating a duplicate.
4. Find the next available numeric ID.
5. Create a short kebab-case filename using the numeric ID.
6. Create the idea file in `.ai/ideas/active/` using `.ai/templates/idea.md`.
7. Describe the problem before the solution.
8. Fill in goal, scope, non-goals, risks, open questions, and possible next step.
9. Update `.ai/ideas/README.md` with the new idea.
10. Stop before implementation.

## Output

- one new or updated idea file
- updated idea index
- short summary of what changed

## Stop conditions

Stop and ask for clarification only if:

- the idea is impossible to understand
- the target project context is missing
- the idea conflicts with current scope or accepted decisions

Do not write application code as part of this skill.
