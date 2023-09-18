import avstack
import itertools
import numpy as np


class _SensorNetwork():
    """Base class for sensor network fusion"""
    def __init__(self, perception, tracking):
        self.perception = perception
        self.tracking = tracking

    def __call__(self, *args, **kwargs):
        return self.ingest(*args, **kwargs)

    def reset(self):
        self.__init__(self.perception)
    
    def ingest(self):
        raise NotImplementedError


class NetworkWithLocalPerception(_SensorNetwork):
    def __init__(self, perception, *args, sensor='lidar', **kwargs):
        super().__init__(perception, None)

    def ingest(self, agent_data):
        if isinstance(self.perception, (dict, list)):
            return {i:self.perception[i](data) for i, data in agent_data.items()}
        else:
            return {i:self.perception(data) for i, data in agent_data.items()}


class NetworkWithLocalTracking(_SensorNetwork):
    def __init__(self, perception, *args, sensor='lidar', **kwargs):
        if sensor == 'lidar':
            self.tracker_base = avstack.modules.tracking.tracker3d.BasicBoxTracker3D
        else:
            raise NotImplementedError
        self.trackers = {}
        super().__init__(perception, None)

    def ingest(self, agent_data):
        for i, data in agent_data.items():
            if len(data) == 0:
                continue
            frame = data.frame
            timestamp = data.timestamp
        
            # Pull data
            if isinstance(data, avstack.sensors.LidarData):
                if isinstance(self.perception, (list, dict)):
                    dets = self.perception[i](data)
                else:
                    dets = self.perception(data)
                platform = data.reference
                self.platform = platform
                change_in_place = False
            else:
                dets = [d.as_box_detection() for d in data]
                platform = self.platform
                change_in_place = True

            # Init tracking
            if i not in self.trackers:
                self.trackers[i] = self.tracker_base(threshold_coast=10)

            # Run tracking
            _ = self.trackers[i](
                frame=frame,
                t=timestamp,
                detections=dets,
                platform=platform,
                change_in_place=change_in_place)
        tracks = {k : self.trackers[k].tracks_confirmed for k in self.trackers}
        return tracks


class NetworkWithDistributedTracking(_SensorNetwork):
    def __init__(self, perception, *args, sensor='lidar', p_share=0.5, **kwargs):
        self.local_network = NetworkWithLocalTracking(perception=perception, sensor=sensor)
        self.p_share = p_share
        self.perception = perception
        
    def ingest(self, agent_data):
        # run the local step first
        tracks_local = self.local_network(agent_data)

        # have agents share data amongst some of each other
        all_pairs = list(itertools.combinations(list(tracks_local.keys()), r=2))
        do_share = np.random.rand(len(tracks_local)) < self.p_share
        for pair in [pair for pair, share in zip(all_pairs, do_share) if share]:
            frame = agent_data[list(agent_data.keys())[0]].frame
            timestamp = agent_data[list(agent_data.keys())[0]].timestamp
            track_data = avstack.datastructs.DataContainer(
                frame=frame,
                timestamp=timestamp,
                data=tracks_local[pair[1]],
                source_identifier=pair[1],
            )
            agent_data = {pair[0] : track_data}
            _ = self.local_network.ingest(agent_data)        
        tracks = {k : self.local_network.trackers[k].tracks_confirmed for k in self.local_network.trackers}
        return tracks