import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from flask import Flask, render_template, request, redirect, url_for, flash, abort
from App.db import run_select, run_execute

app = Flask(__name__)
app.secret_key = "dev-secret"

CRUD_CONFIG = {
    "users": {
        "pk": "id_user",
        "title": "Utilizatori",
        "create_fields": ["username", "password_hash"],
        "update_fields": ["password_hash"],
        "list_fields": ["id_user", "username", "password_hash"],
        "default_sort": "id_user DESC",
        "children": [
            {"table": "user_log", "fk": "id_user"},
        ],
    },
    "clienti": {
        "pk": "id_client",
        "title": "Clienti",
        "create_fields": ["nume_client", "nr_tlf", "email"],
        "update_fields": ["nume_client", "nr_tlf", "email"],
        "list_fields": ["id_client", "nume_client", "nr_tlf", "email"],
        "default_sort": "id_client DESC",
        "children": [
            {"table": "rezervari", "fk": "id_client"},
        ],
    },
    "mese": {
        "pk": "id_masa",
        "title": "Mese",
        "create_fields": ["cod_masa", "status"],
        "update_fields": ["status"],
        "list_fields": ["id_masa", "cod_masa", "status"],
        "default_sort": "id_masa ASC",
        "choices": {"status": ["Libera", "Ocupata", "Rezervata"]},
        "children": [
            {"table": "rezervari", "fk": "id_masa"},
        ],
    },
    "rezervari": {
        "pk": "id_rezervare",
        "title": "Rezervari",
        "create_fields": ["id_client", "id_masa", "data_ora_rezervare", "numar_persoane", "status"],
        "update_fields": ["id_masa", "data_ora_rezervare", "numar_persoane", "status"],
        "list_fields": ["id_rezervare", "id_client", "id_masa", "data_ora_rezervare", "numar_persoane", "status", "data_creare"],
        "default_sort": "id_rezervare DESC",
        "choices": {"status": ["In asteptare", "Confirmata", "Anulata", "Finalizata"]},
        "children": [{"table": "rezervari_meniuri", "fk": "id_rezervare"}],
        "fk_dropdowns": {
            "id_client": ("clienti", "id_client", "nume_client"),
            "id_masa": ("mese", "id_masa", "cod_masa"),
        },
    },
    "meniuri": {
        "pk": "id_meniu",
        "title": "Meniuri",
        "create_fields": ["cod_meniu", "nume_meniu", "pret"],
        "update_fields": ["nume_meniu", "pret"],
        "list_fields": ["id_meniu", "cod_meniu", "nume_meniu", "pret"],
        "default_sort": "id_meniu DESC",
        "children": [
            {"table": "rezervari_meniuri", "fk": "id_meniu"},
        ],
    },
    "rezervari_meniuri": {
        "pk": "id",
        "title": "Meniuri Rezervate",
        "create_fields": ["id_rezervare", "id_meniu", "cantitate"],
        "update_fields": ["cantitate"],
        "list_fields": ["id", "id_rezervare", "id_meniu", "cantitate"],
        "default_sort": "id DESC",
        "fk_dropdowns": {
            "id_rezervare": ("rezervari", "id_rezervare", "id_rezervare"),
            "id_meniu": ("meniuri", "id_meniu", "nume_meniu"),
        },
    },
    "user_log": {
        "pk": "id",
        "title": "Istoric Utilizatori",
        "create_fields": ["id_user", "action"],
        "update_fields": [],
        "list_fields": ["id", "id_user", "action", "created_at"],
        "default_sort": "id DESC",
        "fk_dropdowns": {"id_user": ("users", "id_user", "username")},
    },
}

def ensure_table_allowed(table):
    if table not in CRUD_CONFIG:
        abort(404)
    return CRUD_CONFIG[table]

def has_any_user():
    try:
        rows = run_select("SELECT id_user FROM users LIMIT 1;")
        return bool(rows)
    except Exception:
        return False

def record_exists(table, field, value):
    ensure_table_allowed(table)
    q = f"SELECT 1 FROM {table} WHERE {field}=%s LIMIT 1;"
    return bool(run_select(q, (value,)))

def fetch_list(table):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} ORDER BY {cfg.get('default_sort', pk+' DESC')};"
    rows = run_select(q)
    return cols, rows

def fetch_by_id(table, rec_id):
    cfg = ensure_table_allowed(table)
    pk = cfg["pk"]
    cols = cfg["list_fields"]
    if cols[0] != pk:
        cols = [pk] + [c for c in cols if c != pk]
    q = f"SELECT {', '.join(cols)} FROM {table} WHERE {pk}=%s LIMIT 1;"
    rows = run_select(q, (rec_id,))
    return cols, (rows[0] if rows else None)

def build_fk_options(cfg):
    options = {}
    for field, spec in cfg.get("fk_dropdowns", {}).items():
        parent_table, parent_pk, label_col = spec
        rows = run_select(
            f"SELECT {parent_pk}, {label_col} FROM {parent_table} ORDER BY {parent_pk} DESC;"
        )
        options[field] = [(str(r[0]), str(r[1])) for r in rows]
    return options

def insert_record(table, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["create_fields"]

    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        values.append(v)

    for f, v in zip(fields, values):
        if f.endswith("_id") and "fk_dropdowns" in cfg and f in cfg["fk_dropdowns"]:
            parent_table, parent_pk, _label = cfg["fk_dropdowns"][f]
            if not record_exists(parent_table, parent_pk, v):
                raise ValueError(f"Valoare invalida pentru {f} (nu exista in {parent_table}).")

    cols = ", ".join(fields)
    placeholders = ", ".join(["%s"] * len(fields))
    q = f"INSERT INTO {table} ({cols}) VALUES ({placeholders});"
    run_execute(q, tuple(values))

def update_record(table, rec_id, form):
    cfg = ensure_table_allowed(table)
    fields = cfg["update_fields"]
    if not fields:
        raise ValueError("Acest tabel nu are UPDATE in template.")

    pairs = []
    values = []
    for f in fields:
        v = (form.get(f) or "").strip()
        if v == "":
            raise ValueError(f"Camp obligatoriu lipsa: {f}")
        pairs.append(f"{f}=%s")
        values.append(v)

    values.append(rec_id)
    q = f"UPDATE {table} SET {', '.join(pairs)} WHERE {cfg['pk']}=%s;"
    run_execute(q, tuple(values))

def delete_record_safe(table, rec_id):
    cfg = ensure_table_allowed(table)

    for ch in cfg.get("children", []):
        run_execute(f"DELETE FROM {ch['table']} WHERE {ch['fk']}=%s;", (rec_id,))

    run_execute(f"DELETE FROM {table} WHERE {cfg['pk']}=%s;", (rec_id,))

def allowed_fields_for_table(table: str):
    cfg = ensure_table_allowed(table)
    fields = set()
    for k in ("create_fields", "update_fields", "list_fields"):
        for f in cfg.get(k, []):
            fields.add(f)
    fields.add(cfg["pk"])
    for f in cfg.get("fk_dropdowns", {}).keys():
        fields.add(f)
    return sorted(fields)

@app.route("/api/sqli/query", methods=["POST"])
def api_sqli_query():
    table = (request.form.get("table") or "").strip()
    field = (request.form.get("field") or "").strip()
    value = (request.form.get("value") or "").strip()
    mode = (request.form.get("mode") or "safe").strip().lower()

    ensure_table_allowed(table)

    allowed_fields = allowed_fields_for_table(table)
    if field not in allowed_fields:
        return {"ok": False, "error": f"Camp invalid. Permis: {', '.join(allowed_fields)}"}, 400

    limit = 25

    try:
        if mode == "unsafe":
            sql = f"SELECT * FROM {table} WHERE {field} = '{value}' LIMIT {limit};"
            rows = run_select(sql)
        else:
            sql = f"SELECT * FROM {table} WHERE {field} = %s LIMIT {limit};"
            rows = run_select(sql, (value,))

        cols = [c[0] for c in run_select(f"SHOW COLUMNS FROM {table};")]
        data = [list(r) for r in rows]

        return {
            "ok": True,
            "mode": mode,
            "sql": sql,
            "columns": cols,
            "rows": data,
            "count": len(data),
        }
    except Exception as e:
        return {"ok": False, "error": str(e), "mode": mode}, 500

@app.route("/sqli-lab", methods=["GET"])
def sqli_lab():
    tables = []
    for t, cfg in CRUD_CONFIG.items():
        tables.append({
            "name": t,
            "title": cfg.get("title", t),
            "fields": allowed_fields_for_table(t)
        })
    return render_template("sqli_lab.html", site_cfg=CRUD_CONFIG, tables=tables)

@app.before_request
def guard_if_no_users():
    allowed = {"/", "/setup", "/seed-admin", "/search"}
    if request.path.startswith("/static/"):
        return
    if not has_any_user() and request.path not in allowed:
        return redirect(url_for("setup_required"))

@app.route("/")
def index():
    counts = {}
    ready = has_any_user()
    for t in CRUD_CONFIG.keys():
        try:
            counts[t] = run_select(f"SELECT COUNT(*) FROM {t};")[0][0] if ready else 0
        except Exception:
            counts[t] = 0
    return render_template("index.html", site_cfg=CRUD_CONFIG, counts=counts, ready=ready)

@app.route("/setup")
def setup_required():
    return render_template("setup_required.html", site_cfg=CRUD_CONFIG)

@app.route("/seed-admin")
def seed_admin():
    if has_any_user():
        flash("Exista deja utilizatori.", "info")
        return redirect(url_for("crud_list", table="users"))

    run_execute("INSERT INTO users (username, password_hash) VALUES (%s, %s);", ("admin", "hash_admin"))
    flash("Admin demo creat (admin).", "success")
    return redirect(url_for("crud_list", table="users"))

@app.route("/crud/<table>")
def crud_list(table):
    cfg = ensure_table_allowed(table)
    cols, rows = fetch_list(table)
    return render_template(
        "crud_list.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        cols=cols,
        rows=rows,
    )

@app.route("/crud/<table>/create", methods=["GET", "POST"])
def crud_create(table):
    cfg = ensure_table_allowed(table)
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            insert_record(table, request.form)
            flash("Creat cu succes.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="create",
        fields=cfg["create_fields"],
        values={},
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
    )

@app.route("/crud/<table>/edit/<int:rec_id>", methods=["GET", "POST"])
def crud_edit(table, rec_id):
    cfg = ensure_table_allowed(table)
    cols, row = fetch_by_id(table, rec_id)
    if not row:
        abort(404)

    values = dict(zip(cols, row))
    fk_options = build_fk_options(cfg)

    if request.method == "POST":
        try:
            update_record(table, rec_id, request.form)
            flash("Update reusit.", "success")
            return redirect(url_for("crud_list", table=table))
        except Exception as e:
            flash(str(e), "error")

    return render_template(
        "crud_form.html",
        site_cfg=CRUD_CONFIG,
        table=table,
        table_cfg=cfg,
        mode="edit",
        fields=cfg["update_fields"],
        values=values,
        fk_options=fk_options,
        choices=cfg.get("choices", {}),
        rec_id=rec_id,
    )

@app.route("/crud/<table>/delete/<int:rec_id>", methods=["POST"])
def crud_delete(table, rec_id):
    ensure_table_allowed(table)
    try:
        delete_record_safe(table, rec_id)
        flash("Sters cu succes!", "success")
    except Exception as e:
        flash(str(e), "error")
    return redirect(url_for("crud_list", table=table))

@app.route("/search", methods=["GET", "POST"])
def search():
    result = None
    if request.method == "POST":
        table = (request.form.get("table") or "").strip()
        field = (request.form.get("field") or "").strip()
        value = (request.form.get("value") or "").strip()
        try:
            ensure_table_allowed(table)
            exists = record_exists(table, field, value)
            result = {"ok": True, "exists": exists, "table": table, "field": field, "value": value}
        except Exception as e:
            result = {"ok": False, "error": str(e)}

    return render_template("search.html", site_cfg=CRUD_CONFIG, result=result)

if __name__ == "__main__":
    app.run(debug=True)