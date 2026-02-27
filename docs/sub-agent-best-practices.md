# Sub-Agent Best Practices

**Last Updated:** 2026-02-26

---

## Model Selection

### For Sub-Agents (sessions_spawn)

**Cost-Effective Option (Default):**
```json
{
  "task": "Your task here",
  "model": "moonshot/kimi-k2.5",
  "runTimeoutSeconds": 3600
}
```

**Cost:** ~$0.004/task (50x cheaper than Opus)

**When to Use:**
- Research tasks
- Data processing
- Content generation
- Parallel work
- Background tasks

**When NOT to Use:**
- Security decisions
- Trading strategy changes
- High-stakes reasoning
- Complex debugging

---

## Common Mistakes

### ❌ Wrong Model String
```json
// DON'T DO THIS
"model": "anthropic/kimi-k2.5"  // Wrong!
"model": "kimi-k2.5"             // Wrong!

// ✅ CORRECT
"model": "moonshot/kimi-k2.5"
```

### ❌ Missing Timeout
```json
// DON'T DO THIS - will use default timeout
{
  "task": "Long running task"
}

// ✅ CORRECT
{
  "task": "Long running task",
  "runTimeoutSeconds": 3600
}
```

---

## Night Shift Lessons Learned

**Feb 26, 2026:**
- Spawned 5 sub-agents with wrong model string
- All failed within 400ms due to Anthropic credit exhaustion
- Had to implement directly instead

**Fix:**
- Use `moonshot/kimi-k2.5` for sub-agents
- Always set appropriate timeout
- Verify model applied in response

---

## Template: Spawn Research Sub-Agent

```javascript
sessions_spawn({
  task: `Research task description here.
  
  Deliverables:
  1. Find X
  2. Document Y
  3. Return Z
  
  Be concise. Save results to file.`,
  agentId: "main",
  label: "research-task-name",
  model: "moonshot/kimi-k2.5",  // ✅ Correct
  runTimeoutSeconds: 3600        // 1 hour
})
```

---

## Template: Spawn Code Sub-Agent

```javascript
sessions_spawn({
  task: `Implement feature X.
  
  Requirements:
  - Use Y library
  - Follow Z pattern
  - Include tests
  
  Save to: path/to/file.py`,
  agentId: "main",
  label: "code-feature-x",
  model: "moonshot/kimi-k2.5",
  runTimeoutSeconds: 1800        // 30 minutes
})
```

---

## Monitoring Sub-Agents

**Check Status:**
```bash
sessions_list | grep <label>
```

**View Results:**
Check session transcript:
```bash
~/.nemo/agents/main/sessions/<session-id>.jsonl
```

---

## Cost Comparison

| Model | Cost/Task | Best For |
|-------|-----------|----------|
| Opus | ~$0.20 | Complex reasoning, security |
| Kimi K2.5 | ~$0.004 | Research, coding, parallel work |
| Nomic Embed | Free | Embeddings, memory |

---

## Related

- MEMORY.md — Model routing guidelines
- night-shift-operations.md — Case study in sub-agent failures
- sessions_spawn documentation
