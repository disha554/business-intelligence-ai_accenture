import os,json
from mistralai.client import Mistral
from .sql_tools import query_sql,get_kpi_evidence
SYSTEM="""You are BusinessIntelligence.ai, an evidence-first KPI investigation agent.
Use tools before quantitative claims. SQL/evidence tools are the source of truth.
Do not invent causes. If evidence is insufficient, ABSTAIN and propose an investigation plan.
Return what happened, why, confidence, evidence/lineage, action, owner, urgency and monitoring."""
TOOLS=[
{"type":"function","function":{"name":"query_sql","description":"Run a read-only SELECT on the business SQLite database.","parameters":{"type":"object","properties":{"sql":{"type":"string"}},"required":["sql"]}}},
{"type":"function","function":{"name":"get_kpi_evidence","description":"Retrieve validated evidence across sales, product analytics, incidents, deployments and operations.","parameters":{"type":"object","properties":{"kpi":{"type":"string"}},"required":["kpi"]}}}]
def run_agent(request):
    key=os.getenv("MISTRAL_API_KEY")
    if not key: raise RuntimeError("MISTRAL_API_KEY not configured")
    client=Mistral(api_key=key)
    messages=[{"role":"system","content":SYSTEM},{"role":"user","content":request}]
    for _ in range(4):
        r=client.chat.complete(model=os.getenv("MISTRAL_MODEL","mistral-medium-latest"),messages=messages,tools=TOOLS,tool_choice="auto")
        m=r.choices[0].message; calls=getattr(m,"tool_calls",None)
        if not calls: return m.content
        messages.append(m)
        for call in calls:
            a=json.loads(call.function.arguments)
            result=query_sql(a["sql"]) if call.function.name=="query_sql" else get_kpi_evidence(a.get("kpi","revenue"))
            messages.append({"role":"tool","name":call.function.name,"content":json.dumps(result),"tool_call_id":call.id})
    return "Agent stopped after maximum tool steps."
