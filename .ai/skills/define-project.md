# Skill — Define Project

## Command

`/define-project`

## Purpose

Define or refine the project requirements before implementation starts.

Use this skill to turn a rough, incomplete, or chaotic project description into clear project context for AI-assisted documentation, planning, and implementation.

The user does not need to provide a polished specification.
The skill should organize what is provided, separate facts from assumptions, and ask focused follow-up questions only when something important is unclear.

The goal is to make future AI work grounded in explicit project requirements instead of assumptions.

`/define-project` and `/project-intake` produce the same final project
definition. They differ only in interaction style: `/define-project` organizes
a supplied description and asks only blocking questions, while `/project-intake`
runs an active interview in short rounds. Both fill the same documents,
including `.ai/docs/project-requirements.md`.

## Trigger

Run this skill when the user writes:

`/define-project`

Also use it when the user clearly asks to:

- define a new project
- clarify what the project should do
- gather requirements
- prepare project context for AI implementation
- fill project documentation before coding
- turn a vague project idea into a documented project brief
- organize a messy project description into clear requirements

## Input

Required:

- rough project idea, project name, or chaotic description of what the project should do

Optional:

- target users
- main problem
- desired outcome
- important features
- non-goals
- technical preferences
- constraints
- data inputs and outputs
- integration needs
- quality requirements
- security or privacy requirements
- deployment expectations
- examples of similar projects

## Input handling rule

Accept unstructured input.

The user may provide:

- loose notes
- incomplete thoughts
- mixed Polish and English
- feature ideas without clear priority
- constraints mixed with goals
- examples of similar projects
- things they dislike or want to avoid

Do not reject messy input.

Instead:

1. Extract concrete facts.
2. Group related notes.
3. Separate goals, features, constraints, non-goals, risks, and open questions.
4. Mark uncertain points as assumptions.
5. Ask follow-up questions only for gaps that block useful documentation.
6. Never pretend uncertain requirements are confirmed facts.

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

## Requirement areas

Use `.ai/contracts/project-definition-contract.md` as the canonical list of
decision areas and statuses.

Organize supplied information against those areas. Assign an explicit status
and required metadata to every area in `.ai/docs/project-requirements.md`.
Record assumptions separately from confirmed requirements. Do not duplicate the
full area list here.

## Questioning mode

Ask questions only when the missing information blocks useful documentation.

Prefer grouped questions over a long interrogation.

Ask at most 5 questions at once.
Prioritize questions that affect scope, architecture, data, privacy, or the first usable version.

Start with the smallest useful set only when the user did not already provide the answers:

1. What is the project supposed to do?
2. Who is it for?
3. What problem should it solve?
4. What should be in scope for the first version, including any technology constraints?
5. What should be explicitly out of scope?

If the user already provided enough information, do not ask again.
Use the available information and mark uncertain points as open questions.

## Steps

1. Read the related files.
2. Extract all available project requirements from the user request, even when the input is chaotic.
3. Group extracted information into facts, assumptions, open questions, goals, features, constraints, non-goals, and risks.
4. Identify missing requirements that block useful documentation.
5. Ask concise grouped questions only if needed.
6. Update project identity, problem, goal, users, scope, non-goals, assumptions, and constraints.
7. Update roadmap with a small first phase and later phases.
8. Update glossary with project-specific terms.
9. Fill `.ai/docs/project-requirements.md` with detailed requirements.
10. Fill the project decision status table with an explicit status and required
    metadata for every contract area.
11. Record assumptions in the assumptions section.
12. Record a decision only when the user makes or confirms a meaningful
    product, architecture, or workflow choice.
13. Add open questions where information is still unknown.
14. Stop before implementation and before declaring project readiness.

## Output

- updated project context documents
- updated project requirements document (`.ai/docs/project-requirements.md`)
- explicit decision status for every contract area
- recorded assumptions
- initial roadmap
- known assumptions and open questions
- short summary of what changed
- follow-up questions if required
- recommended next step: complete template customization and the project
  readiness gate in `.ai/onboarding/bootstrap-checklist.md`

## Stop conditions

Stop and ask for clarification only if:

- the project idea is too vague to identify any meaningful problem or user
- there are conflicting project goals
- definition coverage cannot be completed honestly
- a `blocking-question` remains unresolved

Do not write application code as part of this skill.
Do not invent hard requirements that the user did not provide.
Do not declare project readiness before bootstrap checks pass.
Mark uncertain requirements as assumptions or open questions.
