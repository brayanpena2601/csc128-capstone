"""Conversation logic independent from Streamlit and the network."""
from dataclasses import dataclass, field
from classifier import classify
from entities import extract, candidates
from guardrails import check
from retriever import retrieve
from llm import generate

PROMPTS = {
    "topic": "Which CSC-128 topic: capstone, intents, slot filling, conversation state, grounding, Streamlit, or Groq?",
    "resource_type": "Which resource type: notes, instructions, or examples?",
}


@dataclass
class Conversation:
    intent: str | None = None
    slots: dict[str, str] = field(default_factory=dict)
    pending: str | None = None
    question: str = ""


def respond(text: str, state: Conversation, api_key: str = "", model: str = "openai/gpt-oss-20b", generator=generate) -> str:
    text = text.strip()
    if not text:
        return "Please enter a CSC-128 question."
    if len(text) > 1500:
        return "Please shorten your question to 1,500 characters."
    if text.lower() in {"reset", "cancel", "restart", "reiniciar", "cancelar"}:
        state.intent, state.pending, state.question = None, None, ""
        state.slots.clear()
        return "Conversation reset. How can I help with CSC-128?"
    guard = check(text)
    if guard:
        return guard
    if any(len(values) > 1 for values in candidates(text).values()):
        return "Please ask about one topic and one resource type at a time, for example: Find notes about intents."
    found = extract(text)
    intent = classify(text)
    # A recognized answer to the requested slot takes precedence over classifier keywords.
    slot_answer = state.pending and state.pending in found
    if intent and not slot_answer:
        if intent != state.intent:
            state.slots.clear()
        state.intent, state.pending, state.question = intent, None, text
    elif not slot_answer and not (state.intent and found):
        return "I only help with CSC-128. Ask me to find a resource, explain a concept, review assignment requirements, or check course logistics." + ("\n\n" + PROMPTS[state.pending] if state.pending else "")
    if not state.intent:
        return "Would you like a resource, a concept explanation, assignment guidance, or course logistics?"
    if found.get("topic") and found["topic"] != state.slots.get("topic"):
        state.slots.pop("resource_type", None)
    state.slots.update(found)
    required = ("topic", "resource_type") if state.intent == "resource_lookup" else ("topic",)
    for slot in required:
        if slot not in state.slots:
            state.pending = slot
            return PROMPTS[slot]
    state.pending = None
    records = retrieve(state.intent, state.slots)
    if not records:
        return "I do not have a verified source for that request. Check the CSC-128 LMS or ask your instructor. You can change the topic or resource type, or type reset."
    question = f"Request: {state.question}\nCurrent message: {text}\nIntent: {state.intent}\nSelected values: {state.slots}"
    answer = generator(question, records, api_key, model)
    sources = "\n".join(f"- [{r['id']}] {r['source']}" for r in records)
    return f"{answer.text}\n\n**Sources**\n{sources}\n\n_Response mode: {answer.status}_"
