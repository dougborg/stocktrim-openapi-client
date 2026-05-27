#!/usr/bin/env bash
# Fetch unresolved review comments for a PR.
#
# Usage: fetch-unresolved-comments.sh <owner/repo> <pr-number>
# Output: JSON array of unresolved comments with id, path, line, body, author
#
# Uses GraphQL to get resolved status, then filters to unresolved only.

set -euo pipefail

if [ $# -lt 2 ]; then
  echo "Usage: $0 <owner/repo> <pr-number>" >&2
  exit 1
fi

REPO="$1"
PR_NUMBER="$2"
OWNER="${REPO%%/*}"
REPO_NAME="${REPO##*/}"

read -r -d '' query <<'GRAPHQL' || true
  query($owner: String!, $repo: String!, $number: Int!) {
    repository(owner: $owner, name: $repo) {
      pullRequest(number: $number) {
        reviewThreads(first: 100) {
          nodes {
            isResolved
            comments(first: 100) {
              nodes {
                id
                databaseId
                body
                path
                line
                author { login }
              }
            }
          }
        }
      }
    }
  }
GRAPHQL
# For each unresolved thread, surface the LATEST comment. A thread can
# accumulate multiple comments (reviewer's original + author's reply +
# reviewer's follow-up); picking `[0]` would return the original request
# even after newer activity, missing follow-up asks. `[-1]` gives the
# most recent ask, which is what the "reply to every comment" workflow
# actually needs. The reply itself attaches to the thread regardless of
# which comment ID is used as the anchor.
gh api graphql -f query="$query" \
  -F "owner=$OWNER" -F "repo=$REPO_NAME" -F "number=$PR_NUMBER" \
  --jq '[
    .data.repository.pullRequest.reviewThreads.nodes[]
    | select(.isResolved | not)
    | .comments.nodes[-1]
    | {id: .databaseId, path: .path, line: .line, body: .body, author: .author.login}
  ]'
