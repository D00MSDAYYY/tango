import streamlit as st
import pandas as pd
import numpy as np
st.set_page_config(layout="wide")
st.title("Динамическая сетка")

# Количество колонок выбирает пользователь
num_columns = st.slider("Количество колонок", 2, 6, 3)

# Создаем динамические колонки
columns = st.columns(num_columns)

# Заполняем колонки
for i, col in enumerate(columns):
    with col:
        st.subheader(f"Колонка {i+1}")
        
        # Создаем уникальные ключи для каждого виджета
        st.text_input(f"Имя {i+1}", key=f"name_{i}")
        st.number_input(f"Число {i+1}", value=i, key=f"num_{i}")
        st.button(f"Действие {i+1}", key=f"action_{i}")

num_columns = st.slider("Количество колонокr", 2, 6, 3)
columns = st.columns(num_columns)

# Заполняем колонки
for i, col in enumerate(columns):
    k = i + 100
    with col:
        st.subheader(f"Колонка {i+1}")
        
        # Создаем уникальные ключи для каждого виджета
        st.text_input(f"Имя {i+1}", key=f"name_{k}")
        st.number_input(f"Число {i+1}", value=i, key=f"num_{k}")
        st.button(f"Действие {i+1}", key=f"action_{k}")

# Сетка для отображения данных
st.subheader("Сетка карточек с данными")

# Пример данных
data = {
    "Продукт": ["Ноутбук", "Телефон", "Планшет", "Наушники", "Часы"],
    "Цена": [1000, 500, 300, 150, 200],
    "Рейтинг": [4.5, 4.2, 4.0, 4.7, 4.3]
}

df = pd.DataFrame(data)

# Создаем сетку карточек
cols_per_row = 3
rows = (len(df) + cols_per_row - 1) // cols_per_row  # Округление вверх

for row in range(rows):
    cols = st.columns(cols_per_row)
    
    for col_idx in range(cols_per_row):
        item_idx = row * cols_per_row + col_idx
        
        if item_idx < len(df):
            with cols[col_idx]:
                product = df.iloc[item_idx]
                
                # Карточка товара
                with st.container():
                    st.markdown(f"""
                    <div style="
                        border: 1px solid #e0e0e0;
                        border-radius: 10px;
                        padding: 15px;
                        margin-bottom: 10px;
                        background-color: #ffffff;
                        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                    ">
                        <h3 style="margin-top: 0;">{product['Продукт']}</h3>
                        <p><strong>Цена:</strong> ${product['Цена']}</p>
                        <p><strong>Рейтинг:</strong> {product['Рейтинг']}/5</p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Кнопка добавления в корзину
                    if st.button(f"Купить {product['Продукт']}", key=f"buy_{item_idx}"):
                        st.success(f"Добавлено: {product['Продукт']}")