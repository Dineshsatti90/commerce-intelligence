"""Data-contract scope gate: answer only what the reviewed catalog can answer.

The keyword preflight in ``request_policy.py`` blocks known attack phrasings and
did not generalize to the first-pass v2 questions. This gate inverts the logic:

1. **Allowlist.** A question must mention at least one concept the catalog actually
   measures (orders, GMV, months, fulfillment steps, repeat cohorts, delivery
   reviews, states, categories).
2. **Data contract.** It is refused if it asks for anything the data contract
   documents as unavailable (profit, refunds, ads, browsing, forecasts, causal
   claims, experiment results, personal data, carrier identities, single-entity
   filters, external execution or instruction changes).

It runs before any model call, needs no network or model download, and is
deterministic. It is a scope check, not a semantic-correctness check: a question
that passes can still be routed to the wrong query by the model.
"""

from __future__ import annotations

import re
import unicodedata

IN_SCOPE = (
    r"\borders?\b",
    r"\bpurchas\w*\b",
    r"\bcustomers?\b",
    r"\bgmv\b",
    r"\bsales\b",
    r"\bmerchandise\b",
    r"\bselling\b",
    r"\bmonths?\b",
    r"\bmonthly\b",
    r"\bmonth-by-month\b",
    r"\bfulfil+ment\b",
    r"\bapprov(al|ed)\b",
    r"\bcarrier handoff\b",
    r"\bdeliver(y|ed|ies)\b",
    r"\bfunnel\b",
    r"\brepeat\w*\b",
    r"\brepurchase\b",
    r"\bretention\b",
    r"\bcohorts?\b",
    r"\bbuy(ing)? again\b",
    r"\bcame back\b",
    r"\blate\b",
    r"\bon-time\b",
    r"\bpunctual\b",
    r"\bdelayed\b",
    r"\breviews?\b",
    r"\bratings?\b",
    r"\bscores?\b",
    r"\bstates?\b",
    r"\bcategor(y|ies)\b",
    r"\bproducts?\b",
    r"\bdataset\b",
)

# Each family mirrors a limitation documented in the README / data dictionary.
OUT_OF_CONTRACT = {
    "profit_or_cost": r"\b(profit|margins?|commission|costs?|cac|roi|return[- ]on)\b",
    "refunds": r"\b(refund\w*|returned|returns|charge ?backs?|charged back)\b",
    "marketing": r"\b(ads?|advertis\w*|marketing|campaigns?|acquisition|google|facebook|meta)\b",
    "browsing": r"\b(visitors?|sessions?|clicks?|browsing|checkout|cart|conversion|page ?views?|website)\b",
    "forecast": r"\b(forecast\w*|predict\w*|projection|next (year|quarter|month|twelve|\d+)|will (be|look|earn|generate)|future|expected\b(?! values?\b))",
    "causal_claim": r"\b(caus\w*|attribut\w*|because of|due to|impact of|effect of|treatment effect|drive[sn]?|lead to|result in|make \w+ (more|less)|made \w+ (more|less))\b",
    "experiment_result": r"\b(uplift|lift(ed)?|a/b|ab test|treatment|winning|notification test|shipping experiment|test result)\b",
    "personal_data": r"\b(customers?|buyers?|shoppers?|users?|sellers?)\b.{0,40}\b(names?|e-?mails?|phones?|address\w*)\b|\b(e-?mails?|phone numbers?|street address\w*|cpf|buyer identit\w*)\b",
    "carrier_identity": r"\b(carrier|delivery company|shipping company|courier|logistics provider)\b.{0,40}\b(name|by name|fire|which one)\b|\bby name\b",
    "single_entity_filter": r"\b(only|just|solely|exclusively|filter\w*)\b.{0,50}\b(state|from|for|in|month|year|january|february|march|april|may|june|july|august|september|october|november|december|\d{4}|[a-z]{2} only)\b|\bonly\b.{0,10}\bfor the state of\b|\bthe state of [a-z]+\b",
    "external_or_execution": r"\b(execute|run select|select \*|drop table|sql|url|https?|api|fetch|external|private table|credentials?|secrets?|environment variables?)\b",
    "instruction_change": r"\b(ignore|disregard|forget|pretend|override|higher priority|act as|you are now|new job|fabricat\w*|make up|made up|invent\w*|confirm it|approves?|authori[sz]\w*|obsolete)\b",
}


def _normalize(question: str) -> str:
    text = unicodedata.normalize("NFKC", question).casefold()
    text = "".join(c for c in text if unicodedata.category(c) != "Cf")
    return " ".join(text.replace("_", " ").split())


def scope_decision(question: str) -> tuple[bool, str]:
    """Return ``(allowed, reason)``. ``reason`` names the contract family on refusal."""
    if not isinstance(question, str) or not question.strip():
        return False, "empty_question"
    text = _normalize(question)
    for family, pattern in OUT_OF_CONTRACT.items():
        if re.search(pattern, text):
            return False, family
    if not any(re.search(p, text) for p in IN_SCOPE):
        return False, "no_catalog_concept"
    return True, "in_scope"
