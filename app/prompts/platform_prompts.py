from __future__ import annotations

from textwrap import dedent


PLATFORM_PROMPTS = {
    "linkedin": dedent(
        """
        Write for LinkedIn.
        - Professional, credible, insight-driven
        - Clear structure with moderate depth
        - Strong hook, useful takeaway, polished CTA
        - Use short paragraphs and high information density
        - Lead with a business insight or operational pain
        - Favor clarity and strategic relevance over hype
        - This should feel like a smart operator sharing a useful perspective, not a promotional brochure
        - Avoid generic openings like "In today's fast-paced world"
        - Open with a sharper insight, tension, or business consequence
        - Use crisp, confident business language instead of broad motivational phrasing
        - Avoid generic SaaS cliches and empty superlatives
        - Do not sound like brand copy dressed up as thought leadership
        """
    ).strip(),
    "instagram": dedent(
        """
        Write for Instagram.
        - Visual-first, concise, engaging
        - Caption-friendly wording
        - Emphasize emotion, imagery, and audience interaction
        - Keep it scannable and mobile-friendly
        - Use stronger rhythm and lighter phrasing than LinkedIn
        - Favor punchy lines over long explanation
        - This should feel like an Instagram caption, not a LinkedIn post pasted into Instagram
        - Avoid corporate lead-ins
        - Start with energy, tension, or a visual or emotional hook
        - Use sharper, more alive wording instead of brochure language
        - Keep the rhythm punchy and scroll-friendly
        - Avoid bland promo phrases and default brand enthusiasm
        - Sound like a sharp caption, not a campaign asset
        - Favor vibe, tension, contrast, or a strong observation over explanation
        - Avoid sounding like LinkedIn simplified for Instagram
        - Use emoji sparingly or not at all
        - A good Instagram caption feels noticed, not manufactured
        - Write more like: "Remote work didn't kill speed. Waiting did."
        - Write more like: "The hardest part of distributed work isn't distance. It's the lag between needing help and getting it."
        - Write less like: "Ready to transform your team's collaboration?"
        - Write less like: "Say goodbye to delays and hello to productivity!"
        """
    ).strip(),
    "facebook": dedent(
        """
        Write for Facebook.
        - Conversational and community-oriented
        - Slightly more relaxed than LinkedIn
        - Clear CTA and shareable tone
        - Keep it accessible and easy to skim
        - Favor human tone over corporate polish
        - Make it feel like something a person or brand would naturally post to spark conversation
        - Avoid canned openings and broad corporate phrasing
        - Use warmer, more natural language with a clearer point of view
        - Keep it human and specific, not polished into generic brand speak
        - Prefer a practical observation or point of view over hype
        - Sound like a real person or thoughtful brand voice, not a campaign post
        - A little texture is better than generic enthusiasm
        - Avoid canned inspiration and promo phrasing
        - Write more like: "Remote work gets blamed for a lot. Usually the real problem is the delay between needing help and getting it."
        - Write more like: "A lot of teams don't have a communication problem. They have a waiting problem."
        - Write less like: "Join the movement toward seamless collaboration."
        - Write less like: "Say goodbye to the hidden costs of delay."
        - Write less like: "Meet the platform changing everything."
        """
    ).strip(),
    "x": dedent(
        """
        Write for X.
        - Concise, sharp, high-signal
        - Minimal fluff
        - Prioritize clarity and punch
        - Compress aggressively
        - Focus on one strong idea only
        - Do not write a thread, mini-article, or long explanation
        - Open with the strongest observation immediately
        - Keep the post short enough to feel native to X
        - End cleanly; do not over-explain
        - Never open with filler context
        - Use hard, punchy wording instead of polished brochure phrasing
        - Every word should earn its place
        """
    ).strip(),
    "tiktok": dedent(
        """
        Write for TikTok.
        - Fast hook, short beats, creator-style pacing
        - Conversational and attention-grabbing
        - Optimize for spoken delivery and video flow
        - Make it feel performable, not essay-like
        - Favor energetic phrasing and momentum
        - Open with a strong hook in the first line
        - Use creator-style language that sounds alive on camera
        - Avoid corporate wording and explanatory drag
        - Sound like something someone would actually say on video
        - Lead with a spoken hook, not brand copy
        - Prefer one strong idea over a full explanation
        - Do not sound like narration from a corporate promo video
        - Slight bluntness is better than synthetic excitement
        - Write more like: "Remote work isn't the problem. Waiting is."
        - Write more like: "You know what's actually exhausting? Needing one answer and losing half a day."
        - Write less like: "Why settle for slow when you can have seamless?"
        - Write less like: "Let's talk about the future of teamwork."
        """
    ).strip(),
    "blog": dedent(
        """
        Write for a blog post.
        - More depth and explanation
        - Clear title, logical sections, readable flow
        - Useful, informative, and well organized
        - Allow fuller development of the idea than social formats
        - Make the structure feel intentional, not just long
        """
    ).strip(),
    "newsletter": dedent(
        """
        Write for a newsletter.
        - Direct, engaging, subscriber-friendly
        - Clear narrative arc and takeaway
        - Strong subject-line-style hook and closing CTA
        - Make it feel like a message to readers, not a public post
        - Use a guided, reader-addressing tone
        - Build a more intentional open-middle-close flow than social formats
        - Write like a message to a subscriber, not a public-facing post
        - Use a more direct and relational voice
        - Guide the reader through one clear narrative arc
        - Keep the prose strong and purposeful, not generic and padded
        - Avoid sounding like repurposed marketing collateral
        """
    ).strip(),
    "speech": dedent(
        """
        Write for a speech or spoken copy.
        - Natural spoken rhythm
        - Clear transitions and memorable phrasing
        - Easy to say out loud
        - Write for the ear, not the eye
        - Prefer shorter spoken sentences
        - Use audible cadence and emphasis
        - Avoid dense written-style phrasing
        - Every sentence should sound natural when read aloud
        - Prefer spoken cadence over polished written phrasing
        - Use more contrast, pause, and momentum
        - Favor memorable spoken lines over generic explanatory language
        - Avoid stock inspirational business language
        """
    ).strip(),
    "copy": dedent(
        """
        Write marketing copy.
        - Clear value proposition
        - Persuasive but grounded
        - Avoid exaggerated or unverifiable claims
        - Keep it tighter and more conversion-oriented than editorial content
        - Lead with value, not explanation
        - Cut anything that feels like article-style filler
        - Remove any sentence that reads like article exposition
        - Prioritize persuasion, clarity, and action
        - Use cleaner, stronger wording instead of generic marketing language
        - Avoid stock CTA and brochure phrasing
        """
    ).strip(),
}


def normalize_platform(platform: str) -> str:
    value = platform.strip().lower()

    aliases = {
        "twitter": "x",
        "x/twitter": "x",
        "tik tok": "tiktok",
        "blogs": "blog",
        "newsletters": "newsletter",
        "speeches": "speech",
    }

    return aliases.get(value, value)


def get_platform_prompt(platform: str) -> str:
    normalized = normalize_platform(platform)
    return PLATFORM_PROMPTS.get(
        normalized,
        dedent(
            f"""
            Write for the platform "{platform}".
            - Adapt tone, structure, pacing, and wording appropriately
            - Preserve the source meaning
            - Keep the output audience-ready and grounded
            """
        ).strip(),
    )
