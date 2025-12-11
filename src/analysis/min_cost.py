from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from .Result import Result


def min_cost_compare(f_max, round_num, files, labels):
    """
    For A***A.
    """
    series = []
    for file, label in zip(files, labels):
        results = Result.from_file(file)
        
        fa_to_min_total = defaultdict(lambda: float('inf'))
        for r in results:
            rounded_f = round(r.f_gw, round_num)
            if rounded_f != 0.0 and rounded_f <= f_max:
                fa_to_min_total[rounded_f] = min(fa_to_min_total[rounded_f], r.total_cost)
        
        #fa_to_min_total[0.0] = 0.0 # ensure line starts at (0.0, 0.0)
        
        sorted_fa = sorted(fa_to_min_total.items())
        x_vals = [fa for fa, _ in sorted_fa]
        y_vals = [total for _, total in sorted_fa]
        series.append((label, x_vals, y_vals))
    
    colors = ['blue', 'red', 'purple', 'orange', 'green']
    plt.figure(figsize=(10, 6))
    i = 0
    for label, x_vals, y_vals in series:
        plt.plot(x_vals, y_vals, linestyle='-', linewidth=3, marker='o', label=label, color=colors[i])
        i += 1
    
    plt.yscale('log') 
    
    plt.xlabel('Fraction of the gateway active set controlled by attacker', fontsize=16)
    plt.ylabel('Total costs (USD)', fontsize=16)
    #plt.xticks(np.arange(0.0, 0.21, 0.05), fontsize=14)
    plt.yticks(fontsize=14)
    plt.legend(fontsize=14)
    plt.grid(True)
    plt.tight_layout()
    plt.show()
    
        
def min_cost_config_for_AstarA(file, f_gw):
    """
    Parameters:
        file: the file to find the min cost entry for a specified fraction value
        f: the fraction value
        mode: gw or mix. 
    """
        
    results = Result.from_file(file)
    
    valid_entries = []
    for r in results:
        if r.f_gw >= f_gw:
            valid_entries.append(r)
    
    if not valid_entries:
        return None
    cheapest = min(valid_entries, key=lambda r: r.total_cost)
    
    return {
        'B': cheapest.B,
        'A': cheapest.A,
        'bstake': cheapest.bstake,
        'astake': cheapest.astake,
        'cost': cheapest.total_cost,
        'refundable_cost': cheapest.refundable_cost,
        'non_refundable_cost': cheapest.non_refundable_cost
    }

def min_cost_config_for_AAAAA(file, f_gw, f_mix):
    results = Result.from_file(file)
    
    valid_entries_AAAAA = []
    for r in results:
        if r.f_gw >= f_gw and r.f_mix >= f_mix:
            valid_entries_AAAAA.append(r)
            
    if not valid_entries_AAAAA:
        return None
    cheapest = min(valid_entries_AAAAA, key=lambda r: r.total_cost)

    return {
        'B': cheapest.B,
        'A': cheapest.A,
        'bstake': cheapest.bstake,
        'astake': cheapest.astake,
        'cost': cheapest.total_cost,
        'refundable_cost': cheapest.refundable_cost,
        'non_refundable_cost': cheapest.non_refundable_cost
    }
                   

def config_for_AAAAA_constraints(drop_file, f_gw, f_mix, total_nodes):
    
    file = Result.from_file(drop_file)
    
    def satisfies_constraints(entry):
        if (entry.B + entry.A) <= total_nodes:
            if (entry.f_gw >= f_gw) and (entry.f_mix >= f_mix):
                return True
        return False
    
    best_entry = None
    lowest_cost = float('inf')
    for entry in file:
        if satisfies_constraints(entry):
            total = entry.total_cost
            if total < lowest_cost:
                lowest_cost = total
                best_entry = entry

    return best_entry


def config_for_AstarA_constraints(file_gw1, file_gw2, f_gw, total_nodes):
    gw = Result.from_file(file_gw1) 
    if file_gw2 is not None:
        gw += Result.from_file(file_gw2)
    
    def satisfies_constraints(gw_entry):
        if (gw_entry.B + gw_entry.A) <= total_nodes:
            if (gw_entry.f_gw >= f_gw):
                return True
        return False
    
    best_entry = None
    lowest_cost = float('inf')
    for gw_entry in gw:
        if satisfies_constraints(gw_entry):
            total = gw_entry.total_cost
            if total < lowest_cost:
                lowest_cost = total
                best_entry = gw_entry
    
    return best_entry
    

