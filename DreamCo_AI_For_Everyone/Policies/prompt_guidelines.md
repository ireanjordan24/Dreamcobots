# DreamCo Prompt Engineering Guidelines

## Golden Rules
1. **Be specific**: Vague prompts produce vague results. Include context, constraints, and format.
2. **Set the role**: Start prompts with a role assignment — "You are a DreamCo revenue analyst..."
3. **Provide examples**: Few-shot examples dramatically improve output quality.
4. **Define output format**: Request JSON, markdown, bullet points, or structured tables as needed.
5. **Iterate**: Treat prompt engineering as a feedback loop, not a one-shot process.

## Standard Prompt Templates

### Bot Task Prompt
```
You are a DreamCo {bot_name} bot. Your task is to {task_description}.

Context:
- Platform: {platform}
- Tier: {tier}
- Data: {data}

Output format: {format}

Constraints:
- {constraint_1}
- {constraint_2}
```

### Research & Analysis Prompt
```
Analyze the following {topic} data and provide:
1. Key insights (3-5 bullet points)
2. Actionable recommendations
3. Risk factors to monitor

Data: {data}

Format: Structured markdown with headers.
```

### Code Generation Prompt
```
Write a Python function that {description}.

Requirements:
- Follow PEP 8 style
- Include type hints
- Add a docstring
- Handle edge cases: {edge_cases}
- Do NOT use: {excluded_libraries}
```

## Anti-Patterns to Avoid
- ❌ "Write me a bot" (too vague)
- ❌ Injecting raw user input into prompts (security risk)
- ❌ Asking for opinions on sensitive topics in production bots
- ❌ Using prompts that could produce PII in outputs

## Prompt Security
- Sanitize all user inputs before embedding in prompts
- Use system-level instructions to prevent prompt injection
- Log prompt templates (not user data) for audit purposes
- Never include secrets, keys, or credentials in prompts

_Last updated: 2025_
