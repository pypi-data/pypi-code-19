import json
import os
import glob
import recastbackend.resultaccess

from flask import Blueprint, render_template, jsonify, request
blueprint = Blueprint('yadage_result', __name__, template_folder='templates')

@blueprint.route('/result/<analysisid>/<wflowconfigname>/<basicreqid>')
def result_view(analysisid,wflowconfigname,basicreqid):
    fullpath = recastbackend.resultaccess.basicreq_wflowconfigpath(basicreqid,wflowconfigname)
    resultdata = recastbackend.resultextraction.extract_result(fullpath,analysisid,wflowconfigname)
    resultsfiles = []
    for dirpath,subdirs,files in os.walk(fullpath):
        for fl in files:
            resultsfiles.append('/'.join([dirpath.replace(fullpath,''),fl]).lstrip('/'))
    return render_template('recast_result.html', basicreqid = basicreqid, wflowconfigname = wflowconfigname, resultsfiles = resultsfiles, resultdata = resultdata)

@blueprint.route('/result/<analysisid>/<wflowconfigname>/<basicreqid>/json')
def json_result(analysisid,wflowconfigname,basicreqid):
    fullpath = recastbackend.resultaccess.basicreq_wflowconfigpath(basicreqid,wflowconfigname)
    resultdata = recastbackend.resultextraction.extract_result(fullpath,analysisid,wflowconfigname)
    return jsonify(resultdata)
