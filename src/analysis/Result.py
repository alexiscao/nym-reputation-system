import os

from ..utils.util import load_results, get_cost, get_refundable_cost, get_non_refundable_cost

class Config:
    def __init__(self, gw, mix):
        self.paths_f_min = 0.055
        self.paths_f_max = 0.25
        self.GW_FILE = gw
        self.MIX_FILE = mix


# Result class to store all entries in the result json file into objects
class Result:
    def __init__(self, f_gw, f_mix, path_prob, B_gw, A_gw, B_mix, A_mix, B, A, bstake, astake, total_cost, refundable_cost, non_refundable_cost):
        self.f_gw = f_gw
        self.f_mix = f_mix
        self.path_prob = path_prob
        self.B_gw = B_gw
        self.A_gw = A_gw
        self.B_mix = B_mix
        self.A_mix = A_mix
        self.B = B
        self.A = A
        self.bstake = bstake
        self.astake = astake
        self.total_cost = total_cost
        self.refundable_cost = refundable_cost
        self.non_refundable_cost = non_refundable_cost
    
    @classmethod
    def from_file(cls, filename):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        data_path = os.path.join(base_dir, 'sim_data', filename)
        results_loaded = load_results(data_path)
        
        results = []
        for entry in results_loaded:
            obj = cls(
                f_gw = entry['f_gw'],
                f_mix = entry['f_mix'],
                B_gw = entry['B_gw'],
                A_gw = entry['A_gw'],
                B_mix = entry['B_mix'],
                A_mix = entry['A_mix'],
                path_prob = entry['path_prob'],
                B = entry['B'],
                A = entry['A'],
                bstake = entry['B_stake'],
                astake = entry['A_stake'],
                total_cost = get_cost(entry['B'], entry['A'], entry['B_stake'], entry['A_stake']),
                refundable_cost = get_refundable_cost(entry['B'], entry['A'], entry['B_stake'], entry['A_stake']),
                non_refundable_cost = get_non_refundable_cost(entry['B'], entry['A'], entry['B_stake'], entry['A_stake'])
            )
            results.append(obj)
        
        return results