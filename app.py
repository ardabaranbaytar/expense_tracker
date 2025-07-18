from flask import Flask, render_template, request, redirect, jsonify
import os
import datetime

app = Flask(__name__)
FILENAME = "expenses.txt"

# Veri fonksiyonları (dosya tabanlı)
def load_expenses():
    if not os.path.exists(FILENAME):
        return []
    with open(FILENAME, "r") as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def save_expenses(expenses):
    with open(FILENAME, "w") as file:
        for expense in expenses:
            file.write(expense + "\n")

def add_expense(desc, amount):
    date = datetime.date.today().isoformat()
    entry = f"{date} | {desc} | {amount}"
    expenses = load_expenses()
    expenses.append(entry)
    save_expenses(expenses)

def remove_expense(index):
    expenses = load_expenses()
    if 0 <= index < len(expenses):
        expenses.pop(index)
        save_expenses(expenses)

def calculate_total():
    total = 0
    for entry in load_expenses():
        try:
            amount = float(entry.split('|')[-1].strip())
            total += amount
        except:
            continue
    return total

@app.route("/")
def index():
    expenses = load_expenses()
    total = calculate_total()
    return render_template("index.html", expenses=expenses, total=total)

@app.route("/add", methods=["POST"])
def add():
    desc = request.form.get("desc")
    amount = request.form.get("amount")
    if desc and amount:
        try:
            float(amount)
            add_expense(desc, amount)
        except:
            pass
    return redirect("/")

@app.route("/delete/<int:index>", methods=["POST"])
def delete(index):
    remove_expense(index)
    return redirect("/")

@app.route("/api/graph-data")
def graph_data():
    expenses = load_expenses()
    date_totals = {}
    for entry in expenses:
        parts = entry.split('|')
        if len(parts) != 3:
            continue
        date = parts[0].strip()
        try:
            amount = float(parts[2].strip())
        except:
            continue
        date_totals[date] = date_totals.get(date, 0) + amount
    dates = list(date_totals.keys())
    totals = list(date_totals.values())
    return jsonify({"dates": dates, "totals": totals})

if __name__ == "__main__":
    app.run(debug=True)