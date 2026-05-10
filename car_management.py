import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗", layout="wide")

# אתחול בסיס הנתונים בזיכרון
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 יומן רכבים - רשימת הזמנות")

# --- תפריט צד להזמנה ---
with st.sidebar:
    st.header("הזמנת רכב")
    user_name = st.text_input("שם העובד")
    selected_car = st.selectbox("בחר רכב", ["11111111", "2222222"])
    booking_date = st.date_input("תאריך", datetime.now())
    start_t = st.time_input("התחלה", time(9, 0))
    end_t = st.time_input("סיום", time(10, 0))
    reason = st.text_input("סיבה")
    
    if st.button("אשר הזמנה"):
        if user_name and reason:
            # בדיקת כפילויות פשוטה
            new_row = {"עובד": user_name, "רכב": selected_car, "תאריך": str(booking_date), 
                       "שעת התחלה": start_t.strftime('%H:%M'), "שעת סיום": end_t.strftime('%H:%M'), "סיבה": reason}
            st.session_state.bookings = pd.concat([st.session_state.bookings, pd.DataFrame([new_row])], ignore_index=True)
            st.rerun()

# --- עיבוד נתונים (סינון ומיון) ---
df = st.session_state.bookings.copy()
if not df.empty:
    today = datetime.now().date()
    df['temp_date'] = pd.to_datetime(df['תאריך']).dt.date
    # סינון עבר ומיון
    df = df[df['temp_date'] >= today].sort_values(by=['temp_date', 'שעת התחלה'])

# --- תצוגת הרשימה ---
st.write("### רשימת נסיעות פעילות")
st.write("---")

if not df.empty:
    # כותרות לטבלה "הידנית"
    h_col1, h_col2, h_col3, h_col4, h_col5, h_col6 = st.columns([1.5, 1.5, 1.5, 1.5, 3, 0.5])
    h_col1.write("**עובד**")
    h_col2.write("**רכב**")
    h_col3.write("**תאריך**")
    h_col4.write("**שעות**")
    h_col5.write("**סיבה**")
    h_col6.write("") # עמודת הפח
    st.write("---")

    for index, row in df.iterrows():
        col1, col2, col3, col4, col5, col6 = st.columns([1.5, 1.5, 1.5, 1.5, 3, 0.5])
        
        col1.write(row['עובד'])
        col2.write(row['רכב'])
        col3.write(row['תאריך'])
        col4.write(f"{row['שעת התחלה']} - {row['שעת סיום']}")
        col5.write(row['סיבה'])
        
        # כפתור מחיקה עם אישור
        if col6.button("🗑️", key=f"del_{index}"):
            st.session_state[f"confirm_delete_{index}"] = True

        # מנגנון אישור מחיקה שקופץ מתחת לשורה
        if st.session_state.get(f"confirm_delete_{index}", False):
            st.warning(f"למחוק את ההזמנה של {row['עובד']}?")
            c1, c2, _ = st.columns([1, 1, 8])
            if c1.button("כן, מחק", key=f"yes_{index}"):
                st.session_state.bookings = st.session_state.bookings.drop(index).reset_index(drop=True)
                st.session_state[f"confirm_delete_{index}"] = False
                st.rerun()
            if c2.button("ביטול", key=f"no_{index}"):
                st.session_state[f"confirm_delete_{index}"] = False
                st.rerun()
        st.write("---")
else:
    st.info("אין הזמנות עתידיות.")
