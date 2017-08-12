# -*- coding: utf-8 -*-
import os
import recastdb.models as models

def populate_db(db):
    if 'RECAST_MASTERTOKEN' not in os.environ:
            raise RuntimeError('need RECAST_MASTERTOKEN')


    ### populating the db we need to do it in the order of the relationships
    ### so let's first add users

    

    lukas_heinrich = models.User(
        name='Lukas Heinrich',
        email='lukas.heinrich@cern.ch',
        orcid_id = '0000-0002-4048-7584'
    )
    db.session.add(lukas_heinrich)
    db.session.commit()

    kyle_cranmer = models.User(
        name = 'Kyle Cranmer',
        email = 'kyle.cranmer@cern.ch',
        orcid_id = '0000-0002-5769-7094'
    )
    db.session.add(kyle_cranmer)
    db.session.commit()

    josh_ruderman = models.User(
        name='Joshua Ruderman',
        email='ruderman@nyu.edu',
        orcid_id = '0000-0001-6051-9216'
    )
    db.session.add(josh_ruderman)
    db.session.commit()


    theo_rist = models.User(
        name='Theo Rist',
        email='theo.rist@cern.ch',
        orcid_id = '1000-0001-1234-5678'
    )
    db.session.add(theo_rist)
    db.session.commit()


    ### to get API write access we need access tokens, we'll grab a master token from
    ### the environment

    lukas_token = models.AccessToken(
        token = os.environ['RECAST_MASTERTOKEN'],
        token_name = 'Master Token',
        user_id = lukas_heinrich.id
    )
    db.session.add(lukas_token)
    db.session.commit()


    ### now we'll want to add some analyses, for which we need run conditions first-child

    runcondition_ATLAS_8TeV_pp = models.RunCondition(
        name='ATLAS_8TeV_pp',
        description='ATLAS 8TeV pp collisions'
    )
    db.session.add(runcondition_ATLAS_8TeV_pp)
    db.session.commit()

    ### Now the analyses. As an example, we'll take analyses from the pMSSSM scan and Josh's example:


    arxiv_1502_05686 = models.Analysis(
        title='Search for massive supersymmetric particles decaying to many jets using the ATLAS detector in pp collisions at s√=8 TeV',
        collaboration='ATLAS',
        arxiv_id='1502.05686',
        description='''
        Results of a search for decays of massive particles to fully hadronic final states are presented. This search uses 20.3 fb−1 of data collected by the ATLAS detector in s√=8 TeV proton--proton collisions at the LHC. Signatures based on high jet multiplicities without requirements on the missing transverse momentum are used to search for R-parity-violating supersymmetric gluino pair production with subsequent decays to quarks. The analysis is performed using a requirement on the number of jets, in combination with separate requirements on the number of b-tagged jets, as well as a topological observable formed from the scalar sum of the mass values of large-radius jets in the event. Results are interpreted in the context of all possible branching ratios of direct gluino decays to various quark flavors. No significant deviation is observed from the expected Standard Model backgrounds estimated using jet-counting as well as data-driven templates of the total-jet-mass spectra. Gluino pair decays to ten or more quarks via intermediate neutralinos are excluded for a gluino with mass mg̃ <1 TeV for a neutralino mass mχ̃ 01=500 GeV. Direct gluino decays to six quarks are excluded for mg̃ <917 GeV for light-flavor final states, and results for various flavor hypotheses are presented.
        '''.strip('\n').replace('\n',' '),
        owner_id=kyle_cranmer.id,
        run_condition_id=runcondition_ATLAS_8TeV_pp.id,
        doi='10.1103/PhysRevD.91.112016'
        )
    db.session.add(arxiv_1502_05686)
    db.session.commit()



    arxiv_1405_7875 = models.Analysis(
        title='Search for squarks and gluinos with the ATLAS detector in final states with jets and missing transverse momentum using s√=8 TeV proton--proton collision data',
        collaboration='ATLAS',
        arxiv_id='1405.7875',
        description='''
        A search for squarks and gluinos in final states containing high-pT jets, missing transverse momentum and no electrons or muons is presented. The data were recorded in 2012 by the ATLAS experiment in s√=8 TeV proton-proton collisions at the Large Hadron Collider, with a total integrated luminosity of 20.3fb−1. No significant excess above the Standard Model expectation is observed. Results are interpreted in a variety of simplified and specific supersymmetry-breaking models assuming that R-parity is conserved and that the lightest neutralino is the lightest supersymmetric particle. An exclusion limit at the 95% confidence level on the mass of the gluino is set at 1330 GeV for a simplified model incorporating only a gluino and the lightest neutralino. For a simplified model involving the strong production of first- and second-generation squarks, squark masses below 850 GeV (440 GeV) are excluded for a massless lightest neutralino, assuming mass degenerate (single light-flavour) squarks. In mSUGRA/CMSSM models with tanβ=30, A0=−2m0 and μ>0, squarks and gluinos of equal mass are excluded for masses below 1700 GeV. Additional limits are set for non-universal Higgs mass models with gaugino mediation and for simplified models involving the pair production of gluinos, each decaying to a top squark and a top quark, with the top squark decaying to a charm quark and a neutralino. These limits extend the region of supersymmetric parameter space excluded by previous searches with the ATLAS detector.
        '''.strip('\n').replace('\n',' '),
        owner_id=lukas_heinrich.id,
        run_condition_id=runcondition_ATLAS_8TeV_pp.id,
        doi='10.1007/JHEP09(2014)176'
        )
    db.session.add(arxiv_1405_7875)
    db.session.commit()

    arxiv_1403_5294 = models.Analysis(
        title='Search for direct production of charginos, neutralinos and sleptons in final states with two leptons and missing transverse momentum in pp collisions at sqrt(s) = 8 TeV with the ATLAS detector',
        collaboration='ATLAS',
        arxiv_id='1403.5294',
        description='''
        Searches for the electroweak production of charginos, neutralinos and sleptons in final states characterized by the presence of two leptons (electrons and muons) and missing transverse momentum are performed using 20.3 fb-1 of proton-proton collision data at sqrt(s) = 8 TeV recorded with the ATLAS experiment at the Large Hadron Collider. No significant excess beyond Standard Model expectations is observed. Limits are set on the masses of the lightest chargino, next-to-lightest neutralino and sleptons for different lightest-neutralino mass hypotheses in simplified models. Results are also interpreted in various scenarios of the phenomenological Minimal Supersymmetric Standard Model.
        '''.strip('\n').replace('\n',' '),
        owner_id=lukas_heinrich.id,
        run_condition_id=runcondition_ATLAS_8TeV_pp.id,
        doi='10.1007/JHEP05(2014)071'
        )
    db.session.add(arxiv_1403_5294)
    db.session.commit()


    ### Now that we have analyses we can create Scan requests for them


    ### First up, we'll have a true EWK pMSSM request for our dilepton analysis
    EWK_pMSSM_request_one = models.ScanRequest(
        title="EWK pMSSM recast of arXiv:1403.5294",
        description_of_model='electroweak production in pMSSM',
        reason_for_request='This is a lower dimensional recast similar to the existing pMSSM recast (arXiv:1508.06608) but focuses on electroweak production. It is a 5-dimensional subspace of the pMSSM-19',
        additional_information='''
        The requests points have been sampled from the 5-dimensional subspace according to existing constraints such an DM relic abundance and Higgs mass.
        '''.strip('\n'),
        analysis_id=arxiv_1403_5294.id,
        requester_id=theo_rist.id,
        )
    db.session.add(EWK_pMSSM_request_one)
    db.session.commit()

    #adding the individual point requests:

    ewk_point_1 = models.PointRequest(
        scan_request_id=EWK_pMSSM_request_one.id,
        requester_id=theo_rist.id
    )
    db.session.add(ewk_point_1)
    db.session.commit()

    ewk_coord_m1 = models.PointCoordinate(
        title = 'M1', value = 250.0, point_request_id=ewk_point_1.id
    )
    ewk_coord_m2 = models.PointCoordinate(
        title = 'M2', value = 350.0, point_request_id=ewk_point_1.id
    )
    ewk_coord_mu = models.PointCoordinate(
        title = 'mu', value = 127.0, point_request_id=ewk_point_1.id
    )
    ewk_coord_tanbeta = models.PointCoordinate(
        title = 'tan_beta', value = 15, point_request_id=ewk_point_1.id
    )
    ewk_coord_mA = models.PointCoordinate(
        title = 'mA', value = 3000., point_request_id=ewk_point_1.id
    )
    db.session.add(ewk_coord_m1)
    db.session.add(ewk_coord_m2)
    db.session.add(ewk_coord_mu)
    db.session.add(ewk_coord_tanbeta)
    db.session.add(ewk_coord_mA)
    db.session.commit()

    ### for this point we will have a basic request:

    ewk_point_1_basic = models.BasicRequest(
        point_request_id=ewk_point_1.id,
        requester_id=theo_rist.id,
        request_format = 'standard_format'
    )
    db.session.add(ewk_point_1_basic)
    db.session.commit()

    ### for which we have a file stored on AWS

    ewk_point_1_basic_file = models.RequestArchive(
        file_name = "0000-0000-recastdilepton-255125-testfile-0001",
        path = '',
        zenodo_file_id = '',
        original_file_name = '255125.zip',
        basic_request_id = ewk_point_1_basic.id
        )
    db.session.add(ewk_point_1_basic_file)
    db.session.commit()

    ################################################################################
    ### for kicks, we add the GGM scan but without any points
    GGM_pMSSM_request_one = models.ScanRequest(
        title="General Gauge Mediated Models recast of arXiv:1403.5294",
        description_of_model='GGM SUSY',
        reason_for_request='''Previous limits placed on GGM models have been applied to scenarios with both electroweak and strong production, but none have covered electroweak production with a wino-higgsino like neutralino next-to-lightest-sparticle (NLSP). In addition to presenting complete results for the sensitivity to these models with the existing Run 1 data and analyses, this study aims to identify regions of the parameter space which would benefit from targeted analysis in Run 2.''',
        additional_information='''
        Fine scans of the GGM parameter space were conducted with constraints from EWSB breaking conditions, the Higgs boson mass of 125 GeV (never previously applied in this way) and requiring a tachyon-free spectrum
        '''.strip('\n'),
        analysis_id=arxiv_1403_5294.id,
        requester_id=theo_rist.id,
        )
    db.session.add(GGM_pMSSM_request_one)
    db.session.commit()


    import pkg_resources
    import csv
    r = csv.reader(pkg_resources.resource_stream('recastfrontend',
            'resources/testdb_data/GGMmap.txt'))
    ggm_keys = [x.strip() for x in r.next()]
    ggm_data = [dict(zip(ggm_keys[1:],map(float,x[1:]))) for x in r]

    ggm_points = []

    for x in ggm_data:
        GGM_point = models.PointRequest(
            scan_request_id=GGM_pMSSM_request_one.id,
            requester_id=theo_rist.id
        )
        ggm_points.append(GGM_point)
        db.session.add(GGM_point)
        db.session.commit()

        ggm_coord_m1 = models.PointCoordinate(
            title = 'M1', value = 3000.0, point_request_id=GGM_point.id
        )
        ggm_coord_m2 = models.PointCoordinate(
            title = 'M2', value = x['M2'], point_request_id=GGM_point.id
        )
        ggm_coord_tan_beta = models.PointCoordinate(
            title = 'tan_beta', value = x['tan_beta'], point_request_id=GGM_point.id
        )
        ggm_coord_mu = models.PointCoordinate(
            title = 'mu', value = x['mu'], point_request_id=GGM_point.id
        )
        db.session.add(ggm_coord_m1)
        db.session.add(ggm_coord_m2)
        db.session.add(ggm_coord_tan_beta)
        db.session.add(ggm_coord_mu)
        db.session.commit()


    ### for this point we will have a basic request:

    GGM_point_255125_basic = models.BasicRequest(
        point_request_id=ggm_points[24].id,
        requester_id=theo_rist.id,
        request_format = 'standard_format'
    )
    db.session.add(GGM_point_255125_basic)
    db.session.commit()

    ### for which we have a file stored on AWS

    GGM_point_255125_basic_file = models.RequestArchive(
        file_name = "0000-0000-recastdilepton-255125-testfile-0001",
        path = '',
        zenodo_file_id = '',
        original_file_name = '255125.zip',
        basic_request_id = GGM_point_255125_basic.id
        )
    db.session.add(GGM_point_255125_basic_file)
    db.session.commit()


    ################################################################################

    josh_request_one = models.ScanRequest(
        title="Stealth SUSY of ATLAS multijet search arXiv:1502.05686",
        description_of_model='Stealth SUSY',
        reason_for_request='The ATLAS multijet search, 1502.05686, counts events with many jets. This inclusive strategy can be used to constrain any model with new particles with large cross sections that produce many jets. So far it has been interpreted in terms of 2 RPV scenarios. In order to assess the general coverage of the search, it would be interesting to recast more topologies. Stealth SUSY is an R-parity preserving SUSY framework that also leads to multijets, with low missing energy, but leads to different topologies with different phase space for jets and different numbers of jets than the RPV cases considered. No limits have been set on purely hadronic Stealth SUSY scenarios with prompt decays, so recasting 1502.05686 would allow for the first limits on these models.',
        additional_information='''
        Stealth SUSY is described in: 1105.5135 and 1201.4875. Existing LHC searches require photons (1210.2052) and/or leptons (1411.7255) or displaced decays (1504.03634), there have been no searches for the challenging case of prompt purely hadronic topologies. An LHE file will be provided upon request (contact: ruderman@nyu.edu). The first topology to consider is gluino decay to gluon + singlino, singlino decay to two jets plus soft gravitino (the left topology of figure 10 of 1201.4875). The parameters to vary are the gluino and singlino masses (fixing the singlet mass near the singlino mass). This leads to 3 jets on each side, but with different kinematics than the gluino > 3jet RPV topology. Additional topologies with more jets can also be considered.
        '''.strip('\n'),
        analysis_id=arxiv_1502_05686.id,
        requester_id=josh_ruderman.id,
    )
    db.session.add(josh_request_one)
    db.session.commit()

    josh_point_1 = models.PointRequest(
        scan_request_id=josh_request_one.id,
        requester_id=josh_ruderman.id
    )
    db.session.add(josh_point_1)
    db.session.commit()

    josh_coord_mgluino = models.PointCoordinate(
        title = 'Mgluino', value = 250.0, point_request_id=josh_point_1.id
    )
    josh_coord_msinglino = models.PointCoordinate(
        title = 'Msinglino', value = 350.0, point_request_id=josh_point_1.id
    )
    db.session.add(josh_coord_mgluino)
    db.session.add(josh_coord_msinglino)
    db.session.commit()

    ### for this point we will have a basic request:
    josh_point_1_basic_1 = models.BasicRequest(
        point_request_id=josh_point_1.id,
        requester_id=josh_ruderman.id,
        request_format = 'standard_format'
    )
    db.session.add(josh_point_1_basic_1)

    josh_point_1_basic_2 = models.BasicRequest(
        point_request_id=josh_point_1.id,
        requester_id=josh_ruderman.id,
        request_format = 'another_format'
    )
    db.session.add(josh_point_1_basic_2)

    db.session.commit()

    ### for which we have a file stored on AWS

    josh_point_1_basic_1_file = models.RequestArchive(
        file_name = "0000-0000-nevents100-testfile-0001",
        path = '',
        zenodo_file_id = '',
        original_file_name = 'nevents100.zip',
        basic_request_id = josh_point_1_basic_1.id
        )
    db.session.add(josh_point_1_basic_1_file)

    josh_point_1_basic_2_file = models.RequestArchive(
        file_name = "0000-0000-nevents100-testfile-0001",
        path = '',
        zenodo_file_id = '',
        original_file_name = 'nevents100.zip',
        basic_request_id = josh_point_1_basic_2.id
        )
    db.session.add(josh_point_1_basic_2_file)
    db.session.commit()



