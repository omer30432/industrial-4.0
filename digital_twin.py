import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import time
from datetime import datetime, timedelta
import random

# הגדרת עמוד רחב
st.set_page_config(layout="wide", page_title="Digital Twin Simulation", page_icon="🏭")

# עיצוב CSS מותאם - הוספתי כאן את העיצובים לקומפוננטות החדשות
st.markdown("""
<style>
.main-header {
    font-size: 3rem !important;
    font-weight: 700;
    color: #0066cc;
    text-align: center;
    background: linear-gradient(to right, #0b3866, #1a5cb0);
    color: white;
    padding: 1.5rem;
    border-radius: 10px;
    margin-bottom: 2rem;
}
.subheader {
    font-size: 1.5rem !important;
    font-weight: 500;
}
.highlight {
    background-color: rgba(0, 102, 204, 0.1);
    border-radius: 5px;
    padding: 0.5rem;
    margin-bottom: 1rem;
}
.sensor-critical {
    color: #ff0000;
    font-weight: bold;
    animation: blinker 1s linear infinite;
}
.sensor-warning {
    color: #ffa500;
    font-weight: bold;
}
.sensor-normal {
    color: #00cc00;
}
@keyframes blinker {
  50% { opacity: 0.5; }
}
.stButton>button {
    width: 100%;
}
.event-log {
    height: 200px;
    overflow-y: auto;
    background-color: #f0f2f6;
    border-radius: 5px;
    padding: 10px;
    font-family: monospace;
}
/* תוספת עיצובים לקומפוננטות החדשות */
.scenario-card {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
    border-left: 5px solid #0066cc;
}
.lifecycle-risk-high {
    background-color: rgba(255, 0, 0, 0.1);
    border-left: 5px solid #ff0000;
}
.lifecycle-risk-medium {
    background-color: rgba(255, 165, 0, 0.1);
    border-left: 5px solid #ffa500;
}
.lifecycle-risk-low {
    background-color: rgba(0, 204, 0, 0.1);
    border-left: 5px solid #00cc00;
}
.asset-card {
    padding: 15px;
    border-radius: 10px;
    margin-bottom: 10px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}
.progress-container {
    margin-top: 10px;
    margin-bottom: 5px;
    background-color: #f0f0f0;
    border-radius: 5px;
    height: 15px;
}
.progress-bar {
    height: 15px;
    border-radius: 5px;
}
</style>
""", unsafe_allow_html=True)

# כותרת ראשית מרשימה
st.markdown('<div class="main-header">Digital Twin - הדמיה אינטראקטיבית</div>', unsafe_allow_html=True)

# תיאור הפרויקט
with st.expander("מהו תאום דיגיטלי? (הרחב לקריאה)"):
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### תאום דיגיטלי (Digital Twin)
        
        **תאום דיגיטלי** הוא ייצוג וירטואלי מדויק ודינמי של מוצר, תהליך או מערכת פיזית. בניגוד למודל סטטי, 
        תאום דיגיטלי מקבל עדכונים בזמן אמת מהעולם הפיזי באמצעות חיישנים ו-IoT, ומסוגל להשפיע בחזרה על המערכת הפיזית.
        
        #### המאפיינים המרכזיים:
        * **קישוריות דו-כיוונית** - העולם הפיזי משפיע על הדיגיטלי ולהיפך
        * **מבוסס נתוני אמת** - חיישנים מזינים את המודל בנתונים בזמן אמת
        * **יכולות חיזוי** - זיהוי תקלות לפני התרחשותן וחיזוי ביצועים
        * **אופטימיזציה מתמדת** - שיפור תהליכים על בסיס נתונים וסימולציות
        """)
    
    with col2:
        st.image("https://www.techrepublic.com/wp-content/uploads/2022/04/digital-twin.jpeg", 
                 caption="תאום דיגיטלי - דימוי")

# יצירת לוח בקרה עליון
st.markdown('<div class="subheader">פאנל בקרה</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    # הוספנו את "סימולטור תרחישים" לרשימת האפשרויות
    mode = st.selectbox(
        "מצב הדמיה",
        ["מודל המפעל והתאום", "זרימת נתונים בזמן אמת", "זיהוי אנומליות", 
         "אופטימיזציה אוטומטית", "השוואת ביצועים", "סימולטור תרחישים"]
    )

with col2:
    simulation_speed = st.slider("מהירות הדמיה", min_value=0.5, max_value=3.0, value=1.0, step=0.1)
    sensors_active = st.checkbox("חיישנים פעילים", value=True)

with col3:
    time_range = st.select_slider(
        "טווח זמן להצגה",
        options=["שעה אחרונה", "24 שעות אחרונות", "שבוע אחרון", "חודש אחרון"]
    )
    detail_level = st.radio("רמת פירוט", ["גבוהה", "בינונית", "נמוכה"], horizontal=True)

# חלוקת המסך לחלק מרכזי ויומן אירועים
col_main, col_events = st.columns([3, 1])

# יצירת מודל מפעל ותאום דיגיטלי
def create_factory_model():
    # יצירת נתונים בסיסיים למודל המפעל
    machines = ['M1', 'M2', 'M3', 'M4', 'M5', 'M6', 'M7', 'M8']
    x_physical = [0, 10, 20, 30, 5, 15, 25, 35]
    y_physical = [0, 0, 0, 0, 10, 10, 10, 10]
    z_physical = [0, 0, 0, 0, 0, 0, 0, 0]
    
    # העתקת הנתונים לתאום הדיגיטלי עם הזזה
    x_digital = [x + 50 for x in x_physical]
    y_digital = y_physical.copy()
    z_digital = z_physical.copy()
    
    # יצירת נתוני חיישנים
    n_sensors = 40 if detail_level == "גבוהה" else (25 if detail_level == "בינונית" else 15)
    
    sensor_x_physical = []
    sensor_y_physical = []
    sensor_z_physical = []
    sensor_status = []
    
    for i in range(n_sensors):
        machine_idx = i % len(machines)
        sensor_x_physical.append(x_physical[machine_idx] + np.random.uniform(-2, 2))
        sensor_y_physical.append(y_physical[machine_idx] + np.random.uniform(-2, 2))
        sensor_z_physical.append(z_physical[machine_idx] + np.random.uniform(1, 3))
        
        # מצבי חיישנים - רוב החיישנים תקינים, מעט באזהרה ומעט במצב קריטי
        status = np.random.choice(['תקין', 'אזהרה', 'קריטי'], p=[0.7, 0.2, 0.1])
        sensor_status.append(status)
    
    # העתקת נתוני החיישנים לתאום הדיגיטלי
    sensor_x_digital = [x + 50 for x in sensor_x_physical]
    sensor_y_digital = sensor_y_physical.copy()
    sensor_z_digital = sensor_z_physical.copy()
    
    # יצירת המודל התלת-ממדי
    fig = go.Figure()
    
    # יצירת המכונות במודל הפיזי
    for i, (x, y, z, machine) in enumerate(zip(x_physical, y_physical, z_physical, machines)):
        fig.add_trace(go.Mesh3d(
            x=[x-2, x+2, x+2, x-2, x-2, x+2, x+2, x-2],
            y=[y-2, y-2, y+2, y+2, y-2, y-2, y+2, y+2],
            z=[z, z, z, z, z+4, z+4, z+4, z+4],
            i=[0, 0, 0, 0, 4, 4, 4, 4],
            j=[1, 2, 4, 3, 5, 6, 2, 1],
            k=[2, 6, 6, 7, 6, 7, 3, 5],
            color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)],
            opacity=0.7,
            name=f'מכונה {machine} (פיזית)'
        ))
    
    # יצירת המכונות במודל הדיגיטלי
    for i, (x, y, z, machine) in enumerate(zip(x_digital, y_digital, z_digital, machines)):
        fig.add_trace(go.Mesh3d(
            x=[x-2, x+2, x+2, x-2, x-2, x+2, x+2, x-2],
            y=[y-2, y-2, y+2, y+2, y-2, y-2, y+2, y+2],
            z=[z, z, z, z, z+4, z+4, z+4, z+4],
            i=[0, 0, 0, 0, 4, 4, 4, 4],
            j=[1, 2, 4, 3, 5, 6, 2, 1],
            k=[2, 6, 6, 7, 6, 7, 3, 5],
            color=px.colors.qualitative.Plotly[i % len(px.colors.qualitative.Plotly)],
            opacity=0.3,
            name=f'תאום דיגיטלי {machine}'
        ))
    
    # הוספת חיישנים לפי סטטוס
    colors = {'תקין': 'green', 'אזהרה': 'orange', 'קריטי': 'red'}
    
    for status in colors.keys():
        indices = [i for i, s in enumerate(sensor_status) if s == status]
        
        if indices:
            x_status = [sensor_x_physical[i] for i in indices]
            y_status = [sensor_y_physical[i] for i in indices]
            z_status = [sensor_z_physical[i] for i in indices]
            
            fig.add_trace(go.Scatter3d(
                x=x_status,
                y=y_status,
                z=z_status,
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors[status],
                    symbol='circle',
                    opacity=0.9
                ),
                name=f'חיישנים: {status}'
            ))
            
            # הוספת החיישנים גם לתאום הדיגיטלי
            x_digital_status = [sensor_x_digital[i] for i in indices]
            y_digital_status = [sensor_y_digital[i] for i in indices]
            z_digital_status = [sensor_z_digital[i] for i in indices]
            
            fig.add_trace(go.Scatter3d(
                x=x_digital_status,
                y=y_digital_status,
                z=z_digital_status,
                mode='markers',
                marker=dict(
                    size=8,
                    color=colors[status],
                    symbol='diamond',
                    opacity=0.5
                ),
                name=f'חיישנים דיגיטליים: {status}'
            ))
    
    # הוספת קווי חיבור בין העולם הפיזי לדיגיטלי
    for i in range(min(10, n_sensors)):
        fig.add_trace(go.Scatter3d(
            x=[sensor_x_physical[i], sensor_x_digital[i], None],
            y=[sensor_y_physical[i], sensor_y_digital[i], None],
            z=[sensor_z_physical[i], sensor_z_digital[i], None],
            mode='lines',
            line=dict(
                color='blue',
                width=2,
                dash='dash'
            ),
            showlegend=False
        ))
    
    # עדכון פרמטרי תצוגה
    fig.update_layout(
        title='מודל תלת-ממדי של מפעל ותאום דיגיטלי',
        scene=dict(
            xaxis_title='X',
            yaxis_title='Y',
            zaxis_title='Z',
            aspectmode='data'
        ),
        margin=dict(l=0, r=0, b=0, t=30),
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        ),
        height=600
    )
    
    return fig

# יצירת הדמיית זרימת נתונים
def create_data_flow():
    timepoints = 100
    if time_range == "שעה אחרונה":
        time_delta = 1  # שעה
    elif time_range == "24 שעות אחרונות":
        time_delta = 24  # 24 שעות
    elif time_range == "שבוע אחרון":
        time_delta = 24 * 7  # שבוע
    else:
        time_delta = 24 * 30  # חודש
    
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=time_delta)
    timestamps = pd.date_range(start=start_time, end=end_time, periods=timepoints)
    
    # יצירת נתונים לחיישנים שונים
    sensor_names = ['טמפרטורה (°C)', 'לחץ (bar)', 'רעידות (mm/s)', 'זרם חשמלי (A)', 'מהירות (RPM)']
    
    # ערכי בסיס וספים
    base_values = {
        'טמפרטורה (°C)': 75,
        'לחץ (bar)': 120,
        'רעידות (mm/s)': 2.5,
        'זרם חשמלי (A)': 80,
        'מהירות (RPM)': 1750
    }
    
    thresholds = {
        'טמפרטורה (°C)': {'warning': 80, 'critical': 85},
        'לחץ (bar)': {'warning': 130, 'critical': 140},
        'רעידות (mm/s)': {'warning': 3.0, 'critical': 3.5},
        'זרם חשמלי (A)': {'warning': 90, 'critical': 95},
        'מהירות (RPM)': {'warning': 1800, 'critical': 1850}
    }
    
    # יצירת גרף עבור כל חיישן
    fig = go.Figure()
    
    colors = {
        'טמפרטורה (°C)': 'red',
        'לחץ (bar)': 'blue',
        'רעידות (mm/s)': 'orange',
        'זרם חשמלי (A)': 'purple',
        'מהירות (RPM)': 'green'
    }
    
    # יצירת נתונים עם אנומליות
    for sensor in sensor_names:
        base = base_values[sensor]
        
        # יצירת תנודתיות טבעית
        noise_level = 0.05 * base  # 5% רעש
        trend = np.sin(np.linspace(0, 4*np.pi, timepoints)) * 0.1 * base
        
        # ערכי חיישן בסיסיים
        values = base + trend + np.random.normal(0, noise_level, timepoints)
        
        # הוספת אנומליות בהתאם למצב ההדמיה
        if mode in ["זיהוי אנומליות", "אופטימיזציה אוטומטית"]:
            # יצירת 2-3 אנומליות
            for _ in range(random.randint(2, 3)):
                anomaly_start = random.randint(10, timepoints - 20)
                anomaly_length = random.randint(3, 8)
                
                # סוג האנומליה - פיק כלפי מעלה או מטה
                if random.random() > 0.5:
                    # פיק כלפי מעלה
                    for i in range(anomaly_length):
                        if anomaly_start + i < timepoints:
                            values[anomaly_start + i] = base + base * 0.2 + np.random.normal(0, noise_level/2)
                else:
                    # פיק כלפי מטה
                    for i in range(anomaly_length):
                        if anomaly_start + i < timepoints:
                            values[anomaly_start + i] = base - base * 0.15 + np.random.normal(0, noise_level/2)
        
        # אם במצב אופטימיזציה, נראה שיפור לאחר התערבות
        if mode == "אופטימיזציה אוטומטית":
            optimization_point = int(timepoints * 0.7)
            
            # שיפור בנתונים אחרי האופטימיזציה
            for i in range(optimization_point, timepoints):
                # יצירת מגמת שיפור
                values[i] = base + (values[i] - base) * 0.6  # מקטין את החריגה מהבסיס
        
        # סימון אנומליות (חריגות מהספים)
        anomalies_warning = []
        anomalies_critical = []
        
        for i, val in enumerate(values):
            if val >= thresholds[sensor]['critical']:
                anomalies_critical.append((timestamps[i], val))
            elif val >= thresholds[sensor]['warning']:
                anomalies_warning.append((timestamps[i], val))
        
        # הוספת קו עבור ערכי החיישן
        fig.add_trace(go.Scatter(
            x=timestamps,
            y=values,
            mode='lines',
            name=sensor,
            line=dict(
                color=colors[sensor],
                width=2
            )
        ))
        
        # הוספת קווי סף
        fig.add_shape(
            type="line",
            x0=timestamps[0],
            y0=thresholds[sensor]['warning'],
            x1=timestamps[-1],
            y1=thresholds[sensor]['warning'],
            line=dict(
                color="orange",
                width=1,
                dash="dash",
            )
        )
        
        fig.add_shape(
            type="line",
            x0=timestamps[0],
            y0=thresholds[sensor]['critical'],
            x1=timestamps[-1],
            y1=thresholds[sensor]['critical'],
            line=dict(
                color="red",
                width=1,
                dash="dash",
            )
        )
        
        # הוספת סימון לאנומליות
        if anomalies_warning:
            fig.add_trace(go.Scatter(
                x=[x[0] for x in anomalies_warning],
                y=[x[1] for x in anomalies_warning],
                mode='markers',
                marker=dict(
                    size=8,
                    color='orange',
                    symbol='circle',
                    line=dict(
                        color='white',
                        width=1
                    )
                ),
                name=f'אזהרה - {sensor}'
            ))
        
        if anomalies_critical:
            fig.add_trace(go.Scatter(
                x=[x[0] for x in anomalies_critical],
                y=[x[1] for x in anomalies_critical],
                mode='markers',
                marker=dict(
                    size=10,
                    color='red',
                    symbol='x',
                    line=dict(
                        color='white',
                        width=1
                    )
                ),
                name=f'קריטי - {sensor}'
            ))
    
    # אם במצב אופטימיזציה, נוסיף קו אנכי והתראה בנקודת ההתערבות
    if mode == "אופטימיזציה אוטומטית":
        optimization_point = timestamps[int(timepoints * 0.7)]
        
        fig.add_shape(
            type="line",
            x0=optimization_point,
            y0=0,
            x1=optimization_point,
            y1=2000,  # גבוה מספיק לכסות את כל הערכים
            line=dict(
                color="green",
                width=2,
                dash="dot",
            )
        )
        
        fig.add_annotation(
            x=optimization_point,
            y=1900,
            text="התערבות אוטומטית",
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="green",
            font=dict(
                size=12,
                color="green"
            ),
            align="center"
        )
    
    # הגדרות תצוגה
    fig.update_layout(
        title='זרימת נתונים בזמן אמת מחיישנים',
        xaxis_title='זמן',
        yaxis_title='ערך נמדד',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=600
    )
    
    return fig

# יצירת דאשבורד השוואה
def create_comparison_dashboard():
    # יצירת גרף השוואת ביצועים
    categories = ['חיזוי תקלות', 'זמן תגובה', 'איכות תחזוקה', 'יעילות אנרגטית', 'זמינות ציוד']
    
    traditional = [30, 45, 60, 40, 70]
    digital_twin = [90, 95, 85, 80, 95]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=traditional,
        theta=categories,
        fill='toself',
        name='מערכת מסורתית',
        line_color='firebrick'
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=digital_twin,
        theta=categories,
        fill='toself',
        name='עם תאום דיגיטלי',
        line_color='royalblue'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=True,
        title='השוואת ביצועים'
    )
    
    # יצירת גרף ROI
    companies = ['BMW', 'Siemens', 'GE', 'Unilever', 'Industry Average']
    roi_values = [30, 360, 200, 150, 240]
    
    roi_fig = go.Figure(go.Bar(
        x=companies,
        y=roi_values,
        marker_color='royalblue',
        text=[f'{v}%' for v in roi_values],
        textposition='auto'
    ))
    
    roi_fig.update_layout(
        title='ROI של יישומי תאום דיגיטלי',
        xaxis_title='חברה',
        yaxis_title='ROI (%)',
        height=300
    )
    
    # יצירת טבלת השוואת עלויות
    cost_categories = ['עלות תחזוקה', 'זמן השבתה', 'צריכת אנרגיה', 'איכות מוצר']
    traditional_costs = [100, 100, 100, 100]
    dt_costs = [65, 30, 80, 130]  # ערך מעל 100 משמעותו שיפור לאיכות המוצר
    
    cost_fig = go.Figure()
    
    cost_fig.add_trace(go.Bar(
        x=cost_categories,
        y=traditional_costs,
        name='מערכת מסורתית',
        marker_color='firebrick'
    ))
    
    cost_fig.add_trace(go.Bar(
        x=cost_categories,
        y=dt_costs,
        name='עם תאום דיגיטלי',
        marker_color='royalblue'
    ))
    
    for i, (trad, dt) in enumerate(zip(traditional_costs, dt_costs)):
        if cost_categories[i] == 'איכות מוצר':
            diff = ((dt - trad) / trad) * 100
            label = f'+{diff:.0f}%'
            color = 'green'
        else:
            diff = ((trad - dt) / trad) * 100
            label = f'-{diff:.0f}%'
            color = 'green'
        
        cost_fig.add_annotation(
            x=cost_categories[i],
            y=dt + 5,
            text=label,
            showarrow=False,
            font=dict(
                size=14,
                color=color
            )
        )
    
    cost_fig.update_layout(
        title='השפעת תאום דיגיטלי על עלויות וביצועים',
        xaxis_title='קטגוריה',
        yaxis_title='אחוז (בסיס 100)',
        barmode='group',
        height=300
    )
    
    return fig, roi_fig, cost_fig

# פונקציה להוספת אירועים ליומן
def add_event(container):
    event_types = {
        "מודל המפעל והתאום": [
            "חיישן טמפרטורה M3-12 מדווח על עלייה הדרגתית",
            "חיישן לחץ M7-5 חזר לתפקוד תקין",
            "בוצע עדכון לתאום הדיגיטלי של מכונה 2",
            "התקבלה התראה על סטייה קלה בחיישן רעידות",
            "המלצת כיוונון אוטומטית יושמה במכונה 4"
        ],
        "זרימת נתונים בזמן אמת": [
            "זוהתה תנודתיות חריגה בנתוני טמפרטורה",
            "מבוצע ניתוח השוואתי של נתוני לחץ",
            "התקבלה התראה על שינוי מגמה בצריכת אנרגיה",
            "סף אזהרה נחצה בחיישן זרם חשמלי",
            "המערכת מזהה דפוס חדש בנתוני המהירות"
        ],
        "זיהוי אנומליות": [
            "אנומליה קריטית זוהתה במכונה 5 - תחזית לכשל בתוך 48 שעות",
            "התראה: סימני שחיקה מוקדמים במסוע המרכזי",
            "המערכת איתרה דפוס תקלה מוכר - מופעל פרוטוקול מניעה",
            "אנומליה בנתוני חיישן מהירות - תיקון נדרש",
            "מערכת ה-AI זיהתה חריגה משמעותית בנתוני החיישנים"
        ],
        "אופטימיזציה אוטומטית": [
            "הושלמה אופטימיזציה של פרמטרי ייצור - שיפור יעילות ב-12%",
            "בוצע כוונון אוטומטי למכונה 3 - צפוי חיסכון של 8% באנרגיה",
            "מערכת AI ממליצה על שינוי סדר העבודה לחיסכון של 15% בזמן",
            "התאמה אוטומטית של פרמטרי ייצור בעקבות שינוי תנאי סביבה",
            "המלצה: הזזת תחזוקה מתוכננת ב-48 שעות לפי תחזית מערכת"
        ],
        "השוואת ביצועים": [
            "דוח ROI מעודכן: החזר השקעה של 215% לאחר 24 חודשים",
            "זמן השבתה שנמנע הודות לתאום דיגיטלי: 287 שעות השנה",
            "השוואת ביצועים: 42% פחות תקלות לעומת התקופה המקבילה אשתקד",
            "התאום הדיגיטלי זיהה 12 הזדמנויות לשיפור תהליכים שלא זוהו קודם",
            "הושלם ניתוח עלות-תועלת: לתאום הדיגיטלי ROI של פי 3 מהצפוי"
        ],
        "סימולטור תרחישים": [
            "הושלמה סימולציית כשל חיישנים - זוהו 3 נקודות תורפה",
            "סימולציית הפסקת חשמל חשפה צורך בשדרוג מערכת גיבוי",
            "המערכת מזהה סיכון גבוה לכשל בשרשרת בקו ייצור 2",
            "חיזוי החלפת ציוד אופטימלית: מכונה M4 בעוד 8 חודשים",
            "הסתיימה סימולציית תרחיש רעידת אדמה - השפעה צפויה: 65% ירידה בתפוקה"
        ]
    }
    
    current_time = datetime.now().strftime('%H:%M:%S')
    status_class = ""
    
    event = random.choice(event_types.get(mode, event_types["מודל המפעל והתאום"]))
    
    # בדיקה אם מדובר באירוע קריטי
    if "קריטי" in event or "כשל" in event:
        status_class = "sensor-critical"
    elif "התראה" in event or "אזהרה" in event:
        status_class = "sensor-warning"
    else:
        status_class = "sensor-normal"
    
    # הוספת האירוע ליומן
    container.markdown(f"<div class='{status_class}'>{current_time} - {event}</div>", unsafe_allow_html=True)

# ----------------------------------------
# פונקציונליות חדשה: סימולטור תרחישי קיצון
# ----------------------------------------

def create_extreme_scenario_simulator():
    st.markdown("""
    <div class="highlight">
    <strong>סימולטור תרחישי קיצון ועמידות</strong><br>
    בדוק כיצד המערכת תגיב למצבי קיצון ותרחישים בלתי צפויים. התאום הדיגיטלי מאפשר לסמלץ תרחישים שלא היו ניתנים לבדיקה בטוחה בעולם האמיתי.
    </div>
    """, unsafe_allow_html=True)
    
    # בחירת תרחיש
    scenario_type = st.selectbox(
        "בחר סוג תרחיש",
        ["כשל חיישנים", "הפסקת חשמל/מים", "תקלת ציוד קריטי", "שרשרת תגובה", "תנאי קיצון סביבתיים"]
    )
    
    # פרמטרים נוספים לפי סוג התרחיש
    if scenario_type == "כשל חיישנים":
        sensor_failure_percentage = st.slider("אחוז חיישנים כושלים", 10, 90, 30)
        failure_pattern = st.radio(
            "דפוס כשל",
            ["אקראי", "חיישנים קריטיים", "אזור ספציפי"],
            horizontal=True
        )
        redundancy_level = st.select_slider(
            "רמת יתירות במערכת",
            options=["נמוכה", "בינונית", "גבוהה"],
            value="בינונית"
        )
        simulation_params = {
            "sensor_failure": sensor_failure_percentage,
            "pattern": failure_pattern,
            "redundancy": redundancy_level
        }
        
    elif scenario_type == "הפסקת חשמל/מים":
        utility_type = st.radio("סוג תשתית", ["חשמל", "מים", "קיטור", "אוויר דחוס"], horizontal=True)
        outage_duration = st.slider("משך ההפסקה (דקות)", 5, 120, 30)
        backup_systems = st.multiselect(
            "מערכות גיבוי פעילות",
            ["גנרטור חירום", "UPS", "מאגרי מים", "מדחסים עצמאיים"],
            ["גנרטור חירום"]
        )
        simulation_params = {
            "utility": utility_type,
            "duration": outage_duration,
            "backup": backup_systems
        }
        
    elif scenario_type == "תקלת ציוד קריטי":
        equipment = st.selectbox(
            "בחר ציוד קריטי",
            ["מכונה M1 (תחילת קו ייצור)", "מכונה M4 (אמצע קו ייצור)", "מכונה M7 (סוף קו ייצור)", "מערכת בקרה מרכזית"]
        )
        failure_type = st.radio(
            "סוג תקלה",
            ["כשל מלא", "ירידה בביצועים (50%)", "אי-יציבות"],
            horizontal=True
        )
        response_time = st.slider("זמן תגובה למכונאים (דקות)", 5, 120, 30)
        simulation_params = {
            "equipment": equipment,
            "failure_type": failure_type,
            "response_time": response_time
        }
        
    elif scenario_type == "שרשרת תגובה":
        initial_failure = st.selectbox(
            "נקודת כשל התחלתית",
            ["חיישן לחץ M2", "משאבה ראשית", "חיישן טמפרטורה M5", "ספק מתח 24V"]
        )
        cascade_depth = st.slider("עומק שרשרת התגובה", 1, 5, 3)
        safety_systems = st.select_slider(
            "רמת מערכות בטיחות",
            options=["מינימלית", "סטנדרטית", "מתקדמת"],
            value="סטנדרטית"
        )
        simulation_params = {
            "initial_point": initial_failure,
            "cascade_depth": cascade_depth,
            "safety": safety_systems
        }
        
    else:  # תנאי קיצון סביבתיים
        condition_type = st.radio(
            "תנאי קיצון",
            ["טמפרטורה גבוהה", "לחות גבוהה", "קור קיצוני", "רעידת אדמה"],
            horizontal=True
        )
        intensity = st.slider("עוצמה (% מהתנאים המקסימליים)", 70, 100, 85)
        exposure_time = st.slider("משך החשיפה (שעות)", 1, 48, 12)
        simulation_params = {
            "condition": condition_type,
            "intensity": intensity,
            "duration": exposure_time
        }
    
    # כפתור להפעלת הסימולציה
    if st.button("הפעל סימולציה", key="extreme_scenario_btn"):
        st.markdown("### תוצאות סימולציית תרחיש הקיצון")
        
        # חישוב השפעות התרחיש (נשתמש בפונקציה מפושטת כאן)
        impacts = calculate_scenario_impacts(scenario_type, simulation_params)
        
        # הצגת השפעות מיידיות
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("השפעה על תפוקה", f"{impacts['productivity']}%", 
                    f"{impacts['productivity']-100}%", delta_color="inverse")
        
        with col2:
            st.metric("זמן השבתה צפוי", f"{impacts['downtime']} דקות")
        
        with col3:
            st.metric("עלות כלכלית מוערכת", f"${impacts['cost']:,}")
        
        # הצגת השפעות מפורטות לפי תהליכים
        st.markdown("#### השפעת התרחיש על תהליכים")
        
        process_impacts = pd.DataFrame({
            'תהליך': ['קבלת חומרי גלם', 'עיבוד ראשוני', 'הרכבה', 'בקרת איכות', 'אריזה', 'לוגיסטיקה'],
            'השפעה (%)': impacts['process_impacts'],
            'זמן התאוששות (שעות)': impacts['recovery_times']
        })
        
        # ויזואליזציה של השפעות התרחיש
        fig = px.bar(process_impacts, x='תהליך', y='השפעה (%)', 
                    color='השפעה (%)',
                    color_continuous_scale=[(0, 'green'), (0.5, 'orange'), (1, 'red')],
                    range_color=[0, 100])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # הצגת המלצות ופעולות מתקנות
        st.markdown("#### המלצות התאום הדיגיטלי")
        
        for i, recommendation in enumerate(impacts['recommendations']):
            st.markdown(f"""
            <div class="scenario-card">
                <h5>{i+1}. {recommendation['title']}</h5>
                <p>{recommendation['description']}</p>
                <p><strong>השפעה צפויה:</strong> {recommendation['impact']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # הצגת מפת חום של פגיעות
        st.markdown("#### מפת פגיעות המערכת")
        vulnerability_heatmap(impacts['vulnerabilities'])

def calculate_scenario_impacts(scenario_type, params):
    """מחשב את ההשפעות הצפויות של תרחיש הקיצון"""
    impacts = {}
    
    # חישוב ערכי השפעה בסיסיים לפי סוג התרחיש
    if scenario_type == "כשל חיישנים":
        # חישוב פגיעה בתפוקה בהתאם לאחוז החיישנים הכושלים ורמת היתירות
        redundancy_factor = {"נמוכה": 0.3, "בינונית": 0.6, "גבוהה": 0.9}
        base_impact = params["sensor_failure"] / 100
        
        # יתירות מקטינה את ההשפעה
        mitigated_impact = base_impact * (1 - redundancy_factor[params["redundancy"]])
        
        # השפעה גדולה יותר אם החיישנים הקריטיים נפגעים
        if params["pattern"] == "חיישנים קריטיים":
            pattern_multiplier = 1.8
        elif params["pattern"] == "אזור ספציפי":
            pattern_multiplier = 1.5
        else:  # אקראי
            pattern_multiplier = 1.0
        
        productivity_impact = 100 - int(mitigated_impact * pattern_multiplier * 100)
        downtime = int(mitigated_impact * pattern_multiplier * 180)  # זמן השבתה בדקות
        cost = int(downtime * 5000 / 60)  # עלות של 5000$ לשעת השבתה
        
    elif scenario_type == "הפסקת חשמל/מים":
        # השפעה תלויה בסוג התשתית, משך ההפסקה ומערכות גיבוי
        utility_impact = {"חשמל": 1.0, "מים": 0.8, "קיטור": 0.7, "אוויר דחוס": 0.6}
        base_impact = utility_impact[params["utility"]] * params["duration"] / 120
        
        # כל מערכת גיבוי מקטינה את ההשפעה
        backup_reduction = len(params["backup"]) * 0.2
        
        productivity_impact = 100 - int(min(0.95, base_impact - backup_reduction) * 100)
        downtime = params["duration"] if backup_reduction < base_impact else int(params["duration"] * 0.2)
        cost = int(downtime * 5000 / 60)
        
    elif scenario_type == "תקלת ציוד קריטי":
        # השפעה תלויה בסוג הציוד, סוג התקלה וזמן התגובה
        equipment_impact = {
            "מכונה M1 (תחילת קו ייצור)": 0.9,
            "מכונה M4 (אמצע קו ייצור)": 0.7,
            "מכונה M7 (סוף קו ייצור)": 0.5,
            "מערכת בקרה מרכזית": 0.8
        }
        
        failure_impact = {
            "כשל מלא": 1.0,
            "ירידה בביצועים (50%)": 0.5,
            "אי-יציבות": 0.7
        }
        
        base_impact = equipment_impact[params["equipment"]] * failure_impact[params["failure_type"]]
        response_factor = 1.0 + (params["response_time"] - 30) / 120
        
        productivity_impact = 100 - int(min(0.95, base_impact * response_factor) * 100)
        downtime = int(base_impact * params["response_time"] * 1.5)
        cost = int(downtime * 5000 / 60 + base_impact * 20000)  # עלות השבתה + עלות תיקון
        
    elif scenario_type == "שרשרת תגובה":
        # השפעה תלויה בנקודת הכשל ההתחלתית, עומק השרשרת ומערכות בטיחות
        initial_point_impact = {
            "חיישן לחץ M2": 0.4,
            "משאבה ראשית": 0.8,
            "חיישן טמפרטורה M5": 0.5,
            "ספק מתח 24V": 0.7
        }
        
        safety_factor = {"מינימלית": 1.3, "סטנדרטית": 1.0, "מתקדמת": 0.6}
        
        base_impact = initial_point_impact[params["initial_point"]] * (1 + params["cascade_depth"] * 0.2)
        mitigated_impact = base_impact * safety_factor[params["safety"]]
        
        productivity_impact = 100 - int(min(0.95, mitigated_impact) * 100)
        downtime = int(mitigated_impact * params["cascade_depth"] * 60)
        cost = int(downtime * 5000 / 60 + params["cascade_depth"] * 15000)  # עלות השבתה + נזק לציוד
        
    else:  # תנאי קיצון סביבתיים
        # השפעה תלויה בסוג התנאי, עוצמה ומשך החשיפה
        condition_impact = {
            "טמפרטורה גבוהה": 0.6,
            "לחות גבוהה": 0.5,
            "קור קיצוני": 0.7,
            "רעידת אדמה": 0.9
        }
        
        intensity_factor = params["intensity"] / 100 * 1.5
        duration_factor = params["duration"] / 24
        
        base_impact = condition_impact[params["condition"]] * intensity_factor * duration_factor
        
        productivity_impact = 100 - int(min(0.95, base_impact) * 100)
        downtime = int(base_impact * 240)  # עד 4 שעות השבתה
        cost = int(downtime * 5000 / 60 + base_impact * 50000)  # עלות השבתה + נזק תשתיתי
    
    # חישוב השפעות לפי תהליכים - ייחודי לכל תרחיש
    process_impacts, recovery_times = calculate_process_specific_impacts(scenario_type, params)
    
    # המלצות ספציפיות לתרחיש
    recommendations = generate_scenario_recommendations(scenario_type, params)
    
    # מטריצת פגיעות מערכתיות
    vulnerabilities = generate_vulnerability_matrix(scenario_type, params)
    
    # הכנת מבנה התוצאה
    impacts = {
        "productivity": productivity_impact,
        "downtime": downtime,
        "cost": cost,
        "process_impacts": process_impacts,
        "recovery_times": recovery_times,
        "recommendations": recommendations,
        "vulnerabilities": vulnerabilities
    }
    
    return impacts

def calculate_process_specific_impacts(scenario_type, params):
    """מחשב את ההשפעות הספציפיות לכל תהליך והזמן להתאוששות"""
    # התהליכים השונים במפעל
    processes = ['קבלת חומרי גלם', 'עיבוד ראשוני', 'הרכבה', 'בקרת איכות', 'אריזה', 'לוגיסטיקה']
    
    # בסיס השפעה שונה לכל תרחיש
    if scenario_type == "כשל חיישנים":
        base_impacts = [20, 60, 50, 80, 30, 10]
        base_recovery = [1, 4, 3, 6, 2, 1]
    elif scenario_type == "הפסקת חשמל/מים":
        base_impacts = [40, 90, 80, 60, 70, 50]
        base_recovery = [2, 8, 6, 3, 4, 3]
    elif scenario_type == "תקלת ציוד קריטי":
        base_impacts = [30, 80, 90, 50, 40, 20]
        base_recovery = [2, 6, 8, 4, 3, 1]
    elif scenario_type == "שרשרת תגובה":
        base_impacts = [50, 70, 80, 90, 60, 40]
        base_recovery = [4, 6, 8, 10, 5, 3]
    else:  # תנאי קיצון סביבתיים
        base_impacts = [60, 50, 70, 40, 60, 30]
        base_recovery = [6, 5, 7, 3, 6, 4]
    
    # התאמת ההשפעות על פי הפרמטרים הספציפיים של התרחיש
    # זהו רק חישוב דמה - במערכת אמיתית זה יתבסס על מודל מורכב יותר
    impact_modifier = random.uniform(0.8, 1.2)
    recovery_modifier = random.uniform(0.9, 1.1)
    
    # חישוב השפעות סופיות
    process_impacts = [min(100, int(impact * impact_modifier)) for impact in base_impacts]
    recovery_times = [max(1, round(recovery * recovery_modifier, 1)) for recovery in base_recovery]
    
    return process_impacts, recovery_times

def generate_scenario_recommendations(scenario_type, params):
    """מייצר המלצות מותאמות לתרחיש"""
    recommendations = []
    
    if scenario_type == "כשל חיישנים":
        if params["pattern"] == "חיישנים קריטיים":
            recommendations.append({
                "title": "התקנת חיישנים כפולים בנקודות קריטיות",
                "description": "הוספת יתירות כפולה בחיישנים המוגדרים כקריטיים תפחית את הסיכון לכשל מערכתי ב-85%.",
                "impact": "הפחתת זמן השבתה צפוי ב-70% במקרה של כשל חיישנים"
            })
        
        recommendations.append({
            "title": "שדרוג אלגוריתם הניטור לזיהוי התדרדרות חיישנים",
            "description": "יישום אלגוריתם למידת מכונה לזיהוי סימנים מוקדמים להתדרדרות ביצועי חיישנים טרם כשל מלא.",
            "impact": "יכולת חיזוי כשלי חיישנים עד 48 שעות מראש"
        })
        
    elif scenario_type == "הפסקת חשמל/מים":
        if params["utility"] == "חשמל":
            recommendations.append({
                "title": "הרחבת מערך גיבוי החשמל למערכות קריטיות",
                "description": "התקנת מערכת UPS עם זמן גיבוי ארוך יותר ושדרוג גנרטור החירום לכיסוי 100% מצריכת המפעל.",
                "impact": "צמצום ההשפעה על התפוקה ל-15% בלבד במקרה של הפסקת חשמל ממושכת"
            })
        
        recommendations.append({
            "title": "פיתוח פרוטוקול שליטה בעומסים בעת חירום",
            "description": "יצירת מערכת אוטומטית להשלת עומסים בסדר קדימויות מוגדר, לניצול מקסימלי של תשתיות מוגבלות.",
            "impact": "הארכת זמן הפעולה של מערכות קריטיות ב-300% בזמן הפסקת אספקה"
        })
        
    elif scenario_type == "תקלת ציוד קריטי":
        equipment_name = params["equipment"].split(" ")[0] + " " + params["equipment"].split(" ")[1]
        
        recommendations.append({
            "title": f"הטמעת תחזוקה חזויה ל{equipment_name}",
            "description": "יישום ניטור מצב מתקדם המבוסס על בינה מלאכותית לזיהוי סימני התדרדרות טרם כשל.",
            "impact": "הפחתת הסיכון לכשל פתאומי ב-75%"
        })
        
        recommendations.append({
            "title": "הגדרת קו ייצור מקביל לגיבוי",
            "description": "תכנון מחדש של תצורת הייצור לאפשר מעקף זמני של מכונות קריטיות.",
            "impact": "צמצום זמן השבתה צפוי ב-60% במקרה של כשל ציוד"
        })
        
    elif scenario_type == "שרשרת תגובה":
        recommendations.append({
            "title": "יישום מערכת בידוד כשלים אוטומטית",
            "description": "פיתוח מנגנון אוטומטי לזיהוי נקודת הכשל הראשונית ובידוד מיידי למניעת התפשטות שרשרת תגובה.",
            "impact": "צמצום היקף ההשפעה של שרשרת תגובה ב-70%"
        })
        
        recommendations.append({
            "title": "ניתוח תלויות והגדרת 'חומות אש' מערכתיות",
            "description": "מיפוי מלא של תלויות בין מערכות והגדרת נקודות ניתוק אוטומטיות ומבוקרות.",
            "impact": "הגבלת עומק שרשרת התגובה ל-2 מערכות במקרה של כשל"
        })
        
    else:  # תנאי קיצון סביבתיים
        condition = params["condition"]
        
        recommendations.append({
            "title": f"שדרוג עמידות מערכות לתנאי {condition}",
            "description": f"התקנת אמצעי הגנה ייעודיים ושדרוג רכיבים קריטיים לגרסאות בעלות עמידות משופרת לתנאי {condition}.",
            "impact": f"עמידות משופרת ב-40% לתנאי {condition}"
        })
        
        recommendations.append({
            "title": "יישום פרוטוקול פעולה בתנאי קיצון",
            "description": "פיתוח נוהל אוטומטי להתאמת פרמטרי פעולה ומעבר למצב בטוח בזיהוי תנאי קיצון.",
            "impact": "הפחתת נזק צפוי ב-65% במקרה של אירוע קיצון"
        })
    
    # המלצה נוספת כללית תמיד
    recommendations.append({
        "title": "תרגולי חירום וסימולציות היערכות",
        "description": "ביצוע תרגולים תקופתיים של צוותי התפעול והתחזוקה בהתמודדות עם תרחישי הקיצון השונים, תוך שימוש בתאום הדיגיטלי להדמיה מדויקת.",
        "impact": "שיפור זמן התגובה של צוותים ב-50% וצמצום טעויות אנוש בזמן חירום"
    })
    
    return recommendations

def generate_vulnerability_matrix(scenario_type, params):
    """מייצר מטריצת פגיעות למערכות השונות"""
    # המערכות העיקריות
    systems = ['מערכת חשמל', 'הידראוליקה', 'בקרת איכות', 'ניטור', 'לוגיסטיקה', 'תקשורת']
    
    # יצירת מטריצת פגיעויות - לכל מערכת מוגדרת רמת פגיעות בין 0-100
    vulnerabilities = {
        'מערכת': systems,
        'פגיעות': []
    }
    
    # חישוב רמת פגיעות ספציפית לתרחיש (במערכת אמיתית תהיה תלויה במודל מורכב)
    if scenario_type == "כשל חיישנים":
        base_vulnerabilities = [30, 40, 90, 95, 20, 50]
    elif scenario_type == "הפסקת חשמל/מים":
        base_vulnerabilities = [95, 70, 60, 80, 50, 85]
    elif scenario_type == "תקלת ציוד קריטי":
        base_vulnerabilities = [60, 80, 70, 50, 40, 30]
    elif scenario_type == "שרשרת תגובה":
        base_vulnerabilities = [70, 60, 50, 75, 65, 80]
    else:  # תנאי קיצון סביבתיים
        base_vulnerabilities = [50, 60, 40, 65, 55, 75]
    
    # התאמה לפרמטרים ספציפיים של התרחיש
    vulnerability_modifier = random.uniform(0.9, 1.1)
    
    # חישוב פגיעות סופית
    vulnerabilities['פגיעות'] = [min(100, int(vuln * vulnerability_modifier)) for vuln in base_vulnerabilities]
    
    return vulnerabilities

def vulnerability_heatmap(vulnerability_data):
    """מציג מפת חום של פגיעויות מערכתיות"""
    # יצירת סולם צבעים
    colors = []
    for value in vulnerability_data['פגיעות']:
        if value >= 80:
            colors.append('#ff0000')  # אדום - פגיע מאוד
        elif value >= 50:
            colors.append('#ffa500')  # כתום - פגיע בינוני
        else:
            colors.append('#00cc00')  # ירוק - פגיעות נמוכה
    
    # יצירת גרף
    fig = go.Figure(data=[go.Bar(
        x=vulnerability_data['מערכת'],
        y=vulnerability_data['פגיעות'],
        marker_color=colors
    )])
    
    fig.update_layout(
        title='רמת פגיעות מערכות',
        xaxis_title='מערכת',
        yaxis_title='רמת פגיעות (%)',
        yaxis=dict(range=[0, 100])
    )
    
    # הוספת קווי סף
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=50,
        x1=5.5,
        y1=50,
        line=dict(
            color="orange",
            width=2,
            dash="dash",
        )
    )
    
    fig.add_shape(
        type="line",
        x0=-0.5,
        y0=80,
        x1=5.5,
        y1=80,
        line=dict(
            color="red",
            width=2,
            dash="dash",
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------
# פונקציונליות חדשה: ניהול מחזור חיים נכסים
# -----------------------------------------

def create_asset_lifecycle_manager():
    st.markdown("""
    <div class="highlight">
    <strong>ניהול מחזור חיים של נכסים</strong><br>
    התאום הדיגיטלי עוקב אחר הגיל הדיגיטלי האמיתי של ציוד ורכיבים. בניגוד לגיל כרונולוגי, הגיל הדיגיטלי מתחשב בתנאי עבודה, עומסים, תחזוקה ותנאי סביבה.
    </div>
    """, unsafe_allow_html=True)
    
    # בחירת נכס לניתוח
    asset_category = st.radio(
        "קטגוריית נכסים",
        ["מכונות ייצור", "ציוד בקרה ומדידה", "תשתיות", "רובוטים וכלי שינוע"],
        horizontal=True
    )
    
    # הצגת נכסים לפי קטגוריה
    assets = get_assets_by_category(asset_category)
    selected_asset = st.selectbox("בחר נכס לניתוח", assets)
    
    # קבלת נתונים עבור הנכס הנבחר
    asset_data = get_asset_data(selected_asset, asset_category)
    
    # הצגת נתוני הנכס
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {selected_asset}")
        st.markdown(f"""
        **גיל כרונולוגי:** {asset_data['chronological_age']} שנים  
        **גיל דיגיטלי:** {asset_data['digital_age']} שנים  
        **אורך חיים מתוכנן:** {asset_data['expected_lifetime']} שנים  
        **עלות רכישה:** ${asset_data['purchase_cost']:,}  
        **עלות החלפה:** ${asset_data['replacement_cost']:,}  
        **עלות תחזוקה שנתית:** ${asset_data['maintenance_cost']:,}  
        """)
        
        # הצגת גרף התפלגות הגיל
        fig = go.Figure()
        
        fig.add_trace(go.Indicator(
            mode = "gauge+number",
            value = asset_data['lifecycle_percent'],
            title = {'text': "אחוז מחזור חיים שהושלם"},
            gauge = {
                'axis': {'range': [None, 100]},
                'bar': {'color': get_lifecycle_color(asset_data['lifecycle_percent'])},
                'steps': [
                    {'range': [0, 50], 'color': "lightgreen"},
                    {'range': [50, 80], 'color': "lightyellow"},
                    {'range': [80, 100], 'color': "lightcoral"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # הצגת גרף התדרדרות והדרדרות צפויה
        performance_data = asset_data['performance_history']
        
        fig = px.line(
            x=performance_data['dates'], 
            y=performance_data['values'],
            labels={"x": "תאריך", "y": "ביצועים (%)"}
        )
        
        # הוספת תחזית עתידית
        future_dates = asset_data['performance_forecast']['dates']
        future_values = asset_data['performance_forecast']['values']
        
        fig.add_trace(
            go.Scatter(
                x=future_dates,
                y=future_values,
                mode='lines',
                line=dict(color='red', dash='dash'),
                name='תחזית'
            )
        )
        
        # הוספת סף החלפה
        fig.add_shape(
            type="line",
            x0=min(performance_data['dates']),
            y0=asset_data['replacement_threshold'],
            x1=max(future_dates),
            y1=asset_data['replacement_threshold'],
            line=dict(
                color="red",
                width=2,
                dash="dashdot",
            )
        )
        
        # הוספת סף תחזוקה
        fig.add_shape(
            type="line",
            x0=min(performance_data['dates']),
            y0=asset_data['maintenance_threshold'],
            x1=max(future_dates),
            y1=asset_data['maintenance_threshold'],
            line=dict(
                color="orange",
                width=2,
                dash="dashdot",
            )
        )
        
        fig.update_layout(
            title='ביצועים לאורך זמן ותחזית התדרדרות',
            xaxis_title='תאריך',
            yaxis_title='ביצועים (%)',
            yaxis=dict(range=[0, 105])
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # ניתוח כלכלי ונקודת החלפה אופטימלית
    st.markdown("### נקודת החלפה אופטימלית")
    
    # חישוב נקודת החלפה אופטימלית ועלויות שונות
    optimal_data = calculate_optimal_replacement(asset_data)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "החלפה אופטימלית בעוד", 
            f"{optimal_data['optimal_months']} חודשים",
            delta_color="off"
        )
    
    with col2:
        st.metric(
            "חיסכון צפוי", 
            f"${optimal_data['expected_savings']:,}",
            f"{optimal_data['savings_percent']}%"
        )
    
    with col3:
        st.metric(
            "סיכון תפעולי בהמתנה", 
            f"{optimal_data['operational_risk']}%",
            f"+{optimal_data['risk_increase']}%" if optimal_data['risk_increase'] > 0 else f"{optimal_data['risk_increase']}%",
            delta_color="inverse"
        )
    
    # ניתוח עלות-תועלת של החלפה עכשיו מול המתנה
    cost_benefit_data = optimal_data['cost_benefit_data']
    
    fig = px.bar(
        x=['החלפה מיידית', 'החלפה בנקודה אופטימלית', 'תחזוקה ללא החלפה'],
        y=[cost_benefit_data['immediate'], cost_benefit_data['optimal'], cost_benefit_data['maintenance_only']],
        labels={"x": "אסטרטגיה", "y": "עלות כוללת ($)"}
    )
    
    fig.update_layout(
        title='השוואת עלויות לפי אסטרטגיית החלפה',
        xaxis_title='אסטרטגיה',
        yaxis_title='עלות כוללת לטווח ארוך ($)'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # המלצות התאום הדיגיטלי
    risk_class = "lifecycle-risk-high" if optimal_data['operational_risk'] > 70 else ("lifecycle-risk-medium" if optimal_data['operational_risk'] > 40 else "lifecycle-risk-low")
    
    st.markdown(f"""
    <div class="scenario-card {risk_class}">
        <h4>המלצת התאום הדיגיטלי</h4>
        <p>{optimal_data['recommendation']}</p>
        <p><strong>פעולות מומלצות:</strong></p>
        <ul>
            {''.join([f'<li>{action}</li>' for action in optimal_data['actions']])}
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # פרמטרים משפיעים על הגיל הדיגיטלי
    st.markdown("### פרמטרים משפיעים על הגיל הדיגיטלי")
    
    impact_factors = asset_data['impact_factors']
    
    fig = px.bar(
        x=list(impact_factors.keys()),
        y=list(impact_factors.values()),
        labels={"x": "גורם", "y": "השפעה על הגיל הדיגיטלי (%)"}
    )
    
    fig.update_layout(
        title='גורמים משפיעים על הגיל הדיגיטלי',
        xaxis_title='גורם',
        yaxis_title='השפעה על הגיל הדיגיטלי (%)'
    )
    
    st.plotly_chart(fig, use_container_width=True)

def get_assets_by_category(category):
    """מחזיר רשימת נכסים לפי קטגוריה"""
    assets = {
        "מכונות ייצור": [
            "מכונת כרסום CNC מודל XJ-5000",
            "מכונת הזרקת פלסטיק KY-200",
            "רובוט ריתוך אוטומטי WB-400",
            "מערך הרכבה אוטומטי A-Series",
            "מכבש הידראולי H-900"
        ],
        "ציוד בקרה ומדידה": [
            "מערכת בקרת איכות אופטית QC-Vision",
            "סורק תלת-ממד Measure-3D",
            "מערכת לייזר למדידת דיוק L-500",
            "מערכת בקרת תהליך מרכזית CPC-2000",
            "מערך חיישנים היקפי SmartSense"
        ],
        "תשתיות": [
            "מערכת אספקת חשמל ראשית PS-1000",
            "מערכת קירור מרכזית CL-2000",
            "מערך מדחסי אוויר AC-Series",
            "מערכת טיפול בשפכים WT-500",
            "מערכת גיבוי UPS מרכזית"
        ],
        "רובוטים וכלי שינוע": [
            "רובוט הרכבה מדויק Assembly-Bot-5",
            "מלגזה אוטונומית AGV-300",
            "זרוע רובוטית Multi-Axis-7",
            "מערכת הזנה אוטומטית Feed-100",
            "רובוט פריקה וטעינה LogiBot-X"
        ]
    }
    
    return assets.get(category, [])

def get_asset_data(asset_name, category):
    """מחזיר נתונים מלאים על נכס ספציפי"""
    # הגדרות בסיס לפי קטגוריה
    base_data = {
        "מכונות ייצור": {
            "base_lifetime": 15,
            "base_cost": 250000,
            "maintenance_factor": 0.08
        },
        "ציוד בקרה ומדידה": {
            "base_lifetime": 8,
            "base_cost": 120000,
            "maintenance_factor": 0.1
        },
        "תשתיות": {
            "base_lifetime": 20,
            "base_cost": 500000,
            "maintenance_factor": 0.05
        },
        "רובוטים וכלי שינוע": {
            "base_lifetime": 10,
            "base_cost": 180000,
            "maintenance_factor": 0.12
        }
    }[category]
    
    # ערכים אקראיים לסימולציה (במערכת אמיתית יהיו נתונים אמיתיים לכל נכס)
    chronological_age = round(random.uniform(3, base_data["base_lifetime"] * 0.8), 1)
    
    # הגיל הדיגיטלי תלוי בתנאי שימוש, תחזוקה וגורמים נוספים
    digital_age_factor = random.uniform(0.8, 1.4)
    digital_age = round(chronological_age * digital_age_factor, 1)
    
    # פרמטרים נוספים
    expected_lifetime = base_data["base_lifetime"]
    purchase_cost = int(base_data["base_cost"] * random.uniform(0.9, 1.1))
    replacement_cost = int(purchase_cost * random.uniform(1.1, 1.3))  # עלות החלפה גבוהה מהעלות המקורית
    maintenance_cost = int(purchase_cost * base_data["maintenance_factor"] * (1 + digital_age / expected_lifetime))
    
    # אחוז מחזור החיים שכבר הושלם
    lifecycle_percent = round((digital_age / expected_lifetime) * 100, 1)
    
    # היסטוריית ביצועים
    today = datetime.now()
    dates = [(today - timedelta(days=30*i)).strftime('%Y-%m-%d') for i in range(24, -1, -1)]
    
    # נקודת ביצועים התחלתית - 100%, יורדת עם הזמן
    start_performance = 100
    end_performance = max(50, 100 - (digital_age / expected_lifetime) * 70)
    
    # יצירת היסטוריית ביצועים עם תנודתיות מעט אקראית
    values = []
    for i in range(25):
        base_performance = start_performance - (start_performance - end_performance) * (i / 24)
        values.append(min(100, max(1, base_performance + random.uniform(-5, 5))))
    
    performance_history = {
        'dates': dates,
        'values': values
    }
    
    # תחזית ביצועים עתידית
    future_dates = [(today + timedelta(days=30*i)).strftime('%Y-%m-%d') for i in range(1, 25)]
    
    # חישוב תחזית התדרדרות
    forecast_values = []
    last_value = values[-1]
    degradation_rate = (expected_lifetime - digital_age) / expected_lifetime
    degradation_rate = max(0.1, degradation_rate) * random.uniform(0.8, 1.2)
    
    for i in range(24):
        degradation = (i+1) * (10 / (degradation_rate * 100))
        forecast_values.append(max(5, last_value - degradation))
    
    performance_forecast = {
        'dates': future_dates,
        'values': forecast_values
    }
    
    # ספי תחזוקה והחלפה
    maintenance_threshold = 70
    replacement_threshold = 40
    
    # פרמטרים משפיעים על הגיל הדיגיטלי
    impact_factors = {
        "תדירות שימוש": int(random.uniform(5, 30)),
        "עומס עבודה": int(random.uniform(10, 40)),
        "איכות תחזוקה": int(random.uniform(-30, 10)),
        "תנאי סביבה": int(random.uniform(5, 25)),
        "איכות חומרים": int(random.uniform(-20, 5))
    }
    
    return {
        'chronological_age': chronological_age,
        'digital_age': digital_age,
        'expected_lifetime': expected_lifetime,
        'purchase_cost': purchase_cost,
        'replacement_cost': replacement_cost,
        'maintenance_cost': maintenance_cost,
        'lifecycle_percent': lifecycle_percent,
        'performance_history': performance_history,
        'performance_forecast': performance_forecast,
        'maintenance_threshold': maintenance_threshold,
        'replacement_threshold': replacement_threshold,
        'impact_factors': impact_factors
    }

def calculate_optimal_replacement(asset_data):
    """מחשב את נקודת ההחלפה האופטימלית ועלויות שונות"""
    # חישוב מספר החודשים עד נקודת התדרדרות אופטימלית
    forecast_values = asset_data['performance_forecast']['values']
    replacement_threshold = asset_data['replacement_threshold']
    
    # מציאת החודש בו הביצועים יורדים מתחת לסף החלפה
    months_to_threshold = 24  # ברירת מחדל - אם לא יורד מתחת לסף
    for i, value in enumerate(forecast_values):
        if value < replacement_threshold:
            months_to_threshold = i + 1
            break
    
    # חישוב נקודה אופטימלית שלוקחת בחשבון שיקולים כלכליים
    # במערכת אמיתית זה יהיה חישוב מורכב יותר
    optimal_months = max(1, min(months_to_threshold - 2, int(months_to_threshold * 0.7)))
    
    # חישוב חיסכון צפוי
    immediate_replacement_cost = asset_data['replacement_cost']
    
    # עלות תחזוקה מצטברת עד ההחלפה
    cumulative_maintenance = sum([
        asset_data['maintenance_cost'] * (1 + i * 0.05) 
        for i in range(optimal_months)
    ])
    
    # עלות החלפה בנקודה אופטימלית (מועברת לערך נוכחי)
    future_replacement_cost = asset_data['replacement_cost'] * (1 + optimal_months * 0.01)
    npv_factor = 1 / (1 + 0.08) ** (optimal_months / 12)  # שיעור היוון שנתי של 8%
    npv_replacement = future_replacement_cost * npv_factor
    
    # סך עלות בהחלפה אופטימלית
    optimal_total_cost = cumulative_maintenance + npv_replacement
    
    # חיסכון צפוי
    expected_savings = immediate_replacement_cost - optimal_total_cost
    savings_percent = round((expected_savings / immediate_replacement_cost) * 100, 1)
    
    # סיכון תפעולי בהמתנה
    base_risk = 10 + (asset_data['lifecycle_percent'] - 50) * 1.2
    operational_risk = min(95, max(5, round(base_risk, 1)))
    
    # עלייה בסיכון בחודש הקרוב
    risk_increase = round(operational_risk * 0.1, 1)
    
    # ניתוח עלות-תועלת
    cost_benefit_data = {
        'immediate': immediate_replacement_cost,
        'optimal': optimal_total_cost,
        'maintenance_only': asset_data['maintenance_cost'] * 24 * 1.5  # תחזוקה לשנתיים עם פקטור התדרדרות
    }
    
    # המלצה ופעולות מותאמות
    if operational_risk > 70:
        recommendation = f"מומלץ להחליף את הנכס בתוך {min(3, optimal_months)} חודשים. הסיכון התפעולי גבוה והמשך השימוש מעבר לנקודה זו יגדיל משמעותית את הסיכון לכשל מערכתי."
        actions = [
            "להתחיל מיד בתהליך רכש לציוד חלופי",
            "להגביר את תדירות ביקורות התחזוקה ל-2 בשבוע",
            "להכין תכנית מגירה להפעלה חלקית במקרה של כשל"
        ]
    elif operational_risk > 40:
        recommendation = f"מומלץ לתכנן החלפה בעוד {optimal_months} חודשים. קיים סיכון תפעולי מתון, ונדרש איזון בין עלויות להבטחת זמינות המערכת."
        actions = [
            "לתכנן תהליך רכש לציוד חלופי ברבעון הקרוב",
            "לבצע בדיקות תחזוקה מקיפות אחת לשבועיים",
            "להכין תכנית גיבוי חלקית למקרה של תקלות"
        ]
    else:
        recommendation = f"הציוד במצב תקין, וניתן לתכנן החלפה בעוד {optimal_months} חודשים. הסיכון התפעולי נמוך, וקיימת הזדמנות לאופטימיזציה כלכלית."
        actions = [
            "לכלול את ההחלפה בתכנית התקציבית השנתית",
            "להמשיך במשטר התחזוקה הרגיל",
            "לבחון אפשרויות שדרוג במקום החלפה מלאה"
        ]
    
    return {
        'optimal_months': optimal_months,
        'expected_savings': int(expected_savings),
        'savings_percent': savings_percent,
        'operational_risk': operational_risk,
        'risk_increase': risk_increase,
        'cost_benefit_data': cost_benefit_data,
        'recommendation': recommendation,
        'actions': actions
    }

def get_lifecycle_color(percent):
    """מחזיר צבע המתאים לשלב מחזור החיים"""
    if percent < 50:
        return "green"
    elif percent < 80:
        return "orange"
    else:
        return "red"

# תצוגת תוכן ראשי
with col_main:
    if mode == "מודל המפעל והתאום":
        st.plotly_chart(create_factory_model(), use_container_width=True)
        
        # הוספת תיאור למצב זה
        st.markdown("""
        <div class="highlight">
        <strong>מודל תלת-ממדי של מפעל ותאום דיגיטלי</strong><br>
        בתצוגה זו ניתן לראות את הייצוג הפיזי של המפעל (בצד שמאל) ואת התאום הדיגיטלי שלו (בצד ימין). 
        החיישנים על גבי המכונות מעבירים נתונים בזמן אמת לתאום הדיגיטלי, כך שכל שינוי פיזי משתקף מיד במודל.
        צבעי החיישנים מייצגים את מצבם: ירוק - תקין, כתום - אזהרה, אדום - מצב קריטי.
        </div>
        """, unsafe_allow_html=True)
        
    elif mode == "זרימת נתונים בזמן אמת":
        st.plotly_chart(create_data_flow(), use_container_width=True)
        
        # הצגה של סטטיסטיקות נתונים בזמן אמת
        st.markdown("""
        <div class="highlight">
        <strong>נתוני חיישנים בזמן אמת</strong><br>
        בתצוגה זו ניתן לראות את נתוני החיישנים השונים לאורך זמן. הקווים המקווקווים מייצגים את ספי האזהרה (כתום) 
        והמצב הקריטי (אדום). מערכת התאום הדיגיטלי מנטרת ברציפות את הנתונים ומזהה תבניות וחריגות.
        </div>
        """, unsafe_allow_html=True)
        
        # הצגת סטטיסטיקות נוכחיות
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("טמפרטורה ממוצעת", f"76.2°C", "1.8%")
        
        with col2:
            st.metric("לחץ מערכת", f"122.5 bar", "-0.5%")
        
        with col3:
            st.metric("רעידות", f"2.3 mm/s", "0%")
        
        with col4:
            st.metric("יעילות תפעולית", "92%", "4.5%")
        
    elif mode == "זיהוי אנומליות":
        st.plotly_chart(create_data_flow(), use_container_width=True)
        
        # הצגת פירוט האנומליות שזוהו
        st.markdown("""
        <div class="highlight sensor-warning">
        <strong>אנומליות שזוהו</strong><br>
        תצוגה זו מדגישה נקודות שבהן התאום הדיגיטלי זיהה התנהגות חריגה, 
        המערכת מנתחת את הנתונים ההיסטוריים כדי לזהות דפוסים המעידים על תקלות עתידיות.
        </div>
        """, unsafe_allow_html=True)
        
        # מידע על אנומליות שזוהו
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("""
            ### אנומליה #1
            **חיישן**: טמפרטורה (M3-12)  
            **תבנית שזוהתה**: עלייה הדרגתית  
            **תקלה צפויה**: תקלת מנוע חשמלי  
            **זמן התרחשות משוער**: 72 שעות  
            **ודאות חיזוי**: 87%  
            """)
        
        with col2:
            st.markdown("""
            ### אנומליה #2
            **חיישן**: רעידות (M2-05)  
            **תבנית שזוהתה**: תנודות בתדר גבוה  
            **תקלה צפויה**: בלאי מיסב  
            **זמן התרחשות משוער**: 120 שעות  
            **ודאות חיזוי**: 93%  
            """)
        
    elif mode == "אופטימיזציה אוטומטית":
        st.plotly_chart(create_data_flow(), use_container_width=True)
        
        # הצגת ההמלצות האוטומטיות של המערכת
        st.markdown("""
        <div class="highlight">
        <strong>המלצות אופטימיזציה אוטומטיות</strong><br>
        בתצוגה זו ניתן לראות את תהליך האופטימיזציה שמבצע התאום הדיגיטלי. המערכת מזהה הזדמנויות לשיפור 
        ומיישמת שינויים באופן אוטומטי או מציעה פעולות למפעילים, כפי שניתן לראות בקו האנכי הירוק המסמן נקודת התערבות.
        </div>
        """, unsafe_allow_html=True)
        
        # פריסת טבלת פעולות אופטימיזציה
        st.markdown("### פעולות אופטימיזציה שננקטו")
        
        optimization_data = {
            "זמן": ["08:15", "09:30", "11:45", "13:20", "14:50"],
            "מכונה": ["M2", "M7", "M4", "M1", "M5"],
            "פרמטר": ["מהירות סיבוב", "טמפרטורת פעולה", "לחץ עבודה", "זמן מחזור", "צריכת חשמל"],
            "שינוי": ["+5%", "-3°C", "+8 bar", "-12 sec", "-7%"],
            "תועלת צפויה": ["הגדלת תפוקה", "הארכת חיי רכיב", "שיפור איכות", "הגדלת תפוקה", "חיסכון אנרגטי"]
        }
        
        st.dataframe(pd.DataFrame(optimization_data))
        
    elif mode == "השוואת ביצועים":
        comparison_fig, roi_fig, cost_fig = create_comparison_dashboard()
        
        st.plotly_chart(comparison_fig, use_container_width=True)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.plotly_chart(roi_fig, use_container_width=True)
        
        with col2:
            st.plotly_chart(cost_fig, use_container_width=True)
        
        # סיכום השוואתי
        st.markdown("""
        <div class="highlight">
        <strong>השוואת ביצועים מדידים</strong><br>
        השוואה זו מדגישה את היתרונות העסקיים המשמעותיים של יישום תאום דיגיטלי. הפערים בביצועים, החיסכון בעלויות 
        והתשואה הגבוהה על ההשקעה (ROI) מראים בבירור כי מדובר בטכנולוגיה משנת-משחק בתעשייה המודרנית.
        </div>
        """, unsafe_allow_html=True)
        
        # פירוט יתרונות עסקיים
        st.markdown("### יתרונות עסקיים מדידים")
        
        business_data = {
            "מדד": ["ROI", "זמן השבתה", "זמינות ציוד", "עלויות אנרגיה", "עלויות תחזוקה", "איכות מוצר"],
            "ערך לפני יישום": ["0%", "240 שעות/שנה", "92%", "100%", "100%", "98.5%"],
            "ערך אחרי יישום": ["215%", "72 שעות/שנה", "99.2%", "80%", "65%", "99.8%"],
            "שיפור": ["+215%", "-70%", "+7.2%", "-20%", "-35%", "+1.3%"]
        }
        
        st.dataframe(pd.DataFrame(business_data))
        
    elif mode == "סימולטור תרחישים":
        # יצירת טאבים לבחירה בין שני המודולים החדשים
        scenario_tab, lifecycle_tab = st.tabs(["סימולטור תרחישי קיצון", "ניהול מחזור חיים"])
        
        with scenario_tab:
            create_extreme_scenario_simulator()
            
        with lifecycle_tab:
            create_asset_lifecycle_manager()

# תצוגת יומן אירועים
with col_events:
    st.markdown('<div class="subheader">יומן אירועים והתראות</div>', unsafe_allow_html=True)
    
    # יצירת תיבה לתצוגת הודעות
    event_placeholder = st.empty()
    
    # יצירת מכולה להודעות עם גלילה
    with event_placeholder.container():
        event_log = st.empty()
        with event_log:
            st.markdown('<div class="event-log" id="event-log"></div>', unsafe_allow_html=True)
    
    # יצירת פונקציה לעדכון הודעות
    event_log_contents = []
    
    # הוספת כמה אירועים התחלתיים
    for _ in range(5):
        event_log_contents.append(f'<div class="sensor-normal">{datetime.now().strftime("%H:%M:%S")} - מערכת התאום הדיגיטלי מופעלת ומקבלת נתונים</div>')
    
    # תצוגת האירועים
    event_log.markdown(f'<div class="event-log">{"".join(event_log_contents)}</div>', unsafe_allow_html=True)
    
    # הוספת אירועים חדשים
    def update_event_log():
        current_time = datetime.now().strftime('%H:%M:%S')
        event_types = {
            "מודל המפעל והתאום": [
                "חיישן טמפרטורה M3-12 מדווח על עלייה הדרגתית",
                "חיישן לחץ M7-5 חזר לתפקוד תקין",
                "בוצע עדכון לתאום הדיגיטלי של מכונה 2",
                "התקבלה התראה על סטייה קלה בחיישן רעידות",
                "המלצת כיוונון אוטומטית יושמה במכונה 4"
            ],
            "זרימת נתונים בזמן אמת": [
                "זוהתה תנודתיות חריגה בנתוני טמפרטורה",
                "מבוצע ניתוח השוואתי של נתוני לחץ",
                "התקבלה התראה על שינוי מגמה בצריכת אנרגיה",
                "סף אזהרה נחצה בחיישן זרם חשמלי",
                "המערכת מזהה דפוס חדש בנתוני המהירות"
            ],
            "זיהוי אנומליות": [
                "אנומליה קריטית זוהתה במכונה 5 - תחזית לכשל בתוך 48 שעות",
                "התראה: סימני שחיקה מוקדמים במסוע המרכזי",
                "המערכת איתרה דפוס תקלה מוכר - מופעל פרוטוקול מניעה",
                "אנומליה בנתוני חיישן מהירות - תיקון נדרש",
                "מערכת ה-AI זיהתה חריגה משמעותית בנתוני החיישנים"
            ],
            "אופטימיזציה אוטומטית": [
                "הושלמה אופטימיזציה של פרמטרי ייצור - שיפור יעילות ב-12%",
                "בוצע כוונון אוטומטי למכונה 3 - צפוי חיסכון של 8% באנרגיה",
                "מערכת AI ממליצה על שינוי סדר העבודה לחיסכון של 15% בזמן",
                "התאמה אוטומטית של פרמטרי ייצור בעקבות שינוי תנאי סביבה",
                "המלצה: הזזת תחזוקה מתוכננת ב-48 שעות לפי תחזית מערכת"
            ],
            "השוואת ביצועים": [
                "דוח ROI מעודכן: החזר השקעה של 215% לאחר 24 חודשים",
                "זמן השבתה שנמנע הודות לתאום דיגיטלי: 287 שעות השנה",
                "השוואת ביצועים: 42% פחות תקלות לעומת התקופה המקבילה אשתקד",
                "התאום הדיגיטלי זיהה 12 הזדמנויות לשיפור תהליכים שלא זוהו קודם",
                "הושלם ניתוח עלות-תועלת: לתאום הדיגיטלי ROI של פי 3 מהצפוי"
            ],
            "סימולטור תרחישים": [
                "הושלמה סימולציית כשל חיישנים - זוהו 3 נקודות תורפה",
                "סימולציית הפסקת חשמל חשפה צורך בשדרוג מערכת גיבוי",
                "המערכת מזהה סיכון גבוה לכשל בשרשרת בקו ייצור 2",
                "חיזוי החלפת ציוד אופטימלית: מכונה M4 בעוד 8 חודשים",
                "הסתיימה סימולציית תרחיש רעידת אדמה - השפעה צפויה: 65% ירידה בתפוקה"
            ]
        }
        
        event = random.choice(event_types.get(mode, event_types["מודל המפעל והתאום"]))
        status_class = "sensor-normal"
        
        # בדיקה אם מדובר באירוע קריטי
        if "קריטי" in event or "כשל" in event or "סיכון גבוה" in event:
            status_class = "sensor-critical"
        elif "התראה" in event or "אזהרה" in event or "חשפה צורך" in event:
            status_class = "sensor-warning"
        
        # הוספת האירוע ליומן
        event_log_contents.append(f'<div class="{status_class}">{current_time} - {event}</div>')
        
        # שמירה רק על 20 האירועים האחרונים
        if len(event_log_contents) > 20:
            event_log_contents.pop(0)
        
        # עדכון תצוגת היומן
        event_log.markdown(f'<div class="event-log">{"".join(event_log_contents)}</div>', unsafe_allow_html=True)
    
    # הוספת אירועים באופן מחזורי
    if st.button("הוסף אירוע חדש"):
        update_event_log()
    
    st.markdown("---")
    
    # תקציר מצב מערכת
    st.markdown("### תקציר מצב")
    
    # נתוני מצב המשתנים לפי המצב הנבחר
    if mode in ["זיהוי אנומליות", "סימולטור תרחישים"] or "אנומליה" in "".join(event_log_contents) or "סיכון" in "".join(event_log_contents):
        st.markdown('<div class="sensor-warning">⚠️ התראות פעילות: 3</div>', unsafe_allow_html=True)
        st.markdown('<div class="sensor-critical">🚨 אירועים קריטיים: 1</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="sensor-normal">✅ כל המערכות תקינות</div>', unsafe_allow_html=True)
    
    st.markdown(f'💡 חיישנים פעילים: {25 if detail_level == "בינונית" else (40 if detail_level == "גבוהה" else 15)}')
    st.markdown(f'📊 זמן ניטור: {time_range}')
    
    # הסבר על פאנל הבקרה
    with st.expander("הסבר על אפשרויות הדמיה"):
        st.markdown("""
        - **מצב הדמיה**: בחירת היבט התאום הדיגיטלי להצגה
        - **מהירות הדמיה**: שליטה בקצב הדמיית נתונים וזיהוי אנומליות
        - **חיישנים פעילים**: הפעלה/כיבוי של חיישני המערכת
        - **טווח זמן להצגה**: משך הזמן שעבורו מוצגים נתונים
        - **רמת פירוט**: כמות המידע והחיישנים המוצגים בהדמיה
        """)
    
    # מידע על הפרויקט
    st.markdown("---")
    st.markdown("### מידע נוסף")
    
    st.markdown("""
    **מקורות מידע:**
    - [Digital Twin ROI Studies](https://www.industryweek.com/technology-and-iiot/article/21132452/the-roi-of-digital-twins)
    - [Siemens Digital Twin Case Study](https://www.siemens.com/global/en/company/stories/industry/the-digital-twin.html)
    - [Industry 4.0 Implementations](https://www.mckinsey.com/capabilities/operations/our-insights/industry-40-reimagining-manufacturing-operations-after-covid-19)
    """)

# הוסף התראה בסיום
st.success("הדמיית התאום הדיגיטלי פועלת בהצלחה! בחר מצבי הדמיה שונים, בדוק את סימולטור התרחישים וניהול מחזור החיים כדי לראות את היכולות המתקדמות של התאום הדיגיטלי.")