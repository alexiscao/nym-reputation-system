# Artifact Appendix (Required for all badges)

Paper title: **Analysis and Attacks on the Reputation System of Nym**

Requested Badge(s):
  - [x] **Available**
  - [x] **Functional**
  - [x] **Reproduced**

## Description
1. Paper "Analysis and Attacks on the Reputation System of Nym" by Xinmu Alexis Cao and Matthew Green. 
2. The repository consists of a custom-build simulator to mirror different attack strategies on Nym's network monitor (NM) and analysis code to produce figures and tables from simulation results. The main goal of the simulations is to analyze how baseline staking attack compares with framing attack in terms of the costs to achieve an attack objective.

### Security/Privacy Issues and Ethical Concerns
This artifact does not hold security or privacy risks for the machine of the person trying to evaluate or reuse the artifact. The artifact does not run any vulnerable code, and it does not include anonymized transcripts or survey responses. 

## Basic Requirements
For both sections below, if you are giving reviewers remote access to special
hardware (e.g., Intel SGX v2.0) or proprietary software (e.g., Matlab R2025a)
for the purpose of the artifact evaluation, do not provide these instructions
here but rather in the corresponding submission field on HotCRP.

### Hardware Requirements
1. Minimal hardware requirements: can run on a laptop. (However, since the simulations have many iterations and are set to run in parallel, higher CPU cores would reduce the runtime significantly.)
2. The simulations in the artifact were run on a Linux server with 48 CPU cores and 384GB RAM.

### Software Requirements
1. OS: the authors used Rocky Linux 9 and MacOS Sequoia for running the code in this artifact. (Note that the difference in detail between the OSes listed is not reflective of a difference in the specificity of actual requirements. The artifact is compatible with general Linux distributions.)
2. OS packages: python3-pip
3. Artifact packaging: NA
4. Programming language compiler: Python 3.11.1
5. Packages: see requirements.txt
6. Machine Learning Models: NA
7. Datasets: contained in artifact. See path `/sim_data` and `/node_data`

### Estimated Time and Storage Consumption
- The overall human and compute times required to run the artifact: the simulation accounts for the majority of the artifact’s runtime. Full simulation took around 48 hours on a shared-access Rocky Linux 9 server with 48 CPU cores and 384GB RAM. (Note that all simulations are run in parallel with multiprocessing so the runtime depends on the number of available CPU cores.)
- The overall disk space consumed by the artifact: 32.4 MB

## Environment

### Accessibility
To obtain the repository:
```
git clone https://github.com/alexiscao/nym-reputation-system.git
cd nym-reputation-system
```

### Set up the environment 
To set up the environment: users can either install dependencies directly on their host system or build the code using the provided Dockerfile.
1. Option 1: run the following commands to install the dependencies directly.
```
sudo apt update
sudo apt install python3-pip
python3 -m pip install -r requirements.txt
```
Expected results would return "Requirement already satisfied" or "Successfully installed..."

2. Option 2: build the code with Dockerfile. First, to install Docker, please follow the official Docker guides for [macOS](https://docs.docker.com/desktop/setup/install/mac-install/), [Windows](https://docs.docker.com/desktop/setup/install/windows-install/), or [Linux](https://docs.docker.com/desktop/setup/install/linux/).
Next, run the following commands to build the Docker image and start the Docker container. 
```
docker build -t nym-reputation-system .
docker run -it --rm nym-reputation-system
```
Expected results would return shell prompt such as `user@d6072ce1cd69:/nym-reputation-system#`. Users can then follow the instructions and commands in the rest of this file to test the artifact.

### Testing the Environment
```
python3 - << 'EOF'
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy
import tqdm
import papermill
import ipykernel
import jupyterlab
print("All packages imported successfully.")
EOF
```
Expected output:
```
All packages imported successfully.
```

## Artifact Evaluation

(Note: README.md offers explanations on reproducing results as well.)

### Main Results and Claims

#### Main Result 1: attack costs for a defined/single attack outcome
`table`: For a defined attack outcome in terms of a fixed fraction of gateway active set controlled by attacker (f_gw) and fraction of mixnodes active set controlled by attacker (f_mix), we show the costs, optimal nodes, and stake per node settings are to achieve `A***A`, `AAAAA` objectives using baseline staking attack, framing attack, and attack with constraints (Table 1).

#### Main Result 2: attack costs for a wide range of attack outcomes
`cost`: For a wide range of fractions of gateway active set controlled by attacker, we show the minimum cost to achieve each fraction, and how the costs compare with each other when launching framing attacks on different network monitor versions (NMv1, NMv2, NMv3) (Figure 2, 4).

### Main Result 3: fractions of active set controlled by attacker at different epochs
`epoch`: So far, the analyses have been based on the final results after running simulations for consecutive 24 epochs. Here, we analyze how the fraction of the gateway active set controlled by attacker changes for different durations of attack (from the the first epoch to the 24th epoch) (Figure 3).

### Experiments
Considering the large amount of time that some simulations would take to finish running, first we describe three levels a user can reproduce the results. 
* Level 1: able to reproduce the results by running the complete simulation (full simulation takes within an hour.)
* Level 2: able to reproduce the results by running a small scale simulation on a reduced set of values and fewer simulation rounds (full simulation takes 10+ hours.)
* Level 3: able to reproduce the results with provided datasets from previous simulations. In this case, the results can _only_ be reproduced by running the complete simulation that would take 24+ hours.

#### Experiment 1: reproduce Table 1
- Time: 1 human-minute + around 1 computer-hour

This experiment returns the attack costs and optimal attack parameters for a defined/single attack outcome.

1. Run full baseline staking simulations (Level 1.)
```
python3 main.py get_results 'A***A' v2 --no-attack
python3 main.py get_results AAAAA v2 --no-attack
```
  Each will take around 10 to 15 minutes.

2. Run smaller scale framing attack simulations on NMv1 by passing an additional flag `--mini` in the end  (Level 2.)
```
python3 main.py get_results 'A***A' v1 --attack --mini
```
  This will take around 20 minutes. 

3. Get table results by passing an additional flag `--test` to indicate that the analysis is using fresh simulation outputs (without additional flag, analysis relies on provided datasets from previous simulations.)
```
python3 main.py get_analysis table --test
```
Result table is stored in `/src/analysis/table.ipynb`.

#### Experiment 2: reproduce Figure 2 and 4:
- Time: 1 human-minute + around 1 computer-minute

This experiment returns the attack costs corresponding to a wide range of fractions of the gateway active set controlled by an attacker. 

Since Figure 4 includes Figure 2's results, here we show steps to reproduce Figure 4's results. Note that Figure 4 includes cost required to achieve varying fractions of the gateway active set controlled by attacker, which go all the way up to near 1.0. The vast ranges of fraction that the graph shows require simulations with the complete set of nodes values instead of just a small subset. Furthermore, the graph requires simulation on v1, v2, and v3, which all together would take around 48 hours at least. Therefore, we use existing simulation data to reproduce the figure (Level 3.)

To reproduce Figure 4, run:
```
python3 main.py get_analysis cost
```
Running this command executes the Jupyter notebook which will output the corresponding graphs. Path: `/src/analysis/cost.ipynb`

#### Experiment 3: reproduce Figure 3.
- Time: 1 human-minute + around 1 computer-hour
  
1. Run the full simulation that records fraction of the gateway active set at different epochs durations (Level 1.)
```
python3 main.py get_epochs
```
2. Get Figure 3 using fresh simulation results by passing an additional flag `--test`
```
python3 main.py analysis epoch --test
```
Result graphs are stored in `/src/analysis/epoch.ipynb`.

#### Experiment 4: reproduce Figure 12, 13, 14.
- Time: 1 human-minute + around 20 computer-minutes

Note that Figure 12, 13, and 14 show the relationships among fractions of gateway/mixnode active set controlled by attacker, number of reconnections/packets sent by a victim client, and the success probability of having one connection or packet routed through an adversarial path. These results are independent of attack strategies and network monitor versions.

Get analysis using fresh baseline staking simulation outputs from the step reproducing Table 1 results (Level 1.) 
```
python3 main.py get_analysis path_prob --test
```
Result graphs are stored in `/src/analysis/path_prob.ipynb`.


## Limitations 
All results are reproducable using the provided datasets from our previous simulations.
However, if user would like obtain fresh simulation results and perform analysis on such results, required simulation time would differ for different analysis goals. For instance, simulations on baseline staking would take a reasonable amount of time that users can obtain the full results. To reproduce Table 1 result with simulations that take a short amoutn of time, we choose a smaller range of node values to test and we set the simulation to get the average of running 10 times instead of 100 times. Since there's lots of randomness invovled and we only test the node amount by 10 interval (i.e. 10, 20, 30 nodes etc.), the freshly produced simulation results may differ slightly from previous simulation results while the general trend in data remain the same. We further explained some limitations in "Experiment 2: reproduce Figure 2 and 4".

## Notes on Reusability
This artifact can be a general use simulator for simulating Nym's network monitor that 1) it takes in the nodes data of a snapshot of the Nym network and simulate all the existing nodes, and 2) it simulates three versions of network monitor which other researchers can use to explore different attack strategies on these versions of network monitor in a safe manner without disrupting live Nym network.
