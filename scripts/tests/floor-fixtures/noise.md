---
type: spec
status: Accepted
---
# Noise fixture — section-scoping + fence-ignoring
## Acceptance Criteria

### Index
| AC | Name |
|---|---|
| AC-1 | first |
### AC-1 — first
Given x
When y
Then z

A fenced example below must be IGNORED (not parsed as real ACs):

```
| AC | Name |
|---|---|
| AC-9 | fenced-example-row |
### AC-9 — fenced example block
[unverified:   ]
```

## Architecture

A table OUTSIDE the Acceptance Criteria section must be IGNORED:

| AC | Name |
|---|---|
| AC-5 | outside-section-row |
