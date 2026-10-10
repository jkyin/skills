#!/usr/bin/env python3
"""Audit monthly first-parent activity from complete, read-only GitLab JSON exports."""

import argparse
import datetime as dt
import json
from pathlib import Path
import re
import sys
from zoneinfo import ZoneInfo


def parse_timestamp(value):
    if not isinstance(value, str) or not value:
        raise ValueError("Expected a nonempty ISO timestamp")
    parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"Timestamp must include a timezone: {value}")
    return parsed


def period(month, timezone, as_of=None):
    zone = ZoneInfo(timezone)
    if not re.fullmatch(r"\d{4}-\d{2}", month):
        raise ValueError("--month must be YYYY-MM")
    year, number = map(int, month.split("-"))
    start = dt.datetime(year, number, 1, tzinfo=zone)
    end = dt.datetime(year + (number == 12), number % 12 + 1, 1, tzinfo=zone)
    if as_of and re.fullmatch(r"\d{4}-\d{2}-\d{2}", as_of):
        date = dt.date.fromisoformat(as_of) + dt.timedelta(days=1)
        cutoff = dt.datetime.combine(date, dt.time.min, zone) - dt.timedelta(microseconds=1)
    else:
        cutoff = parse_timestamp(as_of).astimezone(zone) if as_of else dt.datetime.now(zone)
    if cutoff < start:
        raise ValueError("The cutoff is before the requested month")
    return zone, start, end, cutoff


def index_commits(commits):
    if not isinstance(commits, list):
        raise ValueError("--commits must contain the complete paginated JSON array")
    indexed = {}
    for commit in commits:
        if not isinstance(commit, dict) or not isinstance(commit.get("id"), str):
            raise ValueError("Each commit must have an id")
        sha = commit["id"]
        if not sha:
            raise ValueError("A commit id cannot be empty")
        parents = commit.get("parent_ids")
        if not isinstance(parents, list) or any(not isinstance(p, str) or not p for p in parents):
            raise ValueError(f"Missing or invalid parent_ids for {sha}")
        parse_timestamp(commit.get("authored_date"))
        prior = indexed.get(sha)
        if prior and any(prior.get(k) != commit.get(k) for k in ("authored_date", "parent_ids")):
            raise ValueError(f"Conflicting records for commit {sha}")
        indexed[sha] = commit
    return indexed


def first_parent_chain(mr, indexed):
    if not isinstance(mr, dict):
        raise ValueError("--mr must contain one MR detail object")
    refs = mr.get("diff_refs") or {}
    head = mr.get("sha") or refs.get("head_sha")
    if mr.get("sha") and refs.get("head_sha") and mr["sha"] != refs["head_sha"]:
        raise ValueError("MR sha and diff_refs.head_sha differ; refresh the snapshot")
    if not head or head not in indexed:
        raise ValueError("MR head is missing from commits; refresh and retrieve every page")
    chain, seen, current = [], set(), head
    while current in indexed:
        if current in seen:
            raise ValueError("A cycle was found in first-parent history")
        seen.add(current)
        commit = indexed[current]
        chain.append(commit)
        parents = commit["parent_ids"]
        current = parents[0] if parents else None
    return head, current, chain


def metrics(commits, zone, start, end, cutoff):
    dated = [(c, parse_timestamp(c["authored_date"]).astimezone(zone)) for c in commits]
    included = [(c, when) for c, when in dated if when <= cutoff]
    monthly = [(c, when) for c, when in included if start <= when < end]
    days = sorted({when.date().isoformat() for _, when in included})
    month_days = sorted({when.date().isoformat() for _, when in monthly})
    return {
        "commits": len(included),
        "month_commits": len(monthly),
        "commit_ratio": len(monthly) / len(included) if included else None,
        "days": len(days),
        "month_days": len(month_days),
        "day_ratio": len(month_days) / len(days) if days else None,
        "active_dates": days,
        "month_active_dates": month_days,
        "excluded_after_cutoff": len(dated) - len(included),
    }


def audit(mr, commits, month, timezone="Asia/Shanghai", as_of=None):
    zone, start, end, cutoff = period(month, timezone, as_of)
    indexed = index_commits(commits)
    head, boundary, chain = first_parent_chain(mr, indexed)
    primary = metrics(chain, zone, start, end, cutoff)
    if primary["month_days"] == 0:
        eligibility = "no_month_activity"
    elif primary["month_days"] * 3 >= primary["days"]:
        eligibility = "eligible"
    else:
        eligibility = "needs_assessment"
    warnings = []
    if primary["excluded_after_cutoff"]:
        warnings.append("Some first-parent records are after the cutoff; verify snapshot dates.")
    if as_of:
        warnings.append("The cutoff filters authored dates only; MR/tag state needs separate historical evidence.")
    return {
        "month": month,
        "timezone": timezone,
        "month_start": start.isoformat(),
        "month_end_exclusive": end.isoformat(),
        "as_of": cutoff.isoformat(),
        "iid": mr.get("iid"),
        "head": head,
        "boundary_parent_outside_mr": boundary,
        "unique_api_records": len(indexed),
        "first_parent_records": len(chain),
        "imported_records_excluded": len(indexed) - len(chain),
        "first_parent": primary,
        "non_merge_first_parent": metrics(
            [c for c in chain if len(c["parent_ids"]) <= 1], zone, start, end, cutoff
        ),
        "all_mr_records": metrics(indexed.values(), zone, start, end, cutoff),
        "eligibility": eligibility,
        "warnings": warnings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mr", required=True, type=Path)
    parser.add_argument("--commits", required=True, type=Path)
    parser.add_argument("--month", required=True, help="YYYY-MM")
    parser.add_argument("--timezone", default="Asia/Shanghai")
    parser.add_argument("--as-of", help="ISO timestamp with timezone, or inclusive local YYYY-MM-DD")
    parser.add_argument("--output", type=Path, help="Local JSON output; stdout when omitted")
    args = parser.parse_args()
    try:
        result = audit(
            json.loads(args.mr.read_text(encoding="utf-8")),
            json.loads(args.commits.read_text(encoding="utf-8")),
            args.month,
            args.timezone,
            args.as_of,
        )
        content = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(content, encoding="utf-8")
        else:
            sys.stdout.write(content)
    except (ValueError, KeyError, TypeError, OSError) as error:
        parser.exit(2, f"Activity audit failed: {error}\n")


if __name__ == "__main__":
    main()
