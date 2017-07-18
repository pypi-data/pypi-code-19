#!/usr/bin/python
from __future__ import print_function
import subprocess, os, json, random, sys, collections
import argparse, pkg_resources
from itertools import chain, imap, islice
from functools import partial
from os.path import dirname, realpath, join, basename


TOP = dirname(dirname(pkg_resources.resource_filename(__name__, __name__)))
VERSION = open(join(TOP, "VERSION")).read()

parser = argparse.ArgumentParser()
# required argument
parser.add_argument("project-spec", help = "path to project spec (jobs) file")
# optional flag
parser.add_argument("-i", "--input",
                    help = "path to free variables JSON")
parser.add_argument("-o", "--output", default = "results.json",
                    help = "location where to output accumulated values")
parser.add_argument("-f", "--free-vars", action="store_true",
                    help = "display a list of free variables")
parser.add_argument("-p", "--path", type = lambda s: s.split(":"),
                    help = """colon-delimited path where
                    to find additional subscripts""")
parser.add_argument("-g", "--dependency-graph-pdf",
                    help = "output the job dependency graph as a pdf")
parser.add_argument("-v", "--verbose", type = int, default = 2,
                    help = "verbosity level 0-2")
parser.add_argument("--version", action = "version", version = VERSION)
parser.add_argument("-s", "--sort-vars-by-job-order", action="store_true",
                    help = "remeber order in which vars are accumulated")

args = vars(parser.parse_args())
verbose = args["verbose"]
default_subscripts = join(TOP, "scripts")
subscripts_path = [default_subscripts] + (args["path"] or [])

class bcolors:
    # http://stackoverflow.com/questions/287871
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def fatal ( msg ):
    print("{}FATAL: {}{}".format(bcolors.FAIL, msg, bcolors.ENDC),
          file = sys.stderr)
    sys.exit(1)

def json_load ( json_in, err_msg = "invalid json", is_string = False ):
    try:
        fun = json.loads if is_string else json.load
        return fun(json_in, object_pairs_hook=collections.OrderedDict)
    except Exception as e:
        fatal("{}:\n{}".format(err_msg, e.__str__()))

def get_template_var ( atom ):
    "if var_name is a template var, return it's non-template name"
    if atom and isinstance(atom, basestring) and atom[0] == "$":
        return atom[1:]

def walk_json_atoms ( obj, fun ):
    def rec ( obj ):
        if isinstance(obj, list):
            return map(rec, obj)
        elif isinstance(obj, dict):
            return dict((rec(k), rec(v)) for (k, v) in obj.iteritems())
        else :
            # string, JSON number or bool
            # non-recursive case, aka atom
            return fun(obj)
    return rec(obj)

def construct_json_input(json_obj, cum_vars):
    def render_var ( atom ):
        if get_template_var(atom):
            return cum_vars[get_template_var(atom)]
        else:
            return atom
    return walk_json_atoms(json_obj, render_var)

def job_inputs ( job ):
    "return vars that must be known before job can be run"
    templates = []
    walk_json_atoms(job["input"], lambda atom:
                    templates.append(get_template_var(atom)))
    return filter(bool, templates)

def job_outputs ( job ):
    "return vars that are produced by the job"
    return job["output"].values()

def free_vars ( jobs, additional_inputs = []):
    all_inputs = reduce(chain, imap(job_inputs,jobs), additional_inputs)
    all_outputs = reduce(chain, imap(job_outputs,jobs))
    free_vars = set(all_inputs).difference(set(all_outputs))
    return free_vars

def sort_jobs ( jobs ):
    """order jobs into sequential batches based on variable dependencies"""
    known_vars = set(free_vars(jobs))

    def job_is_runnable ( known_vars, job ):
        return len(set(job_inputs(job)).difference(known_vars)) == 0

    def groupby ( coll, pred ):
        "itertools.groupby doesn't work if coll isn't sorted"
        groups = {}
        [groups.setdefault(pred(item), []).append(item) for item in coll]
        return groups

    jobs_left = jobs
    ordered_batches = []

    while jobs_left:
        is_runnable = partial(job_is_runnable, known_vars)
        by_runnable = groupby(jobs_left,is_runnable)

        if True not in by_runnable:
            jobs_left_names = map(lambda j: j["script"], jobs_left)
            need = reduce(chain, imap(job_inputs,jobs_left))
            missing = set(need).difference(known_vars)
            fatal("no way to satify inputs for jobs: {}.missing variables: [{}]"
                  .format(jobs_left_names,
                          ",".join(missing)))

        next_batch = by_runnable[True]
        jobs_left = by_runnable.get(False, [])

        ordered_batches.append(next_batch)

        known_vars.update(reduce(chain, imap(job_outputs, next_batch)))

    return ordered_batches


def dependency_graph_pdf ( jobs, outfn_pdf ):
    import graphviz
    batches = sort_jobs(jobs)
    for (i, job) in enumerate(reduce(chain, batches)):
        job["index"] = i+1
    dot = graphviz.Digraph(filename = outfn_pdf)
    var_provider = {}
    for job in jobs:
        var_provider.update((v, job) for v in job_outputs(job))

    def chunks(it, size):
        # http://stackoverflow.com/questions/312443
        it = iter(it)
        return iter(lambda: tuple(islice(it, size)), ())

    def job_label ( job ):
        if isinstance (job, basestring):
            return job
        else:
            return "{}. {}\nIN [{}] \n=>\n OUT [{}]".format(
                job["index"],
                job["script"].upper(),
                "\n".join((", ".join(chunk) for chunk in \
                           chunks(job_inputs(job), 2))),
                "\n".join((", ".join(chunk) for chunk in \
                           chunks(job_outputs(job), 2))))

    free ="FREE VARS"
    var_provider.update((v, free) for v in free_vars(jobs))
    dot.node(free, free)
    last_node = free
    map(lambda job: dot.node(job_label(job), job_label(job)), jobs)
    edges = {}
    for job in jobs:
        for v in job_inputs(job):
            parent = var_provider[v]
            edge_key = (job_label(parent), job_label(job))
            edges.setdefault(edge_key, []).append(v)
    for ((a, b), variables) in edges.iteritems():
        dot.edge(a, b, "\n".join(variables))
    dot.view()

def assert_required_fields ( actual_fields, required_fields,
                             err_msg = "missing fields" ):
    missing = set(required_fields).difference(set(actual_fields))
    if missing:
        fatal("{}: {}".format(err_msg, ",".join(missing)))

def find_script_by_name ( script_name ):
    "return the single executable's path for script_name"
    subscript_path_cands = filter(lambda top: script_name in os.listdir(top),
                                  subscripts_path)

    if len(subscript_path_cands) != 1:
        fatal("found {} directory candidates while looking for subscript {}"
              .format(len(subscript_path_cands),
                      script_name,subscripts_path))

    script_dir = join(subscript_path_cands[0], script_name)

    fns_abs = [os.path.join(script_dir, fn)
               for fn in os.listdir(script_dir)]

    def is_exe(fpath):
        # http://stackoverflow.com/questions/377017
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def basename_sans_ext ( fpath ):
        return os.path.splitext(basename(fpath))[0]

    matching_scripts = filter(lambda fpath:
                              basename_sans_ext(fpath)==script_name and
                              is_exe(fpath),
                              fns_abs)

    if len(matching_scripts) != 1:
        fatal("there must be exactly one {}.EXT executable at {}"
              .format(script_name, script_dir))
    else:
        return matching_scripts[0]


def assert_no_var_overwrites ( jobs ):
    cum_vars = set(free_vars(jobs))
    for job in jobs:
        new_vars = job_outputs(job)
        overwritten = cum_vars.intersection(new_vars)
        if overwritten:
            fatal("job\n{}\noverwrites existing var {}"
                  .format(json.dumps(job, indent = 2), overwritten))
        else:
            local_overwrites = [ var for (var, count) in
                                 collections.Counter(job["output"].values()).items()
                                 if count > 1]
            if local_overwrites:
                fatal("job\n{}\nhas local output overwrites: {}"
                  .format(json.dumps(job, indent = 2), local_overwrites))
            cum_vars.update(new_vars)

def run_jobs ( jobs, free_variables ):

    # dictionary to keep track of all the environment variables bootstrap needs
    cum_vars = free_variables
    child_env = os.environ.copy()
    # allow subscripts to find each other horizontally and compose.
    # add actual dir where exe lives, eg child should be able to "export PATH=$PATH:$CFBOOT_PATH"
    child_env["CFBOOT_PATH"] = ":".join(reduce(
        chain,[[join(scripts_top, dname) for dname in os.listdir(scripts_top)]
               for scripts_top in subscripts_path]))
    batches = sort_jobs(jobs)
    jobs = list(reduce(chain, batches))
    job_required_fields = ["script", "input", "output"]

    assert_no_var_overwrites(jobs)
    # handle each job
    total_jobs = len(jobs)
    for (i, job) in enumerate(jobs):
        assert_required_fields(job, job_required_fields)
        script = job["script"]
        input_vals = job["input"]
        output_vals = job["output"]
        concrete_input_json = construct_json_input(input_vals, cum_vars)
        script_path = find_script_by_name(script)
        if verbose>=2:
            print ("\n\n{}{}RUNNING CHILD {}/{}: '{}' with input:"
                   .format(
                       bcolors.OKBLUE, bcolors.BOLD,
                       i+1, total_jobs,
                       script
                   ), file = sys.stderr)
            json.dump(concrete_input_json, sys.stderr, indent = 2)
            print ( "{}\n\n".format(bcolors.ENDC, file = sys.stderr ))

        child = subprocess.Popen(
            [script_path],
            stdin = subprocess.PIPE,
            stdout = subprocess.PIPE,
            env = child_env)
        json.dump(concrete_input_json, child.stdin)
        (child_output, child_stderr) = child.communicate()

        print ( bcolors.OKGREEN+bcolors.BOLD, file = sys.stderr)
        print ( child_output, file = sys.stderr )
        print ( bcolors.ENDC, file = sys.stderr)

        if child.returncode != 0:
            print ( child_stderr )
            fatal("child {} failed with arguments: \n{}"
                  .format(script, json.dumps(concrete_input_json,
                                             indent = 2)))

        child_output_json = json_load(
            child_output, is_string = True,
            err_msg = "child {} did not produce valid json"
            .format(script))

        required_output_fields = list(job["output"].keys())
        assert_required_fields(
            child_output_json,required_output_fields,err_msg=
            "child {} failed to produce expected keys"
            .format(script))


        # accumulate environment variables for bootstraping
        for key in required_output_fields:
            cum_vars_key = job["output"][key]
            cum_vars[cum_vars_key] = child_output_json[key]

    return cum_vars

def main (  ):
    # TODO allow calling from python
    # load jobs from a file

    with open(args["project-spec"], 'r') as f:
        project_spec = json_load(f, "invalid project spec JSON")

    jobs = project_spec["jobs"]

    if args["free_vars"]:
        json.dump(sorted(free_vars(jobs)), sys.stdout, indent = 2)
        sys.exit(0)
    elif args["dependency_graph_pdf"]:
        fn = args["dependency_graph_pdf"]
        dependency_graph_pdf(jobs, fn)
        sys.exit(0)
    else:
        # load free variables from stdin
        input_fn = args["input"]
        print ( "loading free variables...", file = sys.stderr )
        free_variables = json_load(open(input_fn, "r") if input_fn else sys.stdin,
                                   "error reading free variables")

        expected_free_vars = free_vars(jobs)

        assert_required_fields(free_variables.keys(), expected_free_vars,
                               err_msg = "missing free variables")

        accumulated_vars = run_jobs(jobs, free_variables)

        # print dict to keep accumulated values for bootstraping
        sort_keys = not args.get("sort_vars_by_job_order")
        json.dump(accumulated_vars, sys.stdout, indent=2,
                  sort_keys = sort_keys)
        with open( args["output"], "w") as fh:
            json.dump(accumulated_vars, fh, indent=2, sort_keys = sort_keys)

if __name__ == '__main__':
    main()
