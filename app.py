from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import os
from flask import jsonify
from sqlalchemy.sql import func

app = Flask(__name__)

# Database Configuration
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sales.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Define Sales Model
class Sales(db.Model):
    __tablename__ = 'sales_data'
    id = db.Column(db.Integer, primary_key=True)
    OrderId = db.Column(db.Integer, unique=True, nullable=False)
    OrderItemId = db.Column(db.Integer, nullable=False)
    QuantityOrdered = db.Column(db.Integer, nullable=False)
    ItemPrice = db.Column(db.Float, nullable=False)
    PromotionDiscount = db.Column(db.Float, nullable=False)
    total_sales = db.Column(db.Float, nullable=False)
    net_sale = db.Column(db.Float, nullable=False)
    region = db.Column(db.String(10), nullable=False)

# Initialize Database
with app.app_context():
    db.create_all()

# Extract Data from CSV Files
def extract_data(file_path, region):
    """Reads a CSV file and adds a 'region' column."""
    df = pd.read_csv(file_path)
    df['region'] = region
    return df

# Transform Data (Cleaning & Processing)
def transform_data(df_a, df_b):
    """Combines and cleans sales data."""
    df = pd.concat([df_a, df_b])

    # Convert columns to correct types
    df['QuantityOrdered'] = pd.to_numeric(df['QuantityOrdered'], errors='coerce')
    df['ItemPrice'] = pd.to_numeric(df['ItemPrice'], errors='coerce')
    df['PromotionDiscount'] = pd.to_numeric(df['PromotionDiscount'], errors='coerce')

    # Handle NaN values
    df.fillna({'PromotionDiscount': 0, 'QuantityOrdered': 0, 'ItemPrice': 0}, inplace=True)

    # Compute total and net sales
    df['total_sales'] = df['QuantityOrdered'] * df['ItemPrice']
    df['net_sale'] = df['total_sales'] - df['PromotionDiscount']

    # Remove duplicates (keep latest)
    df = df.sort_values('OrderId').drop_duplicates(subset=['OrderId'], keep='last')

    # Remove records where net_sales <= 0
    df = df[df['net_sale'] > 0]

    return df

# Load Data into SQLite
def load_data_to_db(df):
    """Loads transformed data into SQLite via SQLAlchemy."""
    with app.app_context():
        db.session.query(Sales).delete()  # Clear existing data

        for _, row in df.iterrows():
            sale = Sales(
                OrderId=row['OrderId'],
                OrderItemId=row['OrderItemId'],
                QuantityOrdered=row['QuantityOrdered'],
                ItemPrice=row['ItemPrice'],
                PromotionDiscount=row['PromotionDiscount'],
                total_sales=row['total_sales'],
                net_sale=row['net_sale'],
                region=row['region']
            )
            db.session.add(sale)

        db.session.commit()

# Display Sales Data in HTML
@app.route('/fetch_sales', methods=['GET'])
def fetch_sales():
    """Fetch and display sales records in an HTML page."""
    sales_data = Sales.query.all()
    return render_template('sales.html', sales=sales_data)

# Count total records
@app.route('/count_records', methods=['GET'])
def count_total_records():
    total_records = db.session.query(func.count(Sales.id)).scalar()
    return jsonify({"total_records": total_records})

# Total Sales by Region
@app.route('/total_sales_by_region', methods=['GET'])
def total_sales_by_region():
    results = db.session.query(Sales.region, func.sum(Sales.total_sales)).group_by(Sales.region).all()
    return jsonify({"total_sales_by_region": dict(results)})

# Average Sales per Transaction
@app.route('/average_sales', methods=['GET'])
def avg_sales_per_transaction():
    avg_sales = db.session.query(func.avg(Sales.total_sales)).scalar()
    return jsonify({"average_sales_per_transaction": avg_sales})

# Check for Duplicate Order IDs
@app.route('/check_duplicates', methods=['GET'])
def check_duplicate_order_ids():
    duplicates = db.session.query(Sales.OrderId, func.count(Sales.OrderId)).group_by(Sales.OrderId).having(func.count(Sales.OrderId) > 1).all()
    return jsonify({"duplicate_orders": duplicates})

if __name__ == '__main__':
    df_a = extract_data("order_region_a.csv", "A")
    df_b = extract_data("order_region_b.csv", "B")
    df_transformed = transform_data(df_a, df_b)
    load_data_to_db(df_transformed)
    print("Sales data processed and loaded successfully!")
    app.run(debug=True)
