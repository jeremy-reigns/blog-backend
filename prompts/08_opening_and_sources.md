# 08 – Opening Clause & Source List

You already have a draft blog post on {{TOPIC}} and a set of sources.

Now you will:

1. Refine the **opening clause/paragraph**.
2. Produce a clean list of all sources used.

## Inputs

- {{DRAFT_BLOG}} – the current draft markdown.
- {{OPENING_SAMPLES}} – a set of 2–4 opening paragraphs from other blogs that the user likes.
- {{SOURCE_PACK_AND_DATA_PACK}} – list of sources and stats you’ve used or referenced.

## Task

### A. Opening Clause

- Study {{OPENING_SAMPLES}} to infer:
  - How they hook the reader (story, tension, question, data).
  - Their sentence length, specificity, and tone.
- Write **one** opening paragraph for our {{TOPIC}} that:
  - Feels compatible with those samples but not derivative.
  - Hooks the reader with something concrete (a scenario, question, or tension).
  - Is specific to a new manager with little performance history (for this topic).
  - Avoids AI-slop patterns and generic setup lines.

Return this opening as markdown, ready to replace the first paragraph under the H1.

### B. Source List

- Scan {{DRAFT_BLOG}} and {{SOURCE_PACK_AND_DATA_PACK}}.
- Produce a list of sources actually used in the draft (not everything in the pack).
- For each source:
  - Provide: Author/Org, Title, Year (if known), URL.
  - Add a 1–2 sentence note on what support it provided (framework, stat, case study, etc.).

## Output Format

1. Section: “Proposed Opening Paragraph” with the new opening in markdown.
2. Section: “Sources Used in Draft” with a numbered list of sources as described above.
