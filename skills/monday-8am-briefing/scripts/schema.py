#!/usr/bin/env python3
"""The canonical tables the engine understands, plus presets for known Clio reports.

A firm's export is mapped onto these tables once (mapping.json). Everything downstream works
on the canonical fields, so the same math runs no matter which system the data came from.
"""
from __future__ import annotations

# field: kind. kinds: date, number, text, key
ENTITIES = {
    "leads": {
        "about": "One row per lead or intake inquiry.",
        "required": ["created_date", "source"],
        "fields": {"lead_key": "key", "created_date": "date", "source": "text", "outcome": "text",
                   "outcome_date": "date", "practice_area": "text", "est_value": "number"},
        "outcome_values": ["signed", "lost", "open"],
    },
    "contacts": {
        "about": "One row per lead with when it arrived and when someone first reached out.",
        "required": ["lead_key", "received_at"],
        "fields": {"lead_key": "key", "received_at": "date", "first_contact_at": "date"},
    },
    "spend": {
        "about": "Marketing spend by month and source.",
        "required": ["period", "source", "amount"],
        "fields": {"period": "date", "source": "text", "amount": "number"},
    },
    "time": {
        "about": "One row per time entry, with what was worked, billed and collected.",
        "required": ["date", "billable_amount", "billed_amount"],
        "fields": {"date": "date", "attorney": "text", "practice_area": "text", "billing_method": "text",
                   "matter_id": "key", "billable_amount": "number", "billed_amount": "number",
                   "collected_amount": "number", "outstanding_amount": "number", "hours": "number"},
    },
    "matters": {
        "about": "One row per matter.",
        "required": ["matter_id"],
        "fields": {"matter_id": "key", "client": "text", "practice_area": "text", "status": "text",
                   "opened_date": "date", "closed_date": "date", "attorney": "text", "billing_method": "text",
                   "ar_balance": "number"},
        "status_values": ["open", "closed"],
    },
    "ar": {
        "about": "Accounts receivable aging, one row per bill, as of one snapshot date.",
        "required": ["matter_id", "total"],
        "fields": {"matter_id": "key", "attorney": "text", "invoice_id": "key", "b_current": "number",
                   "b_1_30": "number", "b_31_60": "number", "b_61_90": "number", "b_91_plus": "number",
                   "total": "number"},
        "file_level": ["snapshot_date"],
    },
    "revenue": {
        "about": "Revenue by matter for a date range.",
        "required": ["collected"],
        "fields": {"matter_id": "key", "practice_area": "text", "attorney": "text", "billed": "number",
                   "collected": "number"},
        "file_level": ["period_start", "period_end"],
    },
    "lead_summary": {
        "about": "A lead source summary with no dates, one row per source.",
        "required": ["source", "hired"],
        "fields": {"source": "text", "intake": "number", "hired": "number", "not_hired": "number",
                   "conversion_rate": "number", "revenue": "number", "spend": "number"},
    },
}

# Column signatures from Clio's published report formats (help.clio.com, checked 2026-10-03).
# A file matches when most of the signature columns are present.
PRESETS = {
    "clio_grow_matter_revenue": {
        "system": "Clio Grow", "report": "Matter revenue report", "entity": "leads",
        "signature": ["Contact", "Email", "Source", "Referred by", "Matter", "Matter type",
                      "Matter status - top level", "Matter status - detailed", "Status date", "Created at",
                      "Estimated value"],
        "columns": {"lead_key": "Email", "created_date": "Created at", "source": "Source",
                    "outcome": "Matter status - top level", "outcome_date": "Status date",
                    "practice_area": "Matter type", "est_value": "Estimated value"},
        "value_maps": {"outcome": {"Hired": "signed", "Not hired": "lost", "Did Not Hire": "lost", "Intake": "open"}},
        "needs_value_map": ["practice_area"],
    },
    "clio_grow_lead_source": {
        "system": "Clio Grow", "report": "Lead source revenue report", "entity": "lead_summary",
        "signature": ["Source", "Intake matters", "Hired matters", "Not hired matters", "Hired conversion rate",
                      "Estimated value", "Revenue", "Spend"],
        "columns": {"source": "Source", "intake": "Intake matters", "hired": "Hired matters",
                    "not_hired": "Not hired matters", "conversion_rate": "Hired conversion rate",
                    "revenue": "Revenue", "spend": "Spend"},
    },
    "clio_realization": {
        "system": "Clio Manage", "report": "Realization report", "entity": "time",
        "signature": ["Time entry date", "User", "Original Billable Total", "Billed Time Amount",
                      "Billed Time Collected", "Billed Time Outstanding", "Matter Billing Method",
                      "Practice Area", "Responsible Attorney"],
        "columns": {"date": "Time entry date", "attorney": "User", "practice_area": "Practice Area",
                    "billing_method": "Matter Billing Method", "matter_id": "Matter Number",
                    "billable_amount": "Original Billable Total", "billed_amount": "Billed Time Amount",
                    "collected_amount": "Billed Time Collected", "outstanding_amount": "Billed Time Outstanding",
                    "hours": "Quantity"},
    },
    "clio_ar_aging": {
        "system": "Clio Manage", "report": "Accounts receivable aging report", "entity": "ar",
        "signature": ["Matter", "Bill id", "Current", "1-30 days", "31-60 days", "61-90 days", "91+ days", "Total"],
        "columns": {"matter_id": "Matter", "attorney": "Responsible attorney", "invoice_id": "Bill id",
                    "b_current": "Current", "b_1_30": "1-30 days", "b_31_60": "31-60 days",
                    "b_61_90": "61-90 days", "b_91_plus": "91+ days", "total": "Total"},
        "needs_file_level": ["snapshot_date"],
    },
    "clio_matters": {
        "system": "Clio Manage", "report": "Matters report", "entity": "matters",
        "signature": ["Client", "Matter", "Description", "Practice area", "Status", "Responsible attorney",
                      "Originating attorney", "Billable", "Accounts receivable", "Latest bill"],
        "columns": {"matter_id": "Matter", "client": "Client", "practice_area": "Practice area",
                    "status": "Status", "attorney": "Responsible attorney", "ar_balance": "Accounts receivable"},
        "value_maps": {"status": {"Open": "open", "Pending": "open", "Closed": "closed"}},
    },
    "clio_revenue": {
        "system": "Clio Manage", "report": "Revenue report", "entity": "revenue",
        "signature": ["Matter", "Unbilled time", "Billed time", "Collected time", "Collected expense",
                      "Collected uncategorized", "Client total", "Practice Area", "Responsible Attorney"],
        "columns": {"matter_id": "Matter", "practice_area": "Practice Area", "attorney": "Responsible Attorney",
                    "billed": ["Billed time", "Billed expense"],
                    "collected": ["Collected time", "Collected expense", "Collected uncategorized"]},
        "needs_file_level": ["period_start", "period_end"],
    },
}

# Header words that suggest a canonical field when a file does not match a preset.
SYNONYMS = {
    "lead_key": ["email", "contact email", "lead id", "contact id", "matter id", "id"],
    "created_date": ["created at", "created", "date created", "lead date", "inquiry date", "intake date",
                     "date received", "received", "date opened", "date"],
    "source": ["source", "lead source", "referral source", "marketing source", "channel", "how did you hear"],
    "outcome": ["status", "stage", "outcome", "hired", "retained", "matter status"],
    "outcome_date": ["status date", "date hired", "retained date", "signed date", "date signed", "closed date"],
    "practice_area": ["practice area", "practice", "matter type", "case type", "type"],
    "est_value": ["estimated value", "est value", "case value", "value"],
    "received_at": ["received at", "received", "inquiry time", "lead time", "call time"],
    "first_contact_at": ["first contact at", "first contact", "first response", "contacted at", "first reply"],
    "period": ["month", "period", "date"],
    "amount": ["spend", "cost", "amount", "ad spend"],
    "attorney": ["attorney", "responsible attorney", "lawyer", "lawyer in charge", "user", "timekeeper"],
    "matter_id": ["matter", "matter id", "matter number", "case", "case number", "file number"],
    "opened_date": ["opened", "open date", "date opened", "matter open date"],
    "closed_date": ["closed", "close date", "date closed"],
    "status": ["status", "stage", "matter status"],
    "billing_method": ["billing", "billing method", "matter billing method", "fee type"],
    "billable_amount": ["original billable total", "billable", "worked", "wip"],
    "billed_amount": ["billed time amount", "billed", "invoiced"],
    "collected_amount": ["billed time collected", "collected", "paid"],
    "collected": ["collected", "payments", "paid"],
    "billed": ["billed", "invoiced"],
    "total": ["total", "balance", "outstanding"],
}
