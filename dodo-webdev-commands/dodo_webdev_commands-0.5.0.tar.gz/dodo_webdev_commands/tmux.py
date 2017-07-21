# noqa
from dodo_commands.extra.standard_commands import DodoCommand
import os


class Command(DodoCommand):  # noqa
    help = ""

    def handle_imp(self, **kwargs):  # noqa
        default_script = os.path.join(
            self.get_config("/ROOT/res_dir"),
            "tmux.sh"
        )
        tmux_script = self.get_config("/TMUX/script_file", default_script)
        self.runcmd(["chmod", "+x", tmux_script])
        self.runcmd([tmux_script])
