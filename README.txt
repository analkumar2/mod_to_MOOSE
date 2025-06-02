Translates a NEURON mod file to a python file that can be imported to MOOSE

Briefly, the kinetics is inserted into a sectin in NEURON and simulated at different voltages. The steady state inf and tau parameters of the different gates in the ion channel are recorded. The resulting curves are fitted to 2-parameter sigmoid and a 6-parameter unimodal curve. The kinetics is then written as a py file that MOOSE can parse.


USAGE:

###########################################################################################################
getkineticsfrommod_auto.py
Currently it is not able to parse many mod files

STEP1:
Run the script with the following syntax:
python3 getkineticsfrommod_auto.py <Mod kinetics> <gate powers>
for example:
python3 -i getkineticsfrommod_auto.py NEURONkinetics/K_T.mod 4,1

STEP2:
Copy the dummy_Chan.py and edit the file by replacing the 'dummy' with the ion channel name your choice. Replace the values of Power, and other parameters with the values obtained from STEP1.
############################################################################################################

################################################################################################################
getkineticsfrommod_semimanual.py

STEP 1: modify the .mod file by defining all the inf and tau parameters as RANGE parameters in the NEURON block.
For example, 
NEURON {
    SUFFIX kmb
    USEION k READ ek WRITE ik
    RANGE  gbar,ik, sh
    GLOBAL inf, tau
}
becomes
NEURON {
    SUFFIX kmb
    USEION k READ ek WRITE ik
    RANGE  gbar,ik, sh
    RANGE inf, tau
}

STEP2: compile the file. eg, 
nrnivmodl kmb.mod

STEP3:
In the getkineticsfrommod_semimanual.py file, make the following changes:
1. Replace all the soma.insert lines with your kinetics. For example, if the suffix of your kinetics of interest is kmb, add:
soma.insert('kmb')
while deleting any other soma.insert lines
2. Adjust all the vector record statements. Make sure they are refering to the currect gate variables in the mod files eg. minf_vec.record(soma(0.5).Ca_HVA._ref_mInf)
3. Adjust the plotting accordingly

STEP4:
Run the script. It will first display the kinetics curves (inf and tau). It will then show the results of the fitting procedure. In case the fits do not look good, change the restrict parameters in the script. 

STEP5:
Copy the dummy_Chan.py and edit the file by replacing the 'dummy' with the ion channel name your choice. Replace the values of Power, and other parameters with the values obtained from STEP4.
################################################################################################################

