# Copyright(c) 2016 Nippon Telegraph and Telephone Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import socket

import eventlet
from oslo_log import log as oslo_logging
from oslo_utils import timeutils

import masakarimonitors.conf
from masakarimonitors.ha import masakari
import masakarimonitors.hostmonitor.host_handler.driver as driver
from masakarimonitors.hostmonitor.host_handler import hold_host_status
from masakarimonitors.hostmonitor.host_handler import parse_cib_xml
from masakarimonitors.i18n import _LE
from masakarimonitors.i18n import _LI
from masakarimonitors.i18n import _LW
from masakarimonitors.objects import event_constants as ec
from masakarimonitors import utils

LOG = oslo_logging.getLogger(__name__)
CONF = masakarimonitors.conf.CONF


class HandleHost(driver.DriverBase):
    """Handle hosts.

    This class handles the host status.
    """

    def __init__(self):
        super(HandleHost, self).__init__()
        self.my_hostname = socket.gethostname()
        self.xml_parser = parse_cib_xml.ParseCibXml()
        self.status_holder = hold_host_status.HostHoldStatus()
        self.notifier = masakari.SendNotification()

    def _check_pacemaker_services(self, target_service):
        try:
            cmd_str = 'systemctl status ' + target_service
            command = cmd_str.split(' ')

            # Execute command.
            out, err = utils.execute(*command, run_as_root=True)

            if err:
                raise Exception

            return True

        except Exception:
            return False

    def _check_hb_line(self):
        """Check whether the corosync communication is normal.

        :returns: 0 if normal, 1 if abnormal, 2 if configuration file is
            wrong or neither pacemaker nor pacemaker-remote is running.
        """
        # Check whether the pacemaker services is normal.
        corosync_status = self._check_pacemaker_services('corosync')
        pacemaker_status = self._check_pacemaker_services('pacemaker')
        pacemaker_remote_status = self._check_pacemaker_services(
            'pacemaker_remote')

        if corosync_status is False or pacemaker_status is False:
            if pacemaker_remote_status is False:
                LOG.error(
                    _LE("Neither pacemaker nor pacemaker-remote is running."))
                return 2
            else:
                LOG.info(_LI("Works on pacemaker-remote."))
                return 0

        # Check whether the neccesary parameters are set.
        if CONF.host.corosync_multicast_interfaces is None or \
            CONF.host.corosync_multicast_ports is None:
            msg = ("corosync_multicast_interfaces or "
                   "corosync_multicast_ports is not set.")
            LOG.error(_LE("%s"), msg)
            return 2

        # Check whether the corosync communication is normal.
        corosync_multicast_interfaces = \
            CONF.host.corosync_multicast_interfaces.split(',')
        corosync_multicast_ports = \
            CONF.host.corosync_multicast_ports.split(',')

        if len(corosync_multicast_interfaces) != len(corosync_multicast_ports):
            msg = ("Incorrect parameters corosync_multicast_interfaces or "
                   "corosync_multicast_ports.")
            LOG.error(_LE("%s"), msg)
            return 2

        is_nic_normal = False
        for num in range(0, len(corosync_multicast_interfaces)):
            cmd_str = ("timeout %s tcpdump -n -c 1 -p -i %s port %s") \
                % (CONF.host.tcpdump_timeout,
                   corosync_multicast_interfaces[num],
                   corosync_multicast_ports[num])
            command = cmd_str.split(' ')

            try:
                # Execute crmadmin command.
                out, err = utils.execute(*command, run_as_root=True)

                # If command doesn't raise exception, nic is normal.
                msg = ("Corosync communication using '%s' is normal.") \
                    % corosync_multicast_interfaces[num]
                LOG.info(_LI("%s"), msg)
                is_nic_normal = True
                break
            except Exception:
                msg = ("Corosync communication using '%s' is failed.") \
                    % corosync_multicast_interfaces[num]
                LOG.warning(_LW("%s"), msg)

        if is_nic_normal is False:
            LOG.error(_LE("Corosync communication is failed."))
            return 1

        return 0

    def _check_host_status_by_crmadmin(self):
        try:
            # Execute crmadmin command.
            out, err = utils.execute('crmadmin', '-S', self.my_hostname,
                                     run_as_root=True)

            if err:
                msg = ("crmadmin command output stderr: %s") % err
                raise Exception(msg)

            # If own host is stable status, crmadmin outputs
            # 'S_IDLE' or 'S_NOT_DC'
            if 'S_IDLE' in out or 'S_NOT_DC' in out:
                return 0
            else:
                raise Exception(
                    "crmadmin command output unexpected host status.")

        except Exception as e:
            LOG.warning(_LW("Exception caught: %s"), e)
            LOG.warning(_LW("'%s' is unstable state on cluster."),
                        self.my_hostname)
            return 1

    def _get_cib_xml(self):
        try:
            # Execute cibadmin command.
            out, err = utils.execute('cibadmin', '--query', run_as_root=True)

            if err:
                msg = ("cibadmin command output stderr: %s") % err
                raise Exception(msg)

        except Exception as e:
            LOG.warning(_LW("Exception caught: %s"), e)
            return

        return out

    def _is_poweroff(self, hostname):
        ipmi_values = self.xml_parser.get_stonith_ipmi_params(hostname)
        if ipmi_values is None:
            LOG.error(_LE("Failed to get params of ipmi RA."))
            return False

        cmd_str = ("timeout %s ipmitool -U %s -P %s -I %s -H %s "
                   "power status") \
            % (str(CONF.host.ipmi_timeout), ipmi_values['userid'],
               ipmi_values['passwd'], ipmi_values['interface'],
               ipmi_values['ipaddr'])
        command = cmd_str.split(' ')

        retry_count = 0
        while True:
            try:
                # Execute ipmitool command.
                out, err = utils.execute(*command, run_as_root=False)

                if err:
                    msg = ("ipmitool command output stderr: %s") % err
                    raise Exception(msg)

                msg = ("ipmitool command output stdout: %s") % out

                if 'Power is off' in out:
                    LOG.info(_LI("%s"), msg)
                    return True
                else:
                    raise Exception(msg)

            except Exception as e:
                if retry_count < CONF.host.ipmi_retry_max:
                    LOG.warning(_LW("Retry executing ipmitool command. (%s)"),
                                e)
                    retry_count = retry_count + 1
                    eventlet.greenthread.sleep(CONF.host.ipmi_retry_interval)
                else:
                    LOG.error(_LE("Exception caught: %s"), e)
                    return False

    def _make_event(self, hostname, current_status):

        if current_status == 'online':
            # Set values that host has started.
            event_type = ec.EventConstants.EVENT_STARTED
            cluster_status = current_status.upper()
            host_status = ec.EventConstants.HOST_STATUS_NORMAL

        else:
            # Set values that host has stopped.
            event_type = ec.EventConstants.EVENT_STOPPED
            cluster_status = current_status.upper()

            if not CONF.host.disable_ipmi_check:
                if self._is_poweroff(hostname):
                    # Set value that host status is normal.
                    host_status = ec.EventConstants.HOST_STATUS_NORMAL
                else:
                    # Set value that host status is unknown.
                    host_status = ec.EventConstants.HOST_STATUS_UNKNOWN
            else:
                # Set value that host status is normal.
                host_status = ec.EventConstants.HOST_STATUS_NORMAL

        current_time = timeutils.utcnow()
        event = {
            'notification': {
                'type': ec.EventConstants.TYPE_COMPUTE_HOST,
                'hostname': hostname,
                'generated_time': current_time,
                'payload': {
                    'event': event_type,
                    'cluster_status': cluster_status,
                    'host_status': host_status
                }
            }
        }

        return event

    def _check_if_status_changed(self, node_state_tag_list):

        # Check if host status changed.
        for node_state_tag in node_state_tag_list:

            # hostmonitor doesn't monitor itself.
            if node_state_tag.get('uname') == self.my_hostname:
                continue

            # Get current status and old status.
            current_status = node_state_tag.get('crmd')
            old_status = self.status_holder.get_host_status(
                node_state_tag.get('uname'))

            # If old_status is None, This is first get of host status.
            if old_status is None:
                msg = ("Recognized '%s' as a new member of cluster."
                       " Host status is '%s'.") \
                    % (node_state_tag.get('uname'), current_status)
                LOG.info(_LI("%s"), msg)
                self.status_holder.set_host_status(node_state_tag)
                continue

            # Output host status.
            msg = ("'%s' is '%s'.") % (node_state_tag.get('uname'),
                                       current_status)
            LOG.info(_LI("%s"), msg)

            # If host status changed, send a notification.
            if current_status != old_status:
                if current_status != 'online' and current_status != 'offline':
                    # If current_status is not 'online' or 'offline',
                    # hostmonitor doesn't send a notification.
                    msg = ("Since host status is '%s',"
                           " hostmonitor doesn't send a notification.") \
                        % current_status
                    LOG.info(_LI("%s"), msg)
                else:
                    event = self._make_event(node_state_tag.get('uname'),
                                             current_status)

                    # Send a notification.
                    self.notifier.send_notification(
                        CONF.host.api_retry_max,
                        CONF.host.api_retry_interval,
                        event)

            # Update host status.
            self.status_holder.set_host_status(node_state_tag)

    def _check_host_status_by_cibadmin(self):
        # Get xml of cib info.
        cib_xml = self._get_cib_xml()
        if cib_xml is None:
            # cibadmin command failure.
            return 1

        # Set to the ParseCibXml object.
        self.xml_parser.set_cib_xml(cib_xml)

        # Check if pacemaker cluster have quorum.
        if self.xml_parser.have_quorum() == 0:
            msg = "Pacemaker cluster doesn't have quorum."
            LOG.warning(_LW("%s"), msg)

        # Get node_state tag list.
        node_state_tag_list = self.xml_parser.get_node_state_tag_list()
        if len(node_state_tag_list) == 0:
            # If cib xml doesn't have node_state tag,
            # it is an unexpected result.
            raise Exception(
                "Failed to get node_state tag from cib xml.")

        # Check if status changed.
        self._check_if_status_changed(node_state_tag_list)

        return 0

    def stop(self):
        self.running = False

    def monitor_hosts(self):
        """Host monitoring main method.

        This method monitors hosts.
        """
        try:
            self.running = True
            while self.running:

                # Check whether corosync communication between hosts
                # is normal.
                ret = self._check_hb_line()
                if ret == 1:
                    # Because my host may be fenced by stonith due to split
                    # brain condition, sleep for a certain time.
                    eventlet.greenthread.sleep(CONF.host.stonith_wait)
                elif ret == 2:
                    LOG.warning(_LW("hostmonitor skips monitoring hosts."))
                    eventlet.greenthread.sleep(CONF.host.monitoring_interval)
                    continue

                # Check the host status is stable or unstable by crmadmin.
                # It only checks when this process runs on the full cluster
                # stack of corosync.
                pacemaker_remote_status = self._check_pacemaker_services(
                    'pacemaker_remote')
                if pacemaker_remote_status is False:
                    if self._check_host_status_by_crmadmin() != 0:
                        LOG.warning(_LW("hostmonitor skips monitoring hosts."))
                        eventlet.greenthread.sleep(
                            CONF.host.monitoring_interval)
                        continue

                # Check the host status is online or offline by cibadmin.
                if self._check_host_status_by_cibadmin() != 0:
                    LOG.warning(_LW("hostmonitor skips monitoring hosts."))
                    eventlet.greenthread.sleep(CONF.host.monitoring_interval)
                    continue

                eventlet.greenthread.sleep(CONF.host.monitoring_interval)

        except Exception as e:
            LOG.exception(_LE("Exception caught: %s"), e)

        return
