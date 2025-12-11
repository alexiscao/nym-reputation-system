import time
import datetime

from .SimNode import Config
from .create_nodes import create_target_nodes
from .run_sim import run_many_combo
from .test_epochs import run_epochs

def get_timestamp() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_results(mini: bool, mode: str, version: str, attack: bool) -> None:
    """
    Run simulations.
    """
    start_time = time.time()
    print(f"Program started at: {time.ctime(start_time)}")
    
    config = Config()
    base_topology = create_target_nodes()
    
    if attack:
        a_stake = config.stake_values
        
        if version == 'v1' or version == 'v3':
            b_range = config.num_nodes
            a_range = config.num_nodes
            b_stake = config.stake_values
        
        elif version == 'v2':
            b_stake = config.stake_min
            if mode == 'A***A':
                b_range = config.num_nodes
                a_range = config.num_nodes
            elif mode == 'AAAAA':
                b_range = config.num_nodes_AAAAA
                a_range = config.num_nodes_AAAAA

    else: # baseline
        b_range = [0]
        a_range = config.num_nodes_baseline
        b_stake = [0]
        a_stake = config.stake_values_baseline


    if mini: # mini experiment to run framing attack for v1 for reproducing results
        n_runs = 10 
        if attack:
            a_stake = [10**i for i in range(2, 6)]
            if version == 'v1':
                b_stake = [10**i for i in range(2, 6)]
                b_range = [10, 20, 30, 60, 70, 80, 90, 120, 130, 140]
                a_range = [10, 20, 30] 
    else:
        n_runs = 100 
             
    run_many_combo(base_topology=base_topology,
                        B_range=b_range, A_range=a_range,
                        bstake=b_stake, astake=a_stake, 
                        mode=mode, version=version, attack=attack, n_runs=n_runs)
    
    end_time = time.time()
    print(f"Program ended at: {time.ctime(end_time)}")

def epoch_test():
    start_time = time.time()
    print(f"Program started at: {time.ctime(start_time)}")
    
    base_topology = create_target_nodes()
    
    # those values are set as constants in this test
    bstake = 100
    astake = 1000
    
    run_epochs(base_topology=base_topology, B=60, A=30, bstake=bstake, astake=astake, mode='A***A', version='v1', epochs=list(range(1,25)))
    run_epochs(base_topology=base_topology, B=80, A=30, bstake=bstake, astake=astake, mode='A***A', version='v1', epochs=list(range(1,25)))
    run_epochs(base_topology=base_topology, B=100, A=30, bstake=bstake, astake=astake, mode='A***A', version='v1', epochs=list(range(1,25)))
    
    end_time = time.time()
    print(f"Program ended at: {time.ctime(end_time)}")


