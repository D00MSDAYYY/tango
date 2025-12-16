import streamlit as st
import plotly.graph_objects as go
import numpy as np
import time
from datetime import datetime

st.title("🎬 Кинематографически плавный график (60 FPS)")

# Настройка для максимальной производительности
st.markdown("""
<style>
    .stPlotlyChart {
        will-change: transform;
    }
    div[data-testid="stVerticalBlock"] {
        gap: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация с предзагруженными данными
if 'cinema_data' not in st.session_state:
    # Предзагружаем начальные данные для плавности
    t = np.linspace(0, 10, 100)
    y = np.sin(t)
    st.session_state.cinema_data = {
        'x': t.tolist(),
        'y': y.tolist(),
        'time': [datetime.now()] * len(t)
    }

# Создаем фигуру один раз
fig = go.Figure()

# Основная линия
fig.add_trace(go.Scatter(
    x=st.session_state.cinema_data['x'],
    y=st.session_state.cinema_data['y'],
    mode='lines',
    name='Сигнал',
    line=dict(color='#8A2BE2', width=3),
    opacity=0.9
))

# Эффект свечения
fig.add_trace(go.Scatter(
    x=st.session_state.cinema_data['x'],
    y=st.session_state.cinema_data['y'],
    mode='lines',
    name='Свечение',
    line=dict(color='#9370DB', width=8),
    opacity=0.2,
    showlegend=False
))

fig.update_layout(
    title="Плавный график с кинематографическим качеством",
    xaxis_title="Время",
    yaxis_title="Амплитуда",
    height=400,
    template="plotly_dark",
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(20,20,40,0.1)',
    xaxis=dict(
        showgrid=True,
        gridcolor='rgba(100,100,100,0.2)',
        zeroline=False
    ),
    yaxis=dict(
        showgrid=True,
        gridcolor='rgba(100,100,100,0.2)',
        zeroline=False
    )
)

# Отображаем график
graph_display = st.empty()
graph_display.plotly_chart(fig, use_container_width=True, 
                         config={'displayModeBar': False})

# Производительность
perf_placeholder = st.empty()

# Запуск
if st.button("🎬 Запуск кинематографического режима", type="primary"):
    fps_counter = []
    last_time = time.time()
    
    for frame in range(1000):  # 1000 кадров
        current_time = time.time()
        
        # Генерация нового кадра данных
        t = frame * 0.05
        new_value = (np.sin(t) + 
                    0.3 * np.sin(t * 3) + 
                    0.1 * np.random.randn())
        
        # Добавляем точку
        st.session_state.cinema_data['x'].append(t)
        st.session_state.cinema_data['y'].append(new_value)
        
        # Ограничиваем буфер для производительности
        if len(st.session_state.cinema_data['x']) > 300:
            st.session_state.cinema_data['x'] = st.session_state.cinema_data['x'][-300:]
            st.session_state.cinema_data['y'] = st.session_state.cinema_data['y'][-300:]
        
        # Обновляем только данные в существующих трассах
        fig.data[0].x = st.session_state.cinema_data['x']
        fig.data[0].y = st.session_state.cinema_data['y']
        fig.data[1].x = st.session_state.cinema_data['x']
        fig.data[1].y = st.session_state.cinema_data['y']
        
        # Плавное следование камеры
        if len(st.session_state.cinema_data['x']) > 100:
            fig.update_layout(
                xaxis=dict(
                    range=[
                        st.session_state.cinema_data['x'][-100],
                        st.session_state.cinema_data['x'][-1] + 2
                    ]
                )
            )
        
        # Обновляем график
        graph_display.plotly_chart(fig, use_container_width=True,
                                 config={'displayModeBar': False})
        
        # Расчет FPS
        frame_time = time.time() - current_time
        fps = 1.0 / frame_time if frame_time > 0 else 0
        fps_counter.append(fps)
        
        if len(fps_counter) > 10:
            fps_counter.pop(0)
        
        avg_fps = np.mean(fps_counter)
        
        # Отображение производительности
        with perf_placeholder.container():
            cols = st.columns(3)
            cols[0].metric("🎯 FPS", f"{avg_fps:.1f}")
            cols[1].metric("📊 Точки", len(st.session_state.cinema_data['x']))
            cols[2].metric("⚡ Задержка", f"{frame_time*1000:.1f}ms")
        
        # Точная задержка для целевого FPS
        target_fps = 60
        target_frame_time = 1.0 / target_fps
        elapsed = time.time() - current_time
        sleep_time = max(0, target_frame_time - elapsed)
        time.sleep(sleep_time)