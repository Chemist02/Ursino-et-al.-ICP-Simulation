# Ursino et al. ICP Simulation
## Introduction
This is an implementation of the intracranial pressure (ICP) dynamical system model proposed in the following paper:\
*A simple mathematical model of the interaction between intracranial pressure and cerebral hemodynamics
Mauro Ursino and Carlo Alberto Lodi
Journal of Applied Physiology 1997 82:4, 1256-1269*\
https://journals.physiology.org/doi/full/10.1152/jappl.1997.82.4.1256

It was developed for use at the University of Colorado Anschutz Medical Campus under the guidance of Tell Bennett, MD.

## Installation
Simply clone the repository or download the UrsinoSimulation.py file (it should contain everything you need). The 
Example.py file contains sample code making use of the UrsinoSimulation module (NB: this is also present at the bottom 
of UrsinoSimulation.py). UrsinoSimulation.py contains some documentation should the need arise, but more user-friendly
documentation is also included below in this document.

## Documentation
The UrsinoSimulation.py file contains a single class called, wait for it, UrsinoSimulation. To run a simulation, an
UrsinoSimulation object must be created (you can create as many as you'd like). The class itself is relatively simple, 
and contains the following functions (for more information on what everything does, I highly recommend taking a look
at the paper; especially Figure 1, Table 1, and Appendices A and B):

### \_\_init\_\_:
Constructs an UrsinoSimulation object with the given system parameters. Throws an exception if the high sigmoid bound
is less than the low sigmoid bound.\
#### Parameters (all have the default values shown below, and are therefore optional to include):
ICP: float = 9.5\
AC: float = 0.15\
R_CSF_OUTFLOW: float = 526.3\
R_PROXIMAL_VENOUS: float = 1.24\
R_CSF_FORMATION: float = 2.38e3\
AC_SIGMOID_BOUND_HIGH: float = 0.75\
AC_SIGMOID_BOUND_LOW: float = 0.075\
IC_ELASTANCE_COEFF: float = 0.11\
ARTERIAL_RESIST_COEFF: float = 4.91e4\
AC_TIME_CONSTANT: float = 20.0\
CBF_BASAL: float = 12.5\
AC_AUTOREG_GAIN: float = 1.5\
\
STATE VARIABLES\
These are quantities that define the current state of the system.
- ICP : current intracranial pressure of the system (mmHg).
- AC : current arterial compliance of the cerebrovascular bed (ml * mmHg^-1).
 
CONSTANTS\
These are constant quantities that can be used to vary the physiology/properties of the "simulated person."
- R_CSF_OUTFLOW : resistance encountered by cerebrospinal fluid just before being reabsorbed at venous sinus
  pressure (mmHg * s * ml^-1).
- R_PROXIMAL_VENOUS : proximal venous resistance, representing the resistance of the venous cerebrovascular
  bed (mmHg * s * ml^-1).
- R_CSF_FORMATION : resistance encountered by newly formed cerebrospinal fluid (mmHg * s * ml^-1).
- AC_SIGMOID_BOUND_HIGH/LOW : high/low bounds of the arterial compliance autoregulation sigmoid curve (used to
  model the autoregulation of cerebral blood flow, as it is a function of AC) (ml * mmHg^-1).
- AC_BASAL : basal (default) arterial compliance value (ml * mmHg^-1).
- IC_ELASTANCE_COEFF : intracranial elastance coefficient (defined by Avezaat et al.) (ml^-1).
- ARTERIAL_RESIST_COEFF : coefficient representing arterial resistance, specifically corresponding to the constant
  values in the Hagen-Poiseullile law used for calculating the resistance of the simulated arterial cerebrovasular
  bed (i.e. for simulating the pressure drop across it) (mmHg^3 * s * ml^-1).
- AC_TIME_CONSTANT : Arterial compliance autoregulation time constant (s).
- CBF_BASAL : Basal (default), cerebal blood flow. (NB: In the Ursino paper this is called q_n, and is
  at one point defined as basal cerebrospinal fluid, but this is a typo) (ml * s^-1).
- AC_AUTOREG_GAIN : Gain value multiplied by the percent change in CBF when performing CBF autoregulation
  (ml * mmHg^-1 * 100% CBF change)

### getTime:
Returns the current time of the simulation in seconds.

### getICP:
Returns the current value of the intracranial pressure in mmHg.

### getArterialCompliance:
Returns the current value of the arterial compliance of the cerebrovasular bed in ml * mmHg^-1 (change in volume 
per unit change in pressure).

### getArterialBloodVolume:
Calculates and returns the current volume of blood in the arterial cerebrovasular bed in ml.
#### Parameters:
arterialPressure: float
- arterialPressure : The systemic arterial pressure of the "person" we're modeling, in mmHg. This is one of the 
input parameters of the system (please see the stepSimulation function for more info on that).

### getArterialResistance:
Calculates and returns the resistance of the arterial cerebrovascular bed using a variation of the 
Hagen-Poiseuille law (resistance referring to the electrical circuit analogue of the model).
#### Parameters:
arterialBloodVolume: float
- arterialBloodVolume : Volume of blood in the arterial cerebrovascular bed in ml (please see 
  getArterialBloodVolume).

### getCapillaryPressure:
Calculates and returns the cerebrovascular bed capillary pressure in mmHg.
#### Parameters:
arterialPressure: float\
arterialResistance: float
- arterialPressure : The systemic arterial pressure of the "person" we're modeling, in mmHg. This is one of the 
  input parameters of the system (please see the stepSimulation function for more info on that).
- arterialResistance : The resistance of the arterial cerebrovascular bed in mmHg * s * ml^-1 (please see
  getArterialResistance)
   
### getCBF:
Calculates and returns the value of the cerebral blood flow using an electrical analogue (via Ohm's law; flows are
analogous to currents, pressures to voltages, and "resistance of a tube" to electrical resistance) in ml * s^-1.
#### Parameters:
arterialPressure: float\
capillaryPressure: float\
arterialResistance: float
- arterialPressure : The systemic arterial pressure of the "person" we're modeling, in mmHg. This is one of the 
  input parameters of the system (please see the stepSimulation function for more info on that).
- capillaryPressure : The cerebrovascular bed capillary pressure in mmHg (please see getCapillaryPressure).
- arterialResistance : The resistance of the arterial cerebrovascular bed in mmHg * s * ml^-1 (please see
  getArterialResistance)
   
### getArterialComplianceDelta:
Calculates and returns the numerical derivative of arterial compliance in ml * mmHg^-1 * s^-1.
#### Parameters:
currentCBF: float
- currentCBF : The value of the cerebral blood flow in ml * s^-1
 
### getICPDelta:
Calculates and returns the numerical derivative of ICP.
#### Parameters:
arterialPressure: float\
arterialPressureDelta: float\
ACDelta: float\
capillaryPressure: float\
venousSinusPressure: float\
CSFInjectRate: float
- arterialPressure : The systemic arterial pressure of the "person" we're modeling, in mmHg. This is one of the 
  input parameters of the system (please see the stepSimulation function for more info on that).
- arterialPressureDelta : The numerical derivative of the systemic arterial pressure of the "person" we're modeling, 
  in mmHg * s^-1. This is one of the input parameters of the system (please see the stepSimulation function for 
  more info on that).
- ACDelta : The numerical derivative of arterial compliance in ml * mmHg^-1 * s^-1 (please see
  getArterialComplianceDelta).
- capillaryPressure : The cerebrovascular bed capillary pressure in mmHg (please see getCapillaryPressure).
- venousSinusPressure : Pressure of the dural venous sinuses in mmHg. This is one of the input parameters of the 
  system (please see the stepSimulation function for more info on that).
- CSFInjectRate : Rate at which either mock CSF is being injected into the system (if positive) or CSF is being
  removed from the system in ml * s^-1. This is one of the input parameters of the system (please see the 
  stepSimulation function for more info on that).
   
### stepSimulation:
Step the simulation forward by the specified (ideally infinitesmal) timestep, updating the state variables along the
way (given the input parameters to the system).\
Parameters:\
timestep: float\
arterialPressure: float\
arterialPressureDelta: float\
venousSinusPressure: float\
CSFInjectRate: float
- timestep : An ideally infinitesmal amount of time (in seconds) to step the simulation forward by.
 
INPUT PARAMETERS\
These are quantities that exist outside of the dynamical system but are needed to compute what happens within it.
- arterialPressure : The systemic arterial pressure of the "person" we're modeling, in mmHg. This is one of the 
  input parameters of the system.
- arterialPressureDelta : The numerical derivative of the systemic arterial pressure of the "person" we're modeling, 
  in mmHg * s^-1. This is one of the input parameters of the system.
- venousSinusPressure : Pressure of the dural venous sinuses in mmHg. This is one of the input parameters of the 
  system.
- CSFInjectRate : Rate at which either mock CSF is being injected into the system (if positive) or CSF is being
  removed from the system in ml * s^-1. This is one of the input parameters of the system.
