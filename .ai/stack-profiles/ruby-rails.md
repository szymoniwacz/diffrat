# Ruby / Rails Stack Profile

Stack-specific guidance for AI-assisted work. Global workflow rules still apply.

## Common structure

```txt
app/
  models/
  controllers/
  jobs/
  services/
config/
db/
spec/ or test/
```

Document project-specific layout in `.ai/docs/` if it differs.

## Common commands (placeholders)

Replace with project-defined commands:

```bash
bundle install
bin/rails db:migrate
bin/rails test
bundle exec rspec
bin/rubocop
```

Do not invent commands that are not set up in the project.

## Testing expectations

- Model and service specs for changed behavior
- Request/feature specs for HTTP surface changes
- Job specs for async behavior changes

## Documentation expectations

- Update `.ai/project/scope.md` when features change boundaries
- Record migrations and auth changes in decisions or ADRs
- Keep API or domain notes in `.ai/docs/`

## AI-specific risks

### Migrations

- Follow `.ai/policies/dangerous-actions.md` as the canonical owner for migration controls
- A non-destructive migration required by an already authorized feature may be created or modified autonomously on a branch
- Explicit approval and a rollback plan are required for destructive or irreversible migrations, data-loss risk, material data-model decisions not already approved, and applying migrations to shared, staging, or production environments
- Existing project-defined migrations may be run locally or in tests when required by the authorized task

### Background jobs

- Idempotency and retry behavior need explicit review
- Avoid heavy work in callbacks; prefer jobs or services

### Security / auth

- Treat auth, CSRF, and mass-assignment changes as high risk
- Require human review before merge

### Callbacks

- Avoid adding callbacks that hide side effects
- Prefer explicit service calls for complex flows

### Service objects

- Keep services focused; one responsibility per class
- Do not create service layers without project convention

### Test coverage

- Do not delete tests to make CI pass
- Add regression tests for bugfixes

## What agents should avoid

- Broad `rubocop -A` on unrelated files
- Generator output across many modules in one task
- Changing `config/credentials` or secrets
- Production data in development scripts
- Silent schema changes without migration review

## References

- `.ai/workflows/bugfix.md`
- `.ai/policies/security-policy.md`
