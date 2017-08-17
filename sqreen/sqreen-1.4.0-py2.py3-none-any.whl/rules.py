# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Callbacks rules classes and helpers
"""
import logging
from datetime import datetime

from .callbacks import Callback
from .events import Attack, get_context_payload
from .runtime_infos import RuntimeInfos, runtime
from .runner import MetricsEvent
from .condition_evaluator import ConditionEvaluator, is_condition_empty
from .constants import LIFECYCLE_METHODS
from .rules_call_count import call_count_wrapper
from .rules_check_condition import check_condition_wrapper

LOGGER = logging.getLogger(__name__)


def record_observation(observation_queue, queue, metric_name, key, observation, at=None):
    """
    """
    if at is None:
        at = datetime.utcnow()

    observation_queue.put((metric_name, at, key, observation))

    # Ask the runner thread to aggregate and empty the observation queue
    if observation_queue.half_full():
        queue.put(MetricsEvent)


class RuleCallback(Callback):

    def __init__(self, hook_module, hook_name, rule_name, rulespack_id,
                 block, test, runner, strategy_cls=None, data=None,
                 conditions=None, callbacks=None, call_count_interval=0,
                 metrics=None):
        super(RuleCallback, self).__init__(hook_module, hook_name, strategy_cls)
        self.rule_name = rule_name
        self.rulespack_id = rulespack_id

        if data is None:
            data = {}
        self.data = data
        self.block = block
        self.test = test
        self.runner = runner
        self.metrics = metrics

        if conditions is None:
            conditions = {}
        self.conditions = conditions

        self.callbacks = callbacks

        # Callbacks
        self.call_count_interval = call_count_interval
        self.call_counts = {'pre': 0, 'post': 0, 'failing': 0}

        self._apply_conditions()
        self._apply_call_count()

    @classmethod
    def from_rule_dict(cls, rule_dict, runner):
        """ Return a RuleCallback based on a rule dict
        """
        return cls(
            hook_module=rule_dict['hookpoint']['klass'],
            hook_name=rule_dict['hookpoint']['method'],
            rule_name=rule_dict['name'],
            rulespack_id=rule_dict['rulespack_id'],
            strategy_cls=rule_dict['hookpoint'].get('strategy', 'import_hook'),
            block=rule_dict['block'],
            test=rule_dict['test'],
            data=rule_dict.get('data'),
            conditions=rule_dict.get('conditions'),
            callbacks=rule_dict.get('callbacks'),
            call_count_interval=rule_dict.get('call_count_interval', 0),
            runner=runner,
            metrics=rule_dict.get('metrics', [])
        )

    def _apply_conditions(self):
        """ Wrap each lifecycle methods if the Rule define them and if we have
        conditions for them.
        """
        for lifecycle in LIFECYCLE_METHODS.values():
            conditions = self.conditions.get(lifecycle)

            if not is_condition_empty(conditions) and hasattr(self, lifecycle):
                conditions = ConditionEvaluator(conditions)

                # Wrap the lifecycle method
                lifecycle_method = getattr(self, lifecycle)
                wrapped = check_condition_wrapper(self.data, lifecycle_method,
                                                  conditions, lifecycle)
                setattr(self, lifecycle, wrapped)

    def _apply_call_count(self):
        # Only count calls if call_count_interval is > 0
        if self.call_count_interval == 0:
            return

        for lifecycle in LIFECYCLE_METHODS.values():
            if hasattr(self, lifecycle):
                lifecycle_method = getattr(self, lifecycle)

                observation_key = '%s/%s/%s' % (self.rulespack_id,
                                                self.rule_name, lifecycle)

                wrapped = call_count_wrapper(lifecycle_method, lifecycle,
                                             self.call_count_interval,
                                             observation_key, self)
                setattr(self, lifecycle, wrapped)

    def exception_infos(self, infos={}):
        """ Returns additional infos in case of exception
        """
        return {
            'rule_name': self.rule_name,
            'rulespack_id': self.rulespack_id,
            'should_block': self.should_block()
        }

    def should_block(self):
        """ Return True if this rule should catch an attack based on block
        and test value
        """
        return ((not self.test) and self.block)

    def record_attack(self, infos=None):
        """ Record an attack
        """
        current_request = runtime.get_current_request()

        if current_request is None:
            LOGGER.warning("No request was recorded, couldn't record an attack")
            return

        current_time = RuntimeInfos()._time()['time']

        attack_payload = {
            'rule_name': self.rule_name,
            'rulespack_id': self.rulespack_id,
            'client_ip': current_request.client_ip,
            'headers': current_request.get_client_ips_headers(),
            'time': current_time,
            'test': self.test,
            'block': self.block,
            'infos': infos
        }
        attack_payload.update(current_request.full_payload)
        attack_payload.update(get_context_payload())

        # Whitelisted paths
        attack_payload.update(self.whitelist_path(current_request))

        attack = Attack(attack_payload)
        self.runner.queue.put(attack)

        LOGGER.debug("Attack was pushed to the queue: %s", attack_payload)

    def whitelist_path(self, current_request):
        """ Alter the attack payload if the request patch match a whitelist path
        """
        request_path = current_request.path
        whitelist_match = self.runner.settings.paths_whitelist_match(request_path)
        if whitelist_match is not None:
            return {'block': False, 'whitelist_match': whitelist_match}

        return {}

    def record_observation(self, metric_name, key, observation, at=None):
        """ Record a metric observation, push it to runner
        observations queue
        """
        record_observation(self.runner.observation_queue, self.runner.queue,
                           metric_name, key, observation, at)

    def __repr__(self):
        return "%s(rule_name=%r)" % (self.__class__.__name__, self.rule_name)
