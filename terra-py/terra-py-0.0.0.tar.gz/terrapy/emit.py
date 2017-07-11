from glob import glob
import json
from os.path import basename, dirname, join
from runpy import run_path

import attr

import terrapy.const as const


@attr.s
class TfJsonEmitter:
    """
    emit tf-json for one py file
    """
    filename = attr.ib()
    cfg = attr.ib()

    @cfg.default
    def load_cfg(self):
        mod = run_path(self.filename)
        try:
            cfg = mod['config']
            return cfg
        except KeyError:
            raise ValueError(
                '{} should have a global var "config"'.format(self.filename)
            )

    @property
    def out_file(self):
        src = basename(self.filename)
        out = const.out_fmt.format(src)
        dst = join(dirname(self.filename), out)
        return dst

    def write_cfg(self):
        with open(self.out_file, 'w') as fp:
            json.dump(self.cfg, fp)

    @classmethod
    def walk_current_dir(cls):
        for filename in glob(const.src_glob, recursive=True):
            cls(filename).write_cfg()


if __name__ == '__main__':
    for filename in glob(const.src_glob, recursive=True):
        print(filename)
