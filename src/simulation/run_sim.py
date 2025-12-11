import os
import datetime
from collections import defaultdict
from multiprocessing import Pool, cpu_count, set_start_method
from tqdm import tqdm

from typing import Dict, List, Sequence, Tuple, Optional, Union

from .SimNode import Config, SimNode
from .create_nodes import create_B_A_nodes
from .drop_test_packets import drop_test_packets
from .get_active_set import dropping_calc_probs, no_dropping_calc_probs, get_active_set
from .counts import count_active_set_node_types, get_path_prob
from ..utils.util import save_results, add_then_average

config = Config()
G_BASE_TOPOLOGY = None # global base_topology for worker processes to avoid re-pickling per task

def get_timestamp() -> str:
    """Current timestamp for filenames"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def init_worker(base_topology: Dict[int, List[SimNode]]) -> None:
    """
    Worker initializer to cache the base topology in a global for the process
    Args:
        base_topology: layer -> a list of nodes on each layer
    """
    global G_BASE_TOPOLOGY
    G_BASE_TOPOLOGY = base_topology

def run_one_combo(
    B: int, 
    A: int, 
    bstake: float, 
    astake: float, 
    mode: str, 
    version: str, 
    attack: bool
) -> Dict[str, Union[Union[int, float], Dict[str, float]]]:
    """
    Run one combination once and returns the result regarding to one active set.
    Args:
        B: number of B (sacrifice) nodes
        A: number of A attacking nodes
        bstake: amount of stake on each B node
        astake: amount of stake on each A node
        mode: attack objective A***A or AAAAA
        version: NM versions, v1, v2, or v3
        attack: False-baseline staking; True-framing attack
    Returns:
        result regarding to one active set 
    """
    
    # create a fresh working topology per run from the shared base
    global G_BASE_TOPOLOGY
    if G_BASE_TOPOLOGY is None:
        raise RuntimeError("Base topology not initialized.")
    base_topology = G_BASE_TOPOLOGY
    
    if attack:
        topology = create_B_A_nodes(base_topology, B, A, bstake, astake, mode, version)
        for _ in range(config.epochs):
            for _ in range(4): # each epoch has 4 rounds of testing
                drop_test_packets(topology, version)
                dropping_calc_probs(topology)
            active_set = get_active_set(topology)
    else:
        B = 0
        bstake = 0
        topology = create_B_A_nodes(G_BASE_TOPOLOGY, 0, A, 0, astake, mode, version) # set B and bstake to zero if there's no framing attack.
        no_dropping_calc_probs(topology)
        active_set = get_active_set(topology)
        
    type_counts = count_active_set_node_types(active_set)
    path_prob = get_path_prob(active_set)
    
    f_gw = (type_counts['B_gw'] + type_counts['A_gw']) / (config.entry_gws + config.exit_gws)
    f_mix = (type_counts['B_mix'] + type_counts['A_mix']) / (config.mixnodes_layers * config.mixnodes_per_layer)
    
    result = {
        "f_gw": f_gw,
        "f_mix": f_mix,
        "path_prob": path_prob,
        "B_gw": type_counts["B_gw"],
        "A_gw": type_counts['A_gw'],
        "B_mix": type_counts['B_mix'],
        "A_mix": type_counts['A_mix'],
        "B": B,
        "A": A,
        "B_stake": bstake,
        "A_stake": astake
    }
    
    return result

def run_one_combo_args(args: Tuple[int, int, float, float, str, str, bool]) -> Dict[str, Union[Union[int, float], Dict[str, float]]]:
    return run_one_combo(*args)

def run_many_combo(
    base_topology: Dict[int, List[SimNode]], 
    B_range: Sequence[int], 
    A_range: Sequence[int], 
    bstake: Sequence[float], 
    astake: Sequence[float], 
    mode: str, 
    version: str, 
    attack: bool,
    n_runs: int,
) -> None:
    """
    Run many simulations and save the averaged results across those simulations to file.
    Args:
        base_topology: layers -> a list of nodes on each layer
        B_range: range of number of B nodes
        A_range: range of number of A nodes
        bstake: range of stakes on each B nodes
        astake: range of stakes on each A nodes
        mode: attack objective A***A or AAAAA
        version: NM version, v1, v2, or v3
        attack: False-baseline staking; True-framing attack
        n_runs: number of simulations to run
    """
    
    results_list = []
    
    if attack:
        base_args = [
            (num_b, num_a, s_b, s_a, mode, version, attack)
            for num_b in B_range
            for num_a in A_range
            for s_b in bstake
            for s_a in astake
        ]
    else:
        base_args = [
            (0, num_a, 0, s_a, mode, version, attack)
            for num_a in A_range
            for s_a in astake
        ]
    
    args_list = [args for args in base_args for _ in range(n_runs)]
    
    with Pool(processes=cpu_count(), initializer=init_worker, initargs=(base_topology,)) as pool:
        for result in tqdm(pool.imap_unordered(run_one_combo_args, args_list), total=len(args_list)):
            results_list.append(result)
    
    averaged_results = add_then_average(results_list)
    averaged_results.sort(key=lambda r: r['f_gw'])
    
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    data_dir = os.path.join(project_root, "sim_data")
    os.makedirs(data_dir, exist_ok=True) 
        
    filename = f"{version}_{mode}_{attack}_{n_runs}.json"
    file_path = os.path.join(data_dir, filename)
    save_results(averaged_results, file_path)