from typing import List, Optional

class Config:
    """Nym network and simulation parameters."""
    
    def __init__(self) -> None:
        
        #====== constant values set by Nym as of June, 2025 ======#
        self.total_layers = 5 # total number of layers
        self.mixnodes_layers = 3 # number of layers for mixnodes
        self.total_active_set = 240 # total number of nodes in the active set
        self.mixnodes_per_layer = 40 # number of mixnodes in each layer
        self.entry_gws = 50 # number of active set entry gateways
        self.exit_gws = 70 # number of active set exit gateways
        self.stake_saturation = 1_034_081 # stake saturation amount in NYM 
        self.stake_min = [100] # minimum stake amount required to run a node in NYM 
        self.num_validated_paths = 3 # num of validated_paths that all other nodes uses to form test paths in NMv1
        
        #====== custom values to test different attack settings ======#
        self.epochs = 24 # duration of attack
        
        # settings for baseline attack
        self.stake_values_baseline = [10**i for i in range(3, 7)]
        self.num_nodes_baseline = list(range(100, 10001, 50))
        
        # settings for staking attack
        self.stake_values = [10**i for i in range(2, 7)]
        self.num_nodes = list(range(10, 201, 10))
        self.num_nodes_AAAAA = list(range(10, 301, 10))
        
        
class SimNode:
    """Simulation node"""
    
    def __init__(
        self, 
        role: str, 
        layer: int, 
        type: str, 
        complete: float, 
        incomplete: float, 
        fail: int, 
        uptime: float, 
        score_hist: List[Optional[float]], 
        stake: float, 
        isactive: bool, 
        isvalidated: bool, 
        test_layer: int,
    ) -> None:
        self.role = role # mixnode or gateway
        self.layer = int(layer) # layer
        self.type = type # sacrifice nodes (B), or attacking nodes (A), or honest target nodes (T)
        
        self.complete = float(complete) # a test packet successfully returned to NM
        self.incomplete = float(incomplete) # a test packet didn't return to NM
        self.fail = int(fail) # a node's consecutive test packet fails
        
        self.uptime = float(uptime) # the uptime: average of previous 24 epochs
        self.score_hist = list(score_hist) # previous 24 epochs testing history
        
        self.stake = float(stake) # a node's stake (includes both initial self bond and delegated stake)
        self.select_prob = 0.0 # a node's active set selection probability
        
        self.isactive = bool(isactive) # if a node is in the active set
        
        # for NMv1
        self.isvalidated = bool(isvalidated) # if a node is being selected on the validated path
        self.test_layer = int(test_layer) # the layer a node is on for a test packet
    
    def active_set_select_prob(self) -> None:
        """
        Assign a node's active set selection probability 
        based on stake and performance score.
        """
        config = Config()
        stake_pct = min(self.stake / config.stake_saturation, 1.0)
        prob = (self.uptime ** 20) * stake_pct
        self.select_prob = prob
    
    def average_uptime_24(self, new_score: float) -> None:
        """
        Update a node's 24-epoch-averaged performance score.
        """
        self.score_hist.pop()  
        self.score_hist.insert(0, new_score)
        vals = [v for v in self.score_hist if v is not None]
        self.uptime = sum(vals) / len(vals)
        