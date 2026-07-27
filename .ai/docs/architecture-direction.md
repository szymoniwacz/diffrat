# Architecture Direction

## Purpose

Describe the intended architecture before implementation starts.

This file should not contain final code decisions too early.
It should describe direction, constraints, and boundaries.

## Recommended sections

### System shape

What kind of system is this?

Examples:

- CLI tool
- web application
- library
- internal automation
- API service

### Main boundaries

What responsibilities should stay separated?

Examples:

- input parsing
- domain logic
- persistence
- external integrations
- reporting
- user interface

### Design principles

Use project-specific principles.

Default principles:

- simple first version
- explicit boundaries
- deterministic core where possible
- small reviewable changes
- documentation stays close to design decisions

### Open questions

List architecture questions that are not decided yet.
