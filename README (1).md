# 📡 LoRaWAN Network Simulator

A Python-based simulator for LoRaWAN networks that models the effects of **Spreading Factor (SF)** on packet success rate, signal strength, battery life, and packet collisions.

Built as part of lab preparation for Dr. Hari Prabhat Gupta's research group.

---

## 📸 Output

![Simulation Results](assets/lorawan_simulation_results.png)

---

## 🔍 What It Simulates

- **Packet Success Rate** — how reliably packets reach the gateway at each SF
- **Collision Rate** — packets lost due to simultaneous transmissions on the same SF
- **RSSI vs Sensitivity** — signal strength compared to minimum decode threshold
- **Time on Air** — how long each transmission takes (affects battery)
- **Battery Life Estimate** — estimated days on a 2000 mAh battery

---

## 🛠️ Tech Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Matplotlib](https://img.shields.io/badge/Matplotlib-11557C?style=flat&logo=python&logoColor=white)
![NumPy](https://img.shields.io/badge/NumPy-013243?style=flat&logo=numpy&logoColor=white)

---

## ⚙️ Installation

```bash
git clone https://github.com/Aarushhiii/lorawan-network-simulator.git
cd lorawan-network-simulator
pip install -r requirements.txt
```

---

## ▶️ How to Run

**Default simulation** (20 nodes, 50 packets, 5km radius):
```bash
python lorawan_simulator.py
```

**Interactive What-If mode** — customize nodes, packets, and radius:
```
Run What-If mode? (y/n): y
Number of sensor nodes [default 20]: 50
Packets per node      [default 50]: 100
Network radius (m)    [default 5000]: 3000
```

---

## 📊 Spreading Factor Summary

| SF   | Range    | Battery Life | Time on Air | Best For          |
|------|----------|-------------|-------------|-------------------|
| SF7  | Short    | Longest     | 56.6 ms     | Dense urban areas |
| SF8  | Medium   | Long        | 103.4 ms    | Suburban          |
| SF9  | Medium   | Moderate    | 185.3 ms    | Mixed areas       |
| SF10 | Long     | Moderate    | 370.7 ms    | Rural             |
| SF11 | Longer   | Short       | 741.4 ms    | Remote areas      |
| SF12 | Longest  | Shortest    | 1482.8 ms   | Max range needed  |

---

## 📁 Project Structure

```
lorawan-network-simulator/
│
├── lorawan_simulator.py      # Main simulation script
├── requirements.txt          # Dependencies
├── README.md                 # This file
├── LICENSE                   # MIT License
└── assets/
    └── lorawan_simulation_results.png  # Output chart
```

---

## 🌱 Future Improvements

- Add multi-gateway support
- Simulate ADR (Adaptive Data Rate)
- Add real-world dataset comparison
- Export results to CSV

---

## 👩‍💻 Author

**Aarushi Jain**
[LinkedIn](https://www.linkedin.com/in/aarushi-jain-448606195/) · [GitHub](https://github.com/Aarushhiii)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
