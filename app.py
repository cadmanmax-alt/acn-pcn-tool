import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(layout="wide")
st.title("RNAS Yeovilton ACN-PCN Surface Movement Tool")

# -----------------------------
# AIRCRAFT INPUT
# -----------------------------
aircraft_data = {
    "Custom": None,
    "F-35B": 45,
    "C-130J": 50,
    "A400M": 60,
}

aircraft = st.selectbox("Aircraft", list(aircraft_data.keys()))

if aircraft == "Custom":
    acn = st.number_input("Enter ACN", 1, 150, 50)
else:
    acn = aircraft_data[aircraft]
    st.info(f"ACN = {acn}")

tolerance = st.slider("Overstress tolerance (%)", 0, 25, 10)

# -----------------------------
# PCN OPTIONS
# -----------------------------
pcn_choices = list(range(10, 101))

# -----------------------------
# YEOVILTON LAYOUT (structured)
# -----------------------------
segments = {

    # RUNWAY (09/27 simplified)
    "RWY 09-1": ((0, 0), (10, 0)),
    "RWY 09-2": ((10, 0), (20, 0)),
    "RWY 09-3": ((20, 0), (30, 0)),

    # PARALLEL TAXIWAY
    "TWY A1": ((0, -2), (10, -2)),
    "TWY A2": ((10, -2), (20, -2)),
    "TWY A3": ((20, -2), (30, -2)),

    # CONNECTORS (entry/exit points)
    "TWY B1": ((5, 0), (5, -2)),
    "TWY B2": ((15, 0), (15, -2)),
    "TWY B3": ((25, 0), (25, -2)),

    # APRON ACCESS (north side)
    "TWY C1": ((10, -2), (10, 3)),
    "TWY C2": ((20, -2), (20, 4)),

    # APRON / STANDS CLUSTER
    "APRON N1": ((8, 3), (12, 3)),
    "APRON N2": ((18, 4), (22, 4)),

    "STAND 1": ((8, 3), (8, 5)),
    "STAND 2": ((10, 3), (10, 5)),
    "STAND 3": ((12, 3), (12, 5)),

    "STAND 4": ((18, 4), (18, 6)),
    "STAND 5": ((20, 4), (20, 6)),
    "STAND 6": ((22, 4), (22, 6)),

    # SOUTHERN SPURS (HAS / dispersal style)
    "TWY D1": ((5, -2), (5, -6)),
    "TWY D2": ((15, -2), (15, -7)),
    "TWY D3": ((25, -2), (25, -6)),

    "HAS 1": ((5, -6), (7, -8)),
    "HAS 2": ((15, -7), (17, -9)),
    "HAS 3": ((25, -6), (27, -8)),
}

# -----------------------------
# INPUT PCN PER SEGMENT
# -----------------------------
st.subheader("Assign PCN Values")

pcn_values = {}

cols = st.columns(5)

for i, name in enumerate(segments.keys()):
    col = cols[i % 5]
    pcn_values[name] = col.selectbox(
        name,
        pcn_choices,
        index=40,
        key=name
    )

# -----------------------------
# CLASSIFICATION LOGIC
# -----------------------------
def classify(acn, pcn):
    if acn <= pcn:
        return "GREEN", "green"
    elif acn <= pcn * (1 + tolerance / 100):
        return "AMBER", "orange"
    else:
        return "RED", "red"

# -----------------------------
# DRAW AIRFIELD
# -----------------------------
st.subheader("Surface Movement Assessment")

fig, ax = plt.subplots(figsize=(12, 6))

results = []

for name, ((x1, y1), (x2, y2)) in segments.items():
    pcn = pcn_values[name]
    label, color = classify(acn, pcn)

    # Draw segment
    ax.plot([x1, x2], [y1, y2], linewidth=6, color=color)

    # Label
    ax.text((x1 + x2)/2, (y1 + y2)/2,
            f"{name}\n{pcn}\n{label}",
            fontsize=7, ha='center')

    results.append((name, pcn, label))

# Styling
ax.set_aspect('equal')
ax.set_title("RNAS Yeovilton Layout (Simplified)")
ax.axis('off')

st.pyplot(fig)

# -----------------------------
# SUMMARY (OPS READY)
# -----------------------------
green = sum(1 for _,_,r in results if r == "GREEN")
amber = sum(1 for _,_,r in results if r == "AMBER")
red = sum(1 for _,_,r in results if r == "RED")

st.subheader("Operational Summary")

st.write(f"🟢 Green – Free to operate: {green}")
st.write(f"🟠 Amber – Command authority required: {amber}")
st.write(f"🔴 Red – Under no circumstances: {red}")

# -----------------------------
# GO / NO-GO FLAG
# -----------------------------
if red > 0:
    st.error("NO-GO: Red segments present on manoeuvring surfaces")
elif amber > 0:
    st.warning("CONDITIONAL: Command authority required")
else:
    st.success("GO: All routes within limits")
