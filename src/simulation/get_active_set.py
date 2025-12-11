import numpy as np
from typing import Dict, List

from .SimNode import Config, SimNode


def dropping_calc_probs(topology: Dict[int, List[SimNode]]) -> None:
    """
    Calculate active set selection probability for all nodes when there's dropping.
    Args:
        topology: layer -> a list of nodes on that layer
    """
    for _, nodes in topology.items():
        for node in nodes:
            if (node.complete + node.incomplete) == 0: # in case a node does not receive a test packet
                score = None
            else:
                score = node.complete / (node.complete + node.incomplete)
            node.average_uptime_24(score)
            node.active_set_select_prob()

def no_dropping_calc_probs(topology: Dict[int, List[SimNode]]) -> None:
    """
    Calculate active set selection probability for all nodes when there's no dropping.
    Args:
        topology: layer -> a layer of nodes on that layer
    """
    for _, nodes in topology.items():
        for node in nodes:
            node.active_set_select_prob()
            
            
def get_active_set(topology: Dict[int, List[SimNode]]) -> Dict[int, List[SimNode]]:
    """
    Probablistically select mixnodes into the active set.
    Args:
        topology: layer -> a list of nodes
    Returns:
        active_set: layer --> list of Node objects selected into the active set
    """
    config = Config()
    
    active_set = {0: [], 1: [], 2: [], 3: [], 4: []}
    
    rng = np.random.default_rng()

    for layer in range(config.total_layers):
        layer_nodes = topology[layer]
        n_required = 0
        if layer in [1, 2, 3]:
            n_required = config.mixnodes_per_layer
        elif layer == 0:
            n_required = config.entry_gws
        elif layer == 4:
            n_required = config.exit_gws
        
        nodes_with_prob = [node for node in layer_nodes if node.select_prob > 0]
        nodes_zero_prob = [node for node in layer_nodes if node.select_prob == 0]
        
        # probabilistic sampling from nodes_with_prob
        weights = np.array([node.select_prob for node in nodes_with_prob], dtype=np.float64)
        weights = weights / weights.sum() if weights.sum() > 0 else None
        
        n_prob = min(n_required, len(nodes_with_prob))
        selected_from_prob = []
        if n_prob > 0:
            indices = rng.choice(len(nodes_with_prob), size=n_prob, replace=False, p=weights)
            selected_from_prob = [nodes_with_prob[i] for i in indices]
        
        # if needed, fill remaining with random sample from nodes_zero_prob
        n_remaining = n_required - len(selected_from_prob)
        selected_from_zero = []
        if n_remaining > 0:
            print("shouldn't be here")
            if len(nodes_zero_prob) < n_remaining:
                raise ValueError(f"Not enough nodes to fill layer {layer}: need {n_required}, got {len(layer_nodes)}.")
            indices = rng.choice(len(nodes_zero_prob), size=n_remaining, replace=False)
            selected_from_zero = [nodes_zero_prob[i] for i in indices]

        # combine
        active_set[layer] = selected_from_prob + selected_from_zero
    
    # mark all nodes inactive by default
    for _, nodes in topology.items():
        for node in nodes:
            node.isactive = False
    
    # then mark only selected nodes as active
    for _, nodes in active_set.items():
        for node in nodes:
            node.isactive = True
    
    return active_set 
    