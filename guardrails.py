"""Transparent baseline rules, not a complete adversarial safety system."""
import re


def check(text: str) -> str | None:
    text = text.lower()
    if re.search(r"\b(grade|grade dispute|extension|exception|calificación|prórroga)\b", text):
        return "Please contact your CSC-128 instructor for grades, extensions, or policy exceptions. I cannot make those decisions."
    if re.search(r"\b(do|write|complete|solve|finish|haz|resuelve)\b.{0,50}\b(my|graded|quiz|exam|homework|assignment|tarea|examen)\b", text):
        return "I cannot complete graded work for you. I can explain a CSC-128 concept or help you understand the requirements."
    if re.search(r"ignore.{0,30}(instructions|rules)|system prompt|api.?key|password", text):
        return "I can help with CSC-128 resources and concepts, but cannot reveal secrets or override my instructions."
    return None
