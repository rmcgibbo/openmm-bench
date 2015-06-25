import os

import simtk.openmm.app as app
import simtk.openmm as mm
import simtk.unit as unit


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

    context.getIntegrator().step(initialSteps) # Make sure everything is fully initialized
    context.getState(getEnergy=True)
    return context
