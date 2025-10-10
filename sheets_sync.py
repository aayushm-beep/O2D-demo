# sheets_sync.py
import json
from datetime import date, datetime
from typing import List, Dict, Any, Tuple

import gspread
from google.oauth2.service_account import Credentials
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from config import Config
from models import Order, Product, Customer, Warehouse, Shipment

# ---- Mapping: model, natural key, and column order (must match sheet headers) ----
ENTITY_MAP = {
    "orders": {
        "model": Order,
        "key": "order_id",
        "columns": [
            "order_id","order_date","order_status","order_priority","order_type",
            "order_source","order_channel","sales_rep_id","sales_region","currency_code",
            "total_items","total_quantity","subtotal_amount","discount_amount","tax_amount",
            "shipping_amount"
        ],
        # Optional: column types for parsing imports
        "types": {
            "order_date": "date",
            "total_items": "int",
            "total_quantity": "int",
            "subtotal_amount": "float",
            "discount_amount": "float",
            "tax_amount": "float",
            "shipping_amount": "float",
        }
    },
    "products": {
        "model": Product,
        "key": "product_id",
        "columns": [
            "product_id","name","category","brand","unit_price",
            "stock_level","reorder_level","status"
        ],
        "types": {
            "unit_price": "float",
            "stock_level": "int",
            "reorder_level": "int",
        }
    },
    "customers": {
        "model": Customer,
        "key": "customer_id",
        "columns": [
            "customer_id","name","email","phone","city","state","country",
            "customer_type","credit_limit","outstanding_balance"
        ],
        "types": {
            "credit_limit": "float",
            "outstanding_balance": "float",
        }
    },
    "warehouses": {
        "model": Warehouse,
        "key": "warehouse_id",
        "columns": [
            "warehouse_id","name","location","capacity","current_utilization","status"
        ],
        "types": {
            "capacity": "int",
            "current_utilization": "int",
        }
    },
    "shipments": {
        "model": Shipment,
        "key": "shipment_id",
        "columns": [
            "shipment_id","order_id","carrier","tracking_number","status","ship_date","delivery_date"
        ],
        "types": {
            "ship_date": "date",
            "delivery_date": "date",
        }
    },
}

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

def _sa_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(Config.GOOGLE_SA_JSON, scopes=SCOPES)
    return gspread.authorize(creds)

def _ensure_worksheet(client: gspread.Client, title: str):
    sh = client.open_by_key(Config.GOOGLE_SPREADSHEET_ID)
    try:
        ws = sh.worksheet(title)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(title=title, rows=200, cols=50)
    return ws

def _to_json_safe(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()[:10]
    return v if v is not None else ""

def _parse_value(v: str, typ: str):
    v = (v or "").strip()
    if v == "":
        return None
    try:
        if typ == "int":
            return int(float(v))
        if typ == "float":
            return float(v)
        if typ == "date":
            # Accept ISO or dd/mm/yyyy
            if "-" in v:
                return datetime.fromisoformat(v).date()
            if "/" in v:
                d, m, y = v.split("/")
                return date(int(y), int(m), int(d))
        return v
    except Exception:
        return v

def export_table(session: Session, entity: str) -> Tuple[int, int]:
    """
    Export DB -> Sheet for given entity.
    Returns (written_rows, written_cols)
    """
    meta = ENTITY_MAP[entity]
    model = meta["model"]
    cols = meta["columns"]
    ws = _ensure_worksheet(_sa_client(), Config.SHEETS_TABS[entity])

    # Read from DB
    rows = session.execute(select(model)).scalars().all()

    # Prepare data: header + rows
    data = [cols]
    for r in rows:
        data.append([_to_json_safe(getattr(r, c, "")) for c in cols])

    # Clear and write
    ws.clear()
    # gspread batch write in one go
    ws.update("A1", data)
    return (len(data) - 1, len(cols))

def import_table(session: Session, entity: str) -> Dict[str, int]:
    """
    Import Sheet -> DB for given entity (upsert by natural key).
    Returns counters {inserted, updated, skipped}
    """
    meta = ENTITY_MAP[entity]
    model = meta["model"]
    key = meta["key"]
    cols = meta["columns"]
    types = meta.get("types", {})
    ws = _ensure_worksheet(_sa_client(), Config.SHEETS_TABS[entity])

    # Read all values
    values: List[List[Any]] = ws.get_all_values()
    if not values:
        return {"inserted": 0, "updated": 0, "skipped": 0}

    # Validate header
    header = values[0]
    if [h.strip() for h in header] != cols:
        raise ValueError(
            f"Header mismatch for {entity}. Expected: {cols} — Found: {header}"
        )

    # Build a dict for fast lookup of existing rows by key
    existing = {
        getattr(obj, key): obj
        for obj in session.execute(select(model)).scalars().all()
        if getattr(obj, key) is not None
    }

    inserted = 0
    updated = 0
    skipped = 0

    for row in values[1:]:
        if not any(str(cell).strip() for cell in row):
            continue  # skip empty lines
        record = dict(zip(cols, row))
        k = record.get(key)
        if not k:
            skipped += 1
            continue

        # Parse types
        for c, t in types.items():
            record[c] = _parse_value(record.get(c), t)

        # Upsert
        obj = existing.get(k)
        if obj is None:
            # Insert
            obj = model()
            setattr(obj, key, k)
            for c in cols:
                if c == key:
                    continue
                setattr(obj, c, record.get(c))
            session.add(obj)
            inserted += 1
        else:
            # Update
            changed = False
            for c in cols:
                if c == key:
                    continue
                new_v = record.get(c)
                old_v = getattr(obj, c)
                if str(new_v) != str(old_v):
                    setattr(obj, c, new_v)
                    changed = True
            if changed:
                updated += 1
            else:
                skipped += 1

    session.commit()
    return {"inserted": inserted, "updated": updated, "skipped": skipped}
