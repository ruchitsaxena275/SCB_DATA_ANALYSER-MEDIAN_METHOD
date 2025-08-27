import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import time

# -------- Constants --------
NUM_STRINGS = 18
CR_LOW_THRESHOLD = 0.90   # <90% of median → weak

# -------- Functions --------
def process_file(df):
    # Assume: Col A = timestamp, Col B-S = strings, Col Y = irradiation (ignored here)
    df = df.copy()
    df.iloc[:,0] = pd.to_datetime(df.iloc[:,0])   # timestamp
    df = df.set_index(df.columns[0])

    measured_cols = df.columns[0:NUM_STRINGS]     # B..S → string currents
    measured = df[measured_cols].astype(float)

    # Median across all strings at each timestamp
    median_series = measured.median(axis=1)

    result = measured.copy()
    for i,col in enumerate(measured_cols, start=1):
        result[f"CR_String_{i}"] = np.where(median_series>0, measured[col]/median_series, np.nan)

    result["Median_String_Current"] = median_series
    result["Measured_SCB_Current"] = measured.sum(axis=1)
    return result

def plot_heatmap(df):
    cr_cols = [c for c in df.columns if c.startswith("CR_String_")]
    cr_matrix = df[cr_cols]

    fig, ax = plt.subplots(figsize=(14,6))
    im = ax.imshow(cr_matrix.T, aspect='auto', origin='lower', vmin=0.0, vmax=1.4)
    ax.set_yticks(np.arange(NUM_STRINGS))
    ax.set_yticklabels([f"String {i+1}" for i in range(NUM_STRINGS)])
    xticks = np.linspace(0, len(cr_matrix)-1, min(12, len(cr_matrix))).astype(int)
    ax.set_xticks(xticks)
    ax.set_xticklabels([df.index[i].strftime("%m-%d %H:%M") for i in xticks], rotation=45, ha='right')
    ax.set_title("String Current Ratio (to Median) Heatmap")
    fig.colorbar(im, ax=ax, label="CR (Measured/Median)")
    st.pyplot(fig)

def daily_summary(df):
    cr_cols = [c for c in df.columns if c.startswith("CR_String_")]
    df2 = df[cr_cols].copy()
    df2["date"] = df.index.date
    grouped = df2.groupby("date")

    rows = []
    for date, grp in grouped:
        weak = []
        for i,c in enumerate(cr_cols, start=1):
            frac = (grp[c]<CR_LOW_THRESHOLD).mean()
            if frac > 0.3:   # 30% of the time weak
                weak.append(f"String {i}")
        rows.append({"date": date, "weak_strings": ", ".join(weak)})
    return pd.DataFrame(rows)

# -------- Streamlit UI --------
st.title("SCB String Current Analysis Tool (Median-based Method)")

file = st.file_uploader("Upload Excel file (with fixed format)", type=["xlsx"])
if file:
    df = pd.read_excel(file, engine="openpyxl")
    result = process_file(df)

    # --- Time range selection ---
    st.subheader("Select Time Range")
    min_time = result.index.min().time()
    max_time = result.index.max().time()

    col1, col2 = st.columns(2)
    with col1:
        start_time = st.time_input("Start Time", value=min_time)
    with col2:
        end_time = st.time_input("End Time", value=max_time)

    mask = (result.index.time >= start_time) & (result.index.time <= end_time)
    result = result.loc[mask]

    # --- Display results ---
    st.subheader("Preview of Processed Data")
    st.dataframe(result.head(20))

    st.subheader("Heatmap of Current Ratio (CR)")
    plot_heatmap(result)

    st.subheader("Daily Summary of Weak Strings")
    summary = daily_summary(result)
    st.dataframe(summary)

    # --- Download buttons ---
    csv = result.reset_index().to_csv(index=False).encode("utf-8")
    st.download_button("Download Processed CSV", csv, "processed_data.csv", "text/csv")

    csv2 = summary.to_csv(index=False).encode("utf-8")
    st.download_button("Download Daily Summary", csv2, "daily_summary.csv", "text/csv")
