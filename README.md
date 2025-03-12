
---

### ** README for Question 2: Sales Data Processing API**  
Create a **`README.md`** in your **Sales Data API project** folder.

```md
# Sales Data Processing - Flask API

##  Description
This Flask API processes sales data from two regions, stores it in a database, and provides an HTML page to view the cleaned records.

##  Features
- Extracts data from `order_region_a.csv` and `order_region_b.csv`.
- Cleans data and calculates `total_sales` and `net_sale`.
- Removes **duplicate orders** (keeping the latest).
- Loads data into SQLite via Flask-SQLAlchemy.
- Displays **processed sales data in an HTML table**.
- Provides **SQL query-based validation via API endpoints**.

##  Setup Instructions
### **1 Install Dependencies**
```bash
pip install flask flask-sqlalchemy pandas

url:http://127.0.0.1:5000/fetch_sales
