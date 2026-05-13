
import streamlit as st
import matplotlib.pyplot as plt
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

st.set_page_config(page_title="ACN-PCN Tool", layout="wide")

st.title("Runway ACN vs PCN Assessment Tool")

# Aircraft Data (editable)
aircraft_data = {
    "Custom": None,
    "F-35B": 45,
    "C-130J": 50,
    "A400M": 60,
}

col1, col2 = st.columns(2)

with col1:
    aircraft_choice = st.selectbox("Aircraft", list(aircraft_data.keys()))
    if aircraft_choice == "Custom":
        acn = st.number_input("Enter ACN", 1, 150, 50)
    else:
        acn = aircraft_data[aircraft_choice]
        st.info(f"ACN: {acn}")

with col2:
    tolerance = st.slider("Overstress tolerance (%)", 0, 25, 10)

st.subheader("Runway Sections")
sections = st.slider("Number of sections", 3, 20, 10)

pcn_values = []
cols = st.columns(5)
for i in range(sections):
    col = cols[i % 5]
    p = col.number_input(f"PCN {i+1}", 1, 100, 50, key=i)
    pcn_values.append(p)


def classify(acn, pcn):
    if acn <= pcn:
        return "GREEN", "green"
    elif acn <= pcn * (1 + tolerance/100):
        return "AMBER", "orange"
    else:
        return "RED", "red"

fig, ax = plt.subplots()
results = []

for i, p in enumerate(pcn_values):
    label, color = classify(acn, p)
    ax.plot([i, i+1], [0,0], linewidth=15, color=color)
    ax.text(i+0.5, 0.02, f"{p}", ha='center')
    ax.text(i+0.5, -0.02, label, ha='center', fontsize=8)
    results.append((i+1, p, label))

ax.set_xlim(0, len(pcn_values))
ax.set_yticks([])
ax.set_title("Runway Assessment")

st.pyplot(fig)

# Summary
usable = sum(1 for _,_,r in results if r == "GREEN")
amber = sum(1 for _,_,r in results if r == "AMBER")
red = sum(1 for _,_,r in results if r == "RED")

st.write(f"✅ Green (Free use): {usable}")
st.write(f"⚠️ Amber (Command authority required): {amber}")
st.write(f"⛔ Red (Do not use): {red}")

# PDF Export
if st.button("Export PDF Brief"):
    filename = "runway_brief.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    c.drawString(50, 750, f"ACN: {acn}")
    y = 700
    for sec, p, r in results:
        c.drawString(50, y, f"Section {sec} - PCN {p} - {r}")
        y -= 20
    c.save()

    with open(filename, "rb") as f:
        st.download_button("Download PDF", f, file_name=filename)
