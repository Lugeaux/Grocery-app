grocery_list = []

# --- SETUP SECTION --- (PRE-START POINT)

# 1. Define the functions at the very top



import streamlit as st 
import pandas as pd
import os
import datetime

# --- CSS FOR PRINTING ---
st.markdown(""" 
<style>
@media print {
    [data-testid="stSidebar"], .stButton, header {
        display: none !important;
    }
}
</style>
"""", unsafe_allow_html=True)




#  ------- HELPER FUNCTIONS ----------
def load_data():
    """Reads the file and returns a list of dictionaries."""
    if not os.path.exists("my_grocery_list.txt"):
        return[]
        
    grocery_list = []
    try:
        with open("my_grocery_list.txt", "r") as f:
            for line in f:
                parts = line.strip().split(",")
                if len(parts) == 3:
                    name, qty, cat = parts
                    grocery_list.append({"name": name, "qty": int(qty), "category": cat})
    except Exception as e:
        st.error(f"Could not load your grocery list: {e}")
    return grocery_list
    pass
    
    
    
def save_list(grocery_list):
    try:
        with open("my_grocery_list.txt", "w") as f:
            for entry in grocery_list:
                f.write(f"{entry['name']},{entry['qty']},{entry['category']}\n")
    except PermissionError as e:
        st.error(f"Permission error saving list: {e}")
    
    
    
# --- APP INITIALIZATION ---
st.set_page_config(page_title="Grocery App")
st.title("My Grocery List")

if 'grocery_list' not in st.session_state:
    st.session_state.grocery_list = load_list()



# ---- SIDEBAR MENU ----
st.sidebar.title("Navigation")
menu = st.sidebar.selectbox("Menu", ["View List", "Add Item", "Remove Item", "Backup List", "View By Category", "Backup" "Clear List"])

if menu == "View List":
    st.header("Your List")
    # --- RESET BUTTON ---
    if st.button("Reset View"):
            st.rerun() # This reloads the page, clearing all user inputs
            

    if not st.session_state.grocery_list:
        st.info("Your list is currently empty.")
    # --- SORT & SEARCH ---
    else:
        df = pd.DataFrame(st.session_state.grocery_list)
        df['qty'] = pd.to_numeric(df['qty'])
        col1, col2 = st.columns(2)
        with col1:
            sort_options = ["None", "Name (A-Z)", "Name (Z-A)", "Qty (Low-High)", "Qty (High_Low)"]
            sort_by = st.selectbox("Sort by", sort_options, key="sort_key")
        with col2:
            search_query = st.text_input("Search items", key="search_key")
            
       
        
   
    # --- FILTERING LOGIC ---
        if search_query:
            df = df[df['name'].str.contains(search_query, case=False, na=False)]
        if sort_by == "Name (A-Z)":
            df = df.sort_values(by="name", ascending=True)
        elif sort_by == "Name (Z-A)":
            df = df.sort_values(by="name", ascending=False)
        elif sort_by == "Qty (Low-High)":
            df = df.sort_values(by="qty", ascending=True)
        elif sort_by == "Qty (High-Low)":
            df = df.sort_values(by="qty", ascending=False)
    
        df.index = range(1, len(df) + 1)
        st.dataframe(df, use_container_width=True)
        
       
# --- MAIN APP CONTENT ---
st.header("Your Grocery List")
        
elif menu == "Add Item":
    st.header("Add New Item")
    with st.form("add form", clear_on_submit=True):
        name = st.text_input("Item Name")
        qty = st.number_input("Quantity", min_value=1, step=1)
        cat = st.selectbox("Category", ["Produce", "Meat", "Dairy", "Frozen", "Cold items", "Household", "Personel care", "Pantry", "Other"])
        submit = st.form_submit_button("Add to List")
    
        if submit and name:
            st.session_state.grocery_list.append({"name": name, "qty": qty, "category":cat})
            save_list(st.session_state.grocery_list)
            st.success(f"Added {name} to your list!")
        
elif menu == "Remove Item":
    st.header("Remove Item")
    if st.session_state.grocery_list:
        names = [item['name'] for item in st.session_state.grocery_list]
        selected = st.selectbox("Select item to remove", names)
        confirm = st.checkbox("Are you sure you want to delete this item?")
        if confirm:
            if st.button("Delete Selected"):
                st.session_state.grocery_list = [i for i in st.session_state.grocery_list if i['name'] != selected]
                save_list(st.session_state.grocery_list)
                st.success(f"Removed {selected}")
                st.rerun() # Forces the page to refresh and show the updated list
    else:
        st.write("No items to remove.")

elif menu == "Backup List":
    st.header("Create a Backup")
    # You must check if the button is pressed like this:
    if st.button("Create Backup"):
        date_stamp = datetime.datetime.now().strftime("%Y-%m-%d")
        filename = f"grocery_backup_{date_stamp}.txt"
        try:
            save_list(st.session_state.grocery_list)
            st.success(f"Backup created: {filename}")
        except Exception as e:
            st.error(f"Backup failed: {e}")
            

elif menu == "View By Category":
    st.header("Sort by Category")
    
    # 1. First, check if the list has any data at all
    if not st.session_state.grocery_list:
        st.info("Your list is empty. Add items to see them here.")
    else:
        # 2. Extract unique categories (using 'category' key)
        # We use a list comprehension and set() to get unique items
        all_categories = sorted(list(set(item['category'] for item in st.session_state.grocery_list)))
        
        # 3. Create the dropdown
        selected_cat = st.selectbox("Select Category", all_categories)
        
        # 4. Filter the list based on the selection
        filtered_list = [item for item in st.session_state.grocery_list if item['category'] == selected_cat]
        
        # 5. Display the result
        if filtered_list:
            df = pd.DataFrame(filtered_list)
            df.index = range(1, len(df) + 1) # Ensure index starts at 1
            st.dataframe(df, use_container_width=True)
        else:
            st.write(f"No items found in {selected_cat}.")
   
   
        
elif menu == "Backup":
    st.header("Backup your data")
    data_to_save = "\n".join([f"{i['name']},{i['qty']},{i['category']}" for i in st.session_state.grocery_list])
    st.download_button(
        label="Download Backup File",
        data=data_to_save,
        file_name=f"grocery_backup_{datetime.date.today()}.txt",
        mime="text/plain"
    )
        
elif menu == "Clear List":
    if st.button("Confirm Clear All"):
        st.session_state.grocery_list = []
        save_list(st.session_state.grocery_list)
        st.success("List cleared!")
        st,rerun()
        
        
# --- PRINT BUTTON ---
if st.button("Print My Grocery List"):
    js = "window.print();"
    st.components.v1.html(f"<script>{js}</script>", height=0)
        
        
        
        

    