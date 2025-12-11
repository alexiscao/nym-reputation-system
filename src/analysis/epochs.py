import os
import json
import matplotlib.pyplot as plt
from matplotlib import rcParams
from collections import defaultdict
rcParams['font.family'] = 'serif' 

def epochs_graph(filename, file2, file3):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    data_dir = os.path.join(project_root, "sim_data")
    
    file_path1 = filename if os.path.isabs(filename) else os.path.join(data_dir, filename)
    file_path2 = file2 if os.path.isabs(file2) else os.path.join(data_dir, file2)
    file_path3 = file3 if os.path.isabs(file3) else os.path.join(data_dir, file3)

    with open(file_path1, "r") as f:
        data1 = json.load(f)
    with open(file_path2, "r") as f:
        data2 = json.load(f)
    with open(file_path3, "r") as f:
        data3 = json.load(f)

    records1 = sorted(data1, key=lambda r: r.get("epochs", 0))
    records2 = sorted(data2, key=lambda r: r.get("epochs", 0))
    records3 = sorted(data3, key=lambda r: r.get("epochs", 0))
    xs = [r.get("epochs", 0) for r in records1]
    ys1 = [r.get("f_A", 0.0) for r in records1]
    ys2 = [r.get("f_A", 0.0) for r in records2]
    ys3 = [r.get("f_A", 0.0) for r in records3]
    
    # Plot
    plt.figure(figsize=(10, 6))
    plt.plot(xs, ys1, marker="o", linewidth=2, color='blue', label='S=60')
    plt.plot(xs, ys2, marker="o", linewidth=2, color='red', label='S=80')
    plt.plot(xs, ys3, marker="o", linewidth=2, color='purple', label='S=100')
    
    plt.xticks(xs, fontsize=14) 
    plt.yticks(fontsize=14)
    plt.xlabel("Epochs", fontsize=14)
    plt.ylabel("Fraction of the gateway active set controlled by attacker", fontsize=14)
    plt.grid(True)
    plt.legend(fontsize=14)
    plt.tight_layout()
    plt.show()

    