"""Propriecle grab bag"""
import sys
import os
import time
from random import SystemRandom
import curses
import traceback
import requests
import hvac
import yaml
from hashlib import sha256
from propriecle.ui import string_at, middle_yx, pulse, yesno, \
    popup, init_screen, ask_for
from propriecle.helpers import problems, do_write, finish
from propriecle.vault import seal, unseal, am_root, root_client, \
    rekey_start, rotate_master, regenerate_start, init, \
    regenerate_enter, regenerate_cancel, rekey_enter, rekey_cancel, \
    step_down
from propriecle.keys import list_keys, grok_keys, grok_key
from propriecle.servers import get_server
import propriecle.conf as conf


def update_servers():
    """Kicks off the update process for our Vault servers"""
    servers = []
    for server in conf.get('vaults'):
        servers.append(get_server(server['name']))

    return servers


def do_seal(screen, server):
    """Invoke the GUI action of sealing Vault"""
    client = server['client']
    name = server['name']

    seal_msg = "SEAL %s" % name
    if not yesno(screen, seal_msg):
        return
    screen.refresh()

    try:
        if not seal(server):
            popup(screen, "Unable to seal!")
    except hvac.exceptions.Forbidden:
        popup(screen, "Invalid root token!")
        return


def do_rekey(server):
    """Invoke the GUI action of rekeying unseal keys"""
    if not conf.get('keys') or not conf.get('required'):
        problems('keys and required missing from config')

    rekey_start(server, grok_keys())


def get_keys(screen, server):
    """Generates a list of keys for the user to select from.
    Options also include manually entering a key or using
    any valid key"""
    client = server['client']
    keys = list_keys(server)
    middle_y, middle_x = middle_yx(screen)
    my_x = 30
    my_y = len(keys) + 6
    win_x = middle_x - (my_x/2)
    win_y = middle_y - 10
    win = curses.newwin(my_y, my_x, win_y, win_x)
    status = client.seal_status

    done = False
    selection = 0
    return_keys = []
    while not done:
        win.border()
        win.bkgd(ord(' '), curses.color_pair(1))
        win.addstr(1, 1, "Select Key (%s of %s complete)" %
                   (status['progress'], status['t']),
                   curses.color_pair(2))
        win.addstr(my_y - 2, 1, "[m]anual [a]ny", curses.color_pair(1))
        for key_obj in keys:
            name = key_obj['name']
            i = key_obj['index']
            color = curses.color_pair(2)
            if not key_obj['key']:
                color = curses.color_pair(4)

            if selection == i:
                color = curses.color_pair(6)

            if name.startswith('keybase:'):
                name = name[8:]

            win.addstr(i + 2, 1, "[%s] %s" % (i + 1, name), color)

        win.refresh()
        screen.timeout(500)
        ch = screen.getch()
        if ch == 27:
            del win
            screen.refresh()
            return
        elif ch == curses.KEY_DOWN:
            down_done = False
            while not down_done:
                if selection < len(keys) - 1 and \
                   keys[selection + 1]['key']:
                    selection = selection + 1
                    down_done = True
                elif selection == len(keys) - 1:
                    down_done = True
                else:
                    selection = selection + 1
        elif ch == curses.KEY_UP:
            up_done = False
            while not up_done:
                if selection > 0 and \
                   keys[selection - 1]['key']:
                    selection = selection - 1
                    up_done = True
                elif selection == 0:
                    up_done = True
                else:
                    selection = selection - 1
        elif ch == ord('m') or ch == ord('M'):
            return ask_for(screen, "Key")
        elif ch == ord('a') or ch == ord('A'):
            return_keys = [k for k in keys if k['key']][0:conf.get('required')]
            done = True
        elif ch == 10:
            if keys[selection]['key']:
                done = True

    win.erase()
    win.refresh()
    del win

    if len(return_keys) == 0:
        return_keys = [k for k in keys if k['index'] == selection]

    return return_keys


def do_unseal(screen, server):
    """Invoke the GUI action of unsealing a Vault server"""
    client = server['client']
    status = client.seal_status
    if not status['sealed']:
        popup(screen, "Not actually sealed")
        return

    for key_obj in do_get_keys(screen, server):
        try:
            unseal(client, key_obj['key'])
        except hvac.exceptions.InvalidRequest:
            popup(screen, "Unable to unseal with %s:%s" %
                  (key_obj['index'], key_obj['name']))
            popup(screen, "Invalid Key!")


def refresh_screen(screen, selection, main_win=None):
    """Refreshes the GUI elements of the main screen"""
    y, x = screen.getmaxyx()
    main_x = x - (x / 4)
    main_y = len(conf.get('vaults')) + 5
    if y < main_y or x < main_x:
        problems("screen too small")

    screen.border()
    screen.bkgd(ord(' '), curses.color_pair(1))

    middle_y, middle_x = middle_yx(screen)
    if not main_win:
        main_win = curses.newwin(main_y, main_x,
                                 middle_y - (main_y/2),
                                 middle_x - (main_x/2))
    else:
        main_win.erase()

    main_win.bkgd(ord(' '), curses.color_pair(1))
    main_win.border()
    string_at(main_win, 1, 0, "Vault Friends", curses.color_pair(1), 'center')
    refresh_status(main_win, selection)
    screen.nooutrefresh()
    main_win.nooutrefresh()
    curses.doupdate()
    return main_win


def refresh_initialized(main_win, server, index, selected):
    """Refreshes the lable for a initialized Vault instance"""
    y, x = main_win.getmaxyx()
    name = server['name']
    if server['init'] and not server['sealed'] and server['ha']:
        c_state = 'S'
        if server['leader']:
            c_state = 'L'

        name = "%s [%s %s]" % (server['name'], c_state, server['cluster_name'])

    name_msg = "[%s] %s" % (index, name)
    base_x = len(name_msg) + 1
    line = index + 3
    col = curses.color_pair(1)
    if selected:
        col = curses.color_pair(6)

    string_at(main_win, line, 0, name_msg, col)
    if server['sealed']:
        s_msg = "Sealed"
        string_at(main_win, line, base_x, s_msg, curses.color_pair(3))
    else:
        s_msg = 'OK'
        s_col = 2
        if server['rekey']:
            s_msg = 'REKEY'
            s_col = 7

        string_at(main_win, line, base_x, s_msg, curses.color_pair(s_col))


def randcolor():
    """A random pretty color plz"""
    s_color = 0
    s_rand = SystemRandom().randint(0, 2)
    if s_rand == 0:
        s_color = 1
    elif s_rand == 1:
        s_color = 3
    elif s_rand == 2:
        s_color = 7

    if SystemRandom().randint(0, 1) == 1:
        s_color = s_color | curses.A_BOLD

    return s_color


def refresh_uninitialized(main_win, server, selected, index):
    """Refreshes the label for a uninitialized Vault instance"""
    y, x = main_win.getmaxyx()
    name = server['name']
    name_msg = "[%s] %s" % (index, name)
    base_x = len(name_msg) + 1
    new_msg = 'NEW'
    line = index + 3
    col = curses.color_pair(1)
    if selected:
        col = curses.color_pair(6)

    string_at(main_win, line, 0, name_msg, col)
    string_at(main_win, line,
              base_x, new_msg,
              curses.color_pair(7) | curses.A_BOLD)
    s_anim = ['*', 'o', '.', '^', '_', '-', '|']

    for f in range(0, 5):
        string_at(main_win,
                  line,
                  base_x + len(new_msg) + 2 + f,
                  s_anim[SystemRandom().randint(0, len(s_anim) - 1)],
                  curses.color_pair(randcolor()))


def refresh_offline(main_win, server, selected, index):
    """Refreshes the label for a offline Vault instance"""
    y, x = main_win.getmaxyx()
    name = server['name']
    name_msg = "[%s] %s" % (index, name)
    base_x = len(name_msg) + 1
    new_msg = 'AWOL'
    line = index + 3
    col = curses.color_pair(1)
    if selected:
        col = curses.color_pair(6)

    string_at(main_win, line, 0, name_msg, col)
    string_at(main_win, line, base_x,
              new_msg, curses.color_pair(3) | curses.A_BOLD)


def refresh_status(main_win, selection):
    """Refreshes the label of a Vault instance"""
    y, x = main_win.getmaxyx()
    index = 0
    for server in update_servers():
        if 'init' in server:
            if server['init']:
                refresh_initialized(main_win, server,
                                    index, selection == index)
            else:
                refresh_uninitialized(main_win, server,
                                      selection == index, index)
        else:
            refresh_offline(main_win, server,
                            selection == index, index)

        index = index + 1


def focus_loop(screen, index):
    """Main interaction loop when an actual Vault instance is selected
    and we are looking at the detailed view."""
    done = False
    screen.erase()
    while not done:
        server = get_server(conf.get('vaults')[index]['name'])
        refresh_focused(screen, server)
        if focus_input(screen, server):
            screen.erase()
            return


def focus_input(screen, server):
    """User input for when we are in the detailed view of a Vault instance"""
    screen.timeout(500)
    ch = screen.getch()
    if ch == 27:
        return True

    if 'init' in server:
        if 255 > ch > 0:
            ch_s = chr(ch).lower()
            is_init = server['init']
            is_sealed = server['sealed']
            is_ha = server['ha']            
            if is_ha:
                is_leader = server['leader']

            is_rekey = server['rekey']
            is_regenerating = server['regenerating']
            if ch_s == 's' and is_init and not is_sealed:
                if not is_ha or (is_ha and is_leader):
                    do_seal(screen, server)
            elif ch_s == 'u' and is_init and is_sealed:
                do_unseal(screen, server)
            elif ch_s == 'r' and is_init and not is_sealed and not is_rekey:
                do_rekey(server)
            elif ch_s == 'i' and not is_init:
                do_init(screen, server)
            elif ch_s == 'e' and is_init and is_rekey:
                do_rekey_enter(screen, server)
            elif ch_s == 'c' and is_init and is_rekey:
                if not rekey_cancel(server):
                    popup(screen, "Unable to cancel rekey")
            elif ch_s == 'e' and is_init and is_regenerating:
                do_regenerate_enter(screen, server)
            elif ch_s == 'c' and is_init and is_regenerating:
                if not regenerate_cancel(server):
                    popup(screen, "Unable to cancel regeneration")
            elif ch_s == 'o' and is_init and not is_rekey and \
                 not is_regenerating and not is_sealed:
                if not rotate_master(server):
                    popup(screen, "Unable to rotate master")
            elif ch_s == 'g' and is_init and \
                 not is_rekey and \
                 not is_regenerating and \
                 not is_sealed:
                regenerate_start(server)
            elif ch_s == 'p' and is_init and \
                 is_ha and is_leader:
                step_down(server)


def do_get_keys(screen, server):
    """Selecting keys from a screen I guess"""
    keys = get_keys(screen, server)
    screen.nooutrefresh()
    if not keys:
        popup(screen, "Must specify at least one key")
        return []

    return keys


def do_regenerate_enter(screen, server):
    """GUI context for submitting unseal keys when
    regenerating root token"""
    for key_obj in do_get_keys(screen, server):
        if not regenerate_enter(server, key_obj['key']):
            popup(screen, "Unable to regenerate with %s:%s" %
                  (key_obj['index'], key_obj['name']))


def do_rekey_enter(screen, server):
    """GUI context for submitting unseal keys when rekeying"""
    for key_obj in do_get_keys(screen, server):
        if not rekey_enter(server, key_obj['key']):
            popup(screen, "Unable to rekey with %s:%s" %
                  (key_obj['index'], key_obj['name']))


def refresh_focused(screen, server):
    """Redraw the focus/detail view of a Vault instance"""
    win_x = 30 + len(server['url'])
    win_y = 10
    middle_y, middle_x = middle_yx(screen)
    win = curses.newwin(win_y, win_x,
                        middle_y - (win_y / 2),
                        middle_x - (win_x / 2))
    win.border()
    win.bkgd(ord(' '), curses.color_pair(1))
    string_at(win, 1, 0, server['name'], curses.color_pair(1), 'center')
    string_at(win, 2, 0, server['url'], curses.color_pair(1))
    if 'init' in server:
        if server['init']:
            string_at(win, 3, 0, server['version'], curses.color_pair(1))
            if server['sealed']:
                msg_s = 'SEALED'
                string_at(win, 5, 0, msg_s,
                          curses.color_pair(3) | curses.A_BOLD)
                unseal_remaining = server['unseal_required'] \
                                   - server['unseal_progress']
                msg_details = "%s keys required" % (unseal_remaining)
                string_at(win, 5, len(msg_s) + 1,
                          msg_details, curses.color_pair(1))
            else:
                msg_s = ''
                if server['rekey']:
                    msg_s = 'REKEY'
                    string_at(win, 5, 0,
                              msg_s, curses.color_pair(7))
                    rekey_remaining = server['rekey_required'] \
                                      - server['rekey_progress']
                    string_at(win, 6, 0,
                              "%s keys required" % (rekey_remaining),
                              curses.color_pair(1))
                elif (not server['ha'] or (server['ha'] and server['leader'])) \
                     and server['regenerating']:
                    msg_s = 'REGEN'
                    string_at(win, 5, 0,
                              msg_s, curses.color_pair(7))
                    string_at(win, 6, 0,
                              "%s keys required" %
                              (server['regen_required'] - server['regen_progress']),
                              curses.color_pair(1))
                else:
                    msg_s = 'OK'
                    string_at(win, 5, 0, msg_s, curses.color_pair(2))
                    if 'key_term' in server:
                        string_at(win, 6, 0,
                                  "Key Term %s" % server['key_term'],
                                  curses.color_pair(1))

                ha_msg = "HA"
                if server['ha']:
                    string_at(win, 5, len(msg_s) + 1,
                              ha_msg, curses.color_pair(1))
                    if server['leader']:
                        string_at(win, 5,
                                  len(msg_s) + len(ha_msg) +
                                  len(server['cluster_name']) + 3,
                                  "Leader", curses.color_pair(1))
                    else:
                        string_at(win, 5,
                                  len(msg_s) + len(ha_msg) +
                                  len(server['cluster_name']) + 3,
                                  "Standby", curses.color_pair(1))
                else:
                    ha_msg = ''

                string_at(win, 5,
                          len(ha_msg) + len(msg_s) + 2,
                          server['cluster_name'], curses.color_pair(1))
        else:
            string_at(win, 5, 0, "Uninitialized Vault", curses.color_pair(1))
    else:
        string_at(win, 4, 0,
                  'OFFLINE', curses.color_pair(3) | curses.A_BOLD, 'center')

    win.hline(win_y - 3, 1, curses.ACS_HLINE, win_x - 2)
    refresh_controls(win, server)
    win.refresh()


def refresh_controls(win, server):
    """Refresh our visible controls. This varies based on server state
    and authentication"""
    esc_msg = '[ESC] Quit'
    seal_msg = '[s]eal'
    unseal_msg = '[u]nseal'
    init_msg = '[i]nit'
    rekey_msg = '[r]ekey'
    cancel_msg = '[c]ancel'
    enter_msg = '[e]nter'
    rotate_msg = 'r[o]tate'
    regen_msg = "re[g]en"
    step_msg = 'ste[p]'

    line = win.getmaxyx()[0] - 2
    string_at(win, line, 0, esc_msg, curses.color_pair(1))
    next_x = len(esc_msg) + 2
    if 'init' in server:
        if not server['init']:
            string_at(win, line, next_x, init_msg, curses.color_pair(3))
        else:
            if server['sealed']:
                string_at(win, line, next_x, unseal_msg, curses.color_pair(1))
            else:
                if (not server['ha'] or (server['ha'] and server['leader'])) \
                   and (server['rekey'] or server['regenerating']):
                    string_at(win, line, next_x,
                              cancel_msg, curses.color_pair(7))
                    string_at(win, line,
                              next_x + len(cancel_msg) + 1,
                              enter_msg, curses.color_pair(1))
                else:
                    if server['is_root']:
                        if not server['ha'] or \
                           (server['ha'] and server['leader']):
                            string_at(win, line, next_x,
                                      seal_msg, curses.color_pair(3))
                            string_at(win, line,
                                      next_x + len(seal_msg) + 1,
                                      rekey_msg, curses.color_pair(1))
                            string_at(win, line,
                                      next_x + len(seal_msg) +
                                      len(rekey_msg) + 2,
                                      rotate_msg, curses.color_pair(1))
                            string_at(win, line,
                                      next_x + len(seal_msg) + len(rekey_msg) +
                                      len(rotate_msg) + 3,
                                      regen_msg, curses.color_pair(1))

                        if server['ha'] and server['leader']:
                            string_at(win, line,
                                      next_x + len(seal_msg) + len(rekey_msg) +
                                      len(rotate_msg) + len(regen_msg) + 4,
                                      step_msg, curses.color_pair(1))
                    else:
                        string_at(win, line, next_x,
                                  rekey_msg, curses.color_pair(1))
                        string_at(win, line,
                                  next_x + len(rekey_msg) + 2,
                                  regen_msg, curses.color_pair(1))


def do_init(screen, server):
    """GUI construct for initializing a blank Vault instance"""
    if not init(server):
        popup(screen, 'Unexpected return during vault init!')


def main_loop(screen):
    """Main interaction loop."""
    done = False
    selection = 0
    main_win = None
    while not done:
        main_win = refresh_screen(screen, selection, main_win)
        screen.timeout(500)
        ch = screen.getch()
        if ch == 27:
            screen.erase()
            screen.refresh()
            popup(screen, "Thank you for playing")
            curses.endwin()
            return
        elif ch == curses.KEY_DOWN:
            if selection < len(conf.get('vaults')) - 1:
                selection = selection + 1
        elif ch == curses.KEY_UP:
            if selection > 0:
                selection = selection - 1
        elif ch == 10:
            focus_loop(screen, selection)


def gui():
    """It's amazing what qualifies as a GUI these days"""
    update_servers()
    screen = init_screen()
    try:
        main_loop(screen)
        finish()
    except Exception:
        screen.erase()
        screen.move(1, 1)
        screen.refresh()
        curses.endwin()
        etype, val, trace = sys.exc_info()
        traceback.print_exception(etype, val, trace)
