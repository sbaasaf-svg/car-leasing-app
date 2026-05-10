import streamlit as st
import pandas as pd
from datetime import datetime, time
import os

# הגדרות דף
st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗")

DATA_FILE = "fleet_bookings.csv"

# פונקציה לטעינת נתונים
def load_data():
    if os.path.exists(DATA_FILE):
        return pd.read_csv(DATA_FILE)
    return pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

# פונקציה לשמירת נתונים
def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# טעינת נתונים לזיכרון
if 'bookings' not in st.session_state:
    st.session_state.bookings = load_data()

st.title("🚗 יומן רכבים חכם")

# רשימת רכבים
cars = ["11111111", "2222222"]

with st.sidebar:
    st.header("ביצוע הזמנה")
    user_name = st.text_input("שם העובד")
    selected_car = st.selectbox("בחר רכב", cars)
    date = st.date_input("תאריך", datetime.now())
    
    col1, col2 = st.columns(2)
    with col1:
        start_t = st.time_input("שעת התחלה", time(9, 0))
    with col2:
        end_t = st.time_input("שעת סיום", time(17, 0))
    
    reason = st.text_input("סיבת הנסיעה")
    submit = st.button("אשר הזמנה")

if submit:
    if not user_name or not reason:
        st.error("נא למלא שם וסיבה.")
    elif start_t >= end_t:
        st.error("שעת הסיום חייבת להיות אחרי שעת ההתחלה.")
    else:
        # בדיקת כפילויות (מניעת התנגשות זמנים)
        df = st.session_state.bookings
        # סינון הזמנות לאותו רכב באותו יום
        conflicts = df[(df['רכב'] == selected_car) & (df['תאריך'] == str(date))]
        
        is_conflict = False
        for _, row in conflicts.iterrows():
            # בדיקת חפיפה בין טווחי שעות
            exist_start = datetime.strptime(row['שעת התחלה'], '%H:%M:%S').time()
            exist_end = datetime.strptime(row['שעת סיום'], '%H:%M:%S').time()
            
            if not (end_t <= exist_start or start_t >= exist_end):
                is_conflict = True
                break
        
        if is_conflict:
            st.error(f"הרכב {selected_car} כבר תפוס בשעות האלו!")
        else:
            new_booking = {
                "עובד": user_name,
                "רכב": selected_car,
                "תאריך": str(date),
                "שעת התחלה": start_t.strftime('%H:%M:%S'),
                "שעת סיום": end_t.strftime('%H:%M:%S'),
                "סיבה": reason
            }
            st.session_state.bookings = pd.concat([st.session_state.bookings, pd.DataFrame([new_booking])], ignore_index=True)
            save_data(st.session_state.bookings)
            st.success("ההזמנה בוצעה בהצלחה!")

# הצגת היומן בצורה יפה
st.subheader("📋 לו״ז נסיעות מתוכנן")
if not st.session_state.bookings.empty:
    # מיון לפי תאריך ושעה
    display_df = st.session_state.bookings.sort_values(by=["תאריך", "שעת התחלה"])
    st.table(display_df)
else:
    st.info("אין הזמנות כרגע. היומן ריק.")
