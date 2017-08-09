#!/usr/bin/env python
# http://www.apache.org/licenses/LICENSE-2.0.txt
#
# Copyright 2016 Intel Corporation
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

import json
import os
import sys
import time
from queue import Empty, Queue

import snap_plugin.v1 as snap
from diamond.handler.Handler import Handler


class SnapHandler(Handler):
    """SnapHandler is a diamond handler that transforms the diamond metric into
    a snap metric.

    SnapHandlers are registered for all diamond plugins which are enabled
    through the user supplied config.
    """
    def __init__(self, **kwargs):
        super(SnapHandler, self).__init__(**kwargs)
        self._queue = Queue()

    def process(self, metric):
        snap_metric = snap.Metric(
            namespace=("diamond", metric.getCollectorPath(), metric.getMetricPath()),
            tags={
                "plugin_running_on": metric.host,
                "metric_type": metric.metric_type,
            },
            timestamp=time.time(),
            data=metric.value
        )
        self._queue.put(snap_metric)

    def get_default_config_help(self):
        pass

    def get_default_config(self):
        config = super(SnapHandler, self).get_default_config()
        config.update({
        })
        return config

    def get_metrics(self):
        metrics = []
        while True:
            try:
                metrics.append(self._queue.get_nowait())
            except Empty:
                break
        return metrics


class DiamondCollector(snap.Collector):
    """DiamondCollector is a snap plugin that wraps Diamond plugins making them
    available to Snap.

    Before the snap diamond collector can be loaded it requires configuration
    items defining 'collector_path', where to find the diamond collectors (py
    files) and 'config' valid json that describes which diamond collectors will
    enabled.  Below is an example config provided to snapteld on startup
    (snapteld -t 0 -l 1 --config diamond.yml):

    ---
    control:
    plugins:
        collector:
        diamond:
            versions:
            1:
                collectors_path: "/etc/diamond/collectors"
                config: |
                    {"collectors":{
                            "PingCollector": {"target_google": "8.8.8.8",
                                            "target_grafana": "grafana.net",
                                            "bin": "/bin/ping"},
                            "CPUCollector": {},
                            "DiskUsageCollector": {},
                            "MemoryCollector": {},
                            "IPCollector": {},
                            "VMStatCollector": {}
                    }}

    The above yaml based config tells snap where it can find the diamond
    collectors and which diamond collectors should be loaded and the config
    specific to those collectors if needed.

    How it works:
        The plugin is initialized when the first call to update_catalog or
        collect is made.  The initialization process is a straightforward
        process that involves the following steps:

        1. The diamond configuration is processed
            1a. For each collector defined and instance of the plugin is created
                In the example above 'PingCollector' would be loaded by
                dynamically importing the module 'ping' from the collectors_path
                provided by the user and instantiating an instance of the class
                pass through whatever diamond specific configuration the user
                provided.
            2b. An instance of the SnapHandler is added to the diamond plugin
                instance.
            3c. The plugin_instance is stored saved for future use.

        On update_catalog:
            After initialization we loop over the enabled diamond plugins
            calling collect.  The SnapHandler is automatically called for every
            collect call which transforms the metrics into snap.Metric.  After
            retrieving all of the snap metrics from the handlers we return the
            resulting metrics to the snap metric and they are published to the
            catalog

        On collect:
            On collect we follow the same process just described for updating
            the catalog however on collect we filter out any metrics that were
            not requested.
    """
    def __init__(self, *args, **kwargs):
        super(DiamondCollector, self).__init__(*args, **kwargs)
        self._diamond_plugins = dict()
        self._is_initialized = False

    def collect(self, metrics):
        # initialize the plugin on first collect
        if not self._is_initialized:
            self._init(metrics[0].config)
        # group metrics by (diamond) plugin
        metrics_to_return = []
        metrics_by_plugin = {}
        for metric in metrics:
            if metric.namespace[1].value not in metrics_by_plugin:
                metrics_by_plugin[metric.namespace[1].value] = []
            metrics_by_plugin[metric.namespace[1].value].append(metric)
        # collect
        for (module_name, metric) in metrics_by_plugin.items():
            self._diamond_plugins[module_name].collect()
            for met in self._diamond_plugins[module_name].handlers[0].get_metrics():
                ns_values = [i.value for i in met.namespace]
                for requested_metric in metrics:
                    if ns_values == [n.value for n in requested_metric.namespace]:
                        metrics_to_return.append(met)
        return metrics_to_return

    def update_catalog(self, config):
        metrics = []
        self._init(config)
        for (_, plugin_instance) in self._diamond_plugins.items():
            # add the plugin's metrics to metrics to be returned
            plugin_instance.collect()
            for met in plugin_instance.handlers[0].get_metrics():
                metrics.append(met)
        return metrics

    def get_config_policy(self):
        return snap.ConfigPolicy(
            [
                ("diamond"),
                [
                    ("config", snap.StringRule(required=True)),
                    ("collectors_path", snap.StringRule(default="/usr/share/diamond/collectors"))
                ]
            ]
        )

    def _init(self, config):
        if "config" in config:
            diamond_cfg = json.loads(config["config"])
            if "collectors" in diamond_cfg:
                diamond_collector_cfg = diamond_cfg["collectors"]
                for collector_name in diamond_collector_cfg:
                    snap.LOG.debug("Found '%s' plugin configuration", collector_name)
                    module_name = collector_name.replace("Collector", "").lower()
                    # update path
                    sys.path.append("{}/{}".format(config["collectors_path"], module_name))
                    # import module
                    try:
                        module = __import__(module_name)
                        # get class def
                        plugin_class = getattr(module, collector_name)
                    except ImportError as err:
                        snap.LOG.fatal("Unable to import %s (%s)", collector_name, err.message)
                        sys.exit(1)
                    # create instance of the class
                    plugin_instance = plugin_class(config=diamond_cfg)
                    # add snap_handler to the plugin instance
                    plugin_instance.handlers.append(SnapHandler(config={}))
                    # add the plugin instance to self._diamond_plugins
                    self._diamond_plugins[module_name] = plugin_instance
            else:
                snap.LOG.warning("No 'diamond' collector configurations provided")
        else:
            snap.LOG.warning("No 'diamond' configuration provided.")
        self._is_initialized = True

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
