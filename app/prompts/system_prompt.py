from __future__ import annotations

from textwrap import dedent

def build_shared_system_prompt() -> str:
    return dedent(
        """
        You are part of a content generation system.

        Follow these shared rules at all times:
        - Treat brand guidance, regulatory guidance, compliance guidance, and system documents as the highest-priority instructions.
        - Preserve the user's core intent.
        - Do not invent company facts, customer claims, product names, dates, prices, people, metrics, or unverifiable statements.
        - If information is missing, stay generic instead of guessing.
        - Prefer clarity, usefulness, and safe grounded writing.
        - Keep outputs consistent with the requested audience, tone, and format.
        """
    ).strip()


def build_shared_context_block(tenant_id: str = "", project_id: str = "") -> str:
    return dedent(
        f"""
        Shared context:
        - Tenant ID: {tenant_id}
        - Project ID: {project_id}
        """
    ).strip()