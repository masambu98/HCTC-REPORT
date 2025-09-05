import pandas as pd
import sqlite3
from datetime import date

def generate_report():
    # Connect to database
    conn = sqlite3.connect('callcenter.db')
    
    # Load messages into a DataFrame
    query = "SELECT * FROM messages WHERE date(timestamp) = date('now')"
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    if df.empty:
        print("No messages found for today.")
        return
    
    # Save to CSV
    filename = f"shift_report_{date.today()}.csv"
    df.to_csv(filename, index=False)
    print(f"✅ Report saved as {filename}")

if __name__ == "__main__":
    generate_report()
