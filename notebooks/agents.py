import avstack
import random


class _AgentModel():
    """Base class for agent fusion algorithms"""
    def __init__(self, perception, tracking):
        self.perception = perception
        self.tracking = tracking

    def __call__(self, *args, **kwargs):
        return self.ingest(*args, **kwargs)

    def reset(self):
        self.__init__(self.perception)
        
    def ingest(self):
        raise NotImplementedError



class EgoAgentOnly(_AgentModel):
    """No fusion from other agents"""
    def __init__(self, perception, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker3d.BasicBoxTracker3D(threshold_coast=10)
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agent_detections):
        platform = ego_pc.calibration.reference
        dets_ego = self.perception(ego_pc)
        tracks_out = self.tracking(
            frame=dets_ego.frame,
            t=dets_ego.timestamp,
            detections=dets_ego,
            platform=platform,
        )
        return tracks_out


class EgoDetectionFusion(_AgentModel):
    """Treat elements from other agents as detections""" 
    def __init__(self, perception, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker3d.BasicBoxTracker3D(threshold_coast=10)
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agent_detections):
        platform = ego_pc.calibration.reference
        dets_ego = self.perception(ego_pc)
        dets_all = [dets_ego] + list(agent_detections.values())
        random.shuffle(dets_all)  # shuffle to avoid bias
        frame = ego_pc.frame
        timestamp = ego_pc.timestamp
        for dets in dets_all:
            if len(dets) > 0:
                try:
                    tracks_out = self.tracking(
                        frame=frame,
                        t=timestamp,
                        detections=dets,
                        platform=platform,
                    )
                except NotImplementedError:
                    detections = [d.as_box_detection() for d in dets]
                    for det in detections:
                        det.change_reference(platform, inplace=True)
                    tracks_out = self.tracking(
                        frame=frame,
                        t=timestamp,
                        detections=detections,
                        platform=platform,
                    )
        return tracks_out


class EgoTrackFusion(_AgentModel):
    def __init__(self, perception, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker3d.BasicBoxTracker3D(threshold_coast=10)
        self.fusion = avstack.modules.fusion.BoxTrackToBoxTrackFusion3D()
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agent_tracks):
        # -- first process ego detections
        platform = ego_pc.calibration.reference
        frame = ego_pc.frame
        timestamp = ego_pc.timestamp
        dets_ego = self.perception(ego_pc)
        tracks_ego = self.tracking(
            frame=frame,
            t=timestamp,
            detections=dets_ego,
            platform=platform
        )
        # -- then perform CI fusion of the other tracks
        agent_tracks = list(agent_tracks.values())
        random.shuffle(agent_tracks)
        tracks_out = tracks_ego
        for tracks in agent_tracks:
            if len(tracks) > 0:
                # -- if tracks, perform fusion
                if isinstance(tracks[0], avstack.modules.tracking.tracks._TrackBase):
                    tracks_out = self.fusion(tracks_out, tracks, keep_lones=True)
                else:
                # -- if detections, perform update
                    tracks_out = self.tracking(
                        frame=frame,
                        t=timestamp,
                        detections=tracks,
                        platform=platform
                    )

        return tracks_out


            # for track in tracks:
            #     track.change_reference(platform, inplace=True)
            # for track in tracks_out:
            #     track.change_reference(platform, inplace=True)

# -----------------------------
# PERCEPTION ONLY
# -----------------------------

class EgoCameraPerception(_AgentModel):
    """Only performs ego-based perception"""
    def __init__(self, perception, *args, **kwargs):
        super().__init__(perception, None)

    def ingest(self, ego_image, agents_images):
        return self.perception['ego']['camera'](ego_image)


class AgentsCameraPerception(_AgentModel):
    """Only performs agent-based perception"""
    def __init__(self, perception, *args, **kwargs):
        super().__init__(perception, None)

    def ingest(self, ego_image, agents_images):
        return [self.perception['agent']['camera'](image) for image in agents_images]


class EgoLidarPerception(_AgentModel):
    """Only performs ego-based perception"""
    def __init__(self, perception, *args, **kwargs):
        super().__init__(perception, None)

    def ingest(self, ego_pc, agents_pcs):
        return self.perception['ego']['lidar'](ego_pc)


class AgentsLidarPerception(_AgentModel):
    """Only performs ego-based perception"""
    def __init__(self, perception, *args, **kwargs):
        super().__init__(perception, None)

    def ingest(self, ego_pc, agents_pcs):
        return [self.perception['agent']['lidar'](pc) for pc in agents_pcs]


# -----------------------------
# PERCEPTION AND TRACKING
# -----------------------------

class CameraPerceptionAndTracking(_AgentModel):
    """Only performs ego-based perception and tracking"""
    def __init__(self, perception, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker2d.BasicBoxTracker2D()
        super().__init__(perception, tracking)

    def ingest(self, ego_image, agents_images):
        tracks_ego = self.tracking(self.perception['ego']['camera'](ego_image))
        return tracks_ego

        
class LidarPerceptionAndTracking(_AgentModel):
    """Only performs ego-based perception and tracking"""
    def __init__(self, perception, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker3d.BasicBoxTracker3D()
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agents_pcs):
        tracks_ego = self.tracking(self.perception['ego']['lidar'](ego_pc))
        return tracks_ego


# -----------------------------
# PERCEPTION AND TRACKING WITH FUSION
# -----------------------------

class FusionAtTrackingWithDetections(_AgentModel):
    """Treat detections from other agents as detections""" 
    def __init__(self, perception, n_agents, *args, **kwargs):
        tracking = avstack.modules.tracking.tracker3d.BasicBoxTracker3D()
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agents_pcs):
        dets_ego = self.perception['ego']['lidar'](ego_pc)
        dets_all = [self.perception['agents']['lidar'](agents_pcs[i]) for i in range(len(agents_pcs))]
        dets_all.append(dets_ego)
        for dets in random.shuffle(dets_all):  # shuffle to avoid bias
            tracks_out = self.tracking(dets)  # TODO: need to adjust the configuration of the tracker?
        return tracks_out


class FusionAtTrackingWithTracks(_AgentModel):
    """Treat tracks from other agents as detections""" 
    def __init__(self, perception, n_agents, *args, **kwargs):
        tracking = {
            'ego':avstack.modules.tracking.tracker3d.BasicBoxTracker3D(),
            'agents':[avstack.modules.tracking.tracker3d.BasicBoxTracker3D() for _ in range(n_agents)]
        }
        super().__init__(perception, tracking)

    def ingest(self, ego_pc, agents_pcs):
        dets_ego = self.perception['ego'](ego_pc)
        pseudo_dets_all = [self.tracking['agents'][i](self.perception['agents'](agents_pcs[i])) for i in range(len(agents_pcs))]
        pseudo_dets_all.append(dets_ego)
        for pseudo_dets in random.shuffle(pseudo_dets_all):  # shuffle to avoid bias
            tracks_out = self.tracking(pseudo_dets)  # TODO: need to adjust the configuration of the tracker?
        return tracks_out


class DedicatedFusionLiDAR(_AgentModel):
    """Performs distributed data fusion on tracks from other agents"""
    def __init__(self, perception, n_agents, *args, **kwargs):
        tracking = {
            'ego':avstack.modules.tracking.tracker3d.BasicBoxTracker3D(),
            'agents':[avstack.modules.tracking.tracker3d.BasicBoxTracker3D() for _ in range(n_agents)]
        }
        super().__init__(perception, tracking)

    def fusion(self, tracks_ego, tracks_agents):
        pass
    
    def ingest(self, ego_pc, agents_pcs):
        tracks_ego = self.tracking['ego'](self.perception['ego'](ego_pc))
        tracks_agents = [self.tracking['agents'][i](self.perception['agents'](agents_pcs[i])) for i in range(len(agents_pcs))]
        tracks_out = self.fusion(tracks_ego, tracks_agents)