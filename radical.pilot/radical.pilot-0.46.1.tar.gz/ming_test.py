#!/usr/bin/env python

import os
import radical.pilot as rp

UNITS = 64
TIME = 60 * 6
pdesc_stampede = {
    'resource'      : 'xsede.stampede',
    'cores'         : 16,
    'runtime'       : TIME,
    'project'       : "TG-MCB090174",
    'queue'         : "development"
}

pdesc_local = {
    'resource'      : 'local.localhost',
    'cores'         : 1,
    'runtime'       : TIME,
    'project'       : None,
    'queue'         : None
}

pdesc_osg = {
    'resource'      : 'osg.xsede-virt-clust',
    'cores'         : 1,
    'runtime'       : TIME,
    'project'       : 'TG-CCR140028'
}

session = rp.Session()
try:

    pmgr = rp.PilotManager(session)

    pdescs = list()

    pdescs.append(rp.ComputePilotDescription(pdesc_local))
    pdescs.append(rp.ComputePilotDescription(pdesc_local))
    pdescs.append(rp.ComputePilotDescription(pdesc_local))
    pdescs.append(rp.ComputePilotDescription(pdesc_local))

    pilots = pmgr.submit_pilots(pdescs)


    cuds = list()
    for i in range(UNITS):
        cud = rp.ComputeUnitDescription()
        cud.pre_exec = ['''
        if test ! -d $HOME/ve.synapse
        then 
          virtualenv $HOME/ve.synapse 
          source $HOME/ve.synapse/bin/activate 
          wget -qO- https://github.com/radical-cybertools/radical.utils/archive/v0.41.1.tar.gz \
                  | tar -xzv
          wget -qO- https://github.com/applicationskeleton/Skeleton/archive/v1.2.tar.gz \
                  | tar -xzv
          wget -qO- https://github.com/radical-cybertools/radical.synapse/archive/v0.44.tar.gz \
                  | tar -xzv
          wget -P $HOME/ https://raw.githubusercontent.com/applicationskeleton/Skeleton/feature/task_flops/bin/aimes-skeleton-synapse.py 

          pip install ./radical.utils-0.41.1/
          pip install ./Skeleton-1.2/
          pip install ./radical.synapse-0.44/
          chmod u+x ./aimes-skeleton-synapse.py 
        else
          source $HOME/ve.synapse/bin/activate 
        fi
        '''
                       ]
        cud.executable = './aimes-skeleton-synapse.py'
        cud.arguments = ['serial', 'flops', '1', '1715750072310', '65536', '65536', '0', '0', '0']
        cuds.append(cud)

    umgr = rp.UnitManager(session=session, scheduler='backfilling')
    umgr.add_pilots(pilots)
    units = umgr.submit_units(cuds)
    umgr.wait_units()

except Exception as e:
    print e

finally:
    session.close(cleanup=False)
    os.system('radicalpilot-close-session -m export -s %s' %session.uid)
