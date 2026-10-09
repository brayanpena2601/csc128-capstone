"""Small, inspectable rule classifier; unknown input never defaults to an intent."""
import re

INTENTS = ("resource_lookup", "concept_help", "assignment_guidance", "course_logistics")


def classify(text: str) -> str | None:
    text = text.lower()
    rules = (
        ("course_logistics", r"\b(due|deadline|office hours|contact|points|fecha)\b"),
        # Explicit requests outrank incidental nouns: explaining with examples is
        # concept help, while finding assignment instructions is resource lookup.
        ("resource_lookup", r"\b(find|where|link|looking for|buscar)\b"),
        ("assignment_guidance", r"\b(required|requirements|instructions|deliverables|submit|turn in|need to do|need to include|rubric|assignment|checklist|requisitos|entregar|instrucciones)\b"),
        ("concept_help", r"\b(explain|describe|define|definition|meaning|concept|understand|how does|how do|what is|what are|explica|qué es|que es|cómo funciona)\b"),
        ("resource_lookup", r"\b(resource|resources|notes|examples|recursos|notas|ejemplos)\b"),
        ("course_logistics", r"\b(when|cuando|cuándo)\b"),
    )
    for intent, pattern in rules:
        if re.search(pattern, text):
            return intent
    return None
