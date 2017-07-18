import os
from docker_buildtool import docker_build, dockerfile, rsync

class Builder(object):
    def __init__(self, dockerfile, image, variables=None, fetch=False, default_build_root=None, quiet=False, s3_location=None, run_docker_build=True, docker_args=[], force_rsync=False):
        self.dockerfile = dockerfile
        self.image = image
        self.fetch = fetch

        if self.image is None:
            docker_repo = None
            tag = None
        else:
            parsed_tag = self.image.split(':')
            if len(parsed_tag) > 1:
                docker_repo = parsed_tag[0]
                tag = parsed_tag[1]
            else:
                docker_repo = parsed_tag[0]
                tag = 'latest'

        self.docker_repo = docker_repo
        self.tag = tag

        if variables is None:
            variables = {}
        self.variables = variables
        self.default_build_root = default_build_root
        self.quiet = quiet

        self.spec = self.prepare()
        self.s3_location = s3_location
        self.run_docker_build = run_docker_build
        self.docker_args = docker_args
        self.force_rsync = force_rsync

    def prepare(self):
        return dockerfile.DockerfileBuildSpec(self.dockerfile)

    def run(self, dryrun):
        # _use_rsync is only for the tests
        if self.spec.has_frontmatter:
            build_root = self.spec.build_root
        else:
            build_root = self.default_build_root
        build = docker_build.DockerBuild(
            dockerfile=self.spec.dockerfile,
            build_root=build_root,
            include=self.spec.include,
            workdir=self.spec.workdir,
            ignore=self.spec.ignore,
            docker_repo=self.docker_repo,
            tag=self.tag,
            default_ignore=self.spec.default_ignore,
            include_version_file=self.spec.include_version_file,
            variables=self.variables,
            fetch=self.fetch,
            no_ignore_override=self.spec.no_ignore_override,
            quiet=self.quiet,
            _raw_build_root=self.spec._raw_build_root
        )
        if self.force_rsync or os.getenv('DOCKER_BUILDTOOL_RSYNC'):
            rsync.remote_build(dryrun, build, docker_args=self.docker_args, s3_location=self.s3_location, run_docker_build=self.run_docker_build)
        else:
            build.run(dryrun=dryrun, docker_args=self.docker_args)
