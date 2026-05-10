import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗", layout="wide")

# אתחול בסיס הנתונים בזיכרון
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["ID", "עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 יומן רכבים חכם - ניהול ותפעול")

# רשימת רכבים
cars = ["11111111", "2222222"]

# --- פונקציות עזר ---
def delete_booking(index):
    st.session_state.bookings = st.session_state.bookings.drop(index).reset_index(drop=True)
    st.rerun()

# --- ממשק הזמנה (Sidebar) ---
with st.sidebar:
    st.header("ביצוע הזמנה חדשה")
    user_name = st.text_input("שם העובד")
    selected_car = st.selectbox("בחר רכב", cars)
    booking_date = st.date_input("תאריך", datetime.now())
    
    col1, col2 = st.columns(2)
    with col1:
        start_t = st.time_input("שעת התחלה", time(9, 0))
    with col2:
        end_t = st.time_input("שעת סיום", time(10, 0))
    
    reason = st.text_input("סיבת הנסיעה")
    submit = st.button("אשר הזמנה")

if submit:
    if not user_name or not reason:
        st.error("נא למלא שם וסיבה.")
    elif start_t >= end_t:
        st.error("שעת הסיום חייבת להיות אחרי שעת ההתחלה.")
    elif booking_date < datetime.now().date():
        st.error("לא ניתן להזמין רכב לתאריך מהעבר.")
    else:
        # בדיקת כפילויות
        df = st.session_state.bookings
        same_day_car = df[(df['רכב'] == selected_car) & (df['תאריך'] == str(booking_date))]
        
        is_conflict = False
        for _, row in same_day_car.iterrows():
            exist_start = datetime.strptime(row['שעת התחלה'], '%H:%M').time()
            exist_end = datetime.strptime(row['שעת סיום'], '%H:%M').time()
            if start_t < exist_end and end_t > exist_start:
                is_conflict = True
                conflict_user = row['עובד']
                break
        
        if is_conflict:
            st.error(f"הרכב תפוס ע\"י {conflict_user} בשעות אלו.")
        else:
            new_booking = {
                "ID": datetime.now().strftime("%H%M%S"), # מזהה ייחודי למחיקה
                "עובד": user_name,
                "רכב": selected_car,
                "תאריך": str(booking_date),
                "שעת התחלה": start_t.strftime('%H:%M'),
                "שעת סיום": end_t.strftime('%H:%M'),
                "סיבה": reason
            }
            st.session_state.bookings = pd.concat([st.session_state.bookings, pd.DataFrame([new_booking])], ignore_index=True)
            st.success("ההזמנה בוצעה!")
            st.rerun()

# --- תצוגת יומן הנסיעות ---
st.subheader("📋 לו״ז נסיעות עתידי (ממוין לפי תאריך)")

if not st.session_state.bookings.empty:
    # 1. סינון נסיעות מהעבר (משאיר רק מהיום והלאה)
    today = datetime.now().date()
    df_display = st.session_state.bookings.copy()
    df_display['temp_date'] = pd.to_datetime(df_display['תאריך']).dt.date
    df_display = df_display[df_display['temp_date'] >= today]
    
    # 2. מיון: תאריך קרוב למעלה, ואז לפי שעת התחלה
    df_display = df_display.sort_values(by=['temp_date', 'שעת התחלה'], ascending=[True, True])
    
    # הצגה עם כפתורי מחיקה
    for index, row in df_display.iterrows():
        with st.expander(f"🚗 {row['תאריך']} | {row['שעת התחלה']}-{row['שעת סיום']} | רכב: {row['רכב']} ({row['עובד']})"):
            st.write(f"**סיבת הנסיעה:** {row['סיבה']}")
            if st.button(f"מחק הזמנה", key=f"del_{index}"):
                delete_booking(index)
else:
    st.info("אין הזמנות עתידיות ביומן.")
