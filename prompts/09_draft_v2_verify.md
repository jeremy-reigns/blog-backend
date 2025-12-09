# 09 – Draft v2: Verification, TL;DR, Citations, Bullets Policy

You now have:
- A solid draft blog on {{TOPIC}}.
- A proposed opening paragraph.
- A source pack and data pack.
- A list of sources used.

Your job is to create a **verified, publication-ready version** of the article.

## Format & Layout

- Place a TL;DR immediately after the H1 and byline.
  - Two sentences + 3–6 short bullets.
- Use full paragraphs as the default throughout.
- Use bullets only when they sharpen focus (scripts, key steps, or checklists).
  - Place bullet clusters mid-section or at the end – not at the start of every subsection.
  - Keep bullet items 1–2 lines each; no nested bullets unless essential.
  - Maintain a non-predictable pattern: some sections have no bullets, some have a small cluster in the middle, some at the end.
- Include smooth transition lines at the end of subsections to guide the reader to the next idea.
- Headings:
  - H1 for title.
  - H2 for major sections.
  - H3/H4 for sub-sections as needed.

## Evidence & Citations

- Every non-obvious claim must be cited inline with (Author, Year) and link to the original source.
- Prefer primary or canonical links (publisher, handbook, PDF) over aggregators.
- Use precise numbers when available; use “~” only for reasonable approximations.
- If you lack a source, either:
  - Reframe as an observation, question, or limited claim, or
  - Remove the claim.

## Style Guardrails (AI-Slop Filter)

- Avoid stock openings like “In today’s world…” or “As technology evolves…”.
- Avoid inflated adjectives (“cutting-edge”, “revolutionary”) unless explicitly justified with data.
- Vary sentence length; prefer active voice and specific verbs.
- Define jargon briefly when first used.
- Use short, relevant examples; no forced metaphors.
- Tone: neutral, clear, professional, developer/manager-centric.

## Inputs You Can Assume

- Source pack and data pack: {{SOURCES_OR_DATA_PACK}}.
- The previous draft blog: {{DRAFT_V1}}.
- Proposed opening paragraph: {{OPENING_PARAGRAPH}}.

If a source is listed in {{SOURCES_OR_DATA_PACK}}, you may cite it. If no source exists for a claim, do not invent one.

## Output

- A single, fully revised markdown article that:
  - Incorporates the new opening.
  - Includes TL;DR as specified.
  - Applies bullets policy correctly.
  - Uses inline citations and links appropriately.
  - Obeys all AI-slop and style guardrails.
