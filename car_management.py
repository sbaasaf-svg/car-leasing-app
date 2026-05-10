import streamlit as st
import pandas as pd
from datetime import datetime, time

st.set_page_config(page_title="ניהול צי רכבים", page_icon="🚗")

# טעינת נתונים לזיכרון (כדי שהבדיקה תעבוד בזמן אמת)
if 'bookings' not in st.session_state:
    st.session_state.bookings = pd.DataFrame(columns=["עובד", "רכב", "תאריך", "שעת התחלה", "שעת סיום", "סיבה"])

st.title("🚗 יומן רכבים - בדיקת זמינות")

# רשימת רכבים
cars = ["11111111", "2222222"]

with st.sidebar:
    st.header("ביצוע הזמנה")
    user_name = st.text_input("שם העובד")
    selected_car = st.selectbox("בחר רכב", cars)
    booking_date = st.date_input("תאריך", datetime.now())
    
    start_t = st.time_input("שעת התחלה", time(9, 0))
    end_t = st.time_input("שעת סיום", time(10, 0))
    
    reason = st.text_input("סיבת הנסיעה")
    submit = st.button("אשר הזמנה")

if submit:
    if not user_name or not reason:
        st.error("נא למלא שם וסיבה.")
    elif start_t >= end_t:
        st.error("שעת הסיום חייבת להיות אחרי שעת ההתחלה.")
    else:
        # לוגיקת בדיקת כפילויות חסינה:
        is_conflict = False
        df = st.session_state.bookings
        
        # 1. סינון רק לאותו רכב ובדיוק לאותו תאריך
        same_day_car = df[(df['רכב'] == selected_car) & (df['תאריך'] == str(booking_date))]
        
        for _, row in same_day_car.iterrows():
            # המרת השעות מהטבלה חזרה לאובייקט זמן לצורך השוואה
            existing_start = datetime.strptime(row['שעת התחלה'], '%H:%M').time()
            existing_end = datetime.strptime(row['שעת סיום'], '%H:%M').time()
            
            # בדיקת חפיפה מתמטית:
            # (התחלה חדשה לפני סיום קיים) וגם (סיום חדש אחרי התחלה קיימת)
            if start_t < existing_end and end_t > existing_start:
                is_conflict = True
                conflict_user = row['עובד']
                break
        
        if is_conflict:
            st.error(f"לא ניתן להזמין! הרכב תפוס על ידי {conflict_user} בין {existing_start.strftime('%H:%M')} ל-{existing_end.strftime('%H:%M')}")
        else:
            new_booking = {
                "עובד": user_name,
                "רכב": selected_car,
                "תאריך": str(booking_date),
                "שעת התחלה": start_t.strftime('%H:%M'),
                "שעת סיום": end_t.strftime('%H:%M'),
                "סיבה": reason
            }
            st.session_state.bookings = pd.concat([st.session_state.bookings, pd.DataFrame([new_booking])], ignore_index=True)
            st.success(f"ההזמנה לרכב {selected_car} אושרה!")

# הצגת היומן
st.subheader("📋 לו״ז נסיעות מעודכן")
if not st.session_state.bookings.empty:
    st.dataframe(st.session_state.bookings.sort_values(by=["תאריך", "שעת התחלה"]), use_container_width=True)
else:
    st.info("אין הזמנות כרגע.")
