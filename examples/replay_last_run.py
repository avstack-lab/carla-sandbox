# -*- coding: utf-8 -*-
# @Author: Spencer H
# @Date:   2022-07-29
# @Last Modified by:   Spencer H
# @Last Modified date: 2022-09-12
# @Description:
"""

"""

import os
import avapi


with open('data/last_run.txt', 'r') as f:
    lines = [line.rstrip() for line in f]

if len(lines) > 1:
    raise NotImplementedError('Cannot handle multiple files yet')
else:
    avapi.visualize.replay.replay_ground_truth(lines[0])
