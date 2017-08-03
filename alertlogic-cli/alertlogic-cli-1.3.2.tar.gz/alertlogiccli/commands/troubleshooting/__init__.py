from . import launcher

metadata = {
    "subcommands": [
        launcher.Redeploy()
    ],
    "name": "troubleshooting",
    "help": "troubleshooting commands available only to alertlogic staff"
}
