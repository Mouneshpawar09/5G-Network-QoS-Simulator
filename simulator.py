"""
5G Network Simulator (Basic QoS Model)
---------------------------------------
- Simulates multiple UEs connected to a single gNB.
- Models path-loss + Rayleigh fading + simplified MIMO gain.
- Schedulers: equal share and proportional fair.
- Collects QoS metrics: throughput, latency, SNR.
- Saves plots and CSV summary to ./output folder.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# ----------------------------
# User Equipment (UE) Class
# ----------------------------
class UE:
    def __init__(self, ue_id, distance_m=100):
        self.id = ue_id
        self.distance = distance_m
        self.throughput_history = []
        self.latency_history = []
        self.snr_history = []
        self.avg_throughput = 1e-6  # to avoid divide by zero


# ----------------------------
# 5G Network Simulator Class
# ----------------------------
class FiveGSimulator:
    def __init__(self, num_ues=5, total_bw_hz=20e6, tx_power_dbm=43,
                 noise_fig_db=7, mimo_gain=2, scheduler="equal",
                 sim_steps=50, out_dir="output"):

        self.num_ues = num_ues
        self.total_bw_hz = total_bw_hz
        self.tx_power_dbm = tx_power_dbm
        self.noise_fig_db = noise_fig_db
        self.mimo_gain = mimo_gain
        self.scheduler = scheduler
        self.sim_steps = sim_steps
        self.out_dir = out_dir

        # Create output folder if not exists
        os.makedirs(self.out_dir, exist_ok=True)

        # Initialize UEs with random distances
        self.ues = [UE(i, distance_m=np.random.randint(50, 500))
                    for i in range(self.num_ues)]

    # ----------------------------
    # Helper Functions
    # ----------------------------
    def path_loss_db(self, d, f=3.5e9):
        """Simple log-distance path-loss model"""
        c = 3e8
        d0 = 1
        pl_d0 = 20 * np.log10(4 * np.pi * d0 * f / c)
        n = 3.0  # path-loss exponent
        return pl_d0 + 10 * n * np.log10(d / d0)

    def noise_power_dbm(self, bw_hz):
        kT_dbm_hz = -174  # thermal noise density
        return kT_dbm_hz + 10 * np.log10(bw_hz) + self.noise_fig_db

    # ----------------------------
    # Run Simulation
    # ----------------------------
    def run(self):
        for t in range(self.sim_steps):
            # Compute link quality for each UE
            snrs_linear = []
            inst_caps = []
            for ue in self.ues:
                pl = self.path_loss_db(ue.distance)
                fading = np.random.rayleigh(scale=1.0)
                fading_db = 20 * np.log10(fading + 1e-9)
                mimo_gain_db = 10 * np.log10(self.mimo_gain)
                rx_power = self.tx_power_dbm - pl + fading_db + mimo_gain_db
                noise_dbm = self.noise_power_dbm(self.total_bw_hz)
                snr_db = rx_power - noise_dbm
                snr_lin = 10**(snr_db/10)
                cap = self.total_bw_hz * np.log2(1 + snr_lin)  # Shannon capacity

                snrs_linear.append(snr_lin)
                inst_caps.append(cap)
                ue.snr_history.append(snr_db)

            # Bandwidth allocation
            if self.scheduler == "equal":
                bw_alloc = [self.total_bw_hz / self.num_ues] * self.num_ues
            elif self.scheduler == "pf":
                weights = [c / (ue.avg_throughput + 1e-9) for c, ue in zip(inst_caps, self.ues)]
                total_w = sum(weights)
                bw_alloc = [(w/total_w) * self.total_bw_hz for w in weights]
            else:
                raise ValueError("Scheduler must be 'equal' or 'pf'")

            # Compute throughput & latency
            for ue, bw, snr_lin, cap in zip(self.ues, bw_alloc, snrs_linear, inst_caps):
                cap_bps = bw * np.log2(1 + snr_lin)
                throughput_mbps = cap_bps / 1e6
                ue.throughput_history.append(throughput_mbps)

                # Latency model: packet = 1 Mbit
                packet_bits = 1e6
                tx_time_s = packet_bits / (cap_bps + 1e-9)
                prop_delay_s = ue.distance / 3e8
                latency_ms = (tx_time_s + prop_delay_s + 1e-3) * 1000
                ue.latency_history.append(latency_ms)

                # Update average throughput (EMA)
                ue.avg_throughput = 0.9 * ue.avg_throughput + 0.1 * throughput_mbps

        self.save_results()

    # ----------------------------
    # Save results
    # ----------------------------
    def save_results(self):
        summary = []
        for ue in self.ues:
            summary.append({
                "UE": ue.id,
                "Mean Throughput (Mbps)": np.mean(ue.throughput_history),
                "Median Latency (ms)": np.median(ue.latency_history),
                "Mean SNR (dB)": np.mean(ue.snr_history)
            })
            # Save latency plot per UE
            plt.figure()
            plt.plot(ue.latency_history)
            plt.title(f"UE {ue.id} Latency over Time")
            plt.xlabel("Time Step")
            plt.ylabel("Latency (ms)")
            plt.savefig(os.path.join(self.out_dir, f"latency_ue{ue.id}.png"))
            plt.close()

        # Save throughput bar chart
        plt.figure()
        plt.bar([ue.id for ue in self.ues],
                [np.mean(ue.throughput_history) for ue in self.ues])
        plt.title("Mean Throughput per UE")
        plt.xlabel("UE ID")
        plt.ylabel("Throughput (Mbps)")
        plt.savefig(os.path.join(self.out_dir, "throughput_per_ue.png"))
        plt.close()

        # Save CSV summary
        df = pd.DataFrame(summary)
        df.to_csv(os.path.join(self.out_dir, "summary.csv"), index=False)
        print(f"✅ Results saved in folder: {self.out_dir}")


# ----------------------------
# Main entry point
# ----------------------------
if __name__ == "__main__":
    sim = FiveGSimulator(num_ues=5, sim_steps=100, scheduler="pf")
    sim.run()
