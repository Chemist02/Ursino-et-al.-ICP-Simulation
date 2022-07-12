'''
This is a simple example of how the model can be used. We create a UrsinoSimulation object with two altered constants
and run the simulation for about 30 minutes with constant input parameters. The UrsinoSimulation module contains loads
of additional documentation, as well as a link to the original paper at the top.
'''

from UrsinoSimulation import UrsinoSimulation
import matplotlib.pyplot as plt

def main():
    # Create simulation object; these parameters were shown in the original model to result in self-sustained 
    # oscillations resembling Lundberg A waves.
    simulation = UrsinoSimulation(R_CSF_OUTFLOW=6.32e3, IC_ELASTANCE_COEFF=0.23)
    # Create lists to store ICP measurements and the time of each measurement for later plotting.
    times = []
    ICPReadings = []

    # How many seconds does the simulation move forward each iteration.
    timestep = 0.01
    # Continue while the simulation's time is less than the target time (2000 seconds in this case)
    while (simulation.getTime() < 2000.0):
        times.append(simulation.getTime())
        ICPReadings.append(simulation.getICP())

        # Constant arterial pressure, venous sinus pressure, and a cerebrospinal fluid injection/removal rate of zero 
        # ml/s. These can of course be changed, if desired.
        simulation.stepSimulation(timestep=timestep, arterialPressure=100.0, arterialPressureDelta=0.0, \
                                  venousSinusPressure=6.0, CSFInjectRate=0.0)

    # Construct plot and display.
    figure, axes = plt.subplots()
    axes.set_xlabel("Time (s)")
    axes.set_ylabel("ICP (mmHg)")
    axes.plot(times, ICPReadings)
    plt.show()

if (__name__ == "__main__"):
    main()
