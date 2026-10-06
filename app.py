import streamlit as st
import pandas as pd
from datetime import date, datetime
import urllib.parse
import io

# Page Setup
st.set_page_config(page_title="Team Activity & CRM Planner", layout="wide")

# Mock User Profiles
USERS = {
    "admin": {"name": "Director / Admin", "role": "Admin", "pin": "1234"},
    "varsha": {"name": "Dr. Varsha Varwandkar", "role": "Counselor", "pin": "1111"},
    "tarun": {"name": "Tarun (Media/Operations)", "role": "Media/Ops", "pin": "2222"}
}

# Session State for demo data storage
if "tasks" not in st.session_state:
    st.session_state.tasks = [
        {"id": 1, "task": "Instagram Reel & YouTube Short Upload", "assigned_to": "Media/Ops", "type": "Social Media", "due_date": str(date.today()), "status": "Pending", "notes": "Career guidance topic"},
        {"id": 2, "task": "Send MBBS Admission Guide PDF to Aman", "assigned_to": "Counselor", "type": "Customer Follow-up", "due_date": str(date.today()), "status": "Pending", "notes": "Check NEET score first"}
    ]

if "customers" not in st.session_state:
    st.session_state.customers = [
        {"name": "Aman Sharma", "phone": "919876543210", "query": "NEET MBBS Cutoff Raipur", "next_followup": str(date.today()), "status": "Open"}
    ]

# ----------------- LOGIN SYSTEM -----------------
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None

if not st.session_state.logged_in_user:
    st.title("🔒 Team Activity & Scheduler Login")
    username = st.selectbox("Select Your Profile", list(USERS.keys()), format_func=lambda x: USERS[x]["name"])
    pin = st.text_input("Enter 4-Digit PIN", type="password")
    
    if st.button("Login"):
        if USERS[username]["pin"] == pin:
            st.session_state.logged_in_user = USERS[username]
            st.rerun()
        else:
            st.error("Galat PIN! Kripya dobara check karein.")
    st.stop()

# ----------------- LOGGED IN DASHBOARD -----------------
current_user = st.session_state.logged_in_user

# Sidebar
st.sidebar.title(f"👤 {current_user['name']}")
st.sidebar.write(f"**Role:** {current_user['role']}")
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.rerun()

menu = st.sidebar.radio("Navigation", ["📋 Daily Tasks & Operations", "👥 Customer Lead & Query Punch", "📅 Full Calendar / All Work"])

# ----------------- 1. DAILY TASKS & OPERATIONS -----------------
if menu == "📋 Daily Tasks & Operations":
    st.header("🎯 Operations & Task Management")
    
    # Overdue Task Alert
    today_str = str(date.today())
    overdue = [t for t in st.session_state.tasks if t["due_date"] < today_str and t["status"] != "Completed"]
    if overdue:
        st.error(f"⚠️ **{len(overdue)} Overdue Tasks!** Inhe turant complete karein.")
        for ot in overdue:
            st.write(f"- 🔴 **{ot['task']}** (Assigned: {ot['assigned_to']}, Due: {ot['due_date']})")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Today's Pending Tasks")
        user_tasks = [
            t for t in st.session_state.tasks 
            if (current_user["role"] == "Admin" or t["assigned_to"] == current_user["role"]) and t["status"] != "Completed"
        ]
        
        if not user_tasks:
            st.success("✅ Aaj ke sabhi tasks complete hain!")
        else:
            for t in user_tasks:
                with st.expander(f"📌 {t['task']} | Due: {t['due_date']} ({t['type']})"):
                    st.write(f"**Notes:** {t['notes']}")
                    st.write(f"**Assigned To:** {t['assigned_to']}")
                    if st.button("Mark as Completed", key=f"comp_{t['id']}"):
                        t["status"] = "Completed"
                        st.success("Task complete ho gaya!")
                        st.rerun()
    
    with col2:
        st.subheader("➕ Naya Task Add Karein")
        new_task_title = st.text_input("Task Name (e.g. Post Video, Share Guide)")
        task_type = st.selectbox("Category", ["Social Media / Video", "Customer Follow-up", "Admin / Office", "Calling"])
        assigned_to = st.selectbox("Assign To", ["Counselor", "Media/Ops", "Admin"])
        due_date = st.date_input("Target Date", value=date.today())
        task_notes = st.text_area("Notes / Checklist")
        
        if st.button("Save Task"):
            if new_task_title:
                new_id = len(st.session_state.tasks) + 1
                st.session_state.tasks.append({
                    "id": new_id,
                    "task": new_task_title,
                    "assigned_to": assigned_to,
                    "type": task_type,
                    "due_date": str(due_date),
                    "status": "Pending",
                    "notes": task_notes
                })
                st.success("Task add ho gaya!")
                st.rerun()

# ----------------- 2. CUSTOMER LEAD & QUERY PUNCH -----------------
elif menu == "👥 Customer Lead & Query Punch":
    st.header("📞 Customer Directory & One-Click Connect")
    
    c_col1, c_col2 = st.columns([2, 1])
    
    with c_col1:
        st.subheader("All Leads & Queries")
        for cust in st.session_state.customers:
            with st.container(border=True):
                st.markdown(f"### {cust['name']}")
                st.write(f"**Query:** {cust['query']}")
                st.write(f"**Next Follow-up:** {cust['next_followup']} | **Status:** {cust['status']}")
                
                # WhatsApp & Call Quick Actions
                encoded_msg = urllib.parse.quote(f"Namaste {cust['name']}, Myaglakadam Academy se baat kar rahe hain. Aapki query ke sambhandh me baat karni thi.")
                wa_url = f"https://wa.me/{cust['phone']}?text={encoded_msg}"
                call_url = f"tel:{cust['phone']}"
                
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    st.link_button("💬 Open WhatsApp", wa_url)
                with btn_col2:
                    st.link_button("📞 Direct Call", call_url)
    
    with c_col2:
        st.subheader("➕ Punch New Customer")
        c_name = st.text_input("Student / Parent Name")
        c_phone = st.text_input("WhatsApp Number (with 91 e.g., 919876543210)")
        c_query = st.text_area("Requirement / Query Details")
        c_followup = st.date_input("Next Follow-up Date", value=date.today())
        
        if st.button("Save Customer Query"):
            if c_name and c_phone:
                st.session_state.customers.append({
                    "name": c_name,
                    "phone": c_phone.strip(),
                    "query": c_query,
                    "next_followup": str(c_followup),
                    "status": "Open"
                })
                st.session_state.tasks.append({
                    "id": len(st.session_state.tasks) + 1,
                    "task": f"Follow-up call with {c_name}",
                    "assigned_to": "Counselor",
                    "type": "Calling",
                    "due_date": str(c_followup),
                    "status": "Pending",
                    "notes": c_query
                })
                st.success("Customer saved & follow-up task auto-created!")
                st.rerun()

# ----------------- 3. FULL CALENDAR / ALL WORK -----------------
elif menu == "📅 Full Calendar / All Work":
    st.header("📊 Master Activity Log & Export")
    
    tab1, tab2 = st.tabs(["📋 Tasks Master Data", "👥 Customer Master Data"])
    
    with tab1:
        st.subheader("All Team Tasks")
        df_tasks = pd.DataFrame(st.session_state.tasks)
        st.dataframe(df_tasks, use_container_width=True)
        
        # Excel Download Button for Tasks
        buffer_tasks = io.BytesIO()
        with pd.ExcelWriter(buffer_tasks, engine='openpyxl') as writer:
            df_tasks.to_excel(writer, index=False, sheet_name='Tasks')
        
        st.download_button(
            label="📥 Download Tasks Excel (.xlsx)",
            data=buffer_tasks.getvalue(),
            file_name=f"team_tasks_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    with tab2:
        st.subheader("All Customer Queries & Leads")
        df_cust = pd.DataFrame(st.session_state.customers)
        st.dataframe(df_cust, use_container_width=True)
        
        # Excel Download Button for Customers
        buffer_cust = io.BytesIO()
        with pd.ExcelWriter(buffer_cust, engine='openpyxl') as writer:
            df_cust.to_excel(writer, index=False, sheet_name='Customers')
        
        st.download_button(
            label="📥 Download Customers Excel (.xlsx)",
            data=buffer_cust.getvalue(),
            file_name=f"customers_leads_{date.today()}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
