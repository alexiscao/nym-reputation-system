from ..simulation.SimNode import Config as Config_sim
from .Result import Config as Config_result
from .path_prob import min_f_for_required_paths
from .min_cost import min_cost_config_for_AstarA, min_cost_config_for_AAAAA, config_for_AAAAA_constraints, config_for_AstarA_constraints
import math


def table(dropfile1: str, dropfile2: str, config):
    """
    Output table comparing different attack strategies.
    Args:
        dropfile1: simulation results for A***A objective
        dropfile2: simulation results for AAAAA objective
        (for v1, dropfile1 = dropfile2 since A nodes will always be gateways 
        and B nodes will always be mixnodes which can be selected into the active set)
    """
    GW_FILE = config.GW_FILE
    MIX_FILE = config.MIX_FILE
    
    # set connections and packets based on observations of the nym network
    connections = 50
    packets = 1000
    
    # calculate the f_gw and f_mix required 
    # for one of the packets to go through an adversarial path with 50% probability
    f_gw = 0
    f_mix = 0
    
    total_gw = Config_sim().entry_gws + Config_sim().exit_gws
    total_mix = Config_sim().mixnodes_layers * Config_sim().mixnodes_per_layer
    
    f_gw = min_f_for_required_paths(mode='gw', target_N=connections, config=config)
    if f_gw is not None:
        num_gw = math.ceil(f_gw * total_gw)
        f_gw = math.ceil( (num_gw/total_gw) * 100) / 100
    
    f_mix = min_f_for_required_paths(mode='mix', target_N=packets, config=config)
    if f_mix is not None:
        num_mix = math.ceil(f_mix * total_mix)
        f_mix = math.ceil( (num_mix/total_mix) * 100) / 100

    # optimal B, A, stake set for baseline staking attack 
    baseline_gw = min_cost_config_for_AstarA(file=GW_FILE, f_gw=f_gw)
    baseline_mix = min_cost_config_for_AAAAA(file=MIX_FILE, f_gw=f_gw, f_mix=f_mix)
    
    # optimal B, A, stake set for framing attack
    perf_gw = min_cost_config_for_AstarA(file=dropfile1, f_gw=f_gw)
    perf_mix = min_cost_config_for_AAAAA(file=dropfile2, f_gw=f_gw, f_mix=f_mix)
    
    # print results - lowest cost for baseline and framing attack
    if baseline_gw is not None and baseline_mix is not None:
        
        baseline_AstarA_costs = baseline_gw['cost']
        baseline_AAAAA_costs = baseline_mix['cost']
        
        print(f"base_A***A: {f_gw:.2f} gw, 0.00 mix, {int(baseline_AstarA_costs)} USD ({int(baseline_gw['refundable_cost'])}, {baseline_gw['non_refundable_cost']}), "
              f"{baseline_gw['B']} S, {baseline_gw['A']} A, (0, {baseline_gw['astake']}) Stake")
        print(f"base_AAAAA: {f_gw:.2f} gw, {f_mix:.2f} mix, {int(baseline_AAAAA_costs)} USD ({int(baseline_mix['refundable_cost'])}, {baseline_mix['non_refundable_cost']}), "
              f"{(baseline_mix['B'])} S, {(baseline_mix['A'])} A, (0, {baseline_mix['astake']}) Stake")
    
    if perf_gw is not None and perf_mix is not None:
        
        perf_AstarA_costs = perf_gw['cost']
        perf_AAAAA_costs = perf_mix['cost']
        
        savings_AstarA = (baseline_AstarA_costs - perf_AstarA_costs) / baseline_AstarA_costs
        savings_AAAAA = (baseline_AAAAA_costs - perf_AAAAA_costs) / baseline_AAAAA_costs
        
        print(f"perf_A***A: {f_gw} gw, 0.00 mix, {int(perf_AstarA_costs)} USD ({int(perf_gw['refundable_cost'])}, {perf_gw['non_refundable_cost']}), "
              f"{savings_AstarA:.3f} Savings, {perf_gw['B']} S, {perf_gw['A']} A, ({perf_gw['bstake']}, {perf_gw['astake']}) Stake")
        print(f"perf_AAAAA: {f_gw} gw, {f_mix} mix, {int(perf_AAAAA_costs)} USD ({int(perf_mix['refundable_cost'])}, {perf_mix['non_refundable_cost']}), "
              f"{savings_AAAAA:.3f} Savings, {perf_mix['B']} S, {perf_mix['A']} A, ({perf_mix['bstake']}, {perf_mix['astake']}) Stake")
    
    
    # print results - with constraints setting for framing attack
    max_total_nodes = 1000
    
    # with constraints for A***A
    best_entry_AstarA = None
    best_savings_gw = None
    for total_nodes in range(10, max_total_nodes + 1, 10):
        candidate_gw = config_for_AstarA_constraints(file_gw1=dropfile1, file_gw2=None, f_gw=f_gw, total_nodes=total_nodes)
        if candidate_gw is None:
            continue
        savings = (baseline_AstarA_costs - candidate_gw.total_cost) / baseline_AstarA_costs
        if savings >= 0:
            best_entry_AstarA = candidate_gw
            best_savings_gw = savings
            break
        
    if best_entry_AstarA is not None:
        gw_entry = best_entry_AstarA
        print(
            f"cons_A***A: {f_gw} gw, 0.00 mix, {int(gw_entry.total_cost)} USD ({int(gw_entry.refundable_cost)}, {gw_entry.non_refundable_cost}), "
            f"{best_savings_gw:.3f} Savings, {gw_entry.B} B, {gw_entry.A} A, ({gw_entry.bstake}, {gw_entry.astake}) Stake"
        )

    
    # with constraints for AAAAA
    best_entry_AAAAA = None
    best_savings_all = None
    for total_nodes in range(10, max_total_nodes + 1, 10):
        candidate_all = config_for_AAAAA_constraints(drop_file=dropfile2, f_gw=f_gw, f_mix=f_mix, total_nodes=total_nodes)
        if candidate_all is None:
            continue
        savings = (baseline_AAAAA_costs - candidate_all.total_cost) / baseline_AAAAA_costs
        if savings >= 0:
            best_entry_AAAAA = candidate_all
            best_savings_all = savings
            break
    
    if best_entry_AAAAA is not None:
        all_entry = best_entry_AAAAA
        print(
            f"cons_AAAAA: {f_gw} gw, {f_mix} mix, {int(all_entry.total_cost)} USD ({int(all_entry.refundable_cost)}, {all_entry.non_refundable_cost}), "
            f"{best_savings_all:.3f} Savings, {all_entry.B} B, {all_entry.A} A, ({all_entry.bstake}, {all_entry.astake}) Stake"
        )
        
    
    
