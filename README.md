# BusinessIntelligence.ai — Evidence-first KPI Intelligence Agent

**Architecture:** business data → SQL tools → analytics/materiality/driver scoring → evidence/lineage → Mistral tool-calling agent → persona-specific narrative/action → Streamlit.

**AI agent:** Mistral receives callable `query_sql()` and `get_kpi_evidence()` tools, decides when to call them, receives their results, then synthesizes the response. This follows Mistral's function-calling agent pattern.

**Quantitative truth:** SQL and analytics establish KPI values, evidence, driver scores and guardrails. The LLM is not trusted to calculate numbers or invent causes. If evidence is insufficient, the agent must abstain.

**SQL:** local SQLite for a self-contained competition demo; production can replace the adapter with an authenticated warehouse.

**Analytics:** transparent materiality and driver scoring; production can add forecasting, anomaly detection, contribution analysis and causal inference where justified.

## Run
```bash
pip install -r requirements.txt
python -m src.seed_db
python -m streamlit run app.py
```

## Enable Mistral
Set `MISTRAL_API_KEY` and optionally `MISTRAL_MODEL=mistral-medium-latest`. Never commit `.env`; `.gitignore` excludes it.

Without a key, the deterministic prototype remains usable.
