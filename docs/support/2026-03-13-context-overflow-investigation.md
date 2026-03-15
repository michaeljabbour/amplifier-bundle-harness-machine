# Support Note: Session Unresumable Due to Context Overflow

**Date:** 2026-03-13
**Affected session:** `ecefe0d5-8074-4628-84f2-e00158da0944`
**Project:** amplifier-bundle-autoharness
**Reporter:** @michaeljabbour

## Symptom

A 34-turn session in `/execute-plan` mode became permanently unresumable.
Every attempt to send a message returned Anthropic API errors:

```
{"type": "error", "error": {"type": "overloaded_error", "message": "Overloaded"}}
{"type": "error", "error": {"type": "api_error", "message": "Internal server error"}}
```

Simple curl requests to the same API endpoint with the same API key worked fine,
confirming this was not an account or key issue.

## Diagnosis

Initial investigation treated the "overloaded" error as a potential
context-length rejection. Later analysis confirmed that **the "overloaded"
error was genuinely Anthropic being overloaded** — not a disguised
context-length rejection.

However, the session's transcript had independently grown to ~317k tokens
(58% over Claude's 200k context limit), making it unresumable regardless of
API availability. The two issues were co-occurring: genuine API overload made
the failure noisy, while the silently oversized transcript was the reason the
session could never recover.

A further compounding issue was identified: **retry amplification**. The
provider modules already retry failed requests internally, so any retry logic
added at the orchestrator level would multiply retries exponentially during
genuine API outages.

## Root Cause

Four problems compounded to allow the transcript to silently exceed the
context limit:

### 1. Token estimator undercounts by 40-60% (ROOT CAUSE)

`context-simple` uses `len(str(msg)) // 4` to estimate tokens. For tool-heavy
sessions (delegate agent spawns, large JSON tool results, structured output),
the actual token count is 40-60% higher than this estimate.

**File:** `amplifier-module-context-simple/__init__.py:1205-1207`

```python
def _estimate_tokens(self, messages):
    return sum(len(str(msg)) // 4 for msg in messages)
```

### 2. Compaction triggers too late

Compaction triggers at 92% of budget based on the undercount. The session's
transcript was 1.27MB (~317k actual tokens). With a 195k budget:

- `chars/4` estimate: ~200k → compaction fires but doesn't compact enough
- Compaction's internal size checks also use `_estimate_tokens`, so it stops
  compacting when the *estimated* size is below budget, while the *actual*
  size is still 317k

### 3. No pre-send token verification

The orchestrator (`loop-streaming`) passes whatever `get_messages_for_request()`
returns directly to `provider.complete()` with no secondary size check.

### 4. No ContextLengthError recovery

When the API rejects the oversized payload, the orchestrator catches it with a
bare `except Exception` and exits the loop. There is no typed error handling,
no compact-and-retry, and no actionable error message.

```python
except Exception as e:
    logger.error(f"Provider error: {e}")
    yield (f"\nError: {e}", iteration)
    break
```

## Resolution

All fixes were consolidated into the
**[amplifier-bundle-provider-doctor](https://github.com/microsoft/amplifier-bundle-provider-doctor)**
bundle, which addresses the full chain:

- Conservative token estimation
- Earlier compaction triggers
- Typed error handling for `ContextLengthError` and `ProviderUnavailableError`
- Provider error classification
- Awareness of provider-internal retry to avoid retry amplification

Initial PRs against `context-simple`
([#11](https://github.com/microsoft/amplifier-module-context-simple/pull/11))
and `loop-streaming`
([#17](https://github.com/microsoft/amplifier-module-loop-streaming/pull/17))
were closed in favor of this consolidated approach.

## Timeline

- **Session created:** 2026-03-12 23:55 UTC
- **Session became unresumable:** ~2026-03-13 05:00 UTC (after ~34 turns)
- **Diagnosis:** 2026-03-13 15:30 UTC — confirmed transcript at 317k tokens,
  58% over Claude's 200k context limit
- **Root cause identified:** `_estimate_tokens` undercount allowing transcript
  to grow past compaction's effective range
- **Fixes consolidated:** amplifier-bundle-provider-doctor

## Session Recovery

The session was repaired by:
1. Rewinding transcript to line 292 (removing orphaned tool_calls at lines 293-294)
2. The session remains structurally valid but too large to resume (~300k tokens)
3. All work was committed to git before the session became unresumable
4. User started a new session to continue work
