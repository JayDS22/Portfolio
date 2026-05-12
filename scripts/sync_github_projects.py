#!/usr/bin/env python3
"""Fetch JayDS22's public GitHub repos, infer a domain for each,
and write data/github.json - the data source for the 3D project graph
on /explore/."""

import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

GITHUB_USER = "JayDS22"

# Repos to skip entirely. Two buckets:
#   1. Site infra (the portfolio itself, GH profile config, etc.)
#   2. Learning / coursework / exercise / collection repos that are not
#      standalone projects. The graph is meant to surface project work,
#      not assignments or generic language notes.
EXCLUDE_REPOS = {
    # site infra
    "Portfolio",
    "JayDS22",
    "jayds22.github.io",
    "portfolioweb",
    # coursework, exercises, learning notes, generic collections
    "AIOps-Roadmap",
    "Architecture-Building-Concepts",
    "Coursera-ML-Assignments",
    "data604",
    "Limited_Submissions",
    "Machine-Learning-NLP-Deep-Learning",
    "Power-BI-Projects",
    "Python",
    "SQL-Basic-Excercises",
    "SQL-MySQL-Excercises",
    "Tableau-Repository",
}

# Domain hubs. First match wins (order matters - put more specific domains
# above broader ones like ML & Classification, which is the fallback).
DOMAINS = [
    {
        "id": "computer-vision",
        "name": "Computer Vision",
        "color": "#7c5cff",
        "keywords": [
            "yolo", "computer vision", "object detection", "face mask",
            "image enhancement", "medical image", "lidar", "point cloud",
            "tracking", "surveillance", "pedestrian", "ada compliance",
            "vehicle safety", "metal surface", "industrial quality",
            "kidney disease", "breast cancer", "trajectory", "digital twin",
            "space image", "multi target detection",
        ],
    },
    {
        "id": "llm-agents",
        "name": "LLM & Agents",
        "color": "#22d3ee",
        "keywords": [
            "llm", " rag", "rag ", "gpt", "langchain", "langgraph",
            "autogen", "agentic", "agentforge", "constellation",
            "chatbot", "openai", "claude", "anthropic", "retrieve chat",
            "blog generator", "llama", "code review", "lucid", "kubeflow docs",
            "multi agent", "multi agentic",
        ],
    },
    {
        "id": "nlp-speech",
        "name": "NLP & Speech",
        "color": "#f472b6",
        "keywords": [
            "nlp", "speech", "nemo", "spam", "sentence",
            "natural language", "text normalization",
        ],
    },
    {
        "id": "stats-bayesian",
        "name": "Statistics & Bayesian",
        "color": "#facc15",
        "keywords": [
            "bayesian", "monte carlo", "thompson", "calibration",
            "survival", "cox", "kaplan", "mcmc", "experimentation",
            "a/b", "ab test", "stress test", "regulatory",
            "pd lgd", "credit risk",
        ],
    },
    {
        "id": "quant-finance",
        "name": "Quant & Finance",
        "color": "#10b981",
        "keywords": [
            "quant", "trading", "portfolio", "market", "fraud",
            "credit", "financial", "fintech",
            "prediction market", "bidding", "advertising", "campaign",
            "blockchain",
        ],
    },
    {
        "id": "time-series",
        "name": "Time Series",
        "color": "#fb923c",
        "keywords": [
            "forecasting", "lstm", "time series", "demand",
            "transportation", "traffic", "predictive maintenance",
            "durability", "transformer based trajectory",
        ],
    },
    {
        "id": "rl-robotics",
        "name": "RL & Robotics",
        "color": "#ef4444",
        "keywords": [
            "reinforcement", "multi robot", "robot",
            "autonomous navigation", "ddpg", "ppo", "apollo",
        ],
    },
    {
        "id": "mlops-infra",
        "name": "MLOps & Data Infra",
        "color": "#a855f7",
        "keywords": [
            "kubernetes", "kubeflow", "terraform", "ansible", "devops",
            "mlops", "ci cd", "docker", "k8s", "distributed", "etl",
            " dbt", "snowflake", "airflow", "spark", "data warehouse",
            "big data", "dwh", "infrastructure", "kafka", "delta lake",
            "trino", "flink", "azure", "powerbi", "iac", " 5g",
            "network orchestrator", "logs aggregation", "sql",
            "tableau", "multi gpu", "gpu", "automated infrastructure",
            "chip design", "semiconductor",
        ],
    },
    {
        "id": "ml-general",
        "name": "ML & Classification",
        "color": "#94a3b8",
        "keywords": [
            "churn", "classification", "ensemble", "xgboost",
            "random forest", "scikit", "sklearn", "regression",
            "machine learning", "recommendation", "recommender",
            "marketplace", "hungarian", "optimization", "ml model",
            "shipping", "insurance", "adult census", "deeplearning",
            "spam detection", "data604", "data602", "analytics",
        ],
    },
]


def normalize(s: str) -> str:
    return s.lower().replace("-", " ").replace("_", " ")


def infer_domain(repo: dict) -> str:
    text = " ".join([
        repo.get("name") or "",
        repo.get("description") or "",
        " ".join(repo.get("topics") or []),
    ])
    text = normalize(text)
    # pad with spaces so word-boundary-ish keywords like " 5g" / " dbt" match safely
    text = " " + text + " "
    for d in DOMAINS:
        for kw in d["keywords"]:
            if normalize(kw) in text:
                return d["id"]
    return "ml-general"


def fetch_repos() -> list:
    url = (
        f"https://api.github.com/users/{GITHUB_USER}/repos"
        "?per_page=100&sort=updated"
    )
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": f"{GITHUB_USER}-portfolio-sync",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def build_payload(repos: list) -> dict:
    nodes: list[dict] = []
    links: list[dict] = []

    domains_by_id = {d["id"]: d for d in DOMAINS}
    used_domains: set[str] = set()

    # Add repo nodes (sorted by stars desc, then name)
    for r in sorted(repos, key=lambda x: (-(x.get("stargazers_count") or 0), x["name"].lower())):
        if r.get("fork") or r.get("archived"):
            continue
        if r["name"] in EXCLUDE_REPOS:
            continue
        # skip empty placeholder repos with no description AND tiny size
        if not r.get("description") and (r.get("size") or 0) < 30:
            continue

        domain_id = infer_domain(r)
        used_domains.add(domain_id)
        domain = domains_by_id[domain_id]

        nodes.append({
            "id": f"repo:{r['name']}",
            "name": r["name"].replace("-", " ").replace("_", " "),
            "type": "repo",
            "domain": domain_id,
            "color": domain["color"],
            "val": max(3, (r.get("stargazers_count") or 0) * 4 + 3),
            "stars": r.get("stargazers_count") or 0,
            "language": r.get("language") or "",
            "description": (r.get("description") or "").strip(),
            "url": r["html_url"],
            "updated_at": r.get("updated_at"),
        })
        links.append({"source": f"repo:{r['name']}", "target": f"domain:{domain_id}"})

    # Prepend domain hub nodes (only those that ended up with at least one repo)
    domain_nodes = [
        {
            "id": f"domain:{d['id']}",
            "name": d["name"],
            "type": "domain",
            "color": d["color"],
            "val": 50,
        }
        for d in DOMAINS
        if d["id"] in used_domains
    ]
    nodes = domain_nodes + nodes

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "user": GITHUB_USER,
        "domain_count": len(domain_nodes),
        "repo_count": len(nodes) - len(domain_nodes),
        "nodes": nodes,
        "links": links,
    }


def main() -> int:
    try:
        repos = fetch_repos()
    except urllib.error.HTTPError as e:
        print(f"GitHub API error: {e.code} {e.reason}", file=sys.stderr)
        return 1

    payload = build_payload(repos)

    out_path = Path(__file__).resolve().parent.parent / "data" / "github.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(payload, indent=2) + "\n")

    print(
        f"Wrote {out_path}: "
        f"{payload['repo_count']} repos across {payload['domain_count']} domains"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
