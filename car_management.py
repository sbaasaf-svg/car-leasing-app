import streamlit as st
import pandas as pd
from datetime import datetime

# הגדרות בסיסיות של האפליקציה
st.set_page_config(page_title="ניהול צי רכבים - חברת ליסינג", page_icon="🚗")

st.title("📅 מערכת הזמנת רכבי ליסינג")
st.subheader("ניהול וסנכרון צי הרכבים הארגוני")

# נתוני הצי שלנו
vehicle_numbers = ["11111111", "2222222"]

# אתחול בסיס הנתונים (בזיכרון עבור הדוגמה - ניתן לחבר ל-Google Sheets או SQL)
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["שם העובד", "מספר רכב", "תאריך", "סיבת הזמנה"])

# ממשק הזמנה
with st.form("booking_form"):
    st.write("### בצע הזמנה חדשה")
    user_name = st.text_input("שם מלא")
    selected_car = st.selectbox("בחר מספר רכב", vehicle_numbers)
    booking_date = st.date_input("בחר תאריך", datetime.now())
    reason = st.text_area("הסבר/מטרת הנסיעה")

    submit_button = st.form_submit_button("אשר הזמנה")

# לוגיקה לשמירת הנתונים
if submit_button:
    if user_name and reason:
        new_booking = pd.DataFrame({
            "שם העובד": [user_name],
            "מספר רכב": [selected_car],
            "תאריך": [booking_date],
            "סיבת הזמנה": [reason]
        })
        st.session_state.bookings = pd.concat([st.session_state.bookings, new_booking], ignore_index=True)
        st.success(f"הרכב {selected_car} הועבר לטיפולך עבור תאריך {booking_date}!")
    else:
        st.error("נא למלא את כל השדות.")

# הצגת יומן ההזמנות
st.write("---")
st.write("### 📋 יומן נסיעות מעודכן")
if not st.session_state.bookings.empty:
    st.dataframe(st.session_state.bookings, use_container_width=True)
else:
    st.info("אין הזמנות פעילות כרגע.")
