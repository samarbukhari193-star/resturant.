import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import numpy as np

# Database setup
conn = sqlite3.connect('restaurant.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS restaurant_info (
                id INTEGER PRIMARY KEY,
                name TEXT, owner TEXT, phone TEXT, email TEXT,
                address TEXT, opening_time TEXT, closing_time TEXT,
                type_dinein INTEGER, type_takeaway INTEGER, type_delivery INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS staff (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT, role TEXT, cnic TEXT, phone TEXT,
                salary REAL, shift TEXT, joining_date TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS menu (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                food_name TEXT, category TEXT, price REAL,
                availability TEXT, prep_time INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                table_no INTEGER, waiter_name TEXT, food_item TEXT,
                quantity INTEGER, order_time TEXT, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS billing (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER, food_total REAL, tax REAL,
                discount REAL, final_amount REAL, payment_method TEXT,
                payment_status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_name TEXT, rating INTEGER, comments TEXT, date TEXT)''')

conn.commit()

# Page config
st.set_page_config(page_title="Restaurant Management System", page_icon="🏪", layout="wide")

# Custom CSS for professional modern tabs
st.markdown("""
<style>
    .stTabs [data-baseweb="tab-list"] {
        gap: 25px; justify-content: center; background-color: #f0f2f6;
        padding: 15px; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .stTabs [data-baseweb="tab"] {
        height: 60px; padding: 0 30px; background: white; border-radius: 10px;
        font-size: 16px; font-weight: 600; color: #2c3e50;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4361ee !important; color: white !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🏪 Professional Restaurant Management System")
st.markdown("Complete system with all essential forms • Data saved permanently")

# Tabs
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "🏪 Restaurant Info",
    "👨‍🍳 Staff Registration",
    "🍔 Menu",
    "🧾 Order",
    "🔥 Kitchen Dashboard",
    "💳 Billing",
    "⭐ Feedback",
    "📊 View All Data"
])

with tab1:
    st.header("Restaurant Profile Form")
    with st.form("restaurant_form"):
        name = st.text_input("Restaurant Name *")
        owner = st.text_input("Owner Name *")
        phone = st.text_input("Phone Number *")
        email = st.text_input("Email *")
        address = st.text_area("Complete Address *")
        col1, col2 = st.columns(2)
        opening = col1.time_input("Opening Time")
        closing = col2.time_input("Closing Time")
        st.markdown("#### Restaurant Type")
        dinein = st.checkbox("Dine-In")
        takeaway = st.checkbox("Take Away")
        delivery = st.checkbox("Delivery")
        
        if st.form_submit_button("Save Restaurant Info"):
            if name and owner and phone and email and address:
                c.execute("INSERT INTO restaurant_info (name, owner, phone, email, address, opening_time, closing_time, type_dinein, type_takeaway, type_delivery) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                          (name, owner, phone, email, address, str(opening), str(closing), dinein, takeaway, delivery))
                conn.commit()
                st.success("Restaurant information saved successfully!")
            else:
                st.error("Please fill all required fields")

with tab2:
    st.header("Staff / Employee Registration")
    with st.form("staff_form"):
        name = st.text_input("Full Name *")
        role = st.selectbox("Role *", ["Waiter", "Chef", "Kitchen Staff", "Cashier"])
        cnic = st.text_input("CNIC (Optional)")
        phone = st.text_input("Phone Number *")
        salary = st.number_input("Salary", min_value=0.0)
        shift = st.selectbox("Shift *", ["Morning", "Evening"])
        joining = st.date_input("Joining Date", datetime.today())
        
        if st.form_submit_button("Register Staff"):
            if name and phone:
                c.execute("INSERT INTO staff (name, role, cnic, phone, salary, shift, joining_date) VALUES (?, ?, ?, ?, ?, ?, ?)",
                          (name, role, cnic, phone, salary, shift, str(joining)))
                conn.commit()
                st.success(f"Staff {name} registered! Auto ID generated.")
            else:
                st.error("Required fields missing")

with tab3:
    st.header("Menu / Food Item Form")
    with st.form("menu_form"):
        food_name = st.text_input("Food Name *")
        category = st.selectbox("Category *", ["Fast Food", "BBQ", "Drinks", "Dessert"])
        price = st.number_input("Price *", min_value=0.0)
        availability = st.selectbox("Availability *", ["Yes", "No"])
        prep_time = st.number_input("Preparation Time (minutes)", min_value=1)
        
        if st.form_submit_button("Add to Menu"):
            if food_name and price:
                c.execute("INSERT INTO menu (food_name, category, price, availability, prep_time) VALUES (?, ?, ?, ?, ?)",
                          (food_name, category, price, availability, prep_time))
                conn.commit()
                st.success(f"{food_name} added to menu!")
            else:
                st.error("Required fields missing")

with tab4:
    st.header("Customer Order Form")
    menu_df = pd.read_sql("SELECT food_name FROM menu WHERE availability='Yes'", conn)
    food_items = menu_df['food_name'].tolist() if not menu_df.empty else ["No items available"]
    
    staff_df = pd.read_sql("SELECT name FROM staff WHERE role='Waiter'", conn)
    waiters = staff_df['name'].tolist() if not staff_df.empty else ["No waiters"]
    
    with st.form("order_form"):
        table_no = st.number_input("Table Number", min_value=1)
        waiter = st.selectbox("Waiter Name", waiters)
        food = st.selectbox("Food Item", food_items)
        quantity = st.number_input("Quantity", min_value=1)
        
        if st.form_submit_button("Place Order"):
            order_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.execute("INSERT INTO orders (table_no, waiter_name, food_item, quantity, order_time, status) VALUES (?, ?, ?, ?, ?, 'Pending')",
                      (table_no, waiter, food, quantity, order_time))
            conn.commit()
            st.success("Order placed successfully!")

with tab5:
    st.header("Kitchen Dashboard (Chef View)")
    orders = pd.read_sql("SELECT * FROM orders WHERE status != 'Served'", conn)
    if not orders.empty:
        for _, row in orders.iterrows():
            with st.expander(f"Order ID: {row['id']} | Table: {row['table_no']} | Time: {row['order_time']}"):
                st.write(f"**Food:** {row['food_item']} x {row['quantity']}")
                col1, col2, col3 = st.columns(3)
                if col1.button("Cooking", key=f"cook_{row['id']}"):
                    c.execute("UPDATE orders SET status='Cooking' WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
                if col2.button("Ready", key=f"ready_{row['id']}"):
                    c.execute("UPDATE orders SET status='Ready' WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
                if col3.button("Served", key=f"served_{row['id']}"):
                    c.execute("UPDATE orders SET status='Served' WHERE id=?", (row['id'],))
                    conn.commit()
                    st.rerun()
    else:
        st.info("No pending orders")

with tab6:
    st.header("Billing / Payment Form")
    pending_orders = pd.read_sql("SELECT o.id, o.food_item, o.quantity, m.price FROM orders o JOIN menu m ON o.food_item=m.food_name WHERE o.status='Ready'", conn)
    
    if not pending_orders.empty:
        order_id = st.selectbox("Select Order ID to Bill", pending_orders['id'].unique())
        order_data = pending_orders[pending_orders['id'] == order_id]
        food_total = (order_data['quantity'] * order_data['price']).sum()
        
        st.write(f"**Food Total:** ${food_total:.2f}")
        tax_rate = st.selectbox("Tax", [5, 10])
        tax = food_total * (tax_rate / 100)
        discount = st.number_input("Discount (if any)", min_value=0.0)
        final = food_total + tax - discount
        
        payment_method = st.selectbox("Payment Method", ["Cash", "Card", "Online"])
        status = st.selectbox("Payment Status", ["Paid", "Unpaid"])
        
        if st.button("Generate Bill"):
            c.execute("INSERT INTO billing (order_id, food_total, tax, discount, final_amount, payment_method, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (order_id, food_total, tax, discount, final, payment_method, status))
            conn.commit()
            st.success(f"Bill generated! Final Amount: ${final:.2f}")
    else:
        st.info("No ready orders for billing")

with tab7:
    st.header("Customer Feedback Form")
    with st.form("feedback_form"):
        name = st.text_input("Customer Name (Optional)")
        rating = st.slider("Rating", 1, 5, 3)
        comments = st.text_area("Comments")
        
        if st.form_submit_button("Submit Feedback"):
            date = datetime.now().strftime("%Y-%m-%d")
            c.execute("INSERT INTO feedback (customer_name, rating, comments, date) VALUES (?, ?, ?, ?)",
                      (name, rating, comments, date))
            conn.commit()
            st.success("Thank you for your feedback! ⭐")

with tab8:
    st.header("View All Data")
    table = st.selectbox("Select Table", ["Restaurant Info", "Staff", "Menu", "Orders", "Billing", "Feedback"])
    if table == "Restaurant Info":
        df = pd.read_sql("SELECT * FROM restaurant_info", conn)
    elif table == "Staff":
        df = pd.read_sql("SELECT * FROM staff", conn)
    elif table == "Menu":
        df = pd.read_sql("SELECT * FROM menu", conn)
    elif table == "Orders":
        df = pd.read_sql("SELECT * FROM orders", conn)
    elif table == "Billing":
        df = pd.read_sql("SELECT * FROM billing", conn)
    elif table == "Feedback":
        df = pd.read_sql("SELECT * FROM feedback", conn)
    
    if not df.empty:
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No data yet")

st.markdown("---")
st.caption("Professional Restaurant System • All data saved in database")
