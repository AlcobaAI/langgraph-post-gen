# Agent Layer Details

This folder contains the concrete LLM-backed implementations for the workflow stages.

The current agents are:

- `planner.py`
- `writer.py`
- `judge.py`
- `editor.py`

Each agent is responsible for one step in the workflow and returns structured output rather than free-form text blobs.

## Planner

Purpose:

- turn a user prompt into a set of distinct content angles

High-level example:

Input:

> Generate posts about modern software development practices, including team collaboration, code quality, and scaling engineering teams.

Possible output:

- "How effective code review practices improve team collaboration and code quality"
- "Building scalable systems: architecture patterns and team coordination"
- "The role of automation and CI/CD in modern development workflows"

Important behavior:

- requests an exact number of angles
- removes duplicates
- fills gaps if the model returns too few usable angles

## Writer

Purpose:

- create one platform-neutral source draft for one angle

The writer does not finalize for LinkedIn, Instagram, or other channels directly. Instead, it creates an intermediate draft that can later be adapted by the editor.

Structured draft fields include:

- title
- hook
- body
- visual ideas
- caption
- hashtags
- call to action
- image prompt
- video script

This separation makes the workflow more reusable because the same source draft can be adapted into multiple output formats.

## Judge

Purpose:

- evaluate whether the writer draft is aligned with the requested angle and prompt

The judge checks whether the draft is:

- coherent
- on-topic
- useful enough to keep

High-level example:

- if a draft is relevant, it moves to the editor
- if a draft is weak or off-topic, the final artifact can be marked as skipped

## Editor

Purpose:

- adapt an approved source draft for a specific platform

The editor is where platform-specific behavior is applied.

High-level examples:

- LinkedIn: professional, structured, insight-driven
- Instagram: concise, visual, engagement-oriented
- X: short, sharp, high-signal
- Blog: long-form, detailed, comprehensive
- Newsletter: narrative-driven, personable, story-focused

If the judge rejects a draft, the editor builds a skipped artifact instead of a normal completed one.

## Why This Layer Is Separate

These files are in `infrastructure/agents/` because they are the concrete implementations that talk to models.

That separation is useful because:

- the workflow graph can depend on interfaces instead of hard-coding model logic everywhere
- model-provider details stay isolated
- alternate implementations can be added later without rewriting the whole application

High-level examples:

- OpenAI-backed agents
- mock agents for testing
- alternate provider-backed agents (Claude, Gemini, etc.)
- stricter or domain-specific agent variants

## Adding Custom Agents

To replace or extend any agent:

1. Check the protocol definition in `app/domain/protocols/`
2. Implement the same interface with your custom logic
3. Update `app/services/generate_content.py` to use your implementation
4. No changes needed to the graph layer