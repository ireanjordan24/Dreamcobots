# DreamCo Prompt Engineering Mastery

## Why Prompt Engineering Matters
The quality of AI outputs is directly proportional to the quality of prompts.
Mastering prompt engineering multiplies the effectiveness of every DreamCo bot.

---

## Foundational Techniques

### 1. Role Assignment
```
System: You are a DreamCo Revenue Analyst with 10 years of experience in SaaS.
User: Analyze this month's bot revenue data and identify top performers.
```

### 2. Chain-of-Thought (CoT)
```
Think step by step:
1. First, identify the problem
2. List possible solutions
3. Evaluate each solution
4. Recommend the best option with justification
```

### 3. Few-Shot Examples
```
Classify these integration statuses:
- "Plugin deployed successfully" → success
- "Connection timeout after 30s" → failure
- "API key invalid" → failure
- "Webhook received 200 OK" → [classify this]
```

### 4. Output Structuring
```
Return your response as JSON with these fields:
{
  "status": "success|failure|warning",
  "summary": "one sentence",
  "recommendations": ["item1", "item2"],
  "confidence": 0.0-1.0
}
```

---

## DreamCo Bot-Specific Templates

### Lead Generation Prompt
```
You are a DreamCo lead generation specialist.
Find {n} potential leads for {business_type} in {location}.
For each lead, provide: company name, contact method, estimated budget tier.
Filter: Only include businesses with 10-500 employees.
```

### Revenue Optimization Prompt
```
Given these bot performance metrics: {metrics}
Identify which bots are underperforming and suggest:
1. Configuration changes
2. Tier upgrade recommendations
3. New revenue opportunities
Format as a prioritized action list.
```

### Code Review Prompt
```
Review this DreamCo bot code for:
- GLOBAL AI SOURCES FLOW compliance
- Security vulnerabilities
- Performance bottlenecks
- Missing error handling
Code: {code}
Return: Issues list with severity (critical/high/medium/low) and fix suggestions.
```

---

## Advanced Patterns

### ReAct (Reasoning + Acting)
Useful for multi-step bot workflows where the AI reasons about what to do next.

### Constitutional AI
Build guardrails into system prompts to ensure outputs stay within policy boundaries.

### Prompt Chaining
Break complex tasks into sequential prompts where each output feeds the next.

---

## Common Mistakes & Fixes

| Mistake | Fix |
|---------|-----|
| Over-long prompts | Use message history instead of stuffing context |
| No output format spec | Always specify JSON/markdown/list |
| Missing constraints | Add "Do NOT..." clauses explicitly |
| Ambiguous instructions | Test with adversarial inputs |

_See also: [Policies/prompt_guidelines.md](../Policies/prompt_guidelines.md)_
