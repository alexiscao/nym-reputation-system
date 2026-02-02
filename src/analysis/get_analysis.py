from typing import Iterable
from pathlib import Path
from .average import get_average_across_files
from .min_cost import min_cost_compare
from .path_prob import plot_f_to_path_probs, plot_n_required_for_half_prob_path
from .epochs import epochs_graph
from .table import table
from .Result import Config
from matplotlib import rcParams
rcParams['font.family'] = 'serif' 

def require_files(files: Iterable[str]):
    root = Path.cwd()
    missing = []
    for f in files:
        if not (root / "sim_data" / f).is_file():
            missing.append(f) 
    if missing:
        raise FileNotFoundError(
            "Required result file(s) not found:\n"
            + "\n".join(f"  - {f}" for f in missing)
            + "\nPlease run full simulations to generate the missing files."
        )
            
def get_analysis(test, analysis):
    
    if test:
        gw_file = 'v2_A***A_False_100.json'
        mix_file = 'v2_AAAAA_False_100.json'
    else: # use existing results
        gw_file = 'v2_A***A_False.json'
        mix_file = 'v2_AAAAA_False.json'
    
    config = Config(gw_file, mix_file)
     
    if analysis == 'average':
        get_average_across_files(filenames=[
            '',
        ], outputfile='')
    
    elif analysis == 'path_prob':
        # F_A AND PATH PROBS, independent of dropping. USE THE NO DROPPING DATA.
            
        plot_f_to_path_probs(f_max=0.20, config=config)
        plot_n_required_for_half_prob_path(type="A***A", config=config)
        plot_n_required_for_half_prob_path(type="*AAA*", config=config)
        
    elif analysis == 'cost':
        if test:
            files = [
                'v2_A***A_False_100.json',
                'v1_A***A_True_100.json',
                'v2_A***A_True_100.json',
                'v3_A***A_True_100.json']
        else:
            files = [
                'v2_A***A_False.json', 
                'v1_A***A_True.json', 
                'v2_A***A_True.json', 
                'v3_A***A_True.json']
            
        # OVERALL COSTS COMPARISONS FOR ATTACKS
        try:
            require_files(files)
            min_cost_compare(f_max=0.9, round_num=1,
                        files=files,
                        
                        labels=[
                            'Baseline Attack for A***A', 
                            'Performance Scoring Attack for A***A in NMv1', 
                            'Performance Scoring Attack for A***A in NMv2', 
                            'Performance Scoring Attack for A***A in NMv3'
                            ])
        except FileNotFoundError as e:
            print(e)   
    
    elif analysis == 'table':        
        # TABLE reproducing results in main body
        print("======================== NMv1 ========================")
        if test:
            try:
                require_files(files=['v1_A***A_True_100.json', 'v1_A***A_True_100.json'])
                table(dropfile1='v1_A***A_True_100.json', dropfile2='v1_A***A_True_100.json', config=config)
            except FileNotFoundError as e:
                print(e)
        else:  
            table(dropfile1='v1_A***A_True.json', dropfile2='v1_A***A_True.json', config=config)

        print()
        print("======================== NMv2 ========================")
        if test:
            try:
                require_files(files=['v2_A***A_True_100.json', 'v2_AAAAA_True_100.json'])
                table(dropfile1='v2_A***A_True_100.json', dropfile2='v2_AAAAA_True_100.json', config=config)
            except FileNotFoundError as e:
                print(e)
        else:
            table(dropfile1='v2_A***A_True.json', dropfile2='v2_AAAAA_True.json', config=config)

        print()
        print("======================== NMv3 ========================")
        if test:
            try:
                require_files(files=['v3_A***A_True_100.json', 'v3_AAAAA_True_100.json'])
                table(dropfile1='v3_A***A_True_100.json', dropfile2='v3_AAAAA_True_100.json', config=config)
            except FileNotFoundError as e:
                print(e)
        else:
            table(dropfile1='v3_A***A_True.json', dropfile2='v3_AAAAA_True.json', config=config)
    

def get_analysis_epochs(test):    
    A=30
    if test:
        epochs_graph(f'60_{A}_1000_test.json', f'80_{A}_1000_test.json', f'100_{A}_1000_test.json')
    else:
        epochs_graph(f'60_{A}_1000.json', f'80_{A}_1000.json', f'100_{A}_1000.json')