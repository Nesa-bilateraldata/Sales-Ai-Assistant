from flask import Flask, render_template, request, jsonify
import pandas as pd
from rapidfuzz import process, fuzz
import re
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/ask": {"origins": "http://bilateralinfo.com"}})  

# ðŸ”¹ Sample Sales Data
sales_data = [
    ["INV001", "2024-01-05", "John Doe", "ABC Corp", "ITM101", "Laptop", "Electronics", 2, 50000, 100000],
    ["INV002", "2024-01-07", "Jane Smith", "XYZ Ltd", "ITM102", "Printer", "Electronics", 1, 15000, 15000],
    ["INV003", "2024-01-10", "John Doe", "DEF Inc", "ITM103", "Chair", "Furniture", 4, 2000, 8000],
    ["INV004", "2024-01-15", "Michael Lee", "ABC Corp", "ITM104", "Desk", "Furniture", 1, 10000, 10000],
    ["INV005", "2024-01-20", "Jane Smith", "XYZ Ltd", "ITM101", "Laptop", "Electronics", 3, 50000, 150000],
    ["INV006", "2024-01-22", "John Doe", "DEF Inc", "ITM105", "Phone", "Electronics", 5, 20000, 100000]
]

# ðŸ”¹ Convert to DataFrame
sales_df = pd.DataFrame(sales_data, columns=["Invoice_ID", "Invoice_Date", "Salesperson", "Customer", "Item_ID", "Item_Name", "Category", "Quantity", "Unit_Price", "Total_Sales"])

# ðŸ”¹ Lowercase for matching
sales_df["Category"] = sales_df["Category"].str.lower()

# ðŸ”¹ List of categories
categories = list(sales_df["Category"].unique())

def get_best_match(query_word, choices):
    """Find closest match using fuzzy matching."""
    match = process.extractOne(query_word, choices, scorer=fuzz.partial_ratio)
    return match[0] if match and match[1] > 70 else None  # 70% confidence

def chatbot(query):
    query = query.lower().strip()

    # Extract words
    words = re.findall(r'\b\w+\b', query)

    # Identify category
    found_category = None
    for word in words:
        if not found_category:
            found_category = get_best_match(word, categories)

    # Handle sales queries
    if found_category:
        sales = sales_df[sales_df["Category"] == found_category]["Total_Sales"].sum()
        return f"Total sales for {found_category.title()}: {sales}" if sales > 0 else f"No sales data for {found_category.title()}."

    return "I didn't understand your query. Please rephrase."

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    query = request.form.get("query")
    response = chatbot(query)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)
