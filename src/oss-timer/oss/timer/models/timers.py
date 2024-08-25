from enum import Enum
from oss.timer.timers.stage import StageTimer
from oss.timer.timers.competition import CompetitionTimer


class Timer(Enum):
    STAGE: StageTimer = StageTimer
    COMPETITION: CompetitionTimer = CompetitionTimer
