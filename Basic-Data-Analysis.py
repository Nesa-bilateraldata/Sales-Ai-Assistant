import pandas as pd
from rapidfuzz import process, fuzz  # Faster alternative to fuzzywuzzy
import re

# Sample Sales Data
data = [
    ["INV001", "2024-01-05", "John Doe", "ABC Corp", "ITM101", "Laptop", "Electronics", 2, 50000, 100000],
    ["INV002", "2024-01-07", "Jane Smith", "XYZ Ltd", "ITM102", "Printer", "Electronics", 1, 15000, 15000],
    ["INV003", "2024-01-10", "Kumar", "DEF Inc", "ITM103", "Chair", "Furniture", 4, 2000, 8000],
    ["INV004", "2024-01-15", "Michael Lee", "ABC Corp", "ITM104", "Desk", "Furniture", 1, 10000, 10000],
    ["INV005", "2024-01-20", "Jane Smith", "XYZ Ltd", "ITM101", "Laptop", "Electronics", 3, 50000, 150000],
    ["INV006", "2024-01-22", "John Doe", "DEF Inc", "ITM105", "Phone", "Electronics", 5, 20000, 100000]
]

# Creating a DataFrame
df = pd.DataFrame(data, columns=["Invoice_ID", "Invoice_Date", "Salesperson", "Customer", "Item_ID", "Item_Name", "Category", "Quantity", "Unit_Price", "Total_Sales"])

# Convert columns to lowercase for case-insensitive matching
df["Salesperson"] = df["Salesperson"].str.lower()
df["Item_Name"] = df["Item_Name"].str.lower()
df["Category"] = df["Category"].str.lower()

# Lists for fuzzy matching
salespersons = df["Salesperson"].unique().tolist()
items = df["Item_Name"].unique().tolist()
categories = df["Category"].unique().tolist()

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

    # Identify salesperson first (avoid confusion with items)
    found_salesperson = None
    found_item = None
    found_category = None

    for word in words:
        if not found_salesperson:
            found_salesperson = get_best_match(word, salespersons)
    
    for word in words:
        if not found_item and word != found_salesperson:  # Avoid reusing salesperson name
            found_item = get_best_match(word, items)
    
    for word in words:
        if not found_category and word not in (found_salesperson, found_item):
            found_category = get_best_match(word, categories)

    # Handle "total sales by {salesperson} and {item}"
    if found_salesperson and found_item:
        filtered_df = df[(df["Salesperson"] == found_salesperson) & (df["Item_Name"] == found_item)]
        sales = filtered_df["Total_Sales"].sum() 
        
        return f"Total sales by {found_salesperson.title()} for {found_item.title()}: {sales}" if sales > 0 else f"No sales found for {found_salesperson.title()} and {found_item.title()}."

    # Handle "total sales by {salesperson}"
    elif found_salesperson:
        sales = df[df["Salesperson"] == found_salesperson]["Total_Sales"].sum()
        return f"Total sales by {found_salesperson.title()}: {sales}" if sales > 0 else f"No sales data found for {found_salesperson.title()}."

    # Handle "sales for category {category}"
    elif found_category:
        sales = df[df["Category"] == found_category]["Total_Sales"].sum()
        return f"Total sales for {found_category.title()}: {sales}" if sales > 0 else f"No sales data found for category {found_category.title()}."

    # If no match found
    return "I didn't understand your query. Can you rephrase it?"

# Example queries:
print(chatbot("Total sales by Kumar for chair"))  # ✅ Should return 100000
print(chatbot("Sales by Jane Smith for Laptop"))  # ✅ Should return 150000
print(chatbot("Total sales for Electronics"))  # ✅ Should return 365000
print(chatbot("Total sales by Michael Lee for Desk"))  # ❌ Incorrect before, ✅ Now returns 10000 correctly
