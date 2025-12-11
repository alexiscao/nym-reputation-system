from collections import Counter, defaultdict
from typing import Dict, List

from .SimNode import Config, SimNode

def count_active_set_node_types(active_set: Dict[int, List[SimNode]]) -> Dict[str, int]:
    """
    For 1 active set, count the total number of each type of nodes in the active set
    Args:
        active_set: layer -> list of nodes in each active set layer
    Returns:
        counts: the count for each type
    """
    counts = Counter()
    for nodes in active_set.values():
        for node in nodes:
            counts[node.type] += 1 
            if node.type == 'B':
                if node.role == 'gateway':
                    counts['B_gw'] += 1
                elif node.role == 'mixnode':
                    counts['B_mix'] += 1
            elif node.type == 'A':
                if node.role == 'gateway':
                    counts['A_gw'] += 1
                elif node.role == 'mixnode':
                    counts['A_mix'] += 1
    return {
        'B_gw': counts.get('B_gw', 0),
        'B_mix': counts.get('B_mix', 0),
        'A_gw': counts.get('A_gw', 0),
        'A_mix': counts.get('A_mix', 0),
    }
    

def get_path_prob(active_set: Dict[int, List[SimNode]]) -> Dict[str, float]:
    """
    Get path A***A and *AAA* probabilities for 1 active set. (attacker controlled path: both B and A count towards attacker controlled)
    Count the number of A nodes in each layer of active set
    Then calculate the prob for different path combinations
    Args:
        active_set: layer -> list of nodes in each active set layer
    Returns:
        results: path combination, prob
    """
    config = Config()
    
    pA = [0.0] * config.total_layers
    pN = [0.0] * config.total_layers
    
    for layer in range(config.total_layers):
        nodes = active_set[layer]
        total = len(nodes)
        num_adv = sum(1 for node in nodes if node.type == 'A' or node.type == 'B')
        prob_adv = num_adv / total if total > 0 else 0
        pA[layer] = prob_adv
        pN[layer] = 1 - prob_adv
    
    results = defaultdict(float)
    results['A***A'] = pA[0] * pA[4]
    results['*AAA*'] = pA[1] * pA[2] * pA[3]

    return results


    