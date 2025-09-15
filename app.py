import streamlit as st
import numpy as np
import plotly.graph_objects as go

# ---------------- Page Config ----------------
st.set_page_config(page_title="Low Carbon Cement Optimizer", layout="wide")
st.title("🏗️ Low Carbon Cement RSM Calculator")
st.markdown("### Predict Cement Cost, CO₂ Emission, and 28-Day Strength")

# ---------------- Correct experimental ranges ----------------
MIN_TEMP, MAX_TEMP = 600.0, 900.0
MIN_MARL, MAX_MARL = 5.0, 35.0
MIN_BLAINE, MAX_BLAINE = 3000.0, 9000.0

# ---------------- Model Function ----------------
def model_evals(T, M, B):
    # Cost model
    sqrt_cost = (
        3.41902
        + 5.32139e-05 * T
        + 1.83530e-03 * M
        + 1.00686e-04 * B
        + 1.01425e-05 * T * M
        - 5.12080e-09 * T * B
        - 1.64420e-07 * M * B
        - 4.41702e-09 * T**2
        - 6.93918e-06 * M**2
        - 7.86125e-10 * B**2
    )
    cost = sqrt_cost**2

    # CO₂ model
    sqrt_co2 = 0.65803 + 1.59871e-05*T + 6.39485e-05*M - 6.14217e-20*B
    co2 = sqrt_co2**2

    # Strength model
    sqrt_strength = (
        -12.01562
        + 0.037692*T
        + 0.29934*M
        - 2.07694e-04*B
        - 7.48852e-05*T*M
        + 4.76818e-07*T*B
        + 7.47419e-06*M*B
        - 2.31506e-05*T**2
        - 6.02852e-03*M**2
        - 1.92311e-08*B**2
    )
    strength = sqrt_strength**2

    return {
        "cost": float(cost),
        "co2": float(co2),
        "strength": float(strength)
    }

# ---------------- User Inputs ----------------
calc_temp = st.slider("Calcination Temp (°C)", MIN_TEMP, MAX_TEMP, 750.0)
marl_ratio = st.slider("Marl Ratio (%)", MIN_MARL, MAX_MARL, 20.0)
blaine = st.slider("Blaine Fineness", MIN_BLAINE, MAX_BLAINE, 6000.0)

currency = st.radio("Select Currency", ["USD", "PKR"])
usd_to_pkr = 278.0  # Example conversion rate

# ---------------- Compute Results ----------------
res = model_evals(calc_temp, marl_ratio, blaine)

cost_display = res["cost"] if currency == "USD" else res["cost"] * usd_to_pkr

st.subheader("Predicted Values")
st.metric("Cement Cost", f"{cost_display:.2f} {currency}")
st.metric("CO₂ Emission (fraction)", f"{res['co2']:.4f}")
st.metric("28-Day Strength", f"{res['strength']:.2f} MPa")

# ---------------- 3D Surface Plot ----------------
T_vals = np.linspace(MIN_TEMP, MAX_TEMP, 20)
M_vals = np.linspace(MIN_MARL, MAX_MARL, 20)
T_grid, M_grid = np.meshgrid(T_vals, M_vals)
B_fixed = blaine

strength_grid = np.zeros_like(T_grid)
for i in range(T_grid.shape[0]):
    for j in range(T_grid.shape[1]):
        strength_grid[i, j] = model_evals(T_grid[i, j], M_grid[i, j], B_fixed)["strength"]

fig = go.Figure(data=[go.Surface(z=strength_grid, x=T_grid, y=M_grid, colorscale="Viridis")])
fig.update_layout(scene=dict(
    xaxis_title="Temperature (°C)",
    yaxis_title="Marl Ratio (%)",
    zaxis_title="Strength (MPa)"
))
st.plotly_chart(fig, use_container_width=True)
