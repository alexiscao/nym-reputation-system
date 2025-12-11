from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import math
from .Result import Result, Config


def combined_f_to_path_probs(mode, config):
    """
    Out of results json file for many different combinations,
    For the same f_A (could be same amount of A nodes in active set, but different amount of mixnodes/gws), 
    but what's the average path prob associated with the f_A?
    mode: gw, mix
    Returns:
        output: fraction of A, averaged path probs for AAAAA and A***A
    """
    GW_FILE = config.GW_FILE
    MIX_FILE = config.MIX_FILE

    if mode == 'gw':
        filename = GW_FILE
        f_field = 'f_gw'
        path = 'A***A'
    elif mode == 'mix':
        filename = MIX_FILE
        f_field = 'f_mix'
        path = '*AAA*'
    
    results = Result.from_file(filename)
    grouped = defaultdict(list) # same fraction of rounded f --> diff associated path_probs
    
    for r in results:
        f_val = getattr(r, f_field)
        grouped[f_val].append(r.path_prob.get(path, 0.0))
    
    output = []
    output.append({f_field: 0.0, path: 0.0})
    for f_val in sorted(grouped.keys()):
        path_probs = grouped[f_val]
        avg_val = float(np.mean(path_probs))
        entry = {f_field: f_val, path: avg_val}
        output.append(entry)
    
    return output


def plot_f_to_path_probs(f_max, config):
    """
    fraction of A nodes in active set to averaged path_prob associated with that f.
    """
    f_limit = f_max # NOTE or CHANGE HERE
    
    data_mix = combined_f_to_path_probs('mix', config)
    data_gw = combined_f_to_path_probs('gw', config)
    
    f_mix = [entry["f_mix"] for entry in data_mix if entry["f_mix"] <= f_limit]
    path_prob_mix = [entry["*AAA*"] for entry in data_mix if entry["f_mix"] <= f_limit]
    
    f_gw = [entry["f_gw"] for entry in data_gw if entry["f_gw"] <= f_limit]
    path_prob_gw = [entry["A***A"] for entry in data_gw if entry["f_gw"] <= f_limit]
    
    plt.figure(figsize=(10, 6))
    plt.plot(f_mix, path_prob_mix, label="*AAA*", color='red')
    plt.plot(f_gw, path_prob_gw, label="A***A", color='blue')
    
    plt.xlabel('Fraction of the gateway/mixnode active set controlled by attacker', fontsize=16)
    plt.xticks(fontsize=14)
    plt.ylabel('Probability of attacker objective', fontsize=16)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True)
    #plt.xticks(np.arange(0.0, 1.01, 0.1))
    plt.tight_layout()
    plt.show()


# helper function
def n(p, log):
    return math.inf if p == 0 else math.ceil(log / math.log(1 - p))
        
def n_required_for_prob_path(mode, withLimit, config):
    """
    for each f_A, how many paths are required to achieve at least 50% probability of having one path being AAAAA or A***A?
    mode: gw, mix
    """

    f_min = config.paths_f_min
    f_max = config.paths_f_max
    
    combined_data = combined_f_to_path_probs(mode, config)
    
    results = []
    
    if mode == 'gw':
        f_field = 'f_gw'
        path = 'A***A'
        log_val = math.log(0.5)
    elif mode == 'mix':
        f_field = 'f_mix'
        path = '*AAA*'
        log_val = math.log(0.01)
    
    for entry in combined_data:
        f = entry[f_field]
        p = entry.get(path, 0.0)
        
        if withLimit:
            if f_min < f <= f_max:
                results.append({
                    f_field: f,
                    'num_paths': n(p, log_val)
                })
        else:
            results.append({
                f_field: f,
                'num_paths': n(p, log_val)
            })
            
    return results
    
    
def plot_n_required_for_half_prob_path(type, config):
    """
    type: A***A, *AAA*
    """
    
    results_mix = n_required_for_prob_path('mix', True, config)
    results_gw = n_required_for_prob_path('gw', True, config)
    
    f_values_mix = [entry['f_mix'] for entry in results_mix]
    f_values_gw = [entry['f_gw'] for entry in results_gw]
    
    num_paths_mix  = [entry['num_paths'] for entry in results_mix]
    num_paths_gw  = [entry['num_paths'] for entry in results_gw]
    
    plt.figure(figsize=(10, 6))
    
    if type == "*AAA*":
        plt.plot(f_values_mix, num_paths_mix, label='*AAA*', color='red')
        plt.xlabel('Fractions of the mixnode active set controlled by attacker', fontsize=16)
        plt.ylabel('Number of packets', fontsize=16)
        
    elif type == "A***A":
        plt.plot(f_values_gw, num_paths_gw, label='A***A', color='blue')
        plt.xlabel('Fractions of the gateway active set controlled by attacker', fontsize=16)
        plt.ylabel('Number of connections', fontsize=16)  

    plt.xticks(np.arange(0.05, 0.25, 0.05), fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True)
    plt.tight_layout()
    plt.show()


def min_f_for_required_paths(mode, target_N, config):
    """
    reverse look up from previous function: given path num, look up f required
    mode: gw, mix
    """
    results = n_required_for_prob_path(mode, False, config)
    
    if mode == 'gw':
        f_field = 'f_gw'
    elif mode == 'mix':
        f_field = 'f_mix'
        
    valid_f = [
        entry[f_field] 
        for entry in results 
        if entry.get('num_paths') is not None and entry['num_paths'] <= target_N
    ]
    
    f = min(valid_f) if valid_f else None
    
    return f

    