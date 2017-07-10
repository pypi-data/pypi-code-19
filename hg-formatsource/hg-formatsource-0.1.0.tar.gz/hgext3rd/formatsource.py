# Copyright 2017 Octobus <contact@octobus.net>
#
# This software may be used and distributed according to the terms of the
# GNU General Public License version 2 or any later version.
"""help dealing with code source reformating

The extension provide a way to run code-formatting tool in a way that avoid
conflict related to this formating when merging code not formatted yet.

A new `format-source` command is provided, to apply code formatting tool on
some specific files. This information is recorded into the repository and
reused when merging. The client doing the merge needs the extension for this
logic to kicks of.

Code formatting tools has to be registered in the configuration. The tool
"name" will be used to indentify a specific command accross all repositories.
It is mapped to a command line that must output the formatted content on stdout.

Example::

    [format-source]
    json = python -m json.tools
    clang = clang-format -style=Mozilla

We do not support specifying the mapping of tool name to tool command in the
repository itself for security reason.

The code formatting information is tracked into a .hg-format-source file a the
root of the repository.

Warning: There are not special logic handling renames so moving files to a
directory not covered by the patterns used for the initial formatting will
likely fails.
"""

from __future__ import absolute_import

import tempfile

from mercurial import (
    commands,
    cmdutil,
    error,
    extensions,
    filemerge,
    match,
    merge,
    registrar,
    scmutil,
    util,
)

from mercurial.i18n import _

__version__ = '0.1.0.dev'
testedwith = '4.2.2'
minimumhgversion = '4.2'
buglink = 'XXX'

cmdtable = {}

if util.safehasattr(registrar, 'command'):
    command = registrar.command(cmdtable)
else: # compat with hg < 4.3
    command = cmdutil.command(cmdtable)

file_storage_path = '.hg-format-source'

@command('format-source',
        [] + commands.walkopts + commands.commitopts + commands.commitopts2,
        _('TOOL FILES+'))
def cmd_format_source(ui, repo, tool, *pats, **opts):
    """format source file using a registered tools

    This command run TOOL on FILES and record this information in a commit to
    help with future merge.

    The actual command run for TOOL needs to be registered in the config. See
    :hg:`help -e formatsource` for details.
    """
    if repo.getcwd():
        msg = _("format-source must be run from repository root")
        hint = _("cd %s") % repo.root
        raise error.Abort(msg, hint=hint)

    if not pats:
        raise error.Abort(_('no files specified'))

    # XXX We support glob pattern only for now, the recursive behavior of various others is a bit wonky.
    for pattern in pats:
        if not pattern.startswith('glob:'):
            msg = _("format-source only support explicite 'glob' pattern "
                    "for now ('%s')")
            msg %= pattern
            hint = _('maybe try with "glob:%s"') % pattern
            raise error.Abort(msg, hint=hint)

    # lock the repo to make sure no content is changed
    with repo.wlock():
        # formating tool
        if ' ' in tool:
            raise error.Abort(_("tool name cannot contains space: '%s'") % tool)
        shell_tool = repo.ui.config('format-source', tool)
        if not shell_tool:
            msg = _("unknow format tool: %s (no 'format-source.%s' config)")
            raise error.Abort(msg % (tool, tool))
        cmdutil.bailifchanged(repo)
        cmdutil.checkunfinished(repo, commit=True)
        wctx = repo[None]
        # files to be formatted
        matcher = scmutil.match(wctx, pats, opts)
        # perform actual formatting
        for filepath in wctx.matches(matcher):
            newcontent = run_tools(ui, repo.root, tool, shell_tool, filepath)
            # XXX we could do the whole commit in memory
            with repo.wvfs(filepath, 'wb') as formatted_file:
                formatted_file.write(newcontent)

        # update the storage to mark formated file as formatted
        with repo.wvfs(file_storage_path, mode='ab') as storage:
            for pattern in pats:
                # XXX if pattern was relative, we need to reroot it from the
                # repository root. For now we constrainted the command to run
                # at the root of the repository.
                storage.write('%s %s\n' % (tool, pattern))

        if file_storage_path not in wctx:
            storage_matcher = scmutil.match(wctx, ['path:' + file_storage_path])
            cmdutil.add(ui, repo, storage_matcher, '', True)

        # commit the whole
        with repo.lock():
            commit_patterns = ['path:' + file_storage_path]
            commit_patterns.extend(pats)
            return commands._docommit(ui, repo, *commit_patterns, **opts)

def run_tools(ui, root, tool, cmd, filepath):
    """Run the a formatter tool on a specific file"""
    # XXX escape special character in filepath
    format_cmd = "%s %s" % (cmd, filepath)
    ui.pushbuffer(subproc=True)
    try:
        ui.system(format_cmd,
                  cwd=root,
                  onerr=error.Abort,
                  errprefix=tool)
    finally:
        newcontent = ui.popbuffer()
    return newcontent

def formatted(repo, old_ctx, new_ctx):
    """retrieve the list of formatted patterns between <old> and <new>

    return a {'tool': [patterns]} mapping
    """
    storage_matcher = rootedmatch(repo, new_ctx, [file_storage_path])
    new_formatting = {}
    if file_storage_path in new_ctx:
        status = old_ctx.status(other=new_ctx, match=storage_matcher)
        if status.modified or status.added:
            # quick and dirty line diffing
            # (the file is append only by contract)

            new_lines = set(new_ctx[file_storage_path].data().splitlines())
            old_lines = set()
            if file_storage_path in old_ctx:
                old_lines = set(old_ctx[file_storage_path].data().splitlines())
            new_lines -= old_lines
            for line in new_lines:
                tool, pattern = line.split(' ', 1)
                new_formatting.setdefault(tool, set()).add(pattern)
    return new_formatting

def allformatted(repo, local, other, ancestor):
    """return a mapping of formatting needed for all involved changeset
    """

    cachekey = (local.node, other.node(), ancestor.node())
    cached = getattr(repo, '_formatting_cache', {}).get(cachekey)

    if cached is not None:
        return cached

    local_formating = formatted(repo, ancestor, local)
    other_formating = formatted(repo, ancestor, other)
    full_formating = local_formating.copy()
    for key, value in other_formating.iteritems():
        if key in local_formating:
            value = value | local_formating[key]
        full_formating[key] = value

    all = [
        (local, local_formating),
        (other, other_formating),
        (ancestor, full_formating)
    ]
    for ctx, formatting in all:
        for tool, patterns in formatting.iteritems():
            formatting[tool] = rootedmatch(repo, ctx, patterns)

    final = tuple(formatting for __, formatting in all)
    getattr(repo, '_formatting_cache', {})[cachekey] = cached

    return final

def rootedmatch(repo, ctx, patterns):
    """match patterns agains the root of a repository"""
    # rework of basectx.match to ignore current working directory

    # Only a case insensitive filesystem needs magic to translate user input
    # to actual case in the filesystem.
    icasefs = not util.fscasesensitive(repo.root)
    if util.safehasattr(match, 'icasefsmatcher'): #< hg 4.3
        if icasefs:
            return match.icasefsmatcher(repo.root, repo.root, patterns,
                                        default='glob', auditor=repo.auditor,
                                        ctx=ctx)
        else:
            return match.match(repo.root, repo.root, patterns, default='glob',
                               auditor=repo.auditor, ctx=ctx)
    else:
        return match.match(repo.root, repo.root, patterns, default='glob',
                           auditor=repo.auditor, ctx=ctx, icasefs=icasefs)

def apply_formating(repo, formatting, fctx):
    """apply formatting to a file context (if applicable)"""
    data = None
    for tool, matcher in sorted(formatting.items()):
        # matches?
        if matcher(fctx.path()):
            if data is None:
                data = fctx.data()
            shell_tool = repo.ui.config('format-source', tool)
            if not shell_tool:
                msg = _("format-source, no command defined for '%s',"
                        " skipping formating: '%s'\n")
                msg %= (tool, fctx.path())
                repo.ui.warn(msg)
                continue
            with tempfile.NamedTemporaryFile(mode='wb') as f:
                f.write(data)
                f.flush()
                data = run_tools(repo.ui, repo.root, tool, shell_tool, f.name)
    if data is not None:
        fctx.data = lambda: data

def wrap_filemerge(origfunc, premerge, repo, mynode, orig, fcd, fco, fca,
                   *args, **kwargs):
    """wrap the file merge logic to apply formatting on files that needs them"""
    local = fcd._changectx
    other = fco._changectx
    ances = fca._changectx
    all = allformatted(repo, local, other, ances)
    local_formating, other_formating, full_formating = all
    apply_formating(repo, local_formating, fco)
    apply_formating(repo, other_formating, fcd)
    apply_formating(repo, full_formating, fca)

    if 'data' in vars(fcd): # XXX hacky way to check if data overwritten
        file_path = repo.wvfs.join(fcd.path())
        with open(file_path, 'wb') as local_file:
            local_file.write(fcd.data())

    return origfunc(premerge, repo, mynode, orig, fcd, fco, fca,
                    *args, **kwargs)

def wrap_update(orig, repo, *args, **kwargs):
    """install the formatting cache"""
    repo._formatting_cache = {}
    try:
        return orig(repo, *args, **kwargs)
    finally:
        del repo._formatting_cache


def uisetup(self):
    extensions.wrapfunction(filemerge, '_filemerge', wrap_filemerge)
    extensions.wrapfunction(merge, 'update', wrap_update)
