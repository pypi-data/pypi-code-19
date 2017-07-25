
import click
import json
import sys
import uuid
import time
from datetime import datetime, timedelta

from workflow import config
from workflow.clients import cmp


class Context:

    def __init__(self):
        self.config = config.load()
        self.cmp = cmp.Client(url=self.config.url,
                              auth=(self.config.api_key,
                                    self.config.api_secret),
                              verify_ssl=self.config.verify_ssl)


pass_context = click.make_pass_decorator(Context, ensure=True)


class UUIDParamType(click.ParamType):

    def __init__(self, name):
        self.name = name

    def convert(self, value, param, ctx):
        try:
            uuid.UUID(hex=value)
            return value
        except ValueError as e:
            self.fail("%s" % e)


instanceIDParam = UUIDParamType("instance_id")
workflowIDParam = UUIDParamType("workflow_id")


# CLI helpers
def list_workflows(ctx, args, incomplete):
    fctx = ctx.ensure_object(Context)

    resp = fctx.cmp.get("/workflows")
    resp.raise_for_status()

    data = resp.json()

    return [wf["id"] for wf in data]


def list_instances(ctx, args, incomplete):
    fctx = ctx.ensure_object(Context)

    resp = fctx.cmp.get("/workflows/{}/instances".format(args[1]))
    resp.raise_for_status()

    data = resp.json()

    return [i["id"] for i in data]


# Commands
@click.group(context_settings={"help_option_names": ["-h", "--help"]})
def cli():
    """Workflow manages your flux workflows from the terminal"""
    pass


@cli.command("config")
def cmd_config():
    """Configure the CMP URL and credentials"""
    config.Config({})


@cli.command("list")
@pass_context
def cmd_list(ctx):
    """List existing flux workflows"""
    resp = ctx.cmp.get("/workflows")
    resp.raise_for_status()

    data = resp.json()

    trow = (u'{id:36}  {name:30.30}')  # {user_name:30.30}')

    click.echo(trow.format(**{
        "id": "ID",
        "name": "NAME",
        "user_name": "OWNER",
    }))

    for workflow in data:
        click.echo(trow.format(**workflow))


@cli.command("show")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@pass_context
def cmd_show(ctx, workflow_id):
    """Display details of a Flux workflow"""
    show_workflow(ctx, workflow_id)


def show_workflow(ctx, workflow_id):
    resp = ctx.cmp.get("/workflows/{}".format(workflow_id))
    resp.raise_for_status()

    workflow = resp.json()

    fmt_basic = (
        'Name: {name}\n'
        'Description: {description}\n'
        # 'Owner: {user_name}\n'
        'Created: {created_at}\n'
        'Updated: {updated_at}\n'
        'Timeout: {timeout} seconds\n'
        'Max steps: {max_steps}\n'
        'Max instances: {max_instances}'
    )
    click.echo(fmt_basic.format(**workflow))

    event = workflow["initial_event"]
    click.echo("Initial event:\n{}".format(
        json.dumps(event, indent=4)).replace("\n", "\n    "))

    states = workflow["states"]
    click.echo("States:")

    fmt_transition = (
        "        if {condition}, goto {new_state}"
    )

    for state in states:
        click.echo("  - ID: {id}".format(**state))

        if state["type"] != "":
            click.echo("    Type: {type}".format(**state))

        if "label" in state:
            click.echo("    Label: {label}".format(**state))

        if "timeout" in state:
            click.echo("    Timeout: {timeout} seconds".format(**state))

        if "on_enter" in state:
            click.echo("    On-enter triggers:")
            for trigger in state["on_enter"]:
                click.echo(
                    "      - {}, {}".format(trigger["type"],
                                            json.dumps(trigger["params"])))

        if "transitions" in state:
            click.echo("    Transitions:")
            for transition in state["transitions"]:
                click.echo(fmt_transition.format(**transition))

        if "on_exit" in state:
            click.echo("    On-exit triggers:")
            for trigger in state["on_exit"]:
                click.echo(
                    "      - {}, {}".format(trigger["type"],
                                            json.dumps(trigger["params"])))

        click.echo("")


def show_error(message):
    if message.startswith("Validation error: "):
        m = message[len("Validation error: "):]
        for error in m.split("; "):
            click.echo("{}".format(error))
    else:
        click.echo(message)

    if message != "OK":
        sys.exit(1)


@cli.command("validate")
@click.option("-f", "--file", type=click.File("r"), default="workflow.json",
              help="File to load the workflow from")
@pass_context
def cmd_validate(ctx, file):
    """Validate the current workflow"""

    data = json.load(file)

    resp = ctx.cmp.post("/workflows?validate_only=true", data)

    if resp.status_code not in [200, 400]:
        resp.raise_for_status()

    show_error(resp.json()["message"])


@cli.command("upload")
@click.option("-f", "--file", type=click.File("r"), default="workflow.json",
              help="File to load the workflow from")
@pass_context
def cmd_upload(ctx, file):
    """Upload the current workflow"""

    data = json.load(file)

    resp = ctx.cmp.post("/workflows", data)

    if resp.status_code == 400:
        # Error; parse it and print
        show_error(resp.json()["message"])

    elif resp.status_code == 201:
        click.echo("Successfully uploaded as ID: {}".format(resp.json()["id"]))
    else:
        resp.raise_for_status()


@cli.command("update")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.option("-f", "--file", type=click.File("r"), default="workflow.json",
              help="File to load the workflow from")
@pass_context
def cmd_update(ctx, workflow_id, file):
    """Update (patch) a workflow"""

    data = json.load(file)

    resp = ctx.cmp.patch("/workflows/" + workflow_id, data)

    if resp.status_code == 400:
        # Error; parse it and print
        show_error(resp.json()["message"])

    elif resp.status_code != 200:
        resp.raise_for_status()


@cli.command("delete")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.option("-y", "--yes", is_flag=True,
              help="Skip delete confirmation prompt")
@pass_context
def cmd_delete(ctx, workflow_id, yes):
    """Delete a workflow"""

    if not yes:
        # Show the workflow for confirmation
        show_workflow(ctx,   workflow_id)

        click.confirm('Are you sure you want to delete this workflow?',
                      abort=True)

    resp = ctx.cmp.delete("/workflows/" + workflow_id)

    if resp.status_code == 204:
        click.echo("Workflow deleted.")
    else:
        resp.raise_for_status()


@cli.command("logs")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.option("-i", "--instance",
              help=(
                  "Get logs for a specific instance, "
                  "instead of all instances"
              ),
              type=instanceIDParam,
              autocompletion=list_instances)
@click.option("-f", "--follow", is_flag=True,
              help="Wait for logs and print them as they arrive")
@click.option("-o", "--out", type=click.File("w"), default="-",
              help="Write logs to FILENAME instead of stdout")
@pass_context
def cmd_logs(ctx, workflow_id, instance, follow, out):
    """Get logs for a workflow"""

    dateFormat = "%Y-%m-%dT%H:%M:%SZ"

    if instance:
        lastLog = None
        cont = True
        while cont:
            resp = ctx.cmp.get(
                "/workflows/{}/instances/{}".format(
                    workflow_id,
                    instance))

            if lastLog is not None and resp.status_code == 404:
                return

            resp.raise_for_status()
            logs = resp.json()["logs"]

            if lastLog is not None:
                if lastLog in logs:
                    logs = logs[logs.index(lastLog)+1:]

            for log in logs:
                dt = datetime.strptime(log["time"], dateFormat)

                lastLog = log

                extra = " ".join(sorted(["{}={}".format(x, log[x])
                                         for x in log
                                         if x not in ["time",
                                                      "level",
                                                      "message",
                                                      "event"]]))

                click.echo("{} [{:5}] {:40} {} event={}".format(
                    log["time"],
                    log["level"],
                    log["message"],
                    extra,
                    json.dumps(log["event"]),
                ), file=out)

            cont = follow
            if cont:
                time.sleep(1)

    else:
        lastTime = None
        cont = True
        while cont:
            if lastTime is None:
                resp = ctx.cmp.get("/logs?resource_id=workflow-{}".format(
                    workflow_id
                ))
            else:
                resp = ctx.cmp.get(
                    "/logs?resource_id=workflow-{}&start={}".format(
                        workflow_id,
                        (lastTime + timedelta(seconds=1)).strftime(
                            "%Y-%m-%dT%H:%M:%SZ")))

            resp.raise_for_status()
            logs = resp.json()

            # Logs are returned most-recent-first,
            # so we need to reverse the list
            for log in reversed(logs["hits"]):
                dt = datetime.strptime(log["timestamp"],
                                       "%Y-%m-%dT%H:%M:%S.%fZ")
                lastTime = dt
                dt = dt.replace(microsecond=0)
                click.echo("{}Z [{:5}] {}".format(
                    dt.isoformat(),
                    log["severity"],
                    log["message"],
                ), file=out)

            cont = follow
            if cont:
                time.sleep(1)

    out.close()


@cli.command("list-instances")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@pass_context
def cmd_list_instances(ctx, workflow_id):
    """List instances of a workflow"""

    resp = ctx.cmp.get("/workflows/{}/instances".format(workflow_id))
    resp.raise_for_status()

    data = resp.json()

    row = "{id:36}  {current_state:15}  {steps:10}  {timeout:25}"

    click.echo(row.format(**{
        "id": "ID",
        "current_state": "CURRENT STATE",
        "steps": "STEP COUNT",
        "timeout": "TIMEOUT",
    }))

    for instance in data:
        click.echo(row.format(**instance))


@cli.command("show-instance")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.argument("instance_id",
                type=instanceIDParam, autocompletion=list_instances)
@pass_context
def cmd_show_instances(ctx, workflow_id, instance_id):
    """Display details of an instance"""

    show_instance(ctx, workflow_id, instance_id)


def show_instance(ctx, workflow_id, instance_id):
    resp = ctx.cmp.get(
        "/workflows/{}/instances/{}".format(workflow_id, instance_id))
    resp.raise_for_status()

    instance = resp.json()

    fmt_basic = (
        "Current state: {current_state}\n"
        "Timeout: {timeout}\n"
        "Steps: {steps}\n"
        "State timeout expired: {state_timeout_expired}"
    )
    click.echo(fmt_basic.format(**instance))

    event = instance["event"]
    click.echo("Event:\n{}".format(
        json.dumps(event, indent=4)).replace("\n", "\n    "))

    if instance["parent_instance_id"] != "":
        fmt_parent = (
            "Parent:\n"
            "    Workflow ID: {parent_workflow_id}\n"
            "    Instance ID: {parent_instance_id}\n"
            "    Step count: {parent_step_count}\n"
            "    Child index: {child_index}"
        )

        click.echo(fmt_parent.format(**instance))

    if instance["child_instances_count"] != 0:
        fmt_child = (
            "Children:\n"
            "    Count: {child_instances_count}\n"
            "    Completed: {child_instances_completed}"
        )

        click.echo(fmt_child.format(**instance))


@cli.command("run")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.option("-e", "--event",
              help="The event to pass to the workflow, in JSON format",
              default="{}")
@pass_context
def cmd_run(ctx, workflow_id, event):
    """Run a workflow"""

    resp = ctx.cmp.post(
        "/workflows/{}/instances".format(workflow_id),
        {"event": json.loads(event)})
    resp.raise_for_status()

    instance = resp.json()["instance"]
    click.echo("Instance started as ID: {}".format(instance["id"]))


@cli.command("update-instance")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.argument("instance_id",
                type=instanceIDParam, autocompletion=list_instances)
@click.argument("event", type=click.STRING)
@pass_context
def cmd_update_instance(ctx, workflow_id, instance_id, event):
    """Update an instance's event for debugging"""

    resp = ctx.cmp.patch(
        "/workflows/{}/instances/{}".format(workflow_id, instance_id),
        {"event": json.loads(event)})
    resp.raise_for_status()


@cli.command("delete-instance")
@click.argument("workflow_id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.argument("instance_id",
                type=instanceIDParam, autocompletion=list_instances)
@click.option("-y", "--yes", is_flag=True,
              help="Skip delete confirmation prompt")
@pass_context
def cmd_delete_instance(ctx, workflow_id, instance_id, yes):
    """Delete an instance"""

    if not yes:
        # Show the instance for confirmation
        show_instance(ctx, workflow_id, instance_id)

        click.confirm(
            'Are you sure you want to delete this instance?', abort=True)

    resp = ctx.cmp.delete(
        "/workflows/{}/instances/{}".format(workflow_id, instance_id))

    if resp.status_code == 204:
        click.echo("Instance deleted.")
    else:
        resp.raise_for_status()


@cli.command("get")
@click.argument("workflow-id",
                type=workflowIDParam, autocompletion=list_workflows)
@click.option("-i", "--indent", type=int, default=4,
              help="Number of spaces to indent created file by")
@click.option("-f", "--file", type=click.File("w"), default="workflow.json",
              help="File to save the workflow to")
@pass_context
def cmd_get(ctx, workflow_id, indent, file):
    """Download a workflow to edit or view locally"""

    resp = ctx.cmp.get("/workflows/{}".format(workflow_id))
    resp.raise_for_status()

    workflow = resp.json()

    json.dump(workflow, file, indent=indent)
    file.write("\n")  # json.dump doesn't write a trailing newline


@cli.command("create")
@click.option("-i", "--indent", type=int, default=4,
              help="Number of spaces to indent created file by")
@click.option("-f", "--file", type=click.File("w"), default="workflow.json",
              help="File to save the workflow to")
def cmd_create(indent, file):
    """Create a workflow skeleton"""

    workflow = {
        "name": "Untitled Workflow",
        "description": "",
        "initial_event": {},
        "states": [
            {"id": "begin", "type": "begin", "transitions": [
                {"condition": "true", "new_state": "end"}]},
            {"id": "end", "type": "end"},
        ],
        "max_steps": 100,
        "max_instances": 10,
        "timeout": 600,
    }

    json.dump(workflow, file, indent=indent)
    file.write("\n")  # json.dump doesn't write a trailing newline
