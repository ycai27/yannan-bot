from datetime import datetime
from typing import Union
import pandas as pd

class MonthlyBudget:
    limit: float
    expenses: pd.DataFrame

    def __init__(self, limit: float):
        self.limit = limit
        self.expenses = pd.DataFrame(columns=["date", "cost", "category", "notes"])

    def add_expense(
        self, date: datetime, cost: float, category: str, notes: str
    ) -> None:
        self.expenses.loc[len(self.expenses)] = [date, cost, category, notes]

    def edit_expense(
        self,
        index: int,
        date: Union[datetime, None] = None,
        cost: Union[float, None] = None,
        category: Union[str, None] = None,
        notes: Union[str, None] = None,
    ) -> None:
        if index not in self.expenses.index:
            raise IndexError(f"Expense index {index} does not exist.")

        if date is not None:
            self.expenses.at[index, "date"] = date
        if cost is not None:
            self.expenses.at[index, "cost"] = cost
        if category is not None:
            self.expenses.at[index, "category"] = category
        if notes is not None:
            self.expenses.at[index, "notes"] = notes

    def delete_expense(self, index: int) -> None:
        if index not in self.expenses.index:
            raise IndexError(f"Expense index {index} does not exist.")

        self.expenses = self.expenses.drop(index).reset_index(drop=True)

    def list_expenses(self) -> pd.DataFrame:
        return self.expenses.copy()
    
    def summary(self) -> dict[str, float]:
        spent = self.total_spent()
        return {
            "limit": self.limit,
            "spent": spent,
            "remaining": self.limit - spent,
        } 
