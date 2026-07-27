# TypeScript Web Stack Profile

Stack-specific guidance for AI-assisted work. Global workflow rules still apply.

## Common structure

```txt
src/
  components/
  pages/ or routes/
  lib/
  hooks/
public/
tests/ or __tests__/
```

Document monorepo or framework-specific layout in `.ai/docs/` if needed.

## Common commands (placeholders)

Replace with project-defined commands:

```bash
npm install
npm run dev
npm test
npm run lint
npm run build
```

Do not invent commands that are not set up in the project.

## Testing expectations

- Unit tests for utilities and hooks
- Component tests for UI behavior changes
- Integration or e2e tests for critical flows when the project uses them

## Documentation expectations

- Update `.ai/docs/` for API contracts and UI behavior
- Note breaking UI changes in the review handoff: a review packet or equivalent
  PR description
- Keep environment variable docs accurate

## AI-specific risks

- Client/server boundary confusion in full-stack apps
- Prop drilling vs state management refactors spanning many files
- CSS or design-token changes with wide visual blast radius
- Accidental exposure of secrets in client bundles
- Dependency upgrades bundled with feature work

## What agents should avoid

- Mass `eslint --fix` outside task scope
- Rewriting state management without explicit task
- Adding heavy dependencies for one-off utilities
- Hardcoding API URLs or keys in frontend code
- Changing build config and feature code in one unreviewable PR

## References

- `.ai/policies/dependency-policy.md`
- `.ai/review/diff-risk-checklist.md`
