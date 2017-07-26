# -*- coding: utf-8 -*-

# imports
import sys
import click
from mtsh import mtsh
from termcolor import colored

# print command results
def print_results (results, verbose, quiet):
    if len(results) == 1:
        click.echo(colored("Outputs are synchronized", "green"))
    else:
        click.echo(colored("Outputs are not synchronized", "yellow"))
    if any(results[key][0] for key in results):
        click.echo(colored("One or more outputs contain errors", "red"))
    else:
        click.echo(colored("No outputs contain errors", "green"))
    if not quiet or verbose:
        click.echo("")
        for output, servers in results.iteritems():
            prior = colored("Error: ", "red") if servers[0] else colored("Success: ", "green")
            names = "All servers" if len(results) == 1 and not verbose else ', '.join(servers[1:])
            click.echo(prior + colored(names, "blue"))
            click.echo(output)

# cli options
@click.command()
@click.option("--server", "-s", multiple=True, help="Server connection in the form of user@host.domain.")
@click.option("--file", "-f", type=click.File(), help="Path to file that contains line separated servers.")
@click.option("--command", "-c", multiple=True, help="Command to execute on servers instead of opening shell.")
@click.option("--verbose", "-v", is_flag=True, help="Enable verbose printing for debugging information.")
@click.option("--quiet", "-q", is_flag=True, help="Hide command output, only show run information.")

# main method
def main(server, file, command, verbose, quiet):
    # server strings
    servers = []
    # extend manual specified servers
    servers.extend(server)
    # extend file with list of servers
    if file: servers.extend(file.read().splitlines())
    # initialize the mtsh handler
    try:
        handler = mtsh(servers)
    except Exception as e:
        sys.exit("Error: " + str(e))
    # loop over all commands
    for c in command:
        # perform command on all servers
        results = handler.command(c)
        # print formatted output results
        print_results(results, verbose, quiet)

# main invocation
if __name__ == "__main__":
    main()
