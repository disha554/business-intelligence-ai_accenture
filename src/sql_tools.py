import sqlite3
from pathlib import Path
import pandas as pd
DB=Path(__file__).resolve().parents[1]/"data"/"business.db"

def query_sql(sql:str)->list[dict]:
    if not sql.strip().lower().startswith("select"):
        raise ValueError("Only SELECT statements are allowed.")
    c=sqlite3.connect(DB)
    try: return pd.read_sql_query(sql,c).to_dict("records")
    finally: c.close()

def get_kpi_evidence(kpi="revenue"):
    return {
      "sales":query_sql("SELECT region,product,segment,revenue,expected_revenue,ROUND((revenue-expected_revenue)/expected_revenue*100,2) AS pct_vs_expected FROM sales"),
      "conversion":query_sql("SELECT timestamp,traffic,ROUND(checkout_conversion*100,2) AS conversion_pct FROM product_analytics ORDER BY timestamp"),
      "incidents":query_sql("SELECT timestamp,service,event_type,ticket_count FROM incidents ORDER BY timestamp"),
      "deployments":query_sql("SELECT timestamp,service,version FROM deployments"),
      "operations":query_sql("SELECT date,region,product,inventory,delivery_delay FROM operations")
    }
