# CSC-128 Course Assistant

A narrow course chatbot for students looking for resources, concept explanations,
assignment requirements, and course logistics. It discloses that it is software,
refuses requests to complete graded work, and directs grade/extension decisions to
the instructor. This is an initial implementation, not a completed submission.

## Run in VS Code (Windows PowerShell)

1. Open this folder using **File > Open Folder**.
2. Select Python 3.12 or 3.13 and create a project environment if needed:

   ```powershell
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   ```

3. Edit `.streamlit/secrets.toml` locally. Set `GROQ_API_KEY` to your own key;
   never paste it into chat, a commit, or a screenshot. For a fresh clone, copy
   `.streamlit/secrets.example.toml` to `.streamlit/secrets.toml` first.
4. Start the app:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

Without a key, the app returns local source excerpts and explicitly labels its
offline mode. A real Groq response was verified locally using `openai/gpt-oss-20b`; deployed credentials still require their own check.
The sidebar can disable AI wording. With AI enabled, the question and retrieved
excerpts are sent to Groq; the app does not save chat messages to disk.

## Architecture

| File | Responsibility |
| --- | --- |
| `app.py` | UI, session state, configuration |
| `classifier.py` | Four deterministic intent rules, unknown-input fallback |
| `entities.py` | Topic and resource-type extraction |
| `chatbot.py` | Slot prompts, state transitions, orchestration |
| `guardrails.py` | Refusal and instructor handoff rules |
| `retriever.py` | Exact topic/intent/resource matching |
| `llm.py` | Groq wording, bounded timeout, safe fallbacks |
| `data/resources.json` | Sources with IDs and provenance |

The four intents are `resource_lookup`, `concept_help`, `assignment_guidance`,
and `course_logistics`. Resource lookup requires **two different entities**:
`topic` and `resource_type`. Missing values cause separate questions. Each browser
session owns a `Conversation`; a reset clears slots and chat history.

Try: `Find a resource` → `slot filling` → `examples`.
Also try `Explain intents`, `Capstone requirements`, and
`When is the capstone due?`.

Python controls routing, entities, state, retrieval and guardrails. Groq composes
the final explanation using retrieved records. No matching record means no model
call. Sources are appended by code, not invented by the model. Source labels do
not guarantee every generated sentence is supported: review model answers.

## Sources and limitations

The initial dataset contains student-supplied capstone instructions and clearly
labeled project-authored study notes. It does not contain the full syllabus,
official module lessons, course links, or the complete grading rubric. Unknown
resources are acknowledged rather than fabricated. Do not publish private course
documents or personal data when adding records. Keyword rules are intentionally
simple and can miss paraphrases; they are not an adversarial safety boundary.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

Tests use Python's standard runner, Streamlit AppTest, and mocked Groq calls.
They cover four intents, two-slot dialogue, isolation, reset, topic/intent changes,
missing sources, refusal, UI reruns, and rate-limit/authentication/network failures.
Mocks do not prove a real key or live deployment works.

## Public deployment

1. Initialize a separate Git repository in this folder if needed.
2. Run `git check-ignore -v .streamlit/secrets.toml` before the first commit/push.
   Inspect staged files to ensure no secrets or private course material is present.
3. Create a public GitHub repository and push this project's files.
4. In Streamlit Community Cloud, choose that repository, branch, and `app.py`.
5. Select a supported Python version matching local validation. Paste your key
   into **Advanced settings > Secrets** (or app settings), separately from the
   ignored local file. Use the example TOML structure.
6. Verify all four intents and a live Groq response. Open the public URL in a
   private browser window with no login. Recheck near the deadline.

Deployment reference: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

Groq model reference: https://console.groq.com/docs/models

## Submission status

- Initial code and automated tests: see local validation, not a grade guarantee.
- Instructor feedback and full rubric: awaiting student-provided details.
- Real Groq API check: passed locally with `openai/gpt-oss-20b`. The earlier model returned HTTP 404/model_not_found; the replacement was selected from the authenticated models endpoint.
- Public GitHub repository and Streamlit URL: pending publication.
- 2–3 page design PDF and <=5 minute recorded demo: pending.

See `docs/submission-checklist.md` for the remaining evidence.

### Verified intent definitions

The intents study note and resource-lookup slot-filling example are displayed directly from their sources with response mode `verified_source`. This prevents model wording from renaming code identifiers, inventing resource types, or truncating the retrieved example dialogue. Other matching records still use Groq when enabled.
