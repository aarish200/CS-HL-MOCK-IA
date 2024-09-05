import streamlit as st
import pandas as pd
import os

# Initialize CSV files if they don't exist
if not os.path.exists("tables.csv"):
    tables = pd.DataFrame({
        'Table ID': [i + 1 for i in range(17)],
        'Seats': [2] * 10 + [4] * 5 + [10] * 2,
        'Status': ['Available'] * 17
    })
    tables.to_csv("tables.csv", index=False)

if not os.path.exists("menu.csv"):
    menu = pd.DataFrame({
        'Item ID': [1, 2, 3],
        'Item Name': ['Burger', 'Pizza', 'Pasta'],
        'Price': [100, 200, 150]
    })
    menu.to_csv("menu.csv", index=False)

if not os.path.exists("orders.csv"):
    orders = pd.DataFrame(columns=['Order ID', 'Table ID', 'Items Ordered', 'Total Price'])
    orders.to_csv("orders.csv", index=False)

if not os.path.exists("admin.csv"):
    admin = pd.DataFrame(columns=['Username', 'Password'])
    admin.to_csv("admin.csv", index=False)

if not os.path.exists("reports.csv"):
    reports = pd.DataFrame(columns=['Date', 'Total Sales', 'Total Occupancy'])
    reports.to_csv("reports.csv", index=False)

tables = pd.read_csv("tables.csv")
menu = pd.read_csv("menu.csv")
orders = pd.read_csv("orders.csv")
admin = pd.read_csv("admin.csv")

# Session state for admin login
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

st.title("Restaurant Management System")

menu_option = st.sidebar.selectbox("Menu", ["Home", "Customer", "Admin", "Register Admin"])

if menu_option == "Home":
    st.write("Welcome to the Restaurant Management System!")

elif menu_option == "Customer":
    st.subheader("Customer Interface")
    
    # Ask for the number of people first
    number_of_people = st.number_input("Enter Number of People", min_value=1, max_value=10)

    # Based on the number of people, display available tables
    if number_of_people:
        if number_of_people <= 2:
            available_tables = tables[(tables['Seats'] == 2) & (tables['Status'] == 'Available')]
        elif number_of_people <= 4:
            available_tables = tables[(tables['Seats'] == 4) & (tables['Status'] == 'Available')]
        else:
            available_tables = tables[(tables['Seats'] == 10) & (tables['Status'] == 'Available')]

        st.write(f"Available Tables for {number_of_people} people")
        st.table(available_tables[['Table ID', 'Seats']])
        
        if not available_tables.empty:
            table_id = st.selectbox("Select a Table to Book", available_tables['Table ID'])

            if st.button("Book Table"):
                tables.loc[tables['Table ID'] == table_id, 'Status'] = 'Occupied'
                tables.to_csv("tables.csv", index=False)
                st.success(f"Table {table_id} has been booked.")
        else:
            st.write("No available tables for the selected number of people.")

    st.subheader("Menu")
    st.table(menu)

    st.subheader("Place an Order")
    order_items = st.multiselect("Select Items", menu['Item Name'])
    total_price = menu[menu['Item Name'].isin(order_items)]['Price'].sum()
    st.write(f"Total Price: {total_price}")

    if st.button("Place Order"):
        new_order = pd.DataFrame({
            'Order ID': [len(orders) + 1],
            'Table ID': [table_id if 'table_id' in locals() else None],
            'Items Ordered': [", ".join(order_items)],
            'Total Price': [total_price]
        })
        orders = pd.concat([orders, new_order])
        orders.to_csv("orders.csv", index=False)
        st.success("Order placed successfully!")

    st.subheader("Your Bill")
    if 'table_id' in locals():
        st.write(f"Table ID: {table_id}")
    st.write(f"Items Ordered: {', '.join(order_items)}")
    st.write(f"Total Price: {total_price}")

elif menu_option == "Admin":
    if not st.session_state.logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            if username in admin['Username'].values:
                stored_password = admin[admin['Username'] == username]['Password'].values[0]
                if stored_password == password:
                    st.session_state.logged_in = True
                    st.success("Login successful!")
                else:
                    st.error("Invalid password.")
            else:
                st.error("Invalid username.")
    
    if st.session_state.logged_in:
        st.subheader("Admin Menu")
        admin_menu = st.selectbox("Admin Menu", ["Menu Management", "Table Status Management", "Reports"])
        
        if admin_menu == "Menu Management":
            st.subheader("Manage Menu")
            st.table(menu)
            
            new_item = st.text_input("New Item Name")
            new_price = st.number_input("New Item Price", min_value=0)
            
            if st.button("Add Item"):
                if new_item:
                    new_menu_item = pd.DataFrame({'Item ID': [len(menu) + 1], 'Item Name': [new_item], 'Price': [new_price]})
                    menu = pd.concat([menu, new_menu_item])
                    menu.to_csv("menu.csv", index=False)
                    st.success(f"New item '{new_item}' added successfully!")
            
            st.subheader("Update or Remove Existing Items")
            item_to_update = st.selectbox("Select Item to Update", menu['Item Name'])
            updated_price = st.number_input("Update Price", min_value=0)
            
            if st.button("Update Price"):
                menu.loc[menu['Item Name'] == item_to_update, 'Price'] = updated_price
                menu.to_csv("menu.csv", index=False)
                st.success(f"Price for {item_to_update} updated to {updated_price}")
            
            if st.button("Remove Item"):
                menu = menu[menu['Item Name'] != item_to_update]
                menu.to_csv("menu.csv", index=False)
                st.success(f"Item '{item_to_update}' removed from menu.")
        
        elif admin_menu == "Table Status Management":
            st.subheader("Table Status Management")
            st.table(tables)
            
            table_id = st.number_input("Select a Table to Update Status", min_value=1, max_value=17, step=1)
            new_status = st.selectbox("New Status", ['Available', 'Occupied'])
            
            if st.button("Update Table Status"):
                tables.loc[tables['Table ID'] == table_id, 'Status'] = new_status
                tables.to_csv("tables.csv", index=False)
                st.success(f"Table {table_id} status updated to {new_status}")
        
        elif admin_menu == "Reports":
            st.subheader("Generate Reports")
            report_type = st.selectbox("Report Type", ["Daily Sales", "Table Occupancy"])
            
            if report_type == "Daily Sales":
                daily_sales = orders.groupby('Table ID')['Total Price'].sum()
                st.write("Total Sales Report")
                st.table(daily_sales)
                
                if st.button("Save Report"):
                    reports = pd.concat([reports, pd.DataFrame({
                        'Date': [pd.Timestamp.now()],
                        'Total Sales': [daily_sales.sum()],
                        'Total Occupancy': [len(tables[tables['Status'] == 'Occupied'])]
                    })])
                    reports.to_csv("reports.csv", index=False)
                    st.success("Report saved successfully!")
            
            elif report_type == "Table Occupancy":
                occupancy = tables['Status'].value_counts()
                st.write("Table Occupancy Report")
                st.table(occupancy)

elif menu_option == "Register Admin":
    st.subheader("Register Admin")
    new_username = st.text_input("New Username")
    new_password = st.text_input("New Password", type="password")
    
    if st.button("Register"):
        if new_username in admin['Username'].values:
            st.error("Username already exists. Please choose a different username.")
        else:
            new_admin = pd.DataFrame({'Username': [new_username], 'Password': [new_password]})
            admin = pd.concat([admin, new_admin])
            admin.to_csv("admin.csv", index=False)
            st.success(f"Admin '{new_username}' registered successfully!")
