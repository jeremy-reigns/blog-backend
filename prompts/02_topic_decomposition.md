# 02 – Topic Decomposition & Subtopics

You have global style rules from the previous prompt.

Now you will take a core blog topic and decompose it into the right subtopics to create a logical, satisfying reading experience.

## Inputs

- Main topic or question: {{TOPIC}}
  - Example: “How do I write a great performance review for my team when I'm a new manager and don't have much history with them?”

## Task

1. Identify the key subtopics or questions that must be addressed *before* and *around* the main topic to make the article coherent and trustworthy.
2. For each subtopic:
   - Give a clear, specific subheading.
   - Explain **why** it belongs in this article (a brief critique / justification).
   - Explain how it helps a new manager who has limited history with their team.
3. Order the subtopics to create a natural narrative flow from:
   - Context → constraints → frameworks → practical steps → pitfalls → conclusion.

## Output Format

- A short paragraph that restates {{TOPIC}} in your own words.
- A numbered list of subtopics:
  - `H2/H3 title:`
  - `2–4 sentence critique: why this matters for this topic, what problem it solves, how it supports the main question.`
- A final paragraph summarizing why this structure will feel natural and helpful for the reader.

Use the AI-slop guardrails: avoid generic “understanding X” headings and vague explanations. Be specific and practical.
