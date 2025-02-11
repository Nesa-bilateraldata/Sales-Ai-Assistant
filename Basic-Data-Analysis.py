import pandas as pd
from rapidfuzz import process, fuzz  # Faster alternative to fuzzywuzzy
import re

# 🔹 Sample Sales Data
sales_data = [
    ["INV001", "2024-01-05", "John Doe", "ABC Corp", "ITM101", "Laptop", "Electronics", 2, 50000, 100000],
    ["INV002", "2024-01-07", "Jane Smith", "XYZ Ltd", "ITM102", "Printer", "Electronics", 1, 15000, 15000],
    ["INV003", "2024-01-10", "John Doe", "DEF Inc", "ITM103", "Chair", "Furniture", 4, 2000, 8000],
    ["INV004", "2024-01-15", "Michael Lee", "ABC Corp", "ITM104", "Desk", "Furniture", 1, 10000, 10000],
    ["INV005", "2024-01-20", "Jane Smith", "XYZ Ltd", "ITM101", "Laptop", "Electronics", 3, 50000, 150000],
    ["INV006", "2024-01-22", "John Doe", "DEF Inc", "ITM105", "Phone", "Electronics", 5, 20000, 100000]
]

# 🔹 Sample Purchase Data
purchase_data = [
    ["PUR001", "2024-01-02", "Supplier A", "Electronics", "Laptop", 5, 45000, 225000],
    ["PUR002", "2024-01-05", "Supplier B", "Electronics", "Phone", 10, 18000, 180000],
    ["PUR003", "2024-01-07", "Supplier C", "Furniture", "Chair", 8, 1500, 12000],
    ["PUR004", "2024-01-12", "Supplier D", "Furniture", "Desk", 2, 9000, 18000]
]

# 🔹 Convert data into DataFrames
sales_df = pd.DataFrame(sales_data, columns=["Invoice_ID", "Invoice_Date", "Salesperson", "Customer", "Item_ID", "Item_Name", "Category", "Quantity", "Unit_Price", "Total_Sales"])
purchase_df = pd.DataFrame(purchase_data, columns=["Purchase_ID", "Purchase_Date", "Supplier", "Category", "Item_Name", "Quantity", "Unit_Price", "Total_Purchase"])

# 🔹 Convert columns to lowercase for case-insensitive matching
sales_df["Salesperson"] = sales_df["Salesperson"].str.lower()
sales_df["Item_Name"] = sales_df["Item_Name"].str.lower()
sales_df["Category"] = sales_df["Category"].str.lower()

purchase_df["Supplier"] = purchase_df["Supplier"].str.lower()
purchase_df["Item_Name"] = purchase_df["Item_Name"].str.lower()
purchase_df["Category"] = purchase_df["Category"].str.lower()

# 🔹 Lists for fuzzy matching
salespersons = sales_df["Salesperson"].unique().tolist()
items = list(set(sales_df["Item_Name"].tolist() + purchase_df["Item_Name"].tolist()))
categories = list(set(sales_df["Category"].tolist() + purchase_df["Category"].tolist()))

def get_best_match(query_word, choices):
    """Find the closest match for a word using fuzzy matching."""
    match = process.extractOne(query_word, choices, scorer=fuzz.partial_ratio)
    if match is None:  # If no match is found
        return None
    best_match, score, *_ = match  # Extract values safely
    return best_match if score > 70 else None  # Apply a confidence threshold

def chatbot(query):
    query = query.lower().strip()

    # Extract words using regex
    words = re.findall(r'\b\w+\b', query)

    # Identify salesperson, item, or category
    found_salesperson, found_item, found_category = None, None, None

    for word in words:
        if not found_salesperson:
            found_salesperson = get_best_match(word, salespersons)
    
    for word in words:
        if not found_item and word != found_salesperson:  # Avoid reusing salesperson name
            found_item = get_best_match(word, items)
    
    for word in words:
        if not found_category and word not in (found_salesperson, found_item):
            found_category = get_best_match(word, categories)

    # Detect if the query is about **Sales or Purchases**
    is_sales_query = "sales" in query or "sold" in query or "revenue" in query
    is_purchase_query = "purchase" in query or "bought" in query or "procured" in query

    # Handle "Total sales for {category}"
    if found_category and is_sales_query:
        sales = sales_df[sales_df["Category"] == found_category]["Total_Sales"].sum()
        return f"Total sales for {found_category.title()}: {sales}" if sales > 0 else f"No sales data found for category {found_category.title()}."

    # Handle "Total purchased for {category}"
    if found_category and is_purchase_query:
        purchases = purchase_df[purchase_df["Category"] == found_category]["Total_Purchase"].sum()
        return f"Total purchased for {found_category.title()}: {purchases}" if purchases > 0 else f"No purchase data found for category {found_category.title()}."

    # Handle "Total sales by {salesperson} and {item}"
    if found_salesperson and found_item and is_sales_query:
        filtered_df = sales_df[(sales_df["Salesperson"] == found_salesperson) & (sales_df["Item_Name"] == found_item)]
        sales = filtered_df["Total_Sales"].sum()
        return f"Total sales by {found_salesperson.title()} for {found_item.title()}: {sales}" if sales > 0 else f"No sales found for {found_salesperson.title()} and {found_item.title()}."

    # Handle "Total sales by {salesperson}"
    if found_salesperson and is_sales_query:
        sales = sales_df[sales_df["Salesperson"] == found_salesperson]["Total_Sales"].sum()
        return f"Total sales by {found_salesperson.title()}: {sales}" if sales > 0 else f"No sales data found for {found_salesperson.title()}."

    # If no match found
    return "I didn't understand your query. Can you rephrase it?"

# Example Queries:
print(chatbot("Total sales for Electronics"))  # ✅ Should return 365000
print(chatbot("Total purchased for Electronics"))  # ✅ Should return 405000
print(chatbot("Total sales by John Doe for Phone"))  # ✅ Should return 100000
print(chatbot("Total purchased for Furniture"))  # ✅ Should return 30000
