from .average import get_average_across_files
from .min_cost import min_cost_compare
from .path_prob import plot_f_to_path_probs, plot_n_required_for_half_prob_path
from .epochs import epochs_graph
from .table import table
from .Result import Config
from matplotlib import rcParams
rcParams['font.family'] = 'serif' 

    
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
        # OVERALL COSTS COMPARISONS FOR ATTACKS
        min_cost_compare(f_max=0.9, round_num=1,
                        files=[
                            'v2_A***A_False.json', 
                            'v1_A***A_True.json', 
                            'v2_A***A_True.json', 
                            'v3_A***A_True.json'
                            ],
                        
                        labels=[
                            'Baseline Attack for A***A', 
                            'Performance Scoring Attack for A***A in NMv1', 
                            'Performance Scoring Attack for A***A in NMv2', 
                            'Performance Scoring Attack for A***A in NMv3'
                            ])
    
    elif analysis == 'table':        
        # TABLE reproducing results in main body
        print("======================== NMv1 ========================")
        if test:
            table(dropfile1='v1_A***A_True_10.json', dropfile2='v1_A***A_True_10.json', config=config)
        else:  
            table(dropfile1='v1_A***A_True.json', dropfile2='v1_A***A_True.json', config=config)
        
        print()
        print("======================== NMv2 ========================")
        table(dropfile1='v2_A***A_True.json', dropfile2='v2_AAAAA_True.json', config=config)
        
        print()
        print("======================== NMv3 ========================")
        table(dropfile1='v3_A***A_True.json', dropfile2='v3_AAAAA_True.json', config=config)
    

def get_analysis_epochs(test):    
    A=30
    if test:
        epochs_graph(f'60_{A}_1000_test.json', f'80_{A}_1000_test.json', f'100_{A}_1000_test.json')
    else:
        epochs_graph(f'60_{A}_1000.json', f'80_{A}_1000.json', f'100_{A}_1000.json')