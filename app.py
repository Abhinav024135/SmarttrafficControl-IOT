import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime

st.set_page_config(page_title="Smart Traffic Control", page_icon="🚦", layout="wide")
ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "raw" / "dataset.csv"

@st.cache_data
def load_data():
    d = pd.read_csv(DATA_PATH)
    d["timestamp"] = pd.to_datetime(d["timestamp"], errors="coerce")
    for c in ["vehicle_count","green_duration_s","red_duration_s","peak_hour","emergency_flag"]:
        d[c] = pd.to_numeric(d[c], errors="coerce")
    return d

df = load_data()
if "live" not in st.session_state:
    st.session_state.live = df.tail(24).copy().reset_index(drop=True)
if "cycle" not in st.session_state:
    st.session_state.cycle = 0
if "manual_emergency" not in st.session_state:
    st.session_state.manual_emergency = False
if "mode" not in st.session_state:
    st.session_state.mode = "Automatic"

# Styling
st.markdown("""
<style>
.stApp {background: #0b1220; color: #e5edf7;}
[data-testid="stSidebar"] {background: #111c2e;}
[data-testid="stMetric"] {background:#16243a; padding:16px; border:1px solid #263a55; border-radius:12px;}
.block-container {padding-top:1.4rem;}
h1,h2,h3 {color:#eaf2ff;}
div[data-testid="stAlert"] {border-radius:10px;}
</style>
""", unsafe_allow_html=True)

def traffic_level(v):
    if v < 8: return "LOW"
    if v < 18: return "MEDIUM"
    return "HIGH"

def adaptive_green(v, min_green=10, max_green=60):
    if v < 8: duration = 15
    elif v < 18: duration = 28
    else: duration = 48
    return int(np.clip(duration, min_green, max_green))

def signal_color(row, index=0):
    if int(row.get("emergency_flag",0) or 0) == 1 or st.session_state.manual_emergency:
        return "PRIORITY"
    return "GREEN" if index % 2 == 0 else "RED"

def metric(label, value, help_text=None):
    st.metric(label, value, help=help_text)

st.sidebar.markdown("# 🚦 SMART TRAFFIC")
st.sidebar.caption("Intelligent Adaptive Traffic Management System")
page = st.sidebar.radio("NAVIGATION", [
    "Overview","Live Traffic Monitoring","Adaptive Signal Control",
    "Emergency Management","Intersection Management","Dataset Analytics",
    "Security & Settings"
])
st.sidebar.divider()
st.sidebar.markdown("**Prototype status**")
st.sidebar.success("Software simulation active")
st.sidebar.caption("No physical STM32, ultrasonic sensors, LEDs or wireless module is connected.")
if st.sidebar.button("↻ Generate Next Traffic Cycle", use_container_width=True):
    rng = np.random.default_rng()
    live = st.session_state.live.copy()
    live["vehicle_count"] = (live["vehicle_count"].fillna(0) + rng.integers(-4, 7, len(live))).clip(0, 45)
    live["emergency_flag"] = 0
    live["green_duration_s"] = live["vehicle_count"].apply(adaptive_green)
    live["red_duration_s"] = (90 - live["green_duration_s"]).clip(20, 80)
    st.session_state.live = live
    st.session_state.cycle += 1
    st.session_state.manual_emergency = False
    st.rerun()
st.sidebar.caption(f"Simulation cycle: {st.session_state.cycle}")

live = st.session_state.live.copy()
total_intersections = df["intersection_id"].nunique()
total_lanes = df["lane_id"].nunique()
total_vehicles = int(live["vehicle_count"].fillna(0).sum())
emergencies = int(live["emergency_flag"].fillna(0).sum()) + int(st.session_state.manual_emergency)
avg_green = float(live["green_duration_s"].mean())

if page == "Overview":
    st.title("🚦 Smart Traffic Light Control System")
    st.caption("Centralised monitoring • Adaptive signal timing • Emergency priority")
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Intersections", total_intersections)
    c2.metric("Lanes monitored", total_lanes)
    c3.metric("Vehicles in current view", total_vehicles)
    c4.metric("Emergency alerts", emergencies)
    c5,c6,c7,c8 = st.columns(4)
    c5.metric("Average vehicles / lane", f"{live.vehicle_count.mean():.1f}")
    c6.metric("Average green duration", f"{avg_green:.0f} s")
    c7.metric("Traffic condition", "HIGH" if live.vehicle_count.mean()>=18 else ("MEDIUM" if live.vehicle_count.mean()>=8 else "LOW"))
    c8.metric("Control mode", st.session_state.mode)
    a,b = st.columns(2)
    by_int = live.groupby("intersection_id", as_index=False).vehicle_count.sum()
    a.plotly_chart(px.bar(by_int, x="intersection_id", y="vehicle_count", color="vehicle_count",
                          title="Vehicle count by intersection", color_continuous_scale="Tealgrn"), use_container_width=True)
    by_lane = live.groupby("lane_id", as_index=False).vehicle_count.mean()
    b.plotly_chart(px.bar(by_lane, x="lane_id", y="vehicle_count", color="vehicle_count",
                          title="Average traffic by lane", color_continuous_scale="Blues"), use_container_width=True)
    c,d = st.columns(2)
    timing = pd.DataFrame({"Signal":["Green","Red"],"Seconds":[live.green_duration_s.mean(),live.red_duration_s.mean()]})
    c.plotly_chart(px.pie(timing, names="Signal", values="Seconds", hole=.55, title="Average signal timing split"), use_container_width=True)
    em = df["emergency_flag"].fillna(0).value_counts().rename(index={0:"Normal",1:"Emergency"}).reset_index()
    em.columns=["Traffic type","Records"]
    d.plotly_chart(px.bar(em, x="Traffic type", y="Records", color="Traffic type", title="Dataset emergency-event distribution"), use_container_width=True)
    peak = df.groupby("peak_hour", as_index=False).vehicle_count.mean()
    st.plotly_chart(px.bar(peak, x="peak_hour", y="vehicle_count", title="Average vehicles: non-peak (0) vs peak (1)"), use_container_width=True)

elif page == "Live Traffic Monitoring":
    st.title("📡 Live Traffic Monitoring")
    st.caption("Values below are generated from the supplied traffic log and local simulation state.")
    view = live.copy()
    view["traffic_level"] = view.vehicle_count.apply(traffic_level)
    view["signal_status"] = [signal_color(row, i) for i, (_,row) in enumerate(view.iterrows())]
    view["timer_seconds"] = view.vehicle_count.apply(adaptive_green)
    st.dataframe(view[["intersection_id","lane_id","vehicle_count","traffic_level","signal_status","timer_seconds","emergency_flag"]], use_container_width=True, hide_index=True)
    st.info("Use **Generate Next Traffic Cycle** in the sidebar to change simulated vehicle counts and signal durations.")
    selected = st.selectbox("Select intersection", sorted(view.intersection_id.dropna().unique()))
    selected_df = view[view.intersection_id == selected]
    st.plotly_chart(px.bar(selected_df, x="lane_id", y="vehicle_count", color="traffic_level",
                           title=f"Lane-level traffic at {selected}"), use_container_width=True)

elif page == "Adaptive Signal Control":
    st.title("🧠 Adaptive Signal Control")
    st.write("A transparent rule-based demonstration assigns shorter green times to low traffic and longer times to heavy traffic.")
    mode = st.radio("Control mode", ["Automatic","Manual"], horizontal=True, index=0 if st.session_state.mode=="Automatic" else 1)
    st.session_state.mode = mode
    min_g = st.slider("Minimum green time (seconds)", 10, 25, 10)
    max_g = st.slider("Maximum green time (seconds)", 35, 60, 60)
    if min_g >= max_g:
        st.warning("Maximum green time must be greater than minimum green time.")
    else:
        ctl = live.copy()
        ctl["traffic_level"] = ctl.vehicle_count.apply(traffic_level)
        ctl["recommended_green_s"] = ctl.vehicle_count.apply(lambda x: adaptive_green(x,min_g,max_g))
        ctl["recommended_red_s"] = 90 - ctl["recommended_green_s"]
        ctl["priority"] = ctl.emergency_flag.fillna(0).astype(int).eq(1)
        st.dataframe(ctl[["intersection_id","lane_id","vehicle_count","traffic_level","recommended_green_s","recommended_red_s","priority"]], use_container_width=True, hide_index=True)
        st.success("Safety note: this is a demonstration schedule only. A real intersection controller requires conflict-phase design, interlocks and certified safety validation.")
    st.markdown("**Rule used:** vehicle_count < 8 → 15 s; 8–17 → 28 s; ≥18 → 48 s; clipped to the configured limits.")

elif page == "Emergency Management":
    st.title("🚑 Emergency Vehicle Management")
    st.caption("Emergency priority is demonstrated in software; no real traffic signals are controlled.")
    if st.button("Simulate emergency vehicle at a selected lane", type="primary"):
        st.session_state.manual_emergency = True
    if st.session_state.manual_emergency:
        st.error("CRITICAL — SIMULATED EMERGENCY PRIORITY ACTIVE")
    emergency_rows = df[df.emergency_flag.fillna(0).astype(int)==1]
    if len(emergency_rows):
        st.warning(f"{len(emergency_rows)} emergency-flagged records exist in the supplied dataset.")
        st.dataframe(emergency_rows[["timestamp","intersection_id","lane_id","vehicle_count","emergency_flag"]].head(100), use_container_width=True, hide_index=True)
    else:
        st.info("No emergency-flagged records were found in the supplied dataset. Use the simulation button to demonstrate this workflow.")
    st.markdown("**Demonstration behaviour:** priority flag is raised and the interface highlights the emergency state. A production controller must use a verified safe phase-transition sequence.")

elif page == "Intersection Management":
    st.title("🛣️ Intersection Management")
    summary = live.groupby("intersection_id").agg(
        lanes=("lane_id","nunique"), vehicles=("vehicle_count","sum"),
        avg_green=("green_duration_s","mean"), emergency_events=("emergency_flag","sum")
    ).reset_index()
    summary["traffic_condition"] = summary.vehicles.apply(traffic_level)
    summary["operating_mode"] = st.session_state.mode
    st.dataframe(summary, use_container_width=True, hide_index=True)
    selected = st.selectbox("Inspect intersection", sorted(live.intersection_id.dropna().unique()))
    one = live[live.intersection_id==selected]
    st.subheader(selected)
    for _, row in one.iterrows():
        st.write(f"**{row.lane_id}** — {int(row.vehicle_count)} vehicles • {traffic_level(row.vehicle_count)} traffic • suggested green {adaptive_green(row.vehicle_count)} s")

elif page == "Dataset Analytics":
    st.title("📊 Dataset Analytics")
    st.caption("Analysis uses the original 500-row project dataset, not synthetic simulation records.")
    st.metric("Dataset records", len(df))
    st.metric("Columns", len(df.columns))
    x,y,z = st.columns(3)
    x.metric("Missing cells", int(df.isna().sum().sum()))
    y.metric("Duplicate rows", int(df.duplicated().sum()))
    z.metric("Intersections", df.intersection_id.nunique())
    with st.expander("Dataset preview", expanded=True):
        st.dataframe(df.head(20), use_container_width=True)
    st.subheader("Descriptive statistics")
    st.dataframe(df.describe(include="all").transpose(), use_container_width=True)
    charts = st.tabs(["Intersection","Lane","Peak hour","Signal timing","Emergency"])
    with charts[0]:
        g=df.groupby("intersection_id",as_index=False).vehicle_count.mean()
        st.plotly_chart(px.bar(g,x="intersection_id",y="vehicle_count",title="Average vehicle count by intersection"),use_container_width=True)
    with charts[1]:
        g=df.groupby("lane_id",as_index=False).vehicle_count.mean()
        st.plotly_chart(px.bar(g,x="lane_id",y="vehicle_count",title="Average vehicle count by lane"),use_container_width=True)
    with charts[2]:
        g=df.groupby("peak_hour",as_index=False).vehicle_count.mean()
        st.plotly_chart(px.bar(g,x="peak_hour",y="vehicle_count",title="Peak vs non-peak average traffic"),use_container_width=True)
    with charts[3]:
        g=df.groupby("intersection_id")[["green_duration_s","red_duration_s"]].mean().reset_index().melt("intersection_id")
        st.plotly_chart(px.bar(g,x="intersection_id",y="value",color="variable",barmode="group",title="Mean green/red duration by intersection"),use_container_width=True)
    with charts[4]:
        g=df.groupby("emergency_flag",as_index=False).size()
        g["type"]=g.emergency_flag.map({0:"Normal",1:"Emergency"})
        st.plotly_chart(px.pie(g,names="type",values="size",hole=.45,title="Emergency flag distribution"),use_container_width=True)
    cleaned_path = ROOT/"data"/"processed"/"cleaned_dataset.csv"
    st.download_button("⬇ Download cleaned dataset", cleaned_path.read_bytes(), file_name="cleaned_dataset.csv", mime="text/csv")

elif page == "Security & Settings":
    st.title("🔐 Security & System Settings")
    st.warning("Demonstration-only controls. Fingerprint and keypad hardware are not connected.")
    a,b,c = st.columns(3)
    a.metric("Fingerprint sensor", "SIMULATED")
    b.metric("Keypad", "SIMULATED")
    c.metric("Wireless link", "NOT CONNECTED")
    pin = st.text_input("Demo administrator PIN", type="password", max_chars=8)
    if st.button("Authenticate demo administrator"):
        st.session_state.admin_ok = (pin == "1234")
    if st.session_state.get("admin_ok",False):
        st.success("Demo administrator authenticated (local demo PIN only).")
    else:
        st.info("Enter demo PIN 1234 to demonstrate the local authentication screen.")
    st.selectbox("System mode", ["Automatic","Manual"], key="mode_setting")
    st.caption("No credentials are sent or stored. Do not use this demo PIN in a real system.")

st.divider()
st.caption("Academic software prototype • Smart Traffic Light Control System • Physical hardware integration and field validation remain future work.")
