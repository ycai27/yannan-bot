from datetime import datetime
import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from budget_agent import _parse_date, _build_tools
from classes import MonthlyBudget


def tools_by_name(budget):
    tools = _build_tools(budget)
    return {tool.name: tool for tool in tools}


def test_parse_date_valid():
    parsed = _parse_date("2026-06-21")

    assert parsed == datetime(2026, 6, 21)


def test_parse_date_invalid_format_raises_error():
    with pytest.raises(ValueError):
        _parse_date("06/21/2026")


def test_add_expense_tool_adds_expense():
    budget = MonthlyBudget(limit=1000)
    tools = tools_by_name(budget)

    result = tools["add_expense"].invoke({
        "date": "2026-06-21",
        "cost": 12.50,
        "category": "Food",
        "notes": "Chipotle",
    })

    assert "Added expense" in result
    assert len(budget.expenses) == 1
    assert budget.expenses.loc[0, "cost"] == 12.50
    assert budget.expenses.loc[0, "category"] == "Food"


def test_edit_expense_tool_updates_expense():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")
    tools = tools_by_name(budget)

    result = tools["edit_expense"].invoke({
        "index": 0,
        "cost": 15.00,
        "category": "Dining",
    })

    assert "Updated expense" in result
    assert budget.expenses.loc[0, "cost"] == 15.00
    assert budget.expenses.loc[0, "category"] == "Dining"


def test_delete_expense_tool_deletes_expense():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")
    tools = tools_by_name(budget)

    result = tools["delete_expense"].invoke({"index": 0})

    assert "Deleted expense" in result
    assert len(budget.expenses) == 0


def test_list_expenses_tool_returns_json_serializable_rows():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")
    tools = tools_by_name(budget)

    result = tools["list_expenses"].invoke({})

    assert isinstance(result, list)
    assert result == [
        {
            "date": "2026-06-21",
            "cost": 12.50,
            "category": "Food",
            "notes": "Chipotle",
        }
    ]


def test_budget_summary_tool_returns_summary():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 200, "Rent", "June rent")
    tools = tools_by_name(budget)

    result = tools["budget_summary"].invoke({})

    assert result == {
        "limit": 1000,
        "spent": 200,
        "remaining": 800,
    }
