import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd

# Ініціалізація Firebase лише один раз
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase_key.json")
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://metal-prices-ebe36-default-rtdb.firebaseio.com/'
    })

# Зчитування даних з Firebase
ref = db.reference('metals')
data = ref.get()

st.title("Інформаційна панель: Ціни на метали")

# Вибір джерела
source = st.selectbox("Оберіть джерело даних:", options=["kitco", "matthey"])

if source not in data:
    st.error(f"Джерело {source} не знайдено в базі.")
    st.stop()

source_data = data[source]

# Перетворення даних на DataFrame
df = pd.DataFrame(source_data)

# Залежно від структури, підготувати DataFrame для kitco та matthey
if source == "kitco":
    # Для kitco дані у вигляді списку словників
    df = pd.DataFrame(source_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').sort_index()
elif source == "matthey":
    # Для matthey аналогічно
    df = pd.DataFrame(source_data)
    df['Date'] = pd.to_datetime(df['Date'])
    df = df.set_index('Date').sort_index()

# Вибір металів
all_metals = list(df.columns)
if 'Metal' in all_metals:
    all_metals.remove('Metal')  # видаляємо колонку Metal, якщо вона є

selected_metals = st.multiselect("Оберіть метали для візуалізації:", options=all_metals, default=all_metals[:3])

# Вибір дат
min_date = df.index.min()
max_date = df.index.max()
date_range = st.date_input("Оберіть часовий проміжок:", value=(min_date, max_date), min_value=min_date, max_value=max_date)

if len(date_range) != 2:
    st.warning("Будь ласка, оберіть початкову та кінцеву дату.")
    st.stop()

start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])

# Фільтрація по датах
filtered_df = df.loc[(df.index >= start_date) & (df.index <= end_date)]

if filtered_df.empty:
    st.warning("Немає даних за обраний період.")
    st.stop()

# Відображення графіку
if selected_metals:
    st.line_chart(filtered_df[selected_metals])
else:
    st.info("Оберіть хоча б один метал для відображення графіку.")

# Відображення цін за попередні дні
days_back = st.number_input("Кількість попередніх днів для відображення у текстовому форматі:", min_value=1, max_value=30, value=5)

prev_days_df = filtered_df.tail(days_back)

st.write(f"Ціни за останні {days_back} днів:")

st.dataframe(prev_days_df[selected_metals])


