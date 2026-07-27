# Skill — Expand Idea

## Command

`/expand-idea`

## Purpose

Turn a rough idea into a plan-ready idea.

Use this skill when an idea already exists but is too vague to become an implementation plan.

## Trigger

Run this skill when the user writes:

`/expand-idea`

Also use it when the user clearly asks to:

- expand an existing idea
- refine an idea
- clarify scope for an idea
- make an idea ready for planning
- split a vague idea into a clearer next step

## Input

Required:

- selected idea file or clear idea reference

Optional:

- extra context from the user
- new constraints
- priority
- target milestone
- known risks

## Related files

Read:

- selected idea file from `.ai/ideas/active/`
- `.ai/conventions/idea-rules.md`
- `.ai/project/product-context.md`
- `.ai/project/scope.md`
- `.ai/project/decisions.md`

Update:

- selected idea file
- `.ai/ideas/README.md`

Move when ready:

- from `.ai/ideas/active/`
- to `.ai/ideas/expanded/`

## Steps

1. Read the selected idea and related context.
2. Clarify the problem statement.
3. Separate the goal from implementation details.
4. Define scope and non-goals.
5. Add risks and open questions.
6. Identify assumptions that need validation.
7. Suggest the smallest useful next step.
8. Move the idea to `.ai/ideas/expanded/` only when it is ready for planning.
9. Update `.ai/ideas/README.md` if status, location, title, or notes changed.
10. Stop before implementation.

## Output

- expanded idea file
- updated idea index when needed
- short summary of what changed
- recommendation for the next command: `/execute-goal` by default, or
  `/plan-small-step` only when the user explicitly wants preparation without
  implementation

## Stop conditions

Stop and ask for clarification only if:

- no target idea can be identified
- multiple ideas match and the target is ambiguous
- the idea conflicts with current scope or accepted decisions

Do not write application code as part of this skill.
