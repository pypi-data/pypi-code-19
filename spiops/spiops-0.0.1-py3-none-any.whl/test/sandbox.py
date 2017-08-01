from spiops import spiops




cov = spiops.cov_spk_obj(mk='MEX_OPS.TM',
                             object='MEX',
                             time_format='UTC',
                             report=True)

print(cov)



cov = spiops.cov_ck_obj(mk='MEX_OPS.TM',
                            object='MEX_SC_REF',
                            time_format='UTC',
                            report=True)

print(cov)

