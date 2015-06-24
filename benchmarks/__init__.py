from __future__ import print_function
import sys
import os
import timeit
from functools import wraps

import simtk.openmm.app as app
import simtk.openmm as mm
import simtk.unit as unit
from .setup import createContext


def timeIntegration(context, steps, initialSteps):
    """Integrate a Context for a specified number of steps, then return how many seconds it took."""
    context.getIntegrator().step(initialSteps) # Make sure everything is fully initialized
    context.getState(getEnergy=True)
    start = timeit.default_timer()
    context.getIntegrator().step(steps)
    context.getState(getEnergy=True)
    end = timeit.default_timer()
    return (end - start)
    

def create_benchmark(**params):
    def decorator(func):
        def setup():
            global context, initialSteps
            context, initialSteps = createContext(params)            

        @wraps(func)
        def benchmark():
            steps = 20
            while True:
                time = timeIntegration(context, steps, initialSteps)
                if time >= 0.5*benchmark.seconds:
                    break
                if time < 0.5:
                    # Integrate enough steps to get a reasonable estimate for how many we'll need.
                    steps = int(steps*1.0/time)
                else:
                    steps = int(steps*benchmark.seconds/time)

            dt = context.getIntegrator().getStepSize()
            return round((dt*steps*86400/time).value_in_unit(unit.nanoseconds), 2)

        def teardown():
            global context
            del context

        benchmark.setup = setup
        benchmark.teardown = teardown
        benchmark.unit = 'nanoseconds / day'
        benchmark.seconds = 30.0

        return benchmark

    return decorator


def createContext(options):
    """Perform a single benchmarking simulation."""
    explicit = (options['test'] in ('rf', 'pme', 'amoebapme'))
    amoeba = (options['test'] in ('amoebagk', 'amoebapme'))
    hydrogenMass = None

    platform = mm.Platform.getPlatformByName(options['platform'])
    
    # Create the System.
    
    if amoeba:
        constraints = None
        epsilon = float(options['epsilon'])
        if epsilon == 0:
            polarization = 'direct'
        else:
            polarization = 'mutual'
        if explicit:
            ff = app.ForceField('amoeba2009.xml')
            pdb = app.PDBFile(os.path.join(os.path.dirname(__file__),                                           
                                           '5dfr_solv-cube_equil.pdb'))
            cutoff = 0.7*unit.nanometers
            vdwCutoff = 0.9*unit.nanometers
            system = ff.createSystem(pdb.topology, nonbondedMethod=app.PME, nonbondedCutoff=cutoff, vdwCutoff=vdwCutoff, constraints=constraints, ewaldErrorTolerance=0.00075, mutualInducedTargetEpsilon=epsilon, polarization=polarization)
        else:
            ff = app.ForceField('amoeba2009.xml', 'amoeba2009_gk.xml')
            pdb = app.PDBFile(os.path.join(os.path.dirname(__file__),
                                           '5dfr_minimized.pdb'))
            cutoff = 2.0*unit.nanometers
            vdwCutoff = 1.2*unit.nanometers
            system = ff.createSystem(pdb.topology, nonbondedMethod=app.NoCutoff, constraints=constraints, mutualInducedTargetEpsilon=epsilon, polarization=polarization)
        dt = 0.001*unit.picoseconds
    else:
        if explicit:
            ff = app.ForceField('amber99sb.xml', 'tip3p.xml')
            pdb = app.PDBFile(os.path.join(os.path.dirname(__file__),
                                           '5dfr_solv-cube_equil.pdb'))
            if options['test'] == 'pme':
                method = app.PME
                cutoff = options['cutoff']
            else:
                method = app.CutoffPeriodic
                cutoff = 1*unit.nanometers
        else:
            ff = app.ForceField('amber99sb.xml', 'amber99_obc.xml')
            pdb = app.PDBFile(os.path.join(os.path.dirname(__file__),
                                           '5dfr_minimized.pdb'))
            method = app.CutoffNonPeriodic
            cutoff = 2*unit.nanometers
        if options['heavy']:
            dt = 0.005*unit.picoseconds
            constraints = app.AllBonds
            hydrogenMass = 4*unit.amu
        else:
            dt = 0.002*unit.picoseconds
            constraints = app.HBonds
            hydrogenMass = None
        system = ff.createSystem(pdb.topology, nonbondedMethod=method, nonbondedCutoff=cutoff, constraints=constraints, hydrogenMass=hydrogenMass)

    # print('Step Size: %g fs' % dt.value_in_unit(unit.femtoseconds))
    properties = {}
    initialSteps = 5
    if options['device'] is not None:
        if platform.getName() == 'CUDA':
            properties['CudaDeviceIndex'] = options['device']
        elif platform.getName() == 'OpenCL':
            properties['OpenCLDeviceIndex'] = options['device']
        if ',' in options['device'] or ' ' in options['device']:
            initialSteps = 250
    if options['precision'] is not None:
        if platform.getName() == 'CUDA':
            properties['CudaPrecision'] = options['precision']
        elif platform.getName() == 'OpenCL':
            properties['OpenCLPrecision'] = options['precision']
    
    # Run the simulation.
    
    integ = mm.LangevinIntegrator(300*unit.kelvin, 91*(1/unit.picoseconds), dt)
    integ.setConstraintTolerance(1e-5)
    if len(properties) > 0:
        context = mm.Context(system, integ, platform, properties)
    else:
        context = mm.Context(system, integ, platform)
    context.setPositions(pdb.positions)
    context.setVelocitiesToTemperature(300*unit.kelvin)

    return context, initialSteps
