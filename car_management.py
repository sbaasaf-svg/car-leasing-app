import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗", layout="wide")

# CSS עדין לשיפור הריווח בלי ליצור עומס
st.markdown("""
    <style>
    .stButton button { width: 40px; height: 40px; padding: 0; }
    hr { margin: 0.8rem 0rem; }
    </style>
    """, unsafe_allow_html=True)

if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 יומן רכבי ליסינג")

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

# --- עיבוד נתונים (סינון ומיון) ---
df = st.session_state.bookings.copy()
if not df.empty:
    df['temp_date'] = pd.to_datetime(df['תאריך']).dt.date
    # מציג רק מהיום והלאה וממיין לפי תאריך ושעה
    df = df[df['temp_date'] >= datetime.now().date()].sort_values(by=['temp_date', 'שעת התחלה'])

st.markdown("### רשימת נסיעות")
st.write("---")

# כותרות - נתנו לעמודת הפח (האחרונה) רוחב ספציפי כדי שלא תתנגש
h_cols = st.columns([1.5, 1.2, 1.2, 1.5, 3, 0.8])
titles = ["**עובד**", "**רכב**", "**תאריך**", "**שעות**", "**סיבה**", "**מחיקה**"]
for col, title in zip(h_cols, titles):
    col.write(title)
st.write("---")

if not df.empty:
    for index, row in df.iterrows():
        # יצירת שורה עם מרווחים מוגדרים
        cols = st.columns([1.5, 1.2, 1.2, 1.5, 3, 0.8])
        
        cols.write(row['עובד'])
        cols.write(row['רכב'])
        cols.write(row['תאריך'])
        cols.write(f"{row['שעת התחלה']} - {row['שעת סיום']}")
        cols.write(row['סיבה'])
        
        # כפתור מחיקה בעמודה מרווחת משלו
        if cols.button("🗑️", key=f"del_{index}"):
            st.session_state[f"confirm_{index}"] = True

        # הודעת אישור מחיקה במידת הצורך
        if st.session_state.get(f"confirm_{index}", False):
            with st.status(f"מחיקת ההזמנה של {row['עובד']}", expanded=True):
                st.write("האם אתה בטוח שברצונך למחוק את ההזמנה?")
                b1, b2 = st.columns(2)
                if b1.button("✅ כן, מחק", key=f"y_{index}"):
                    st.session_state.bookings = st.session_state.bookings.drop(index).reset_index(drop=True)
                    st.session_state[f"confirm_{index}"] = False
                    st.rerun()
                if b2.button("❌ ביטול", key=f"n_{index}"):
                    st.session_state[f"confirm_{index}"] = False
                    st.rerun()
        
        st.write("---")
else:
    st.info("אין הזמנות עתידיות במערכת.")
