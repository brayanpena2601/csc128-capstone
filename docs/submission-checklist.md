# Submission evidence checklist

- Confirm the instructor's proposal response and implement the actual feedback.
- Compare against the complete rubric; do not assume all 280 points are covered.
- Validate the source dataset against course materials before publication.
- Record a real successful Groq response; mocked tests are insufficient evidence.
- Confirm secrets are ignored and absent from staged files and Git history.
- Add the public GitHub URL and public Streamlit URL to the submission.
- Test the public URL cold in a private browser window.
- Prepare a 2–3 page design PDF explaining users/problem, intents/entities,
  deterministic/model split, three actual failures and fixes, refusal/handoff,
  and a realistic four-week extension plan.
- Log actual failures while testing. Do not present imagined failures as observed.
- Record a demo of <=5 minutes: disclosure; two-slot flow; remaining intents;
  state/reset; refusal/handoff; simulated API failure; sources; public URL.
- Verify the deadline and timezone in the LMS. Supplied text says Friday,
  October 9 at 11:59 PM without a timezone.

## Known limitations to investigate

- Classifier rules cover a small vocabulary and need real user paraphrase testing.
- Multi-topic messages receive clarification; test more complex corrections and paraphrases.
- Source coverage is intentionally small; no official module mapping is fabricated.
- Groq output can still contain unsupported wording despite the grounding prompt.

## Failure log

Record reproduction, observed output, fix, and regression check for each real issue.
No model-call or deployment success should be claimed until actually observed.

### Observed during local implementation

1. `What do I need to turn in for capstone?` returned no intent. Added the
   submission phrase `turn in` to assignment routing. Regression test:
   `test_natural_submission_phrase`.
2. `Help me understand conversation memory` selected concept_help but extracted
   no topic. Added conversation memory as a state alias. Regression test:
   `test_memory_alias`.
3. `Explain intents and grounding` silently answered only intents. Added explicit
   ambiguity detection and a one-topic clarification without changing state.
   Regression test: `test_multiple_topics_request_clarification`.

These were observed in offline local commands, not in a live user study or deployment.
