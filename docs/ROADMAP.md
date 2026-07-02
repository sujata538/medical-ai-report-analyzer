# Roadmap: Future ML Architecture

This build ships a **transparent, rule-based** scoring and recommendation
system deliberately — it's auditable, testable, and safe by construction.
The following describes how to evolve it into a learned system without
compromising those properties.

## 1. Predictive health-risk model
- Collect (or license) a labeled dataset of parameter panels → outcomes.
- Train a scikit-learn classifier/regressor (start simple: logistic
  regression or gradient boosting) as an *additional* signal alongside,
  not a replacement for, the rule-based score.
- Use `shap.Explainer` (already listed in requirements, guarded behind
  `ENABLE_TRANSFORMER_MODELS`) to attribute predictions per parameter —
  `app/ml/explainability.py` already exposes the same interface the
  rule-based breakdown uses, so swapping in real SHAP values requires no
  API changes.

## 2. Improved extraction
- Fine-tune or prompt a biomedical NER model (e.g. scispaCy) specifically
  on lab-report layouts to reduce reliance on the fixed vocabulary list.
- Add table-structure detection (e.g. via `pdfplumber`'s table extraction)
  for reports that present values in genuine tabular form rather than
  line-based "Name: Value" pairs.

## 3. Vector database for report history
- `app/ml/semantic.py` already produces sentence embeddings; the natural
  next step is persisting them (e.g. in a lightweight vector store such as
  Chroma or a Postgres `pgvector` column) to power "find similar past
  results" and better duplicate-detection across a user's report history.

## 4. LangChain-ready summary generation
- `AIService.generate_summary_with_llm` is the documented seam for
  plugging in an LLM call. A LangChain chain could sit here to retrieve
  relevant patient history (via the vector store above) before generating
  a summary — as long as the chain is constrained to rephrase computed
  facts rather than introduce new ones, preserving the safety property
  that "the model never diagnoses."

## 5. Multi-report longitudinal analysis
- Track individual parameter trends (not just the aggregate health score)
  over time, and surface parameters trending toward an abnormal range
  even while still "normal" today.

## Non-goals

- This system will **never** output a diagnosis, a named condition as a
  probable cause, or medication/dosage advice — any future ML work should
  preserve this boundary by construction (e.g. train models to predict a
  *risk category*, not a diagnosis label).
