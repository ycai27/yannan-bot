from datetime import datetime
import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

from classes import MonthlyBudget


def test_add_expense_adds_row():
    budget = MonthlyBudget(limit=1000)

    budget.add_expense(
        date=datetime(2026, 6, 21),
        cost=12.50,
        category="Food",
        notes="Chipotle",
    )

    assert len(budget.expenses) == 1
    assert budget.expenses.loc[0, "cost"] == 12.50
    assert budget.expenses.loc[0, "category"] == "Food"
    assert budget.expenses.loc[0, "notes"] == "Chipotle"


def test_edit_expense_updates_row():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")

    budget.edit_expense(index=0, cost=15.00, category="Dining")

    assert budget.expenses.loc[0, "cost"] == 15.00
    assert budget.expenses.loc[0, "category"] == "Dining"
    assert budget.expenses.loc[0, "notes"] == "Chipotle"


def test_delete_expense_removes_row_and_resets_index():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")
    budget.add_expense(datetime(2026, 6, 22), 5.00, "Coffee", "Starbucks")

    budget.delete_expense(index=0)

    assert len(budget.expenses) == 1
    assert budget.expenses.index.tolist() == [0]
    assert budget.expenses.loc[0, "notes"] == "Starbucks"


def test_edit_missing_index_raises_error():
    budget = MonthlyBudget(limit=1000)

    with pytest.raises(IndexError):
        budget.edit_expense(index=0, cost=10)


def test_delete_missing_index_raises_error():
    budget = MonthlyBudget(limit=1000)

    with pytest.raises(IndexError):
        budget.delete_expense(index=0)


def test_total_spent():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")
    budget.add_expense(datetime(2026, 6, 22), 5.00, "Coffee", "Starbucks")

    assert budget.total_spent() == 17.50


def test_summary():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 200, "Rent", "June rent")

    assert budget.summary() == {
        "limit": 1000,
        "spent": 200,
        "remaining": 800,
    }


def test_list_expenses_returns_dataframe_copy():
    budget = MonthlyBudget(limit=1000)
    budget.add_expense(datetime(2026, 6, 21), 12.50, "Food", "Chipotle")

    rows = budget.list_expenses()

    assert isinstance(rows, pd.DataFrame)
    assert len(rows) == 1

    rows.loc[0, "cost"] = 999

    assert budget.expenses.loc[0, "cost"] == 12.50
