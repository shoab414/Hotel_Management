import csv

def export_query_to_csv(conn, query, params, path, headers=None):
    cur = conn.cursor()
    cur.execute(query, params or ())
    rows = cur.fetchall()
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        if headers:
            w.writerow(headers)
        for r in rows:
            w.writerow([r[k] for k in r.keys()])
