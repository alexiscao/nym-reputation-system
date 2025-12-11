import os
import pandas as pd
import numpy as np
import copy
from typing import Dict, List

from .SimNode import SimNode


def create_target_nodes() -> Dict[int, List[SimNode]]:
    """
    Create target nodes to mirror all exisiting nodes in Nym.
    Returns:
        topology: mapping of layer index to a list of nodes on that index.
    """
    topology: Dict[int, List[SimNode]] = {0: [], 1: [], 2: [], 3: [], 4: []}
    
    # get the file representing one snapshot of the Nym network 
    # to create a topology of nodes mirroring that snapshot.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, '..', '..', 'node_data', 'all_nodes.csv')
    df = pd.read_csv(data_path)

    for _, row in df.iterrows():
        if row['declared_role'] == 'mixnode':
            role = 'mixnode'
            layer = np.random.choice([1, 2, 3])
        else:
            role = 'gateway'
            layer = np.random.choice([0, 4], p=[0.4, 0.6])

        T_node = SimNode(
            role = role,
            layer = layer,
            type = 'T',
            complete = 0,
            incomplete = 0,
            fail = 0,
            uptime = row['uptime'],
            score_hist = [row['uptime'] for _ in range(24 * 4)],
            stake = row['total_stake'] / 1_000_000, # Nym Explorer shows stake amount in actual stake * 1_000_000 format. 
            isactive = False,
            isvalidated = False,
            test_layer = 0 
        )
        topology[layer].append(T_node)
    
    return topology


def create_B_A_nodes(
    base_topology: Dict[int, List[SimNode]], 
    B: int, 
    A: int, 
    bstake: float, 
    astake: float, 
    mode: str, 
    version: str,
) -> Dict[int, List[SimNode]]:
    """
    Create 2 sets of attacker controlled nodes: B, A 
    Args:
        base_topology: layer --> list of Node objects on each layer
        B: number of bad nodes
        A: number of attacking nodes
        bstake: stake for each B node
        astake: stake for each A node
        mode: A***A or AAAAA
        version: network monitor v1, or v2, or v3
    Returns:
        topology: updated topology with B, A nodes added. 
    """   
    
    topology = copy.deepcopy(base_topology)
    
    # create B nodes (always take on the role of mixnodes)
    for _ in range(B):
        role = 'mixnode'
        layer = np.random.choice([1,2,3])
        
        B_node = SimNode(
            role = role,
            layer = layer,
            type = 'B',
            complete = 0,
            incomplete = 0,
            fail = 0,
            uptime = 0.98,
            score_hist = [0.98 for _ in range(24 * 4)],
            stake = bstake,
            isactive = False,
            isvalidated = False,
            test_layer = 0 
        )
        topology[layer].append(B_node)
    
    # assign the number of A mixnodes or A gateways based on different NM versions and attack modes
    if version == 'v1': # in v1 and v3, regardless of mode, A is only gw because S can do damage to others without harming itself
        num_mix = 0
        num_gw = A
    else: # in v2 and v3
        if mode == 'A***A':
            num_mix = 0
            num_gw = A
        elif mode == 'AAAAA':
            num_mix = int(A * (3/5))
            num_gw = A - num_mix
    
    # create A mixnodes    
    for _ in range(num_mix):
        layer = np.random.choice([1,2,3])
        A_node = SimNode(
            role = 'mixnode',
            layer = layer,
            type = 'A',
            complete = 0,
            incomplete = 0,
            fail = 0,
            uptime = 0.98,
            score_hist = [0.98 for _ in range(24 * 4)],
            stake = astake,
            isactive = False,
            isvalidated = False,
            test_layer = 0 
        )
        topology[layer].append(A_node)
    
    # create A gateways
    for _ in range(num_gw):
        layer = np.random.choice([0, 4], p=[0.4, 0.6])
        A_node = SimNode(
            role = 'gateway',
            layer = layer,
            type = 'A',
            complete = 0,
            incomplete = 0,
            fail = 0,
            uptime = 0.98,
            score_hist = [0.98 for _ in range(24 * 4)],
            stake = astake,
            isactive = False,
            isvalidated = False,
            test_layer = 0 
        )
        topology[layer].append(A_node)
    
    return topology
        
        
        