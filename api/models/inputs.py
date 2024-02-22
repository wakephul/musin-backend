from typing import Optional
import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
  
class Input(db.Model):
    
    __tablename__ = "input"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    name = Column(String(255), nullable=False)
    multiple = Column(Boolean, nullable=False, default=False)
    rate_start = Column(Float, nullable=False)
    rate_end = Column(Float, nullable=True)
    rate_step = Column(Float, nullable=True)
    first_spike_latency_start = Column(Float, nullable=False)
    first_spike_latency_end = Column(Float, nullable=True)
    first_spike_latency_step = Column(Float, nullable=True)
    number_of_neurons_start = Column(Integer, nullable=False)
    number_of_neurons_end = Column(Integer, nullable=True)
    number_of_neurons_step = Column(Integer, nullable=True)
    trial_duration_start = Column(Integer, nullable=False)
    trial_duration_end = Column(Integer, nullable=True)
    trial_duration_step = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self,
        code: str,
        name: str,
        multiple: bool,
        rate_start: float,
        rate_end: Optional[float],
        rate_step: Optional[float],
        first_spike_latency_start: float,
        first_spike_latency_end: Optional[float],
        first_spike_latency_step: Optional[float],
        number_of_neurons_start: int,
        number_of_neurons_end: Optional[int],
        number_of_neurons_step: Optional[int],
        trial_duration_start: int,
        trial_duration_end: Optional[int],
        trial_duration_step: Optional[int]
    ):
        self.code = code
        self.name = name
        self.multiple = multiple
        self.rate_start = rate_start
        self.rate_end = rate_end
        self.rate_step = rate_step
        self.first_spike_latency_start = first_spike_latency_start
        self.first_spike_latency_end = first_spike_latency_end
        self.first_spike_latency_step = first_spike_latency_step
        self.number_of_neurons_start = number_of_neurons_start
        self.number_of_neurons_end = number_of_neurons_end
        self.number_of_neurons_step = number_of_neurons_step
        self.trial_duration_start = trial_duration_start
        self.trial_duration_end = trial_duration_end
        self.trial_duration_step = trial_duration_step

    @staticmethod
    def create(
        name: str,
        multiple: bool,
        rate_start: float,
        rate_end: Optional[float],
        rate_step: Optional[float],
        first_spike_latency_start: float,
        first_spike_latency_end: Optional[float],
        first_spike_latency_step: Optional[float],
        number_of_neurons_start: int,
        number_of_neurons_end: Optional[int],
        number_of_neurons_step: Optional[int],
        trial_duration_start: int,
        trial_duration_end: Optional[int],
        trial_duration_step: Optional[int]
    ):
        code = str(uuid.uuid4())
        to_create = Input(
            code = code,
            name = name,
            multiple = multiple,
            rate_start = rate_start,
            rate_end = rate_end,
            rate_step = rate_step,
            first_spike_latency_start = first_spike_latency_start,
            first_spike_latency_end = first_spike_latency_end,
            first_spike_latency_step = first_spike_latency_step,
            number_of_neurons_start = number_of_neurons_start,
            number_of_neurons_end = number_of_neurons_end,
            number_of_neurons_step = number_of_neurons_step,
            trial_duration_start = trial_duration_start,
            trial_duration_end = trial_duration_end,
            trial_duration_step = trial_duration_step
        )
        db.session.add(to_create)
        db.session.commit()
        return code

    @staticmethod
    def get_one(code):
        result = Input.query.get(code)
        if not result:
            return None
        return {
            'code': result.code,
            'name': result.name,
            'multiple': result.multiple,
            'rate_start': result.rate_start,
            'rate_end': result.rate_end,
            'rate_step': result.rate_step,
            'first_spike_latency_start': result.first_spike_latency_start,
            'first_spike_latency_end': result.first_spike_latency_end,
            'first_spike_latency_step': result.first_spike_latency_step,
            'number_of_neurons_start': result.number_of_neurons_start,
            'number_of_neurons_end': result.number_of_neurons_end,
            'number_of_neurons_step': result.number_of_neurons_step,
            'trial_duration_start': result.trial_duration_start,
            'trial_duration_end': result.trial_duration_end,
            'trial_duration_step': result.trial_duration_step,
            'created_at': result.created_at
        }
    
    @staticmethod
    def get_name(code):
        result = Input.query.get(code)
        if not result:
            return None
        return result.name

    @staticmethod
    def get_all():
        return [
            {
            'code': i.code,
            'name': i.name,
            'multiple': i.multiple,
            'rate_start': i.rate_start,
            'rate_end': i.rate_end,
            'rate_step': i.rate_step,
            'first_spike_latency_start': i.first_spike_latency_start,
            'first_spike_latency_end': i.first_spike_latency_end,
            'first_spike_latency_step': i.first_spike_latency_step,
            'number_of_neurons_start': i.number_of_neurons_start,
            'number_of_neurons_end': i.number_of_neurons_end,
            'number_of_neurons_step': i.number_of_neurons_step,
            'trial_duration_start': i.trial_duration_start,
            'trial_duration_end': i.trial_duration_end,
            'trial_duration_step': i.trial_duration_step,
            'created_at': i.created_at
            }
        for i in Input.query.all()]