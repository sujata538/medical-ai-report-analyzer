"""
AI service: natural-language summary & explanation generation.

Generates a plain-language, cautiously-worded summary of a report from its
flagged parameters. This is implemented as a template-based generator by
default (zero external dependencies, fully deterministic, easy to unit
test) with a clearly marked extension point for plugging in an LLM (e.g.
via the Anthropic API) to make the prose more natural — see
`generate_summary_with_llm()`.

Design principle: the LLM (if used) is only ever allowed to *rephrase*
the facts already computed by the rule-based pipeline (flags, score,
recommendations) — never to introduce new claims. This keeps the safety
properties of the app independent of whatever language model is plugged
in.
"""
from __future__ import annotations

import logging
import os
from typing import List

from app.models.parameter import ExtractedParameter, ParameterFlag

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "This summary is generated for educational purposes only and is not a "
    "medical diagnosis. Please consult a licensed healthcare provider to "
    "interpret these results in the context of your health history."
)


class AIService:
    def __init__(self):
        # If an ANTHROPIC_API_KEY is present, `generate_summary_with_llm`
        # can be wired up; otherwise we always use the deterministic
        # template summary, so the app has no hard dependency on an
        # external API key to function.
        self.llm_enabled = bool(os.getenv("ANTHROPIC_API_KEY"))

    def generate_summary(self, parameters: List[ExtractedParameter], health_score: float) -> str:
        abnormal = [p for p in parameters if p.flag != ParameterFlag.NORMAL and p.flag != ParameterFlag.UNKNOWN]
        normal_count = len(parameters) - len(abnormal)

        if not parameters:
            return (
                "We couldn't confidently extract lab values from this report. "
                "Try uploading a clearer scan, or a native (non-scanned) PDF if available. "
                f"\n\n{DISCLAIMER}"
            )

        lines = [
            f"This report includes {len(parameters)} extracted parameter(s), "
            f"of which {normal_count} fall within typical reference ranges "
            f"and {len(abnormal)} fall outside them.",
            f"Overall computed health score: {health_score}/100.",
        ]

        if abnormal:
            lines.append("Parameters outside the typical range:")
            for p in abnormal:
                lines.append(f"  • {p.name}: {p.value}{p.unit or ''} ({p.flag.value.replace('_', ' ')})")
        else:
            lines.append("All extracted parameters fall within typical reference ranges.")

        lines.append("")
        lines.append(DISCLAIMER)
        return "\n".join(lines)

    def generate_summary_with_llm(self, parameters: List[ExtractedParameter], health_score: float) -> str:
        """
        Extension point: rephrase the deterministic summary using an LLM
        for more natural prose. Falls back to the template summary if no
        API key is configured or the call fails, so callers can always use
        this method safely.
        """
        base_summary = self.generate_summary(parameters, health_score)
        if not self.llm_enabled:
            return base_summary

        try:
            # Example integration point (requires `pip install anthropic`):
            #
            # import anthropic
            # client = anthropic.Anthropic()
            # response = client.messages.create(
            #     model="claude-sonnet-4-6",
            #     max_tokens=400,
            #     messages=[{
            #         "role": "user",
            #         "content": (
            #             "Rephrase the following lab report summary in warm, "
            #             "plain language. Do not add any new facts, numbers, "
            #             "or medical claims beyond what is stated. Keep the "
            #             "disclaimer verbatim.\n\n" + base_summary
            #         ),
            #     }],
            # )
            # return response.content[0].text
            logger.info("LLM summary rewriting is a documented extension point; not invoked in this build.")
            return base_summary
        except Exception:  # noqa: BLE001
            logger.exception("LLM summary generation failed; falling back to template summary.")
            return base_summary
