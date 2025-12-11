import numpy as np
from typing import Dict, List, Tuple

from .SimNode import Config, SimNode

config = Config()

def drop_test_packets(
    topology: Dict[int, List[SimNode]], 
    version: str,
) -> None:
    """
    Run dropping strategy given a network monitor version.
    Args:
        topology: layer -> a layer of nodes on that layer
        version: network monitor version of v1, v2, or v3
    """
    
    if version == 'v1':
        drop_v1(topology)
    
    elif version == 'v2':
        paths = form_test_paths(topology)
        for path in paths:
            drop_v2(path)
    
    elif version == 'v3':
        paths = form_test_paths(topology)
        for path in paths:
            drop_v3(path)
    

def form_test_paths(topology: Dict[int, List[SimNode]]) -> List[List[SimNode]]:
    """
    Form test paths for 1 round of testings).
    Args: 
        topology: layer -> a list of nodes on that layer
    Returns:
        a list of test paths, where each path is [gw, l1, l2, l3, gw] 
    """
    rng = np.random.default_rng()
    
    total_gateways = topology[0] + topology[4]
    layer1 = topology[1]
    layer2 = topology[2]
    layer3 = topology[3] 
          
    total_nodes = sum(len(nodes) for nodes in topology.values())
    num_paths = total_nodes * 4 
    
    # generate all random indices at once 
    L1, L2, L3, LG = len(layer1), len(layer2), len(layer3), len(total_gateways)
    idx1 = rng.integers(L1, size=num_paths)
    idx2 = rng.integers(L2, size=num_paths)
    idx3 = rng.integers(L3, size=num_paths)
    idxG = rng.integers(LG, size=num_paths)
    
    all_paths = []
    for i1, i2, i3, ig in zip(idx1, idx2, idx3, idxG):
        node1 = layer1[i1]
        node2 = layer2[i2]
        node3 = layer3[i3]
        gateway = total_gateways[ig]
        path = [gateway, node1, node2, node3, gateway]
        all_paths.extend([path] * 3) # to mirror NM sending 3 packets down the same path 
        
    return all_paths         
        
        
def drop_v3(path: List[SimNode]) -> None:
    """
    Attack on NMv3 schemes.
    For every path, bad nodes decides if they were to drop the packets.
    Then update, the complete, incomplete, and fail counts for three nodes on the single path.
    
    Args:
        path: a single test path
    """

    path_complete = True
    has_B = False
    
    for i, node in enumerate(path):
        if node.type == 'B':
            has_B = True
            
            # B can't drop if it's in the active set
            if node.isactive == True:
                path_complete = True
                break
            
            # don't drop if bad node already has 2 fail counts
            if node.fail == 2:
                path_complete = True
                break
            
            # don't drop if previous or next node is an A node
            prev_is_A = (i > 0 and path[i-1].type == 'A')
            next_is_A = (i < len(path) - 1 and path[i+1].type == 'A')
            if prev_is_A or next_is_A:
                path_complete = True
                break
            else:
                path_complete = False 
            
    if not has_B:
        path_complete = True
        
    # update complete, incomplete, fail
    if path_complete:
        for node in path:
            node.complete += 1
            node.fail = 0
    else:
        guilty = []
        for node in path:
            node.fail +=1 
            if node.fail > 2:
                guilty.append(node)
                node.incomplete += 1
        if len(guilty) == 0:
            for node in path:
                node.incomplete += 1
    
            
def drop_v2(path: List[SimNode]) -> None:
    """
    Attack on NMv2. 
    Args: 
        path: a single test path
    """
    path_complete = True 
    for i, node in enumerate(path):
        if node.type == 'B':
            prev_is_A = (i > 0 and path[i-1].type == 'A')
            next_is_A = (i < len(path) - 1 and path[i+1].type == 'A')
            if prev_is_A or next_is_A:
                path_complete = True
                break
            else:
                path_complete = False
    
    if path_complete:
        for node in path:
            node.complete += 1
    else:
        for node in path:
            node.incomplete += 1


#====== THE FOLLOWINGS ARE FOR NMV1 ===#
def get_validated_paths(topology: Dict[int, List[SimNode]]) -> List[List[SimNode]]:
    """
    Randomly sample 3 validated paths based on previous 24 hours performance scores.
    
    Args:
        topology: layer -> a list of nodes on that layer
    Return:
        validated_paths: a list of validated paths [gw, l1, l2, l3, gw].
    """
    
    validated_paths = []
    
    gateways = topology[0] + topology[4]
    layer1 = topology[1]
    layer2 = topology[2]
    layer3 = topology[3]
    
    # selection without replacement across all paths
    rng = np.random.default_rng()
    selected_nodes = set()
    eps = 1e-10
    
    # random weighted selection based on performance scores
    def weighted_choice(nodes):
        weights = np.array([n.uptime for n in nodes], dtype=np.float64) + eps
        probs = weights / weights.sum() if weights.sum() > 0 else 0
        return list(rng.choice(nodes, size=config.num_validated_paths, replace=False, p=probs))
       
    available_list = [
        [n for n in gateways if n not in selected_nodes],
        [n for n in layer1 if n not in selected_nodes],
        [n for n in layer2 if n not in selected_nodes],
        [n for n in layer3 if n not in selected_nodes],
    ]
        
    gws, mix1s, mix2s, mix3s = [weighted_choice(lst) for lst in available_list]
        
    validated_paths = [[gws[i], mix1s[i], mix2s[i], mix3s[i], gws[i]] for i in range(config.num_validated_paths)]

    for path in validated_paths:
        for node in path:
            node.isvalidated = True
    
    return validated_paths


def form_test_paths_v1(
    topology: Dict[int, List[SimNode]],
) -> Tuple[List[Tuple[List[SimNode], SimNode]], List[Tuple[List[SimNode], SimNode]]]:
    """
    Form test paths for NMv1.
    Args: 
        topology: layer -> a list of nodes on that layer
    Return:
        mix_test_paths: [(test path, the test mixnode on that path)], 
        gw_test_paths: [(test path, the test gateway on that path)]
    """
    
    validated_paths = get_validated_paths(topology)
    mix_test_paths = []
    gw_test_paths = []
    
    gateways = topology[0] + topology[4]
    mixnodes = topology[1] + topology[2] + topology[3]
    
    # randomly assign mixnodes to a layer just for testing
    for node in mixnodes:
        node.test_layer = np.random.choice([1,2,3])
    
    for v_path in validated_paths:
        
        for mix in mixnodes:
            test_mixp = [v_path[0], v_path[1], v_path[2], v_path[3], v_path[4]]
            test_mixp[mix.test_layer] = mix #switch one node from validated path with a test node
            mix_test_paths.extend([(test_mixp, mix)] * 3)
            
        for gw in gateways:
            test_gwp = [gw, v_path[1], v_path[2], v_path[3], gw]
            gw_test_paths.extend([(test_gwp, gw)] * 3)    
    
    return mix_test_paths, gw_test_paths


def strategy(path: List[SimNode], test_node: SimNode) -> None:
    """
    V1 Dropping strategy.
    Args:
        path: [gw, mix1, mix2, mix3, gw]
        test_node: the test node on that path
    """
    path_complete = True 
    for i, node in enumerate(path):
        
        if (node.isvalidated) and (node.type == 'B'):
            
            prev_is_BA = (i > 0 and (path[i-1].type == 'A' or path[i-1].type == 'B') )
            next_is_BA = (i < len(path) - 1 and (path[i+1].type == 'A' or path[i+1].type == 'B'))
            if prev_is_BA or next_is_BA:
                path_complete = True
                break
            else:
                path_complete = False
    
    if path_complete:
        test_node.complete += 1 
    else:
        test_node.incomplete += 1


def drop_v1(topology: Dict[int, List[SimNode]]) -> None:
    """
    Dropping for NMv1 for a 15 minutes round.
    Args:
        topology: layer -> a list of nodes on that layer
    """
    
    mix_test_paths, gw_test_paths = form_test_paths_v1(topology)

    for path, test_node in mix_test_paths:
        strategy(path, test_node)
    
    for path, test_node in gw_test_paths:
        strategy(path, test_node)
