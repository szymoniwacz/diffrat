# Project Vision

## One-sentence vision

Numbat is a local CLI for developers and reviewers that helps assess pull-request
diffs with git context and actionable review guidance.

## Problem

Reviewing diffs is repetitive and easy to get wrong under time pressure. Reviewers
and authors miss risky changes, lack consistent focus areas, and spend time
reconstructing context that git already has (commits, branches, file history).

## Desired outcome

After Numbat exists, a developer or reviewer should be able to run one command
in a repository and get a concise, trustworthy read on what changed, what deserves
attention, and why — without opening a web UI or scanning the entire codebase.

## Non-goals

- Full-project static analysis or architecture scanning
- Hosted review platform or web dashboard
- Automatic merge or approval decisions
- CI integration in the first version
