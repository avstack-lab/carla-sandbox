from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from avstack.sensors import LidarData

from avstack.config import MODELS
from avstack.modules import BaseModule
from avstack.utils.decorators import apply_hooks


@MODELS.register_module()
class ConcaveHullLidarFOVEstimator(BaseModule):
    def __init__(
        self,
        concavity: int = 1,
        length_threshold: float = 4,
        name="fovestimator",
        *args,
        **kwargs
    ):
        super().__init__(name=name, *args, **kwargs)
        self.concavity = concavity
        self.length_threshold = length_threshold

    @apply_hooks
    def __call__(
        self, pc: "LidarData", in_global: bool, *args: Any, **kwds: Any
    ) -> Any:
        fov = pc.concave_hull_bev(
            concavity=self.concavity,
            length_threshold=self.length_threshold,
            in_global=in_global,
        )
        return fov
