# BrainViz

Describe a scenario in plain English, and watch the brain regions it's associated with light up on an interactive 3D brain — grounded in real, cited neuroscience research, not guesswork.

**Live demo:** https://brain-viz-frontend.vercel.app/
*(Free-tier hosting: the backend sleeps after ~15 minutes idle, so the first request after a quiet stretch can take 30-60 seconds. The database pauses after a week of total inactivity and is restored from the host dashboard — if the link seems broken, this is almost certainly why.)*

---

## What it does

Type a scenario — "I'm walking through a jungle, see a snake, and become afraid" — and the app:

1. Extracts up to 3 relevant cognitive/psychological concepts using an LLM (Claude)
2. Looks up real, published neuroimaging evidence for each concept in a database built from the [Neurosynth](https://neurosynth.org) meta-analytic dataset (14,371 studies, 507,891 reported brain coordinates, 1,049,299 study-concept associations)
3. Selects the strongest, most representative coordinates per concept using a weighted evidence-selection algorithm
4. Renders those coordinates on an interactive 3D brain model, colored by evidence strength
5. Generates a plain-language explanation that walks through the scenario and cites the actual supporting studies by name

Built as a study aid for psych/neuro students — designed to make an abstract textbook fact ("the amygdala is involved in fear") into something explorable and explained, grounded in real data rather than a generic AI answer.

---

## Architecture

The system is deliberately split into three layers with a clear separation of responsibility:

**1. LLM semantic layer** — Claude reads the user's message, decides whether it describes a relevant scenario, and (if so) extracts up to 3 standardized concept names using a controlled vocabulary designed to match the database below. This layer never has access to the evidence database directly, and it cannot introduce a brain region that isn't backed by retrieved data.

**2. Deterministic evidence layer** — A Postgres database holds the full Neurosynth dataset (studies, coordinates, concepts, and study-concept weight associations). Given a concept name, a dedicated query function retrieves the top-weighted studies, reduces each study's many coordinates to a single centroid-nearest representative point, filters out weak evidence below a threshold, and returns real coordinates with real study citations and an evidence-strength label (High/Medium/Low). **If a concept has no match in this layer, no coordinate is ever shown for it** — the system cannot fabricate evidence.

**3. Visualization layer** — The real, retrieved coordinates (never invented ones) are rendered on a 3D anatomical brain model (NIH 3D / Allen Human Reference Atlas), positioned using real MNI-space coordinate math, colored by evidence strength, and made explorable via hover and click interaction.

This separation is the core design principle of the whole project: **the LLM interprets language, but it is never the source of the science.**

---

## Tech stack

- **Frontend:** React (Vite), Three.js / react-three-fiber, deployed on Vercel
- **Backend:** FastAPI (Python), deployed on Render
- **Database:** PostgreSQL (Supabase), ~1.6M rows of Neurosynth data plus application data
- **LLM:** Claude (Anthropic API), used for concept extraction and natural-language explanation generation
- **3D asset:** NIH 3D (Allen Human Reference Atlas), CC BY 4.0

---

## Evaluation

The pipeline was tested against 21 hand-written scenarios spanning six categories: strong/well-covered concepts, multi-concept complexity, ambiguous input, non-psychological input, vocabulary-matching edge cases, and near-miss/meta-question phrasing.

**Results:**
- **16 of 21 (76%)** correctly produced grounded concepts and real Neurosynth coordinates.
- **4 of 21 (19%)** correctly identified that no relevant concept applied (ambiguous or non-scientific input) and returned an empty concept list with a plain conversational reply, rather than forcing a match.
- **1 of 21 (5%)** extracted concepts that matched nothing in the database, correctly returning zero coordinates rather than inventing evidence.

**A real bug found and fixed during testing:** the first run of this evaluation surfaced a crash on two non-psychological scenarios ("The weather is nice today," "I'm making a sandwich for lunch"), caused by an empty concept list being treated as truthy in a Python conditional, which triggered an unnecessary second API call with empty content. Diagnosed and fixed the same day; both scenarios pass cleanly on retest.

**A genuine finding, not a failure:** "I'm making a sandwich for lunch" unexpectedly returned real concepts (planning, motor control, reward) and 10 grounded coordinates on one run. Making a sandwich genuinely does involve sequential planning and motor execution — a reminder that the system finds real psychological content in scenarios that look mundane on the surface, rather than a sign something's wrong.

---

## Limitations (honest, by design)

This project treats scientific honesty as a core requirement, not an afterthought. Known limitations:

- **Association, not proof.** The underlying data is meta-analytic — it shows which brain regions are *statistically associated* with a concept across many published studies, not a direct measurement of any individual's brain activity. The app is explicit about this in its UI and generated explanations.
- **LLM explanation can occasionally overclaim.** Testing surfaced one real case where a Low-confidence, single-study finding was correctly hedged in the structured coordinate summary but stated with more apparent certainty in the plain-language narrative. Partially mitigated on Sept 28 with an explicit instruction to keep narrative confidence proportional to evidence strength; a full, properly-tested refinement pass is planned for Phase 2 rather than patched further under deadline pressure.
- **No user accounts or persistent history.** Every page load starts a fresh, anonymous conversation. Conversations are saved in the database but there's no way to return to a previous one.
- **Rate limiting is IP-based.** Limits daily messages per IP address to protect API budget; bypassable with a VPN. A reasonable tradeoff for a portfolio project, not production-grade abuse prevention.
- **Free-tier hosting caveats.** Backend cold starts after idle periods; database pauses after a week of no activity.
- **Concept-to-coordinate reduction is a simplification.** Each study's many reported coordinates are reduced to a single centroid-nearest point for display clarity, which means some of a study's reported spatial detail isn't shown.

---

## Future work (Phase 2 — explicitly not built)

These are real, considered extensions, deliberately scoped out of the initial build rather than overlooked:

- **Predict Mode** — an active-learning mode where the user guesses which regions will activate before the reveal, turning the tool from a demo into a genuine study aid.
- **Full prompt refinement pass** — a dedicated, properly multi-scenario-tested revision of both the extraction and explanation prompts (the Sept 28 fix addressed one specific failure mode; a broader pass deserves its own focused time rather than incremental patches).
- **Decoupled extraction/reply calls** — currently one LLM call handles both the conversational reply and concept extraction, relying on prompt instructions to reliably do both. A fully decoupled architecture (two independent calls) would be more robust, at the cost of roughly doubling API calls per message.
- **Systematic evidence-gap analysis** — running a much larger batch of scenarios (50-100+) and categorizing *why* concepts fail to match evidence, to identify real patterns in which categories of psychological concepts are underrepresented in meta-analytic neuroscience literature.
- **Knowledge graph modeling, conversation timeline/rewind, Compare Mode, and a standalone search/explore interface** — all genuine ideas, intentionally out of scope for the initial build in favor of a smaller, fully-working, honestly-documented system.

---

## Credits & Acknowledgments

- Brain model: NIH 3D (3DPX-020960), built from the Allen Human Reference Atlas, licensed CC BY 4.0
- Neuroimaging data: [Neurosynth](https://neurosynth.org)
- Frontend refined by Claude, Backend coded by Rishav
- Inspiration: this project was shaped in part by [Avi Agola](https://linkedin.com/in/avi-agola)'s [$100 grant post](https://aviagola.me/grants) on building lightweight tools for tracking and predicting brain/behavioral response, in the spirit of Meta's TRIBE v2 — which also directly informed this project's visual and interaction design goals.

Built by Rishav Rangapure.
