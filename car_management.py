import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗", layout="wide")

# סגנון CSS להקטנת מרווחים (Padding) בין אלמנטים
st.markdown("""
    <style>
    .block-container {padding-top: 1rem; padding-bottom: 0rem;}
    div[data-testid="stVerticalBlock"] > div {margin-bottom: -1rem;}
    hr {margin: 0.5rem 0rem;}
    </style>
    """, unsafe_allow_html=True)

if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 ניהול צי רכבים - מבט מרוכז")

# --- תפריט צד ---
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

# --- תצוגה צפופה ---
st.markdown("---")
# כותרות צפופות
h_cols = st.columns([1, 1, 1, 1.2, 3, 0.4])
titles = ["**עובד**", "**רכב**", "**תאריך**", "**שעות**", "**סיבה**", ""]
for col, title in zip(h_cols, titles):
    col.write(title)
st.markdown("---")

if not df.empty:
    for index, row in df.iterrows():
        # יצירת שורה צפופה
        cols = st.columns([1, 1, 1, 1.2, 3, 0.4])
        cols[0].write(row['עובד'])
        cols[1].write(row['רכב'])
        cols[2].write(row['תאריך'])
        cols[3].write(f"{row['שעת התחלה']}-{row['שעת סיום']}")
        cols[4].write(row['סיבה'])
        
        # כפתור מחיקה קטן במיוחד
        if cols[5].button("🗑️", key=f"del_{index}"):
            st.session_state[f"confirm_{index}"] = True

        # אישור מחיקה בשורה נפרדת רק אם נלחץ
        if st.session_state.get(f"confirm_{index}", False):
            with st.container():
                st.warning(f"למחוק הזמנה של {row['עובד']}?")
                b1, b2, _ = st.columns([1, 1, 8])
                if b1.button("✅ אישור", key=f"y_{index}"):
                    st.session_state.bookings = st.session_state.bookings.drop(index).reset_index(drop=True)
                    st.session_state[f"confirm_{index}"] = False
                    st.rerun()
                if b2.button("❌ ביטול", key=f"n_{index}"):
                    st.session_state[f"confirm_{index}"] = False
                    st.rerun()
        
        st.markdown("<hr style='margin:0.2rem 0rem; opacity:0.2;'>", unsafe_allow_html=True)
else:
    st.info("אין הזמנות פעילות.")

