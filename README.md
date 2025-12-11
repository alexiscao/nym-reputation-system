# Analysis and Attacks on the Reputation System of Nym

This repository holds the code and data for our PoPETs 2026.2 paper "Analysis and Attacks on the Reputation System of Nym".

Authors: Xinmu Alexis Cao, Matthew Green.

## Obtaining this repository and setting up the environment
To obtain the repository:
```
git clone git@github.com:alexiscao/nym-reputation-system.git
cd nym-reputation-system
```
To set up the environment:
```
sudo apt update
sudo apt install python3-pip
python3 -m pip install -r requirements.txt
```

## Overview of simulations and analysis
The repository consists of a custom-build simulator to mirror different attack strategies on Nym's network monitor (NM) and analysis code to produce figures and tables from simulation results. 
The main goal of the simulations is to analyze how baseline staking attack compares with framing attack in terms of the costs to achieve an attack objective. The analysis includes the following four main parts.
1. `path_prob`: How different fractions of the active set controlled by attackers affect the probability that an attacker will achieve the objective of an `A***A` or `*AAA*` path, after exactly one path is selected by the client (Figure 12) and how different fractions of the active set controlled by attackers affect the the number of packets (resp. connections) that a client must generate to achieve a set probability of having one `A***A` path (resp. `*AAA*` path) (Figure 13, 14).
2. `table`: For a defined attack outcome in terms of a fixed fraction of gateway active set controlled by attacker (f_gw) and fraction of mixnodes active set controlled by attacker (f_mix), what the costs, optimal nodes, and stake per node settings are to achieve `A***A`, `AAAAA` objectives using baseline staking attack, framing attack, and attack with constraints (Table 1 and Table 5).
3. `cost`: For a wide range of fractions of gateway active set controlled by attacker, what is the minimum cost to achieve each fraction, and how the costs compare with each other when launching framing attacks on different network monitor versions (NMv1, NMv2, NMv3) (Figure 2, 4).
4. `epoch`: So far, the analyses have been based on the final results after running simulations for consecutive 24 epochs. Here, we analyze how the fraction of the gateway active set controlled by attacker changes for different durations of attack (from the the first epoch to the 24th epoch) (Figure 3).

## Running simulations
Here we outline the general steps to run the **_full_** simulations on both baseline and framing attack with the entire ranges of nodes and stakes values as mentioned in the paper. We will then provide an approximate time that each simulation will take to finish. For simulations that take an extremely long time to run (24-48 hours), we describe steps on a smaller scale simulation that user can run to reproduce in results in section [Reproducing results](#reproducing-results).

In general, to run the simulation, the command has the following structure:
```
python3 main.py get_results {mode} {version} {--attack}
```
1. {mode} denotes the attack objective to run. Choices for {mode}: `'A***A'` or `AAAAA` (note that it's `'A***A'` due to the asterisks.)
2. {version} denotes the NM versions that attack strategies need to adapt to. Choices for {version}: `v1`, `v2`, or `v3`
3. {--attack} denotes whether to run framing attack or baseline staking. Choices for {--attack}: `--attack` or `--no-attack` (`--attack` runs framing attack while `--no-attack` runs baseline staking)

### Baseline staking simulations
Since the strategy of baseline attacks is independent of network monitor versions and solely relies on staking a large amount on each adversarial node and does not invovle any packet dropping strategies tailored to a specific network monitor, we set to run baseline staking on `v2`. Thus, to run simulations on baseline staking strategy for `A***A` objective:
```
python3 main.py get_results 'A***A' v2 --no-attack
```
And to run simulations on baseline staking strategy for `AAAAA` objective:
```
python3 main.py get_results AAAAA v2 --no-attack
```
Each simulation above took around 15 minutes. 

### Framing attack simulations
As an example, here we provide the commands of simulating framing attack against NMv1. Note that for NMv1, the attack setting to achieve `A***A` would achieve `AAAAA` as well considering that all the nodes dropping packets take on the role of mixnodes, and given the design choices of NMv1, mixnodes can get drop packets while minimally harm their scores so that they can be selected as the middle three nodes too as they promote additional A gateway nodes into the active set (i.e. do not need additional A mixnodes to achieve `AAAAA`). 

Thus, to simulate framing attack for NMv1, run:
```
python3 main.py get_results 'A***A' v1 --attack
```
To simulate framing attack against NMv2 or NMv3, change the version to `v2` or `v3`.
The simulation above took around 10 hours.

### Varying epochs simulations
All of the simulations so far have only considered running the attack for 24 consecutive hours. To test how different attack durations affect the fraction of active set an attacker can control, run the following:
```
python3 main.py get_epochs
```
This simulation took around an hour to finish.

## Analyzing simulation results
In general, to run the analysis on simulation results, the command has the following structure:
```
python3 main.py get_analysis {analysis}
```
{analysis} denotes the type of analysis to run. Choices: `path_prob`, `table`, `cost`, `epoch`

Running the above command will execute the corresponding Jupyter notebook, and the results are stored in the Jupyter notebook.

For example, to get the `table` results, run:
```
python3 main.py get_analysis table
```
The results will be stored in Jupyter notebook `table.ipynb`. The full path to the notebook is  `/src/analysis/table.ipynb`. (Similarly, graphs for `cost` are stored in `/src/analysis/cost.ipynb` etc.)

## Reproducing results
Considering the large amount of time that some simulations would take to finish running, first we describe three levels a user can reproduce the results. 
Level 1: able to reproduce the results by running the complete simulation (full simulation takes within an hour.)
Level 2: able to reproduce the results by running a small scale simulation on a reduced set of values and fewer simulation rounds (full simulation takes 10+ hours.)
Level 3: able to reproduce the results with provided datasets from previous simulations. In this case, the results can _only_ be reproduced by running the complete simulation that would take 24+ hours.

Here we focus on steps to reproduce the table and figures in main body of the paper (Table 1, Figure 2, 3, 4.) 

### To reproduce Table 1 results:
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

### To reproduce Figure 2 and 4: 
Since Figure 4 includes Figure 2's results, here we show steps to reproduce Figure 4's results. Note that Figure 4 includes cost required to achieve varying fractions of the gateway active set controlled by attacker, which go all the way up to near 1.0. The vast ranges of fraction that the graph shows require simulations with the complete set of nodes values instead of just a small subset. Furthermore, the graph requires simulation on v1, v2, and v3, which all together would take around 48 hours at least. Therefore, we use existing simulation data to reproduce the figure (Level 3.)

To reproduce Figure 4, run:
```
python3 main.py get_analysis cost
```
Running this command executes the Jupyter notebook which will output the corresponding graphs. Path: `/src/analysis/cost.ipynb`

### To reproduce Figure 3:
1. Run the full simulation that records fraction of the gateway active set at different epochs durations (Level 1.)
```
python3 main.py get_epochs
```
2. Get Figure 3 using fresh simulation results by passing an additional flag `--test`
```
python3 main.py get_epochs --test
```
Result graphs are stored in `/src/analysis/epoch.ipynb`.

### To reproduce Figure 12, 13, 14 (Appendix H)
1. Get analysis using fresh baseline staking simulation output from reproducing Table 1 results.
```
python3 main.py get_analysis path_prob --test
```
Result graphs are stored in `/src/analysis/path_prob.ipynb`
