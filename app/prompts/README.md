# Prompt And Platform Behavior

This folder contains the prompt-construction logic for the workflow.

The prompt layer is separated from the graph and route layers so that content behavior can evolve without changing transport or orchestration code.

## What Lives Here

### `agent_prompts.py`

Builds the core prompt instructions for:

- planner
- writer
- judge
- editor

These prompts define what each stage is supposed to do, what counts as a valid result, and how the model should structure its output.

### `platform_prompts.py`

Defines platform-specific guidance used by the editor.

Current supported platform styles include:

- `linkedin` — professional, insight-driven, business-focused
- `instagram` — visual, concise, engagement-oriented
- `facebook` — community-driven, conversational, story-focused
- `x` — short, sharp, high-signal, time-sensitive
- `tiktok` — casual, trendy, format-aware (short-form video)
- `blog` — long-form, detailed, SEO-friendly, comprehensive
- `newsletter` — narrative-driven, personable, narrative arc
- `speech` — oral delivery, pacing, speaker notes
- `copy` — general copywriting, headlines, persuasive

It also normalizes aliases such as:

- `twitter` → `x`
- `x/twitter` → `x`
- `tik tok` → `tiktok`

### `persona_prompts.py`

Defines reusable persona guidance used by the editor.

Current supported personas include:

- `professional` — formal, business-appropriate, industry-standard
- `casual` — friendly, conversational, approachable
- `educational` — informative, clear, explanation-focused
- `energetic` — enthusiastic, motivational, action-oriented
- `thoughtful` — reflective, nuanced, deep-dive oriented
- `witty` — clever, humor-driven, entertaining

The persona layer can also accept a user-defined custom persona instruction through the API request model. That custom persona is injected into the editor prompt without changing the built-in persona catalog.

### `system_prompt.py`

Holds shared system-level context used across stages.

## How Prompting Fits Into The Workflow

At a high level:

1. the planner prompt asks for distinct angles based on the user request
2. the writer prompt asks for a structured source draft for each angle
3. the judge prompt verifies alignment and usefulness of each draft
4. the editor prompt adapts the approved draft for a target platform with optional persona guidance

That means prompt responsibility is distributed by role instead of trying to do everything in one large prompt.

## High-Level Example

For a request like:

> Generate LinkedIn and Instagram posts about effective remote team collaboration, productivity strategies, and building strong distributed team culture.

the prompt layer supports behavior such as:

- planner: produce 2-3 distinct angles with different perspectives
- writer: produce one reusable source draft for each angle
- judge: verify that the draft still matches the requested angle and topic
- editor: adapt the approved draft for LinkedIn (professional tone) and Instagram (visual, casual tone)

## Why This Separation Matters

Keeping prompts in their own layer makes it easier to:

- adjust tone and persona without changing the graph
- add a new platform without rewriting agent orchestration
- refine stage behavior independently
- reuse the same workflow with different prompt strategies
- A/B test different prompt approaches

High-level examples:

- add a `youtube`-style editor prompt with channel optimization guidance
- tighten judge behavior for stricter quality control or niche topics
- change writer behavior to be more conversational or more formal
- add or refine built-in personas without changing graph orchestration
- add platform-specific hashtag or formatting rules
- customize tone for industry-specific content (medical, legal, technical, etc.)

## Customization

### Adding a New Platform

1. Add platform name and guidance to `platform_prompts.py`
2. Include tone, length guidelines, formatting, and best practices
3. Reference it in the API route documentation
4. No changes needed to graph or agent layer

### Adding a New Persona

1. Add persona name and description to `persona_prompts.py`
2. Define voice, tone, word choice, and delivery style
3. Test via the API with `platformPersonaPairs` or `persona` parameter
4. No changes needed to orchestration layer

### Customizing Per-Stage Behavior

1. Edit the relevant prompt function in `agent_prompts.py`
2. Change instructions, output format, or quality checks
3. Restart the service to pick up changes
4. The workflow adapts automatically