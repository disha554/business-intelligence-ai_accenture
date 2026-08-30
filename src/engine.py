import time
import pandas as pd

def source_catalog():
    return [
        {"Source":"Sales / warehouse","Key KPIs":"Revenue, units, returns","Grain":"day × region × product × segment","Refresh":"Daily"},
        {"Source":"Product analytics","Key KPIs":"Traffic, checkout conversion","Grain":"hour × channel × product","Refresh":"Hourly"},
        {"Source":"CRM / marketing","Key KPIs":"Campaign spend, conversion, win/loss","Grain":"day × campaign × region","Refresh":"Daily"},
        {"Source":"Incident / ticket system","Key KPIs":"Payment failures, incidents","Grain":"event / ticket","Refresh":"Near-real-time"},
        {"Source":"Deployment / operations","Key KPIs":"Releases, inventory, delivery delays","Grain":"event / warehouse","Refresh":"Event-driven"},
    ]

def kpi_catalog():
    return ["Revenue","Conversion","Traffic","Payment failures","Inventory"]

def run_engine(scenario, persona, role):
    start = time.perf_counter()
    if scenario == "Checkout outage — high confidence":
        return high_confidence(persona, role, start)
    if scenario == "Ambiguous revenue decline":
        return ambiguous(persona, role, start)
    return new_kpi(persona, role, start)

def telemetry(start, calls=2, tokens=1840, cost="$0.01"):
    return {"latency": f"{max(0.8, time.perf_counter()-start):.2f} sec (local demo)", "llm_calls": calls, "tokens": tokens, "cost": cost}

def access(role):
    if role == "Executive":
        return "Company-wide KPI summaries; restricted operational details are aggregated."
    if role == "Engineering":
        return "Engineering incidents, checkout/payment signals and permitted technical evidence."
    return "Marketing KPIs, campaign and traffic signals; restricted technical details are summarized."

def high_confidence(persona, role, start):
    persona_text = {
        "Business Leader": "West-region revenue fell 8.2% versus an expected 1.4% seasonal decline. The decline is concentrated in Enterprise buyers of Product X. Traffic remained flat while checkout conversion dropped 11%.",
        "Engineering Manager": "Checkout conversion dropped 11% after a payment-service release at 10:12. Payment-failure tickets rose 340%, providing independent operational evidence.",
        "Marketing Manager": "Traffic held flat while conversion fell 11%, making acquisition volume an unlikely primary driver of the revenue decline."
    }[persona]
    drivers = pd.DataFrame([
        {"Rank":1,"Driver":"Checkout/payment outage","Evidence strength":"Very high","Confidence":"93%","Contribution":"Primary"},
        {"Rank":2,"Driver":"Product X availability","Evidence strength":"High","Confidence":"81%","Contribution":"Secondary"},
        {"Rank":3,"Driver":"Traffic/acquisition","Evidence strength":"Low","Confidence":"22%","Contribution":"Not supported"}])
    evidence=[
        {"source":"Sales system","claim":"Revenue −8.2% vs expected −1.4%.","lineage":"sales.revenue → Apr-2026 → West → Enterprise → Product X"},
        {"source":"Product analytics","claim":"Checkout conversion −11%; traffic flat.","lineage":"analytics.checkout_conversion → Apr-2026"},
        {"source":"Incident/ticket system","claim":"Payment-failure tickets +340% after 10:12 release.","lineage":"tickets.payment_failure → release_10:12"},
        {"source":"Deployment log","claim":"Payment-service release preceded the incident spike.","lineage":"deployments.payment_service → release_10:12"}]
    return {"movement":"−8.2%","expected":"−1.4%","deviation":"6.8 pp","confidence":"93%","summary":persona_text,"drivers":drivers,"evidence":evidence,"abstain":False,
            "recommendation":"ROLL BACK the payment-service deployment. Expected recovery: 6–8% (estimate). Validate by rechecking checkout conversion hourly.","owner":"Engineering","urgency":"High","impact":"6–8% recovery (estimate)","recheck":"Hourly",
            "trace":[{"Stage":"Detect","Result":"Material deviation: 6.8 percentage points beyond expected seasonal movement."},
                     {"Stage":"Localize","Result":"West region → Enterprise → Product X."},
                     {"Stage":"Explain","Result":"Conversion −11%; traffic flat; payment failures +340%."},
                     {"Stage":"Prove","Result":"Multiple independent signals align around checkout/payment failure."},
                     {"Stage":"Guardrail","Result":access(role)}],
            "telemetry":telemetry(start)}

def ambiguous(persona, role, start):
    drivers=pd.DataFrame([
        {"Rank":1,"Driver":"Competitor discount","Evidence strength":"Medium","Confidence":"45%","Contribution":"Possible"},
        {"Rank":2,"Driver":"Reduced marketing","Evidence strength":"Medium","Confidence":"38%","Contribution":"Possible"},
        {"Rank":3,"Driver":"Weather / delivery delays","Evidence strength":"Low","Confidence":"34%","Contribution":"Possible"}])
    evidence=[
        {"source":"Sales system","claim":"Revenue decline is material, but driver separation is inconclusive.","lineage":"sales.revenue → period comparison"},
        {"source":"CRM / campaign data","claim":"Signals exist for multiple hypotheses without a dominant explanation.","lineage":"crm.win_loss + marketing.campaigns"},
        {"source":"Operations","claim":"Delivery-delay data is incomplete for causal attribution.","lineage":"ops.delivery → partial coverage"}]
    return {"movement":"−8.0%","expected":"−1.5%","deviation":"6.5 pp","confidence":"No dominant cause","summary":"Revenue decline is material, but available evidence does not support a reliable single root cause. The engine abstains instead of presenting correlation as causation.","drivers":drivers,"evidence":evidence,"abstain":True,
            "recommendation":"ABSTAIN: no dominant cause. Investigation plan: compare unaffected regions, test price-sensitive segments, mine CRM win/loss reasons, and correlate delivery delays with cancellations.","owner":"Business Analytics","urgency":"Medium","impact":"Not estimated until evidence improves","recheck":"After investigation",
            "trace":[{"Stage":"Detect","Result":"Material deviation detected."},{"Stage":"Localize","Result":"Several segments move, but none dominates."},{"Stage":"Explain","Result":"Three plausible hypotheses found."},{"Stage":"Prove","Result":"Evidence is contradictory/incomplete."},{"Stage":"Guardrail","Result":"Abstain and ship an investigation plan."}],
            "telemetry":telemetry(start,2,1510,"$0.008")}

def new_kpi(persona, role, start):
    drivers=pd.DataFrame([{"Rank":1,"Driver":"Insufficient history","Evidence strength":"Insufficient","Confidence":"—","Contribution":"Cannot rank"}])
    evidence=[{"source":"KPI catalog","claim":"KPI was newly launched and lacks enough historical baseline.","lineage":"kpi_registry → launch_date"},
              {"source":"Time series","claim":"Only two weeks of observations are available.","lineage":"kpi_value → 14 days"}]
    return {"movement":"+18%","expected":"N/A","deviation":"N/A","confidence":"Low","summary":"The KPI moved +18%, but the engine cannot establish a trustworthy baseline because the KPI is newly launched. No causal story is generated.","drivers":drivers,"evidence":evidence,"abstain":True,
            "recommendation":"ABSTAIN: collect more history before attributing the movement. Suggested action: define the KPI contract, monitor daily, and establish a baseline once sufficient observations accumulate.","owner":"Analytics","urgency":"Low","impact":"Not estimated","recheck":"Daily",
            "trace":[{"Stage":"Detect","Result":"Movement observed, but materiality cannot be established."},{"Stage":"Localize","Result":"Not attempted due to insufficient baseline."},{"Stage":"Explain","Result":"No causal inference performed."},{"Stage":"Prove","Result":"Insufficient historical coverage."},{"Stage":"Guardrail","Result":"Abstain and request more data."}],
            "telemetry":telemetry(start,1,620,"$0.003")}
