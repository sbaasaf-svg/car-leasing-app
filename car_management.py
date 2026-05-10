import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗", layout="wide")

# אתחול הנתונים
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 יומן רכבי ליסינג")

# --- תפריט צד להזמנה ---
with st.sidebar:
    st.header("הזמנה חדשה")
    user_name = st.text_input("שם")
    selected_car = st.selectbox("רכב", ["11111111", "2222222"])
    booking_date = st.date_input("תאריך", datetime.now())
    c1, c2 = st.columns(2)
    start_t = c1.time_input("התחלה", time(9, 0))
    end_t = c2.time_input("סיום", time(10, 0))
    reason = st.text_input("סיבה")
    
    if st.button("בצע הזמנה"):
        if user_name and reason:
            new_row = {"עובד": user_name, "רכב": selected_car, "תאריך": str(booking_date), 
                       "שעת התחלה": start_t.strftime('%H:%M'), "שעת סיום": end_t.strftime('%H:%M'), "סיבה": reason}
            st.session_state.bookings = pd.concat([st.session_state.bookings, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# --- עיבוד נתונים ---
df = st.session_state.bookings.copy()
if not df.empty:
    df['temp_date'] = pd.to_datetime(df['תאריך']).dt.date
    df = df[df['temp_date'] >= datetime.now().date()].sort_values(by=['temp_date', 'שעת התחלה'])

# --- תצוגת הרשימה ---
st.write("### רשימת נסיעות")
st.write("---")

# כותרות
h_cols = st.columns([1.5, 1.2, 1.2, 1.5, 3, 0.8])
h_cols[0].write("**עובד**")
h_cols[1].write("**רכב**")
h_cols[2].write("**תאריך**")
h_cols[3].write("**שעות**")
h_cols[4].write("**סיבה**")
h_cols[5].write("**מחיקה**")
st.write("---")

if not df.empty:
    for index, row in df.iterrows():
        # יצירת השורה - גישה לכל עמודה לפי אינדקס [0], [1] וכו'
        cols = st.columns([1.5, 1.2, 1.2, 1.5, 3, 0.8])
        
        cols[0].write(row['עובד'])
        cols[1].write(row['רכב'])
        cols[2].write(row['תאריך'])
        cols[3].write(f"{row['שעת התחלה']} - {row['שעת סיום']}")
        cols[4].write(row['סיבה'])
        
        # כפתור מחיקה
        if cols[5].button("🗑️", key=f"del_{index}"):
            st.session_state[f"confirm_{index}"] = True

        # אישור מחיקה
        if st.session_state.get(f"confirm_{index}", False):
            st.warning(f"למחוק את ההזמנה של {row['עובד']}?")
            b1, b2 = st.columns([1, 1])
            if b1.button("✅ אישור", key=f"y_{index}"):
                st.session_state.bookings = st.session_state.bookings.drop(index).reset_index(drop=True)
                st.session_state[f"confirm_{index}"] = False
                st.rerun()
            if b2.button("❌ ביטול", key=f"n_{index}"):
                st.session_state[f"confirm_{index}"] = False
                st.rerun()
        st.write("---")
else:
    st.info("אין הזמנות עתידיות.")
