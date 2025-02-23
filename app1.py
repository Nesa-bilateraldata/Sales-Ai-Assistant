import mysql.connector

# Connect to MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="your_mysql_root_password",
    database="sales_ai_db"
)

cursor = db.cursor()

# Example: Insert a user
cursor.execute("INSERT INTO users (name, email) VALUES (%s, %s)", ("John Doe", "john@example.com"))
db.commit()

print("User added successfully!")
