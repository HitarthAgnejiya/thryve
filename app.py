import streamlit as st
import pandas as pd
from datetime import datetime
from pathlib import Path
import uuid

st.set_page_config(page_title="RoadGuard AI", page_icon="🛣️", layout="wide")

st.markdown("""
<style>
.stApp {background: radial-gradient(ellipse at 12% 0%, #1c3550 0%, #0a1423 48%, #07101c 100%); color:#eaf2ff}
h1,h2,h3 {color:#f4f8ff}
[data-testid="stMetric"] {background:linear-gradient(145deg,#14263b,#0e1b2d);border:1px solid #29405b;padding:18px 20px;border-radius:16px}
[data-testid="stMetricLabel"] {color:#a9bdd4}
[data-testid="stMetricValue"] {color:#c5f36a}
</style>
""", unsafe_allow_html=True)

st.title("🛣️ RoadGuard AI")
st.caption("AI-assisted road distress reporting · Hackathon prototype")
st.warning("Prototype only. Verify every detection and severity assessment with a human reviewer.")

if "reports" not in st.session_state:
    st.session_state.reports = [
        {"id":"RG-1042","reported_at":"2026-10-20 09:42","area":"Sample Road, Demo City","lat":23.0225,"lon":72.5714,"severity":"High","status":"Needs review","source":"Demo data","notes":"Large road-surface defect in left lane."},
        {"id":"RG-1041","reported_at":"2026-10-20 08:17","area":"Market Street, Demo City","lat":23.0300,"lon":72.5800,"severity":"Medium","status":"Under review","source":"Demo data","notes":"Uneven surface; verify on site."},
        {"id":"RG-1038","reported_at":"2026-10-19 18:04","area":"Ring Road, Demo City","lat":23.0100,"lon":72.5600,"severity":"Low","status":"Verified","source":"Demo data","notes":"Small surface damage."},
    ]

with st.sidebar:
    st.markdown("## 🛣️ RoadGuard **AI**")
    st.caption("See the road. Flag the risk.")
    page = st.radio("NAVIGATION", ["Overview", "Scan a road image", "Report a hazard", "Road issue map", "Reports & export"])
    st.divider()
    st.markdown("**DEMO STATUS**")
    st.write("🟢 Dashboard online")
    st.write("🧠 AI model: optional setup")
    st.write("✓ Human review: enabled")

reports = pd.DataFrame(st.session_state.reports)
if page == "Overview":
    st.markdown("### AI FOR SAFER STREETS")
    st.header("Spot the damage. Prioritise the repair.")
    st.write("RoadGuard AI turns road images and community reports into a location-aware road-distress dashboard, helping teams find, review and prioritise hazards.")
    a,b,c,d = st.columns(4)
    a.metric("Road reports", len(reports))
    b.metric("High priority", int((reports["severity"] == "High").sum()))
    c.metric("Awaiting review", int(reports["status"].isin(["Needs review","Under review"]).sum()))
    d.metric("Verified", int((reports["status"] == "Verified").sum()))
    st.subheader("Latest reports")
    st.dataframe(reports.sort_values("reported_at", ascending=False), use_container_width=True, hide_index=True)
    st.info("AI inference is optional and requires compatible pothole-trained model weights. Demo records are illustrative.")
elif page == "Scan a road image":
    st.header("Scan a road image")
    image = st.file_uploader("Upload a road or dashcam image", type=["jpg","jpeg","png","webp"])
    if image:
        st.image(image, caption="Uploaded road image", use_container_width=True)
        model_path = Path("models/pothole_model.pt")
        if model_path.exists():
            try:
                from ultralytics import YOLO
                model = YOLO(str(model_path))
                result = model.predict(image.getvalue(), verbose=False)
                st.image(result[0].plot(), caption="Model prediction — verify manually", use_container_width=True)
                st.caption("Model confidence is not a measure of real-world safety or accuracy.")
            except Exception as exc:
                st.error(f"Could not run model inference: {exc}")
        else:
            st.info("No model weights found at models/pothole_model.pt. Add a compatible pothole-trained Ultralytics model to enable inference.")
elif page == "Report a hazard":
    st.header("Report a road hazard")
    with st.form("hazard_form", clear_on_submit=True):
        area = st.text_input("Road / area", placeholder="Street name or nearby landmark")
        lat = st.number_input("Latitude", min_value=-90.0, max_value=90.0, value=23.0225, format="%.6f")
        lon = st.number_input("Longitude", min_value=-180.0, max_value=180.0, value=72.5714, format="%.6f")
        severity = st.selectbox("Estimated severity", ["High","Medium","Low","Unassessed"])
        notes = st.text_area("Notes", placeholder="Describe the visible road issue")
        submitted = st.form_submit_button("Submit report")
    if submitted:
        if not area.strip():
            st.error("Please enter a road or area.")
        else:
            st.session_state.reports.append({"id":f"RG-{uuid.uuid4().hex[:6].upper()}","reported_at":datetime.now().strftime("%Y-%m-%d %H:%M"),"area":area.strip(),"lat":lat,"lon":lon,"severity":severity,"status":"Needs review","source":"User report","notes":notes.strip()})
            st.success("Report added to this session's dashboard.")
            st.info("Reports are stored only in the current Streamlit session. Export them before closing.")
elif page == "Road issue map":
    st.header("Road issue map")
    st.caption("Coordinates shown below are demo or user-entered values. Verify locations before taking action.")
    df = pd.DataFrame(st.session_state.reports)
    if df.empty:
        st.info("No reports to map yet.")
    else:
        st.map(df.rename(columns={"lat":"latitude","lon":"longitude"})[["latitude","longitude"]])
        st.dataframe(df[["id","area","severity","status","lat","lon"]], use_container_width=True, hide_index=True)
else:
    st.header("Reports & export")
    df = pd.DataFrame(st.session_state.reports)
    if df.empty:
        st.info("No reports yet.")
    else:
        severity = st.multiselect("Severity", ["High","Medium","Low","Unassessed"], default=["High","Medium","Low","Unassessed"])
        statuses = sorted(df["status"].dropna().unique().tolist())
        status = st.multiselect("Status", statuses, default=statuses)
        query = st.text_input("Search road / notes")
        filtered = df[df["severity"].isin(severity) & df["status"].isin(status)]
        if query.strip():
            mask = filtered.astype(str).apply(lambda col: col.str.contains(query.strip(), case=False, na=False)).any(axis=1)
            filtered = filtered[mask]
        st.dataframe(filtered, use_container_width=True, hide_index=True)
        st.download_button("Download filtered reports (CSV)", filtered.to_csv(index=False).encode("utf-8"), file_name="roadguard_reports.csv", mime="text/csv")
        st.download_button("Download all reports (CSV)", df.to_csv(index=False).encode("utf-8"), file_name="roadguard_all_reports.csv", mime="text/csv")

st.divider()
st.caption("ROADGUARD AI · AI-assisted road distress reporting · Prototype only — verify detections and severity with a human reviewer.")
