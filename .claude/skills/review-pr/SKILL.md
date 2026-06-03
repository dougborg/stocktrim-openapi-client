---
name: review-pr
description: Review and address PR feedback using 6-dimensional code review
argument-hint: '[PR number or URL]'
allowed-tools: Bash(gh pr *), Bash(gh api *), Bash(gh repo *), Bash(git status), Bash(git branch *), Bash(git diff *), Bash(git log *), Bash(git show *), Bash(git add *), Bash(git commit *), Bash(git push *), Bash(git pull *), Bash(git rebase *), Bash(git stash *), Bash(git fetch *), Bash(git merge *), Bash(jq *), Bash(.claude/skills/review-pr/*), Bash(.claude/skills/shared/*), Bash(.claude/skills/pr-comments/reply-to-comment.sh*), Read
---

# /review-pr — Structured PR Review

Review a PR using 6 dimensions or address unresolved review feedback systematically.

## PURPOSE

Analyze code changes thoroughly and respond to review comments without missing issues or
duplicating automated findings.

## CRITICAL

- **Rebase on the target branch before fixing — no exceptions** — if the PR shows
  `mergeStateStatus=BEHIND` or `git log HEAD..origin/<base> --oneline` shows anything,
  rebase before reading comments or making code changes. Reasons: (a) comments may be
  obsolete after the base advanced; (b) fixes pushed onto a stale branch trigger CI
  against the still-stale base; (c) auto-merge stays blocked on BEHIND even when CI is
  green and threads are resolved; (d) `fixup-and-push` autosquash collides with
  intervening base commits — this is exactly the PR #203 failure mode, where a
  mid-review force-push hit simplify commits because the rebase step was skipped. Use
  `git rebase origin/<base>` directly, or invoke `/rebase` for conflict resolution +
  `uv.lock` bundling.
- **Same rebase check applies before every `--force-with-lease` after a fixup.**
- **Never dismiss review findings** — Code quality concerns are the entire point of code
  review. Never rationalize skipping them ("not blocking", "acceptable given dataset
  size", "good for future refinement"). Every finding gets fixed, deferred with a
  tracked issue, or explicitly discussed with the reviewer. "CI is green" and "tests
  pass" do not override review feedback. Merging with unaddressed findings is forbidden.
- **Never merge without addressing all comments** — Every comment must be resolved
  (fixed, acknowledged with issue link, or discussed) before merging. No exceptions. If
  you think a finding is wrong, reply explaining why — don't silently skip it.
- **Never duplicate automated findings** — Codecov, linters, type checkers, and CI
  checks already flag style/type/coverage issues. Skip these unless adding important
  context.
- **Explain the "why", not just the "what"** — Comments like "break this into a
  function" are weak. Explain impact: "This reduces complexity from O(n²) to O(n)" or
  "Improves testability by isolating mutation logic."
- **Use the review prompt template** (in DETAIL) for consistency across reviews
- **Reply to EVERY comment — automatically** — Fix → push → reply is ONE atomic
  sequence. Never stop after pushing. The replies are what close the loop for reviewers.
  Nothing left hanging or unaddressed.
- **Fix first, reply after push** — Confirm the fix is live before responding. But never
  stop at "fix pushed" — the replies are mandatory, not a follow-up task.
- **Reply to the correct PR** — When fixes are made in a follow-up PR, reply on THAT
  PR's comments, not the original. When fetching review comments or selecting comment
  IDs (e.g., via `gh pr view` or `gh api repos/{owner}/{repo}/pulls/{number}/comments`),
  always verify the PR number matches the PR you're actually working on. Replying to the
  wrong PR is invisible to reviewers and leaves the actual PR unaddressed.

## ASSUMES

- You have GitHub CLI (`gh`) installed and authenticated
- The PR exists and is accessible to you
- Project has a verification command (test suite, linter, type checker)

## STANDARD PATH

### 1. Identify PR and Mode

```bash
/review-pr [PR#]                    # Or: /review-pr (current branch)
gh pr view <PR#> --json state,reviews
```

- **No review comments** → Mode A: Initial review (analyze with code-reviewer agent)
- **Unresolved comments** → Mode B: Address feedback (fix issues, validate, reply)

### 2. Sync branch with target (mandatory before either mode)

Check out the PR's head branch, then rebase against the latest base. See CRITICAL — this
is not optional:

```bash
head_ref=$(gh pr view <PR#> --json headRefName --jq '.headRefName')
base_ref=$(gh pr view <PR#> --json baseRefName --jq '.baseRefName')
gh pr checkout <PR#>
test "$(git branch --show-current)" = "$head_ref"

git fetch origin "$base_ref"
git log "HEAD..origin/$base_ref" --oneline    # any commits? rebase before doing anything else.
git rebase "origin/$base_ref"
```

If `uv.lock` or other artifacts drift post-rebase, bundle them into the rebased commit
(`git add uv.lock && git commit --amend --no-edit`) and `git push --force-with-lease`.
After the rebase, re-fetch the comment list — some comments may now reference
deleted/moved lines and need to be re-classified.

### 3. Mode A: Initial Review

```bash
gh pr view <PR#> --json title,body,diff
[Invoke code-reviewer agent with PR context]
Organize findings: BLOCKING → SUGGESTION → NITPICK
Post structured review via gh pr review
```

### 4. Mode B: Address Feedback

```bash
[For each unresolved comment]
1. Read affected code
2. Fix or acknowledge
3. Run project verification (test suite, lint, type-check)
4. Re-rebase if base advanced again, then commit, push
5. Reply to EVERY comment in-thread (this step is NOT optional)
```

**Steps 4-5 are atomic.** Never finish at "pushed fixes" — always continue to reply to
every comment before reporting done. See DETAIL: Mode B Workflow.

## EDGE CASES

- [Large PRs with many files] — Read DETAIL: Handling Large PRs (sample files, skip
  boilerplate)
- [Merge conflicts during review] — Read DETAIL: Conflict Resolution (rebase, resolve,
  continue)
- [CI failures blocking review] — Read DETAIL: CI Failures (distinguish code vs.
  infrastructure issues)
- [Review prompt template] — Read DETAIL: Review Prompt Template (consistency guide)
- [Responding to comments] — Read DETAIL: Comment Response Format
  (fix/deferred/already-fixed patterns)

______________________________________________________________________

## DETAIL: Handling Large PRs

For PRs with many changed files or thousands of lines:

1. **Skip boilerplate** — Auto-generated code, vendor updates, large diffs from mass
   refactoring
1. **Sample by category** — Review logic changes, skip formatting-only files
1. **Focus on critical paths** — Auth, payments, data mutation, API contracts first
1. **Ask for split if necessary** — If review is >1 hour, ask author to break into
   smaller PRs

**Example:**

```text
This PR is quite large (47 files, 2500 lines). I've reviewed:
- Core auth changes (critical path)
- Data mutation logic (sampled 5 files for pattern)
- Tests (coverage spot-check)

Blocked on: Vendor update changes (auto-generated, skipping).
Recommendation: For future PRs, split refactors by domain
(auth, API, database) for focused reviews.
```

______________________________________________________________________

## DETAIL: Conflict Resolution

If the PR has merge conflicts, the rebase from STANDARD PATH step 2 will surface them.
Resolve in place:

```bash
# You're already on the PR's head branch from gh pr checkout.
# $base_ref was set in STANDARD PATH step 2 (gh pr view ... --json baseRefName).
git rebase "origin/$base_ref"
# Resolve conflicts in each file (keep our branch's intent integrated with base changes)
git add <resolved-files>
git rebase --continue
git push --force-with-lease origin HEAD:refs/heads/<branch-name>
```

If the conflicts originated from an explicit `git merge` instead (e.g., GitHub's "Update
branch" button created a merge commit on the remote), pull that merge first with
`git pull --no-rebase` and resolve normally.

**Conflicts can invalidate prior comments** — recheck affected sections after resolving.

______________________________________________________________________

## DETAIL: CI Failures

Check CI status before responding to review comments:

```bash
gh pr view {number} --json mergeable,mergeStateStatus
gh pr checks {number}
```

**If code-related** (lint, type, test failure):

1. Fix immediately
1. Run project verification locally
1. Commit, rebase (see CRITICAL — fetch base + rebase before every force-push), push

**If infrastructure-related** (flaky CI, timeout, infrastructure issue):

1. Document in response
1. Don't block on it
1. Link to infrastructure ticket if available

**Always sync the branch and resolve conflicts/build failures before addressing review
comments** — review comments may no longer apply after a rebase + base advance.

______________________________________________________________________

## DETAIL: Review Prompt Template

Use this structure for consistent, thorough reviews (avoid repeating automated
findings):

```markdown
# Review: [PR Title]

## What This Changes

[1-2 sentences summarizing the change and its impact]

## 6-Dimensional Analysis

### Correctness
- [Semantic correctness, type safety, logic]
- [Any potential bugs or edge cases]

### Design
- [Architecture, interfaces, patterns vs. project conventions]
- [Trade-offs and alternatives considered?]

### Readability
- [Naming clarity, documentation, code flow]
- [Any confusing sections?]

### Performance
- [Efficiency, algorithms, resource usage]
- [Any obvious optimizations possible?]

### Testing
- [Test coverage for new code]
- [Edge cases and error conditions covered?]

### Security
- [Input validation, auth, secrets, injection risks]
- [Any exposed internals or vulnerabilities?]

## Findings

### BLOCKING (must fix before merge)
[Only items that break functionality or violate critical constraints]

### SUGGESTION (worth addressing)
[Improvements that enhance quality, maintainability, or safety]

### NITPICK (nice-to-have)
[Style, naming, minor clarity suggestions]

### What Looks Good
[Highlight strong aspects: good patterns, clever solutions, solid testing]

## Summary
- Verdict: Approved / Changes requested / Comment
- Ready to merge after addressing blocking items
```

______________________________________________________________________

## DETAIL: Comment Response Format

Reply to each comment with one of these patterns:

### Fix Implemented

```text
Fixed — [describe what changed].
[If tests added: Also added tests for X].
```

### Already Fixed in Prior Commit

```text
This was addressed in [commit hash] — [brief explanation].
```

### Acknowledged but Deferred

```text
Acknowledged — [reason for deferral].
Tracked in #NNN [link to GitHub issue].
```

### Cannot Reproduce or Misunderstanding

```text
I wasn't able to reproduce this. Can you clarify [specific question]?
```

______________________________________________________________________

## DETAIL: Mode A Workflow

Initial PR review (no comments yet).

### 1. Fetch PR Context

```bash
ctx=$(.claude/skills/shared/resolve-github-context.sh <PR#>)
owner_repo=$(echo "$ctx" | jq -r '"\(.owner)/\(.repo)"')
.claude/skills/shared/fetch-pr-context.sh "$owner_repo" <PR#>
```

### 2. Invoke code-reviewer Agent

Pass compiled context:

```text
PR Title: [title]
Author: [author]
Description: [body]
Labels: [labels]
Diff: [patch]
Existing Comments: [any automated reviewer comments]
```

Agent returns: 6D analysis + findings organized by severity.

### 3. Present Findings

```text
BLOCKING: [list items that must be fixed]
SUGGESTION: [list improvements]
NITPICK: [list nice-to-haves]
What Looks Good: [highlight strengths]
```

### 4. Post Review

```bash
gh pr review <PR#> --approve    # or --request-changes / --comment
```

______________________________________________________________________

## DETAIL: Mode B Workflow

Address unresolved review feedback.

### 1. Sync branch first

See STANDARD PATH step 2 — `gh pr checkout`, fetch base, rebase. This is **mandatory**
and must happen before fetching comments (some may become obsolete after the rebase).

### 2. Fetch Unresolved Comments

```bash
ctx=$(.claude/skills/shared/resolve-github-context.sh {number})
owner_repo=$(echo "$ctx" | jq -r '"\(.owner)/\(.repo)"')
.claude/skills/review-pr/fetch-unresolved-comments.sh "$owner_repo" {number}
```

Returns JSON array of unresolved comments with id, path, line, body, author. Resolved
threads are already filtered out.

### 3. Triage Each Comment

Read affected code. Classify:

- **fix needed** — code change required
- **already fixed** — issue addressed in prior commit
- **acknowledge** — valid point but deferring (must file GitHub issue)

### 4. Fix All Issues

Make code changes. Validate:

```bash
cmd=$(.claude/skills/shared/discover-verification-cmd.sh)
eval "$cmd"   # ALL must pass
```

### 5. Re-rebase if base advanced, then Commit and Push

**Before every force-push, re-check the base** (see CRITICAL — autosquash conflicts with
stale branches are the exact PR #203 failure mode):

```bash
# $base_ref was set in STANDARD PATH step 2; re-fetch if it's not in scope.
git fetch origin "$base_ref"
git log "HEAD..origin/$base_ref" --oneline    # any commits? rebase first.
git rebase "origin/$base_ref"                  # only if commits appeared
```

Then use the fixup-and-push script (stages, creates fixup commit, autosquash rebases,
force-pushes):

```bash
.claude/skills/review-pr/fixup-and-push.sh "$base_ref" "original commit subject" <file1> <file2> ...
```

### 6. Reply to Each Comment (After Push)

**Verify the PR number first** — confirm you're replying on the correct PR (e.g., via
`gh pr view` or the web UI). If fixes were made in a follow-up PR, reply on that PR, not
the original.

Use the reply script — it validates the comment belongs to the correct PR before
posting:

```bash
.claude/skills/pr-comments/reply-to-comment.sh {owner}/{repo} {number} {comment_id} 'Fixed — [explanation]'
```

**Never reply before pushing** — replies confirm fix is live.

### 7. Resolve Review Threads

After replying to all comments, resolve all review threads to clear the "changes
requested" status:

```bash
resolved=$(.claude/skills/shared/resolve-all-threads.sh {owner}/{repo} {number})
echo "Resolved $resolved review threads"
```

### 8. Summary

Print results:

- Fixed: X comments
- Acknowledged: Y comments
- Already fixed: Z comments
- Threads resolved: X
- Validation: PASSED/FAILED
- Any unaddressed items

______________________________________________________________________

## IMPORTANT RULES

- **Rebase before every force-push** — Stale branches cause autosquash conflicts, BEHIND
  status, and obsolete comments. See CRITICAL.
- **Never dismiss findings** — Every review finding gets fixed or deferred with an
  issue. Never rationalize merging with unaddressed comments.
- **Never merge with open comments** — All comments resolved before merge. No
  exceptions.
- **Never duplicate automated findings** — Linters, type checkers, CI checks already
  flag these
- **Explain the why** — Don't just say "improve this", explain impact (perf, complexity,
  testability)
- **Reply to every comment — automatically** — Push + reply is atomic. Never stop at
  "pushed". Nothing left hanging.
- **Fix first, reply after** — Push must complete before replying. But replying is
  mandatory, not a separate task.
- **Clean history** — Use fixup + autosquash, no "address review" commits
- **No shortcuts** — Never use `--no-verify`, `# noqa`, `type: ignore`
- **Deferred work needs issues** — Acknowledged items must link to `gh issue create`
  ticket
- **Stage specific files** — Never `git add -A` or `git add .`
- **Use HEREDOC** — Pass commit messages via HEREDOC (not inline)

______________________________________________________________________

## RELATED

> Some of the skills below come from the
> [harness-kit](https://github.com/dougborg/harness-kit) plugin at runtime (e.g.
> `/rebase`); others (`/code-reviewer`, `/pr-comments`, `/commit`) have local overlays
> in `.claude/skills/` that extend or specialize the upstream version. When both exist,
> the local overlay wins.

- `/rebase` — Canonical conflict-resolution wrapper with `uv.lock` bundling
  (harness-kit)
- `/code-reviewer` — 6-dimensional review reference — local overlay
- `/pr-comments` — Systematic reply workflow (alternative to this skill's Mode B) —
  local overlay
- `/commit` — Quality-gated conventional commits — local overlay
- `code-reviewer` agent — Automated 6D analysis (spawned by this skill)
