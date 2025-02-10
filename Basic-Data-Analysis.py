import pandas as pd

# Sample Sales Data
data = [
    ["INV001", "2024-01-05", "John Doe", "ABC Corp", "ITM101", "Laptop", "Electronics", 2, 50000, 100000],
    ["INV002", "2024-01-07", "Jane Smith", "XYZ Ltd", "ITM102", "Printer", "Electronics", 1, 15000, 15000],
    ["INV003", "2024-01-10", "John Doe", "DEF Inc", "ITM103", "Chair", "Furniture", 4, 2000, 8000],
    ["INV004", "2024-01-15", "Michael Lee", "ABC Corp", "ITM104", "Desk", "Furniture", 1, 10000, 10000],
    ["INV005", "2024-01-20", "Jane Smith", "XYZ Ltd", "ITM101", "Laptop", "Electronics", 3, 50000, 150000],
    ["INV006", "2024-01-22", "John Doe", "DEF Inc", "ITM105", "Phone", "Electronics", 5, 20000, 100000]
]

# Creating a DataFrame
df = pd.DataFrame(data, columns=["Invoice_ID", "Invoice_Date", "Salesperson", "Customer", "Item_ID", "Item_Name", "Category", "Quantity", "Unit_Price", "Total_Sales"])

# Convert Salesperson column to lowercase for case-insensitive matching
df["Salesperson"] = df["Salesperson"].str.lower()
df["Category"] = df["Category"].str.lower()

def chatbot(query):
    query = query.lower().strip()
    
    if "total sales by" in query:
        salesperson = query.replace("total sales by ", "").strip()
        sales = df[df["Salesperson"] == salesperson]["Total_Sales"].sum()
        return f"Total sales by {salesperson.title()}: {sales}" if sales > 0 else f"No sales data found for {salesperson.title()}."
    
    elif "items sold by" in query:
        salesperson = query.replace("items sold by ", "").strip()
        items = df[df["Salesperson"] == salesperson]["Item_Name"].tolist()
        return f"Items sold by {salesperson.title()}: {', '.join(items)}" if items else f"No items found for {salesperson.title()}."
    
    elif "sales for category" in query:
        category = query.replace("sales for category ", "").strip()
        sales = df[df["Category"] == category]["Total_Sales"].sum()
        return f"Total sales for {category.title()}: {sales}" if sales > 0 else f"No sales data found for category {category.title()}."
    
    else:
        return "I didn't understand your query."

# Example usage:
print(chatbot("Total sales by John Doe"))  # Should return 108000
print(chatbot("Items sold by Jane Smith"))  # Should return 'Laptop, Printer'
print(chatbot("Sales for category Electronics"))  # Should return 365000
