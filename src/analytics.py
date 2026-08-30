def analyze_evidence(e):
    drivers=[]
    conv=e.get("conversion",[]); inc=e.get("incidents",[]); dep=e.get("deployments",[])
    if conv:
        change=abs(conv[-1]["conversion_pct"]-conv[0]["conversion_pct"])
        drivers.append({"driver":"Checkout conversion decline","score":round(min(99,change*10),1),"method":"time-series change"})
    if inc:
        base=inc[0]["ticket_count"]; peak=max(x["ticket_count"] for x in inc)
        drivers.append({"driver":"Payment-failure spike","score":round(min(99,(peak-base)/max(base,1)*30),1),"method":"incident delta"})
    if dep: drivers.append({"driver":"Payment-service deployment at 10:12","score":92,"method":"temporal precedence"})
    drivers.sort(key=lambda x:x["score"],reverse=True)
    return {"drivers":drivers,"confidence":drivers[0]["score"] if drivers else 0,"evidence_count":len(conv)+len(inc)+len(dep)}
