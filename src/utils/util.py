import json
from collections import defaultdict

def save_results(results, filename):
    with open(filename, 'w') as f:
        json.dump(results, f, indent=2)
def load_results(filename):
    with open(filename, 'r') as f:
        return json.load(f) 

def add_then_average(all_entries):
    aggregates = {}
    for r in all_entries:
        key = (r['B'], r['A'], r['B_stake'], r['A_stake'])
        if key not in aggregates:
            aggregates[key] = {
                'count': 0,
                'f_gw_sum': 0.0,
                'f_mix_sum': 0.0,
                'path_prob_sum': defaultdict(float), 
                'B_gw_sum': 0.0,
                'A_gw_sum': 0.0,
                'B_mix_sum': 0.0,
                'A_mix_sum': 0.0
            }
        agg = aggregates[key]
        agg['count'] += 1
        agg['f_gw_sum'] += r['f_gw']
        agg['f_mix_sum'] += r['f_mix']
        for k, v in r['path_prob'].items():
            agg['path_prob_sum'][k] += v
        agg['B_gw_sum'] += r['B_gw']
        agg['A_gw_sum'] += r['A_gw']
        agg['B_mix_sum'] += r['B_mix']
        agg['A_mix_sum'] += r['A_mix']
        
    averaged_results = []
    for (B, A, B_stake, A_stake), agg in aggregates.items():
        cnt = max(agg['count'], 1)
        avg_path_prob = {k: v / cnt for k, v in agg['path_prob_sum'].items()}
        averaged_results.append({
            'f_gw': agg['f_gw_sum'] / cnt,
            'f_mix': agg['f_mix_sum'] / cnt,
            'path_prob': avg_path_prob,
            'B_gw': agg['B_gw_sum'] / cnt,
            'A_gw': agg['A_gw_sum'] / cnt,
            'B_mix': agg['B_mix_sum'] / cnt,
            'A_mix': agg['A_mix_sum'] / cnt,
            'B': B,
            'A': A,
            'B_stake': B_stake,
            'A_stake': A_stake,
        })
    
    return averaged_results
    
     
def get_cost(B, A, bstake, astake):
    vps = (B+A) * 20
    self_bond = (B+A) * 100 * 0.04
    total_stake = (A * (astake * 0.04)) + (B * (bstake * 0.04))
    cost = vps + self_bond + total_stake
    return cost

def get_refundable_cost(B, A, bstake, astake):
    self_bond = (B+A) * 100 * 0.04
    total_stake = (A * (astake * 0.04)) + (B * (bstake * 0.04))
    refundable_cost = self_bond + total_stake
    return refundable_cost


def get_non_refundable_cost(B, A, bstake, astake):
    vps = (B+A) * 20
    return vps