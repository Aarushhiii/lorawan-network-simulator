"""
LoRaWAN Network Simulator
=========================
Simulates a LoRaWAN network with multiple sensor nodes transmitting
to a single gateway. Models spreading factor effects on:
  - Packet success rate
  - Signal strength (RSSI)
  - Time on Air (battery usage)
  - Packet collisions

Requirements:
    pip install matplotlib numpy

Run:
    python lorawan_simulator.py
"""

import random
import math
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import numpy as np

# ─────────────────────────────────────────────
# LORA PARAMETERS
# ─────────────────────────────────────────────

SPREADING_FACTORS = [7, 8, 9, 10, 11, 12]

# Time on Air in milliseconds for a 20-byte payload at BW=125kHz
# Higher SF = longer time on air = more battery used
TIME_ON_AIR_MS = {
    7:  56.6,
    8:  103.4,
    9:  185.3,
    10: 370.7,
    11: 741.4,
    12: 1482.8,
}

# Sensitivity (dBm) — minimum signal strength to decode packet
# Higher SF = can detect weaker signals = longer range
SENSITIVITY_DBM = {
    7:  -123,
    8:  -126,
    9:  -129,
    10: -132,
    11: -134.5,
    12: -137,
}

# Transmission power (dBm) — fixed for all nodes
TX_POWER_DBM = 14

# Path loss model constants (log-distance model)
PATH_LOSS_EXPONENT = 2.7   # urban environment
REFERENCE_DISTANCE  = 1.0  # meters
REFERENCE_LOSS_DBM  = 40   # dBm at reference distance

# Noise / shadowing standard deviation
SHADOWING_STD = 6.0        # dB


# ─────────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────────

def calculate_path_loss(distance_m):
    """Log-distance path loss model."""
    if distance_m <= 0:
        distance_m = 0.1
    loss = (REFERENCE_LOSS_DBM
            + 10 * PATH_LOSS_EXPONENT * math.log10(distance_m / REFERENCE_DISTANCE)
            + random.gauss(0, SHADOWING_STD))
    return loss


def calculate_rssi(distance_m):
    """Received Signal Strength Indicator (dBm)."""
    return TX_POWER_DBM - calculate_path_loss(distance_m)


def packet_received(rssi, sf):
    """Return True if the signal is strong enough to decode."""
    return rssi >= SENSITIVITY_DBM[sf]


def detect_collision(node_times, node_sf, current_node, current_sf, current_start):
    """
    Simple collision detection:
    Two packets collide if they use the same SF and their transmission
    windows overlap in time.
    """
    current_duration = TIME_ON_AIR_MS[current_sf]
    for i, (start, sf) in enumerate(zip(node_times, node_sf)):
        if i == current_node:
            continue
        if sf != current_sf:
            continue   # different SF — no collision in LoRa
        duration = TIME_ON_AIR_MS[sf]
        # overlap check
        if current_start < start + duration and current_start + current_duration > start:
            return True
    return False


def estimate_battery_life_days(sf, transmissions_per_hour=1, battery_mah=2000):
    """
    Rough estimate of battery life.
    Assumes 100mA during transmission, 10uA sleep current.
    """
    tx_time_hours = (TIME_ON_AIR_MS[sf] / 1000) * transmissions_per_hour / 3600
    sleep_time_hours = 1 - tx_time_hours
    current_ma = tx_time_hours * 100 + sleep_time_hours * 0.01
    life_hours = battery_mah / current_ma
    return life_hours / 24


# ─────────────────────────────────────────────
# MAIN SIMULATION
# ─────────────────────────────────────────────

def run_simulation(num_nodes=20, num_packets_per_node=50, area_radius_m=5000):
    """
    Simulate a LoRaWAN network.

    Returns a dict of results keyed by spreading factor.
    """
    results = {}

    for sf in SPREADING_FACTORS:
        success_count  = 0
        collision_count = 0
        total_packets  = num_nodes * num_packets_per_node
        rssi_values    = []

        # Random node positions
        node_distances = [random.uniform(100, area_radius_m)
                          for _ in range(num_nodes)]

        for packet_idx in range(num_packets_per_node):

            # Each node transmits at a random time within a 60-second window
            tx_times = [random.uniform(0, 60_000) for _ in range(num_nodes)]
            tx_sfs   = [sf] * num_nodes

            for node_idx, (dist, t_start) in enumerate(zip(node_distances, tx_times)):
                rssi = calculate_rssi(dist)
                rssi_values.append(rssi)

                received = packet_received(rssi, sf)
                collided = detect_collision(tx_times, tx_sfs,
                                            node_idx, sf, t_start)

                if received and not collided:
                    success_count += 1
                elif collided:
                    collision_count += 1

        success_rate  = (success_count / total_packets) * 100
        collision_rate = (collision_count / total_packets) * 100
        avg_rssi      = sum(rssi_values) / len(rssi_values)
        battery_days  = estimate_battery_life_days(sf)

        results[sf] = {
            "success_rate":   round(success_rate,   2),
            "collision_rate": round(collision_rate, 2),
            "avg_rssi":       round(avg_rssi,       2),
            "time_on_air_ms": TIME_ON_AIR_MS[sf],
            "battery_days":   round(battery_days,   1),
            "sensitivity":    SENSITIVITY_DBM[sf],
        }

    return results


# ─────────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────────

def plot_results(results):
    sfs         = list(results.keys())
    success     = [results[sf]["success_rate"]   for sf in sfs]
    collisions  = [results[sf]["collision_rate"] for sf in sfs]
    rssi        = [results[sf]["avg_rssi"]       for sf in sfs]
    toa         = [results[sf]["time_on_air_ms"] for sf in sfs]
    battery     = [results[sf]["battery_days"]   for sf in sfs]
    sensitivity = [results[sf]["sensitivity"]    for sf in sfs]

    fig = plt.figure(figsize=(16, 10))
    fig.suptitle("LoRaWAN Network Simulator — Spreading Factor Analysis",
                 fontsize=15, fontweight="bold", y=0.98)

    gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35)

    colors = ["#378ADD", "#1D9E75", "#D85A30", "#BA7517", "#D4537E", "#7F77DD"]

    # ── 1. Packet success rate ──────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    bars = ax1.bar([f"SF{sf}" for sf in sfs], success, color=colors, edgecolor="white")
    ax1.set_title("Packet Success Rate (%)", fontweight="bold")
    ax1.set_ylabel("Success Rate (%)")
    ax1.set_ylim(0, 110)
    ax1.axhline(y=90, color="red", linestyle="--", linewidth=1, alpha=0.6, label="90% target")
    ax1.legend(fontsize=9)
    for bar, val in zip(bars, success):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 1,
                 f"{val}%", ha="center", va="bottom", fontsize=9)

    # ── 2. Collision rate ───────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.plot([f"SF{sf}" for sf in sfs], collisions,
             marker="o", color="#E24B4A", linewidth=2, markersize=7)
    ax2.fill_between(range(len(sfs)), collisions, alpha=0.15, color="#E24B4A")
    ax2.set_title("Packet Collision Rate (%)", fontweight="bold")
    ax2.set_ylabel("Collision Rate (%)")
    ax2.set_xticks(range(len(sfs)))
    ax2.set_xticklabels([f"SF{sf}" for sf in sfs])
    ax2.set_ylim(0, max(collisions) * 1.4 + 1)

    # ── 3. Average RSSI vs Sensitivity ─────────
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.plot([f"SF{sf}" for sf in sfs], rssi,
             marker="s", color="#378ADD", linewidth=2, markersize=7, label="Avg RSSI")
    ax3.plot([f"SF{sf}" for sf in sfs], sensitivity,
             marker="^", color="#D85A30", linewidth=2,
             markersize=7, linestyle="--", label="Sensitivity threshold")
    ax3.set_title("RSSI vs Sensitivity (dBm)", fontweight="bold")
    ax3.set_ylabel("dBm")
    ax3.legend(fontsize=9)
    ax3.set_xticks(range(len(sfs)))
    ax3.set_xticklabels([f"SF{sf}" for sf in sfs])

    # ── 4. Time on Air ──────────────────────────
    ax4 = fig.add_subplot(gs[1, 0])
    bars4 = ax4.bar([f"SF{sf}" for sf in sfs], toa, color=colors, edgecolor="white")
    ax4.set_title("Time on Air per Packet (ms)", fontweight="bold")
    ax4.set_ylabel("Milliseconds")
    for bar, val in zip(bars4, toa):
        ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                 f"{val}", ha="center", va="bottom", fontsize=9)

    # ── 5. Battery life ─────────────────────────
    ax5 = fig.add_subplot(gs[1, 1])
    ax5.plot([f"SF{sf}" for sf in sfs], battery,
             marker="D", color="#1D9E75", linewidth=2, markersize=7)
    ax5.fill_between(range(len(sfs)), battery, alpha=0.15, color="#1D9E75")
    ax5.set_title("Estimated Battery Life (days)", fontweight="bold")
    ax5.set_ylabel("Days (2000 mAh battery)")
    ax5.set_xticks(range(len(sfs)))
    ax5.set_xticklabels([f"SF{sf}" for sf in sfs])
    for i, (x, y) in enumerate(zip(range(len(sfs)), battery)):
        ax5.annotate(f"{y}d", (x, y), textcoords="offset points",
                     xytext=(0, 8), ha="center", fontsize=9)

    # ── 6. Summary table ────────────────────────
    ax6 = fig.add_subplot(gs[1, 2])
    ax6.axis("off")
    headers = ["SF", "Success%", "RSSI(dBm)", "ToA(ms)", "Battery(d)"]
    table_data = [
        [f"SF{sf}",
         f"{results[sf]['success_rate']}%",
         f"{results[sf]['avg_rssi']}",
         f"{results[sf]['time_on_air_ms']}",
         f"{results[sf]['battery_days']}"]
        for sf in sfs
    ]
    table = ax6.table(
        cellText=table_data,
        colLabels=headers,
        cellLoc="center",
        loc="center",
        bbox=[0, 0, 1, 1],
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    for (row, col), cell in table.get_celld().items():
        if row == 0:
            cell.set_facecolor("#378ADD")
            cell.set_text_props(color="white", fontweight="bold")
        elif row % 2 == 0:
            cell.set_facecolor("#f0f4ff")
        cell.set_edgecolor("#dddddd")
    ax6.set_title("Summary Table", fontweight="bold", pad=10)

    plt.savefig("lorawan_simulation_results.png", dpi=150,
                bbox_inches="tight", facecolor="white")
    print("\nChart saved as: lorawan_simulation_results.png")
    plt.show()


# ─────────────────────────────────────────────
# WHAT-IF MODE  (interactive terminal)
# ─────────────────────────────────────────────

def what_if_mode():
    print("\n" + "="*55)
    print("  LoRaWAN What-If Playground")
    print("="*55)

    try:
        num_nodes = int(input("Number of sensor nodes [default 20]: ") or 20)
        packets   = int(input("Packets per node      [default 50]: ") or 50)
        radius    = int(input("Network radius (m)    [default 5000]: ") or 5000)
    except ValueError:
        print("Invalid input — using defaults.")
        num_nodes, packets, radius = 20, 50, 5000

    print(f"\nSimulating {num_nodes} nodes × {packets} packets each "
          f"in a {radius}m radius network...\n")

    results = run_simulation(num_nodes, packets, radius)

    print(f"{'SF':<6} {'Success%':<12} {'Avg RSSI':<14} "
          f"{'ToA (ms)':<12} {'Battery (days)'}")
    print("-" * 60)
    for sf in SPREADING_FACTORS:
        r = results[sf]
        print(f"SF{sf:<4} {r['success_rate']:<12} {r['avg_rssi']:<14} "
              f"{r['time_on_air_ms']:<12} {r['battery_days']}")

    print("\nGenerating charts...")
    plot_results(results)


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    print("="*55)
    print("  LoRaWAN Network Simulator")
    print("  Project 1 — Dr. Hari Prabhat Gupta Lab Prep")
    print("="*55)

    print("\nRunning default simulation (20 nodes, 50 packets, 5km radius)...")
    results = run_simulation()
    plot_results(results)

    again = input("\nRun What-If mode? (y/n): ").strip().lower()
    if again == "y":
        what_if_mode()
