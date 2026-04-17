from __future__ import annotations

import json
import os
from dotenv import load_dotenv

from datetime import datetime
from typing import Any

from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent

from classes import MonthlyBudget


DATE_FMT = "%Y-%m-%d"


def _parse_date(date_str: str) -> datetime:
    return datetime.strptime(date_str, DATE_FMT)


def _build_tools(budget: MonthlyBudget):
    @tool
    def add_expense(date: str, cost: float, category: str, notes: str) -> str:
        """
        Add one expense row to the monthly budget.
        date format must be YYYY-MM-DD.
        """
        budget.add_expense(
            date=_parse_date(date),
            cost=cost,
            category=category,
            notes=notes,
        )
        return f"Added expense. Total rows: {len(budget.expenses)}"

    @tool
    def edit_expense(
        index: int,
        date: str | None = None,
        cost: float | None = None,
        category: str | None = None,
        notes: str | None = None,
    ) -> str:
        """
        Edit an expense by row index.
        date format must be YYYY-MM-DD when provided.
        """
        parsed_date = _parse_date(date) if date is not None else None
        budget.edit_expense(
            index=index,
            date=parsed_date,
            cost=cost,
            category=category,
            notes=notes,
        )
        return f"Updated expense at index {index}."

    @tool
    def delete_expense(index: int) -> str:
        """Delete one expense row by row index."""
        budget.delete_expense(index=index)
        return f"Deleted expense at index {index}. Total rows: {len(budget.expenses)}"

    @tool
    def list_expenses() -> list[dict[str, Any]]:
        """Return all expenses as JSON-serializable rows."""
        rows = budget.expenses.copy()
        if rows.empty:
            return []
        rows["date"] = rows["date"].astype(str)
        return rows.to_dict(orient="records")

    @tool
    def budget_summary() -> dict[str, float]:
        """Return limit, spent, and remaining amounts."""
        spent = float(budget.expenses["cost"].sum()) if not budget.expenses.empty else 0.0
        return {
            "limit": float(budget.limit),
            "spent": spent,
            "remaining": float(budget.limit - spent),
        }

    return [add_expense, edit_expense, delete_expense, list_expenses, budget_summary]


def build_budget_agent(limit: float = 1000.0, model: str = "gpt-5.4-mini"):
    budget = MonthlyBudget(limit=limit)
    llm = ChatOpenAI(model=model, temperature=0)

    prompt = (
        "You are a monthly budget assistant. "
        "Use tools to add/edit/delete/list expenses and answer budget questions. "
        "Always use YYYY-MM-DD for dates when calling tools."
    )
    return create_react_agent(model=llm, tools=_build_tools(budget), prompt=prompt)


def run_cli() -> None:
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError("Set OPENAI_API_KEY before running this script.")

    graph = build_budget_agent()
    print("Budget agent ready. Type 'exit' to quit.")

    while True:
        user_input = input("> ").strip()
        if user_input.lower() in {"exit", "quit"}:
            break

        result = graph.invoke({"messages": [{"role": "user", "content": user_input}]})
        messages = result.get("messages", [])
        if not messages:
            print("(no response)")
            continue

        final_message = messages[-1].content
        if isinstance(final_message, str):
            print(final_message)
        else:
            print(json.dumps(final_message, indent=2))


if __name__ == "__main__":
    run_cli()
