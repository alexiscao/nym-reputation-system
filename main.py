#!/usr/bin/env python3
import argparse
import papermill as pm

from src.simulation.get_results import get_results, epoch_test
from src.analysis.get_analysis import get_analysis

def main():
    parser = argparse.ArgumentParser(description="Run simulations and analysis")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # subcommand 1 get_results
    p_results = subparsers.add_parser("get_results", help="Run simulations and save results to file") 
    p_results.add_argument("mode", choices=["A***A", "AAAAA"], help="Choose modes")        
    p_results.add_argument("version", choices=["v1", "v2", "v3"], help="Choose versions")  
    p_results.add_argument("--attack", action=argparse.BooleanOptionalAction, default=False,
                           help="Choose: --attack or --no-attack")   
    p_results.add_argument("--mini", action="store_true", default=False, help="Choose scale of simulations")    
    
    # subcommand 2 get_epochs
    p_epochs = subparsers.add_parser("get_epochs", help="Run simulations and store each epoch's results to file")  
    
    # subcommand 3 get_analysis
    p_analysis = subparsers.add_parser("get_analysis", help="Run analysis")
    p_analysis.add_argument("analysis", choices=["average", "path_prob", "cost", "table", "epoch"], 
                            help="Choose which analysis to run")
    p_analysis.add_argument("--test", action="store_true", default=False, help="Use own test data")

    args = parser.parse_args()
    if args.command == "get_results":
        get_results(args.mini, args.mode, args.version, args.attack)
   
    elif args.command == 'get_epochs':
        epoch_test()
        
    elif args.command == "get_analysis":
        if args.analysis == 'path_prob':
            pm.execute_notebook("src/analysis/path_prob.ipynb", "src/analysis/path_prob.ipynb", parameters={"test": args.test}, kernel_name="python3")
        if args.analysis == 'cost':
            pm.execute_notebook("src/analysis/cost.ipynb", 'src/analysis/cost.ipynb', kernel_name="python3")
        if args.analysis == 'table':
            pm.execute_notebook("src/analysis/table.ipynb", "src/analysis/table.ipynb", parameters={"test": args.test}, kernel_name="python3")
        if args.analysis == 'epoch':
            pm.execute_notebook("src/analysis/epoch.ipynb", "src/analysis/epoch.ipynb", parameters={"test": args.test}, kernel_name="python3")
        
if __name__ == "__main__":
    main() 