import os
import streamlit as st
import pandas as pd
from src.engine import run_engine, source_catalog, kpi_catalog
from src.sql_tools import get_kpi_evidence
from src.analytics import analyze_evidence
from src.agent import run_agent

st.set_page_config(page_title="BusinessIntelligence.ai", page_icon="📊", layout="wide")

st.title("📊 BusinessIntelligence.ai")
st.caption("KPI Intelligence-to-Action Engine • evidence before explanation")

with st.sidebar:
    st.header("Investigation Controls")
    scenario = st.selectbox(
        "Demo scenario",
        ["Checkout outage — high confidence", "Ambiguous revenue decline", "Newly launched KPI"]
    )
    persona = st.selectbox("Persona", ["Business Leader", "Engineering Manager", "Marketing Manager"])
    role = st.selectbox("Access role", ["Executive", "Engineering", "Marketing"])

result = run_engine(scenario, persona, role)
sql_evidence=get_kpi_evidence('revenue')
analytics_result=analyze_evidence(sql_evidence)

# KPI/source coverage required by the brief
st.subheader("Connected KPI & source layer")
k1, k2, k3, k4, k5 = st.columns(5)
for col, (name, value) in zip(
    [k1,k2,k3,k4,k5],
    [("Revenue","−8.2%"),("Conversion","−11%"),("Traffic","0.0%"),("Payment failures","+340%"),("Inventory","−30%")]
):
    col.metric(name, value)

with st.expander("Data contracts, grain & refresh cadence", expanded=False):
    st.dataframe(pd.DataFrame(source_catalog()), use_container_width=True, hide_index=True)
    st.caption("Prototype uses synthetic records. The source layer is designed so adapters can be replaced by SQL/warehouse, product analytics, CRM and operational connectors.")

c1,c2,c3,c4 = st.columns(4)
c1.metric("KPI movement", result["movement"])
c2.metric("Expected", result["expected"])
c3.metric("Deviation", result["deviation"])
c4.metric("Confidence", result["confidence"])

st.subheader("1 · What happened?")
st.info(result["summary"])

left,right = st.columns([1.15,1])
with left:
    st.subheader("2 · Why did it happen?")
    st.dataframe(result["drivers"], use_container_width=True, hide_index=True)
with right:
    st.subheader("Evidence & lineage")
    for e in result["evidence"]:
        st.markdown(f"**{e['source']}**  \n{e['claim']}  \n`{e['lineage']}`")

st.subheader("3 · What next?")
if result["abstain"]:
    st.warning(result["recommendation"])
else:
    st.success(result["recommendation"])

m1,m2,m3,m4 = st.columns(4)
m1.write("**Owner**"); m1.write(result["owner"])
m2.write("**Urgency**"); m2.write(result["urgency"])
m3.write("**Expected impact**"); m3.write(result["impact"])
m4.write("**Recheck**"); m4.write(result["recheck"])

st.divider()
st.subheader("Decision trace")
st.dataframe(pd.DataFrame(result["trace"]), use_container_width=True, hide_index=True)

st.subheader("Analyst feedback")
fb1,fb2 = st.columns([1,2])
with fb1:
    feedback = st.radio("Was the conclusion useful?", ["Correct","Incorrect","Needs review"], horizontal=True)
with fb2:
    comment = st.text_input("Correction / comment", placeholder="e.g., Marketing pause was the actual primary cause")
if st.button("Submit feedback"):
    st.success(f"Feedback recorded: {feedback}" + (f" — {comment}" if comment else ""))

with st.expander("LLM vs non-LLM processing"):
    st.markdown("""
    **Non-LLM / deterministic:** KPI calculations, baseline comparison, materiality checks,
    driver scoring, evidence/lineage, confidence guardrails and access rules.

    **LLM-assist (production design):** intent understanding, contextual retrieval,
    narrative synthesis and recommendation wording using only validated evidence.
    """)

with st.expander("Runtime telemetry"):
    t = result["telemetry"]
    st.write(f"Latency: **{t['latency']}** · Model calls: **{t['llm_calls']}** · Estimated tokens: **{t['tokens']}** · Estimated cost: **{t['cost']}**")

st.divider()
st.subheader("🤖 Evidence-first AI agent")
st.caption("SQL + analytics establish quantitative truth; Mistral performs tool-using investigation and narrative synthesis.")
with st.expander("Agent tools and analytics", expanded=False):
    st.write("Tools: `query_sql()` · `get_kpi_evidence()`")
    st.write(f"Validated evidence records: **{analytics_result['evidence_count']}**")
    st.write(f"Transparent analytics confidence score: **{analytics_result['confidence']}**")
    if os.getenv("MISTRAL_API_KEY"):
        if st.button("Run live Mistral agent"):
            prompt=f"Investigate the {scenario} for a {persona} with {role} access. Use SQL/evidence tools first. Never invent quantitative facts. Abstain if evidence is insufficient."
            with st.spinner("Mistral agent is using SQL/evidence tools..."):
                try: st.write(run_agent(prompt))
                except Exception as e: st.error(f"Live agent error: {e}")
    else:
        st.info("Mistral key not configured. The deterministic prototype remains active; set MISTRAL_API_KEY to enable the live agent.")

st.caption("Competition prototype • synthetic data • quantitative truth is not generated by the LLM.")
