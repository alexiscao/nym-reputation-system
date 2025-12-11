import json, os
from collections import defaultdict
from ..utils.util import save_results, add_then_average

def get_average_across_files(filenames, outputfile):
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    data_dir = os.path.join(project_root, "sim_data")
    
    files = []
    for fn in filenames:
        full_path = os.path.join(data_dir, fn)
        files.append(full_path)
        
    all_entries = []
    for f in files:
        with open(f, "r") as fh:
            entries = json.load(fh)  
            all_entries.extend(entries)

    averaged_results = add_then_average(all_entries)
    
    averaged_results.sort(key=lambda r: r['f_gw'])
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../"))
    data_dir = os.path.join(project_root, "sim_data")
    os.makedirs(data_dir, exist_ok=True) 
    file_path = os.path.join(data_dir, outputfile)
   
    save_results(averaged_results, file_path)
