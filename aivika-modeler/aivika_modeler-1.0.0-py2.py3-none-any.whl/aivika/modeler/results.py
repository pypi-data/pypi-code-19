# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

from simulation.aivika.modeler.util import *

def empty_results():
    """Return empty results."""
    return 'mempty'

def all_results():
    """Return all results."""
    return 'id'

class ResultSource:
    """Represents the result source."""

    def __init__(self):
        """Initializes a new instance by the specified name."""
        pass

class RawSource(ResultSource):
    """Represents the result source by the specified raw code."""

    def __init__(self, code):
        """Initializes a new instance by the specified code."""
        ResultSource.__init__(self)
        self._code = code

    def read_results(self):
        """Return the corresponding code."""
        return self._code

class SamplingStatsSource(ResultSource):
    """The result source for observation statistics based on samples."""

    def __init__(self, source):
        """Initializes a new instance by the specified result source."""
        ResultSource.__init__(self)
        self._source = source
        self.count = self._get_source_property('SamplingStatsCountId')
        self.min_value = self._get_source_property('SamplingStatsMinId')
        self.max_value = self._get_source_property('SamplingStatsMaxId')
        self.mean_value = self._get_source_property('SamplingStatsMeanId')
        self.mean2_value = self._get_source_property('SamplingStatsMean2Id')
        self.variance = self._get_source_property('SamplingStatsVarianceId')
        self.deviation = self._get_source_property('SamplingStatsDeviationId')

    def read_results(self):
        """Return the code that identifies the specified results."""
        return self._source.read_results()

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        return [self.count, self.min_value, self.max_value,
            self.mean_value, self.mean2_value, self.variance, self.deviation]

    def _get_source_property(self, result_id):
        """Return the specified property by the result identifier."""
        code = self._source.read_results()
        code += ' >>> expandResults >>> resultById '
        code += result_id
        return RawSource(code)

class TimingStatsSource(ResultSource):
    """The result source for time-persistent statistics."""

    def __init__(self, source):
        """Initializes a new instance by the specified result source."""
        ResultSource.__init__(self)
        self._source = source
        self.count = self._get_source_property('TimingStatsCountId')
        self.min_value = self._get_source_property('TimingStatsMinId')
        self.max_value = self._get_source_property('TimingStatsMaxId')
        self.mean_value = self._get_source_property('TimingStatsMeanId')
        self.variance = self._get_source_property('TimingStatsVarianceId')
        self.deviation = self._get_source_property('TimingStatsDeviationId')
        self.min_time = self._get_source_property('TimingStatsMinTimeId')
        self.max_time = self._get_source_property('TimingStatsMaxTimeId')
        self.start_time = self._get_source_property('TimingStatsStartTimeId')
        self.last_time = self._get_source_property('TimingStatsLastTimeId')
        self.sum_value = self._get_source_property('TimingStatsSumId')
        self.sum2_value = self._get_source_property('TimingStatsSum2Id')

    def read_results(self):
        """Return the code that identifies the specified results."""
        return self._source.read_results()

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        return [self.count, self.min_value, self.max_value,
            self.mean_value, self.variance, self.deviation,
            self.min_time, self.max_time, self.start_time, self.last_time,
            self.sum_value, self.sum2_value]

    def _get_source_property(self, result_id):
        """Return the specified property by the result identifier."""
        code = self._source.read_results()
        code += ' >>> expandResults >>> resultById '
        code += result_id
        return RawSource(code)

class PortSource(ResultSource):
    """Represents the result source originated from the port."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        ResultSource.__init__(self)
        self._port = port

    def read_results(self):
        """Return the code that identifies the specified results."""
        return 'resultByName ' + encode_str(self._port.get_source_name())

    def _get_source_property(self, result_id):
        """Return the specified property by the result identifier."""
        code = self.read_results()
        code += ' >>> resultById '
        code += result_id
        return RawSource(code)

class ResourceSource(PortSource):
    """Represents the resource result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.count = self._get_source_property('ResourceCountId')
        self.count_stats = TimingStatsSource(self._get_source_property('ResourceCountStatsId'))
        self.utilisation_count = self._get_source_property('ResourceUtilisationCountId')
        self.utilisation_count_stats = TimingStatsSource(self._get_source_property('ResourceUtilisationCountStatsId'))
        self.queue_count = self._get_source_property('ResourceQueueCountId')
        self.queue_count_stats = TimingStatsSource(self._get_source_property('ResourceQueueCountStatsId'))
        self.total_wait_time = self._get_source_property('ResourceTotalWaitTimeId')
        self.wait_time = SamplingStatsSource(self._get_source_property('ResourceWaitTimeId'))

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources.append(self.count)
        sources += self.count_stats.expand_results()
        sources.append(self.utilisation_count)
        sources += self.utilisation_count_stats.expand_results()
        sources.append(self.queue_count)
        sources += self.queue_count_stats.expand_results()
        sources.append(self.total_wait_time)
        sources += self.wait_time.expand_results()
        return sources

class PreemptibleResourceSource(PortSource):
    """Represents the preemptible resource result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.count = self._get_source_property('ResourceCountId')
        self.count_stats = TimingStatsSource(self._get_source_property('ResourceCountStatsId'))
        self.utilisation_count = self._get_source_property('ResourceUtilisationCountId')
        self.utilisation_count_stats = TimingStatsSource(self._get_source_property('ResourceUtilisationCountStatsId'))
        self.queue_count = self._get_source_property('ResourceQueueCountId')
        self.queue_count_stats = TimingStatsSource(self._get_source_property('ResourceQueueCountStatsId'))
        self.total_wait_time = self._get_source_property('ResourceTotalWaitTimeId')
        self.wait_time = SamplingStatsSource(self._get_source_property('ResourceWaitTimeId'))

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources.append(self.count)
        sources += self.count_stats.expand_results()
        sources.append(self.utilisation_count)
        sources += self.utilisation_count_stats.expand_results()
        sources.append(self.queue_count)
        sources += self.queue_count_stats.expand_results()
        sources.append(self.total_wait_time)
        sources += self.wait_time.expand_results()
        return sources

class UnboundedQueueSource(PortSource):
    """Represents the unbounded queue result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.storing_queue_strategy = self._get_source_property('EnqueueStoringStrategyId')
        self.output_queue_strategy = self._get_source_property('DequeueStrategyId')
        self.empty = self._get_source_property('QueueNullId')
        self.count = self._get_source_property('QueueCountId')
        self.count_stats = TimingStatsSource(self._get_source_property('QueueCountStatsId'))
        self.enqueue_store_count = self._get_source_property('EnqueueStoreCountId')
        self.dequeue_count = self._get_source_property('DequeueCountId')
        self.dequeue_extract_count = self._get_source_property('DequeueExtractCountId')
        self.enqueue_store_rate = self._get_source_property('EnqueueStoreRateId')
        self.dequeue_rate = self._get_source_property('DequeueRateId')
        self.dequeue_extract_rate = self._get_source_property('DequeueExtractRateId')
        self.wait_time = SamplingStatsSource(self._get_source_property('QueueWaitTimeId'))
        self.dequeue_wait_time = SamplingStatsSource(self._get_source_property('DequeueWaitTimeId'))
        self.rate = self._get_source_property('QueueRateId')

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources.append(self.storing_queue_strategy)
        sources.append(self.output_queue_strategy)
        sources.append(self.empty)
        sources.append(self.count)
        sources += self.count_stats.expand_results()
        sources.append(self.enqueue_store_count)
        sources.append(self.dequeue_count)
        sources.append(self.dequeue_extract_count)
        sources.append(self.enqueue_store_rate)
        sources.append(self.dequeue_rate)
        sources.append(self.dequeue_extract_rate)
        sources += self.wait_time.expand_results()
        sources += self.dequeue_wait_time.expand_results()
        sources.append(self.rate)
        return sources

class QueueSource(PortSource):
    """Represents the bounded queue result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.input_queue_strategy = self._get_source_property('EnqueueStrategyId')
        self.storing_queue_strategy = self._get_source_property('EnqueueStoringStrategyId')
        self.output_queue_strategy = self._get_source_property('DequeueStrategyId')
        self.empty = self._get_source_property('QueueNullId')
        self.full = self._get_source_property('QueueFullId')
        self.capacity = self._get_source_property('QueueMaxCountId')
        self.count = self._get_source_property('QueueCountId')
        self.count_stats = TimingStatsSource(self._get_source_property('QueueCountStatsId'))
        self.enqueue_count = self._get_source_property('EnqueueCountId')
        self.enqueue_lost_count = self._get_source_property('EnqueueLostCountId')
        self.enqueue_store_count = self._get_source_property('EnqueueStoreCountId')
        self.dequeue_count = self._get_source_property('DequeueCountId')
        self.dequeue_extract_count = self._get_source_property('DequeueExtractCountId')
        self.load_factor = self._get_source_property('QueueLoadFactorId')
        self.enqueue_rate = self._get_source_property('EnqueueRateId')
        self.enqueue_store_rate = self._get_source_property('EnqueueStoreRateId')
        self.dequeue_rate = self._get_source_property('DequeueRateId')
        self.dequeue_extract_rate = self._get_source_property('DequeueExtractRateId')
        self.wait_time = SamplingStatsSource(self._get_source_property('QueueWaitTimeId'))
        self.total_wait_time = SamplingStatsSource(self._get_source_property('QueueTotalWaitTimeId'))
        self.enqueue_wait_time = SamplingStatsSource(self._get_source_property('EnqueueWaitTimeId'))
        self.dequeue_wait_time = SamplingStatsSource(self._get_source_property('DequeueWaitTimeId'))
        self.rate = self._get_source_property('QueueRateId')

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources.append(self.input_queue_strategy)
        sources.append(self.storing_queue_strategy)
        sources.append(self.output_queue_strategy)
        sources.append(self.empty)
        sources.append(self.full)
        sources.append(self.capacity)
        sources.append(self.count)
        sources += self.count_stats.expand_results()
        sources.append(self.enqueue_count)
        sources.append(self.enqueue_lost_count)
        sources.append(self.enqueue_store_count)
        sources.append(self.dequeue_count)
        sources.append(self.dequeue_extract_count)
        sources.append(self.load_factor)
        sources.append(self.enqueue_rate)
        sources.append(self.enqueue_store_rate)
        sources.append(self.dequeue_rate)
        sources.append(self.dequeue_extract_rate)
        sources += self.wait_time.expand_results()
        sources += self.total_wait_time.expand_results()
        sources += self.enqueue_wait_time.expand_results()
        sources += self.dequeue_wait_time.expand_results()
        sources.append(self.rate)
        return sources

class ServerSource(PortSource):
    """Represents the server result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.init_state = self._get_source_property('ServerInitStateId')
        self.state = self._get_source_property('ServerStateId')
        self.total_input_wait_time = self._get_source_property('ServerTotalInputWaitTimeId')
        self.total_processing_time = self._get_source_property('ServerTotalProcessingTimeId')
        self.total_output_wait_time = self._get_source_property('ServerTotalOutputWaitTimeId')
        self.total_preemption_time = self._get_source_property('ServerTotalPreemptionTimeId')
        self.input_wait_time = SamplingStatsSource(self._get_source_property('ServerInputWaitTimeId'))
        self.processing_time = SamplingStatsSource(self._get_source_property('ServerProcessingTimeId'))
        self.output_wait_time = SamplingStatsSource(self._get_source_property('ServerOutputWaitTimeId'))
        self.preemption_time = SamplingStatsSource(self._get_source_property('ServerPreemptionTimeId'))
        self.input_wait_factor = self._get_source_property('ServerInputWaitFactorId')
        self.processing_factor = self._get_source_property('ServerProcessingFactorId')
        self.output_wait_factor = self._get_source_property('ServerOutputWaitFactorId')
        self.preemption_factor = self._get_source_property('ServerPreemptionFactorId')

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources.append(self.init_state)
        sources.append(self.state)
        sources.append(self.total_input_wait_time)
        sources.append(self.total_processing_time)
        sources.append(self.total_output_wait_time)
        sources.append(self.total_preemption_time)
        sources += self.input_wait_time.expand_results()
        sources += self.processing_time.expand_results()
        sources += self.output_wait_time.expand_results()
        sources += self.preemption_time.expand_results()
        sources.append(self.input_wait_factor)
        sources.append(self.processing_factor)
        sources.append(self.output_wait_factor)
        sources.append(self.preemption_factor)
        return sources

class ArrivalTimerSource(PortSource):
    """Represents the arrival timer result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
        self.processing_time = SamplingStatsSource(self._get_source_property('ArrivalProcessingTimeId'))

    def expand_results(self):
        """Expand the result source and return a list of sources."""
        sources = []
        sources += self.processing_time.expand_results()
        return sources

class RefSource(PortSource):
    """Represents the reference result source."""

    def __init__(self, port):
        """Initializes a new instance by the specified port."""
        PortSource.__init__(self, port)
