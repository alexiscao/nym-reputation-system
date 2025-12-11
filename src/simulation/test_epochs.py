import os
import datetime
import time
from collections import defaultdict
from multiprocessing import Pool, cpu_count, set_start_method
from tqdm import tqdm

from .SimNode import Config
from .create_nodes import create_target_nodes, create_B_A_nodes
from .drop_test_packets import drop_v1
from .get_active_set import dropping_calc_probs, get_active_set
from .counts import count_active_set_node_types
from ..utils.util import save_results

def get_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_one_combo(base_topology, B, A, bstake, astake, mode, version, epoch):
    config = Config()
    topology = create_B_A_nodes(base_topology, B, A, bstake, astake, mode, version)
    
    for _ in range(epoch * 4): 
        drop_v1(topology) # one drop_v1 corresponds to 1 round of testing
        dropping_calc_probs(topology)
    active_set = get_active_set(topology)    
    
    type_counts = count_active_set_node_types(active_set)
    
    f_A = type_counts['A_gw'] / (config.entry_gws + config.exit_gws)
    
    result = {
        "f_A": f_A,
        "B": B,
        "A": A,
        "epochs": epoch
    }
    
    return result

def run_one_combo_args(args):
    return run_one_combo(*args)

def run_epochs(base_topology, B, A, bstake, astake, mode, version, epochs):
    results_list = []

    base_args = [
        (base_topology, B, A, bstake, astake, mode, version, epoch)
        for epoch in epochs
    ]

    # NOTE SET SIMULATION ROUNDS
    n_runs = 1000
    args_list = [args for args in base_args for _ in range(n_runs)]

    # Run in parallel with progress bar
    with Pool(processes=cpu_count()) as pool:
        for result in tqdm(pool.imap_unordered(run_one_combo_args, args_list), total=len(args_list)):
            results_list.append(result)

    # Aggregate averages per unique combination
    aggregates = {}
    for r in results_list:
        key = (r['B'], r['A'], r['epochs'])
        if key not in aggregates:
            aggregates[key] = {
                'count': 0,
                'f_A_sum': 0.0,
            }
        agg = aggregates[key]
        agg['count'] += 1
        agg['f_A_sum'] += r['f_A']
    
    averaged_results = []
    for (B, A, epochs_val), agg in aggregates.items():
        cnt = max(agg['count'], 1)
        averaged_results.append({
            'f_A': agg['f_A_sum'] / cnt,
            'B': B,
            'A': A,
            'epochs': epochs_val,
        })

    # Save averaged results
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    data_dir = os.path.join(project_root, "sim_data")
    os.makedirs(data_dir, exist_ok=True) 
    filename = f"{B}_{A}_{n_runs}_test.json"
    file_path = os.path.join(data_dir, filename)

    averaged_results.sort(key=lambda r: r['epochs'])
    save_results(averaged_results, file_path)

