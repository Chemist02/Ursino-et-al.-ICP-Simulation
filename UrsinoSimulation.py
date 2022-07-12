import math

# Represents the simplified intracranial pressure model proposed by Ursino et al. in 1997.
# Link to a pdf of the paper: 
# https://journals.physiology.org/doi/epdf/10.1152/jappl.1997.82.4.1256 
class UrsinoSimulation:
    # Constructs a new simulation object with given parameters. The parameters defined below represent the following 
    # abstract quantities (in order of appearance):
    # - time : current time of the simulation in seconds (s).
    # 
    # STATE VARIABLES
    # - ICP : current intracranial pressure of the system (mmHg).
    # - AC : current arterial compliance of the cerebrovascular bed (ml * mmHg^-1).
    #
    # CONSTANTS
    # - R_CSF_OUTFLOW : resistance encountered by cerebrospinal fluid just before being reabsorbed at venous sinus 
    #   pressure (mmHg * s * ml^-1).
    # - R_PROXIMAL_VENOUS : proximal venous resistance, representing the resistance of the venous cerebrovascular 
    #   bed (mmHg * s * ml^-1).
    # - R_CSF_FORMATION : resistance encountered by newly formed cerebrospinal fluid (mmHg * s * ml^-1).
    # - AC_SIGMOID_BOUND_HIGH/LOW : high/low bounds of the arterial compliance autoregulation sigmoid curve (used to 
    #   model the autoregulation of cerebral blood flow, as it is a function of AC) (ml * mmHg^-1).
    # - AC_BASAL : basal (default) arterial compliance value (ml * mmHg^-1).
    # - IC_ELASTANCE_COEFF : intracranial elastance coefficient (defined by Avezaat et al.) (ml^-1).
    # - ARTERIAL_RESIST_COEFF : coefficient representing arterial resistance, specifically corresponding to the constant
    #   values in the Hagen-Poiseullile law used for calculating the resistance of the simulated arterial cerebrovasular
    #   bed (i.e. for simulating the pressure drop across it) (mmHg^3 * s * ml^-1).
    # - AC_TIME_CONSTANT : Arterial compliance autoregulation time constant (s).
    # - CBF_BASAL : Basal (default), cerebal blood flow. (NB: In the Ursino paper this is called q_n, and is 
    #   at one point defined as basal cerebrospinal fluid, but this is a typo) (ml * s^-1).
    # - AC_AUTOREG_GAIN : Gain value multiplied by the percent change in CBF when performing CBF autoregulation 
    #   (ml * mmHg^-1 * 100% CBF change).
    #
    # The default values provided are directly from Table 1 in the paper.
    # If the high sigmoid bound is less than low sigmoid bound, throw exception.
    def __init__(self, 
                 ICP: float = 9.5,\
                 AC: float = 0.15,\
                 R_CSF_OUTFLOW: float = 526.3,\
                 R_PROXIMAL_VENOUS: float = 1.24,\
                 R_CSF_FORMATION: float = 2.38e3,\
                 AC_SIGMOID_BOUND_HIGH: float = 0.75,\
                 AC_SIGMOID_BOUND_LOW: float = 0.075,\
                 IC_ELASTANCE_COEFF: float = 0.11,\
                 ARTERIAL_RESIST_COEFF: float = 4.91e4,\
                 AC_TIME_CONSTANT: float = 20.0,\
                 CBF_BASAL: float = 12.5,\
                 AC_AUTOREG_GAIN: float = 1.5\
                ):
        # Current time of the simulation in seconds (starts at 0.0s).
        self.time = 0.0

        # Set up state variables.
        # Intracranial pressure.
        self.ICP = ICP
        # Arterial compliance.
        self.AC = AC

        # Set up constant values.
        # Cerebrospinal fluid outflow resistance.
        self.R_CSF_OUTFLOW = R_CSF_OUTFLOW
        # Proximal venous resistance.
        self.R_PROXIMAL_VENOUS = R_PROXIMAL_VENOUS
        # Cerebrospinal fluid formation resistance.
        self.R_CSF_FORMATION = R_CSF_FORMATION

        # Upper and lower bounds of arterial compliance autoregulation sigmoid curve.
        # Ensure high bound is actually the high bound.
        if (AC_SIGMOID_BOUND_HIGH < AC_SIGMOID_BOUND_LOW):
            raise Exception("ERROR: High autoregulation sigmoid bound is less than the low bound!")
        # If it is, we're good.
        self.AC_SIGMOID_BOUND_HIGH = AC_SIGMOID_BOUND_HIGH
        self.AC_SIGMOID_BOUND_LOW = AC_SIGMOID_BOUND_LOW

        # Basal arterial compliance.
        self.AC_BASAL = AC
        # Intracranial elastance coefficient (defined by Avezaat et al.)
        self.IC_ELASTANCE_COEFF = IC_ELASTANCE_COEFF
        # Arterial resistance proportionality coefficient.
        self.ARTERIAL_RESIST_COEFF = ARTERIAL_RESIST_COEFF
        # Arterial compliance autoregulation time constant.
        self.AC_TIME_CONSTANT = AC_TIME_CONSTANT
        # Basal cerebral blood flow.
        self.CBF_BASAL = CBF_BASAL
        # Arterial compliance autoregulation gain.
        self.AC_AUTOREG_GAIN = AC_AUTOREG_GAIN

    # Returns the amount of time that has been simulated by this object (i.e. the amount of time the simulation has run
    # from the persective of the simulated world).
    def getTime(self):
        return self.time

    # Returns the current value of the intracranial pressure.
    def getICP(self):
        return self.ICP

    # Returns the current value of the arterial compliance of the cerebrovascular bed.
    def getArterialCompliance(self):
        return self.AC

    # Calculate and return blood volume of the arterial cerebrovascular bed 
    # volume = arterial compliance * (systemic arterial pressure - intracranial pressure).
    def getArterialBloodVolume(self, arterialPressure: float):
        return self.AC * (arterialPressure - self.ICP)

    # Calculate and return the resistance of the arterial cerebrovascular using a variation of the Hagen-Poiseuille law.
    # resistance = (arterial resistance coefficient * basal arterial compliance^2) / arterial blood volume^2
    def getArterialResistance(self, arterialBloodVolume: float):
        return (self.ARTERIAL_RESIST_COEFF * (self.AC_BASAL**2)) / (arterialBloodVolume**2)

    # Calculate and return the cerebrovascular bed capillary pressure (NB: either of the below two equations work, 
    # but the first one negects pressure due to cerebrospinal fluid formation, assuming is it insignificant compared 
    # to CBF while the second one does not. Only one of them is needed and the other is commented out, but I've decided 
    # to include both for curiosity's sake. For the record, the authors recommend the simplifed one and didn't even
    # bother to include the complete one in Appendix B).
    def getCapillaryPressure(self, arterialPressure: float, arterialResistance: float):
        # SIMPLIFIED VERSION
        return ((arterialPressure * self.R_PROXIMAL_VENOUS) + (self.ICP * arterialResistance)) / \
                (self.R_PROXIMAL_VENOUS + arterialResistance)
        # UNABRIDGED VERSION
        # return ((self.ICP * self.R_PROXIMAL_VENOUS * arterialResistance) + \
        #         (self.ICP * self.R_CSF_FORMATION * arterialResistance) + \
        #         (self.R_CSF_FORMATION * self.R_PROXIMAL_VENOUS * arterialPressure)) / \
        #        ((arterialResistance * self.R_PROXIMAL_VENOUS) + \
        #         (arterialResistance * self.R_CSF_FORMATION) + \
        #         (self.R_PROXIMAL_VENOUS * self.R_CSF_FORMATION))

    # Calculate and return the value of the cerebral blood flow using an electrical analogue (via Ohm's law; flows are
    # analogous to currents, pressures to voltages, and "resitance of a tube" to electrical resistance).
    def getCBF(self, arterialPressure: float, capillaryPressure: float, arterialResistance: float):
        return (arterialPressure - capillaryPressure) / arterialResistance

    # Calculate and return the numerical derivative of arterial compliance given the current cerebral blood flow.
    def getArterialComplianceDelta(self, currentCBF: float):
        # Noramlize CBF relative to basal CBF value.
        normalizedCBF = (currentCBF - self.CBF_BASAL) / self.CBF_BASAL

        # Compute value of sigmoid function used to model the AC autoregulation process.
        # Determine the amplitude of the sigmoid and value of sigmoid slope constant depending on noralized CBF value.
        centralSigmoidValue = 0.0
        if (normalizedCBF < 0.0):
            centralSigmoidValue = self.AC_SIGMOID_BOUND_HIGH
        elif (normalizedCBF > 0.0):
            centralSigmoidValue = self.AC_SIGMOID_BOUND_LOW

        # The only other case is equals by the trichotmy axiom, and the amplitude doesn't matter there
        # (the resulting sigmoid will be continuous on the CBF domain regardless).

        sigmoidSlopeConstant = centralSigmoidValue / 4.0
        eToPower = math.e**((self.AC_AUTOREG_GAIN * normalizedCBF) / sigmoidSlopeConstant)
        sigma = ((self.AC_BASAL + (centralSigmoidValue / 2.0)) + \
                 ((self.AC_BASAL - (centralSigmoidValue / 2.0)) * eToPower)) / \
                (1 + eToPower)

        # Return final approximate change in arterial compliance per infinitesmal unit time.
        return (sigma - self.AC) / self.AC_TIME_CONSTANT
    
    # Calculate and return the numerical derivative of ICP given all other system parameters (defined elsewhere).
    def getICPDelta(self, arterialPressure: float, arterialPressureDelta: float, ACDelta: float, \
                    capillaryPressure: float, venousSinusPressure: float, CSFInjectRate: float):
        return ((self.IC_ELASTANCE_COEFF * self.ICP) / (1 + self.AC * self.IC_ELASTANCE_COEFF * self.ICP)) * \
               ( self.AC * arterialPressureDelta + ACDelta * (arterialPressure - self.ICP) + \
                (capillaryPressure - self.ICP) / self.R_CSF_FORMATION - \
                (self.ICP - venousSinusPressure) / self.R_CSF_OUTFLOW + CSFInjectRate \
               )

    # Step the simulation forward by the specified (ideally infinitesmal) timestep, given instantaneous systemic 
    # arterial pressure (mmHg), the time derivative of arterial pressure (arterialPressureDelta; mmHg / s), the venous 
    # simus pressure (mmHg), and mock CSF injection rate (if positive) or CSF removal rate (if negative) 
    # (CSFInjectRate; ml / s).
    # *** Please see Appendix B of the paper for more details. ***
    def stepSimulation(self, timestep: float, arterialPressure: float, arterialPressureDelta: float, \
                       venousSinusPressure: float, CSFInjectRate: float):
        # Calculate blood volume of the arterial cerebrovascular bed.
        arterialBloodVolume = self.getArterialBloodVolume(arterialPressure)

        # Calculate resistance of the arterial cerebrovascular bed to account for the pressure drop of the fluid 
        # moving across it.
        arterialResistance = self.getArterialResistance(arterialBloodVolume)

        # Calculate cerebrovascular bed capillary pressure.
        capillaryPressure = self.getCapillaryPressure(arterialPressure, arterialResistance)

        # Calculate the current cerebral blood flow.
        CBF = self.getCBF(arterialPressure, capillaryPressure, arterialResistance)
        
        # Calculate the numerical derivative of arterial compliance given the current cerebral blood flow.
        ACDelta = self.getArterialComplianceDelta(CBF)
  
        # Calculate and return the numerical derivative of ICP.
        ICPDelta = self.getICPDelta(arterialPressure, arterialPressureDelta, ACDelta, capillaryPressure, \
                   venousSinusPressure, CSFInjectRate)

        # Actually update the state variables using their corresponding derivatives and the specified timestep.
        self.ICP += ICPDelta * timestep
        self.AC += ACDelta * timestep

        #Increment time by timestep.
        self.time += timestep

# Test code (also avilible in the Example.py file).
if (__name__ == "__main__"):
    # Use matplotlib to create plot.
    import matplotlib.pyplot as plt

    # Create simulation object; these paraemetrs were shown in the original model to result in self-sustained 
    # oscillations resembling Lundberg A waves.
    simulation = UrsinoSimulation(R_CSF_OUTFLOW=6.32e3, IC_ELASTANCE_COEFF=0.23)
    # Create lists to store ICP measurements and the time of each measurement for later plotting.
    times = []
    ICPReadings = []

    # How many seconds does the simulation move forward each iteration.
    timestep = 0.01
    while (simulation.getTime() < 2000.0):
        times.append(simulation.getTime())
        ICPReadings.append(simulation.getICP())

        # Constant arterial pressure, venous sinus pressure, and a cerebrospinal fluid injection/removal rate of zero ml/s.
        simulation.stepSimulation(timestep=timestep, arterialPressure=100.0, arterialPressureDelta=0.0, \
                                  venousSinusPressure=6.0, CSFInjectRate=0.0)

    # Construct plot and display.
    figure, axes = plt.subplots()
    axes.set_xlabel("Time (s)")
    axes.set_ylabel("ICP (mmHg)")
    axes.plot(times, ICPReadings)
    plt.show()
