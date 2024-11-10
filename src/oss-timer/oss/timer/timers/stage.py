import logging
from datetime import timedelta, datetime
from typing import Callable
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from oss.core.models.discipline.multi_stage import MultiStageDiscipline, Discipline
from oss.core.models.discipline.single_stage import SingleStageDiscipline
from oss.core.log import Log
from oss.core.message import BrokerConnection, BrokerExchangeType, BrokerMessage
from oss.core.models.base.timer import BaseTimer, SchedulerState, TimerControl, SchedulerAction


# Activate module wide logging
logger = Log.get_logger_function()(__name__)
logger.setLevel(logging.INFO)


class StageTimer(BaseTimer):
    _timer_controls: dict[TimerControl, Callable] = {}
    _discipline_configuration: MultiStageDiscipline | SingleStageDiscipline
    state: SchedulerState = SchedulerState.STOPPED
    _scheduler: BackgroundScheduler = BackgroundScheduler()
    _action_schedule: list[SchedulerAction] = []
    execution_offset: float = 0.0
    current_stage: int = 1
    current_phase: int = 1

    def __init__(self) -> None:
        self._discipline_configuration = Discipline.load_discipline("service_pistool.json")
        self._map_timer_controls()
        self._broker_connection = self._setup_broker_connection()
        self._broker_connection.channel.start_consuming()  # This will be the active line until finished consuming!

    def __del__(self) -> None:
        pass

    def _create_schedule(self) -> None:
        for stage_number, stage in enumerate(self._discipline_configuration.stages):
            stage_number = stage_number + 1  # Compensate 0 base array vs 1 base numbering system
            for phase_number, phase in enumerate(stage["phases"]):
                phase_number = phase_number + 1  # Compensate 0 base array vs 1 base numbering system
                for step_number, step in enumerate(phase["steps"]):
                    step_number = step_number + 1  # Compensate 0 base array vs 1 base numbering system
                    for action_number, action in enumerate(step["actions"]):
                        action_number = action_number + 1  # Compensate 0 base array vs 1 base numbering system
                        scheduler_action: SchedulerAction = SchedulerAction(
                            stage_number=stage_number,
                            stage_name=stage["name"],
                            phase_number=phase_number,
                            phase_name=phase["name"],
                            step_number=step_number,
                            step_name=step["name"],
                            action_number=action_number,
                            action=action["action"],
                            action_worker=action["worker"],
                            action_arguments=action["arguments"],
                            start_offset=action["start_offset"],
                        )
                        self._action_schedule.append(scheduler_action)

    def _start_scheduler(self, stage: int = 1, phase: int = 1) -> None:
        # We need to schedule in the future so all actions will have the same starting base.
        # if we schedule from datetime.now() this will are missing time before the first event.
        # if we schedule every scheduler action separately based on datetime.now() we get a time drift based on
        # execution time from the scheduler.
        base_datetime: datetime = datetime.now() + timedelta(milliseconds=10) + timedelta(seconds=self.execution_offset)

        filtered_action_schedule: list[SchedulerAction] = [
            scheduler_action
            for scheduler_action in self._action_schedule
            if scheduler_action.stage_number == stage and scheduler_action.phase_number >= phase
        ]

        # Clear all jobs that might still be in the scheduler queue
        self._scheduler.remove_all_jobs()

        # Schedule the new jobs
        for scheduler_action in filtered_action_schedule:
            # Every action just sends a broker message at the right time.
            # Creat the broker message for this scheduler_action
            broker_message: BrokerMessage = BrokerMessage(
                producer=self._identifier,
                body={"action": scheduler_action.action, "arguments": scheduler_action.action_arguments},
            )

            # Now add the send method of the broker_message to the scheduler. The method is the actual action being run
            # on time
            self._scheduler.add_job(
                broker_message.send,
                trigger=DateTrigger(run_date=base_datetime + timedelta(seconds=scheduler_action.start_offset)),
                args=[self._broker_connection, "audio", "audio.action.buzzer"],
            )

        # Start the scheduler with the jobs that have been scheduled
        self._scheduler.start()
        self._pause_scheduler()

    def _stop_scheduler(self) -> None:
        self._scheduler.remove_all_jobs()

    def _pause_scheduler(self) -> None:
        print(self._scheduler.get_jobs()[0].next_run_time)

    def _setup_broker_connection(self) -> BrokerConnection:
        broker_connection = BrokerConnection(host="localhost", port=5672)
        broker_connection.setup_channel(name="remote", exchange_type=BrokerExchangeType.TOPIC)
        broker_connection.channel.queue_declare(queue="remote", exclusive=True)
        broker_connection.channel.queue_bind(exchange="remote", queue="remote", routing_key="remote.*.action")
        broker_connection.channel.basic_consume(
            queue="remote",
            on_message_callback=self._handle_broker_message,
            auto_ack=True,
        )
        return broker_connection

    def _map_timer_controls(self):
        self._timer_controls.update(
            {
                TimerControl.TOGGLE_PHASE: self._toggle_phase,
                TimerControl.RESET_PHASE: self._reset_phase,
                TimerControl.SET_TOGGLE_DELAY: self._set_toggle_offset,
            }
        )

    def _handle_broker_message(self, ch, method, properties, body) -> None:
        broker_message: BrokerMessage = BrokerMessage.from_json(body)
        try:
            action_name: str = broker_message.body["action"]  # Access the "action" field in the broker message
            timer_control = TimerControl(action_name)
            timer_function = self._timer_controls[timer_control]  # Retrieve the actual callable from the Enum
            timer_function()  # Call the actual function
        except KeyError:
            logger.error("Invalid action in broker message")

    def _toggle_phase(self) -> None:
        # If the timer is stopped then start it
        new_state: SchedulerState = SchedulerState.INVALID
        if self.state == SchedulerState.STOPPED:
            self._create_schedule()
            self._start_scheduler()
        elif self.state == SchedulerState.RUNNING:
            self._stop_scheduler()
        elif self.state == SchedulerState.PAUSED:
            self._create_schedule()
            self._start_scheduler()

        logger.info(f"Switching timer state from {self.state} to {new_state}")
        self.state = new_state

    def _reset_phase(self) -> None:
        print("reset phase function")

    def _set_toggle_offset(self) -> None:
        configured_offset: float = 5.0
        self.execution_offset = configured_offset if self.execution_offset != configured_offset else 0.0
