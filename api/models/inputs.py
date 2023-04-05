import uuid

from api.api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
  
class Input(db.Model):
    
    __tablename__ = "input"

    code = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4().hex))
    rate_start = Column(Float, nullable=False)
    rate_end = Column(Float, nullable=False)
    first_spike_latency_start = Column(Float, nullable=False)
    first_spike_latency_end = Column(Float, nullable=False)
    number_of_neurons_start = Column(Integer, nullable=False)
    number_of_neurons_end = Column(Integer, nullable=False)
    trial_duration_start = Column(Integer, nullable=False)
    trial_duration_end = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, code: str, rate_start: float, rate_end: float, first_spike_latency_start: float, first_spike_latency_end: float, number_of_neurons_start: int, number_of_neurons_end: int, trial_duration_start: int, trial_duration_end: int):
        self.code = code
        self.rate_start = rate_start
        self.rate_end = rate_end
        self.first_spike_latency_start = first_spike_latency_start
        self.first_spike_latency_end = first_spike_latency_end
        self.number_of_neurons_start = number_of_neurons_start
        self.number_of_neurons_end = number_of_neurons_end
        self.trial_duration_start = trial_duration_start
        self.trial_duration_end = trial_duration_end

    @staticmethod
    def create(rate_start: float, rate_end: float, first_spike_latency_start: float, first_spike_latency_end: float, number_of_neurons_start: int, number_of_neurons_end: int, trial_duration_start: int, trial_duration_end: int):
        code = str(uuid.uuid4())
        to_create = Input(code=code, rate_start=rate_start, rate_end=rate_end, first_spike_latency_start=first_spike_latency_start, first_spike_latency_end=first_spike_latency_end, number_of_neurons_start=number_of_neurons_start, number_of_neurons_end=number_of_neurons_end, trial_duration_start=trial_duration_start, trial_duration_end=trial_duration_end)
        db.session.add(to_create)
        db.session.commit()
        return code

    @staticmethod
    def get_one(code):
        result = Input.query.get(code)
        if not result:
            return None
        return {'code': result.code, 'rate_start': result.rate_start, 'rate_end': result.rate_end, 'first_spike_latency_start': result.first_spike_latency_start, 'first_spike_latency_end': result.first_spike_latency_end, 'number_of_neurons_start': result.number_of_neurons_start, 'number_of_neurons_end': result.number_of_neurons_end, 'trial_duration_start': result.trial_duration_start, 'trial_duration_end': result.trial_duration_end, 'created_at': result.created_at}

    @staticmethod
    def get_all():
        return [{'code': i.code, 'rate_start': i.rate_start, 'rate_end': i.rate_end, 'first_spike_latency_start': i.first_spike_latency_start, 'first_spike_latency_end': i.first_spike_latency_end, 'number_of_neurons_start': i.number_of_neurons_start, 'number_of_neurons_end': i.number_of_neurons_end, 'trial_duration_start': i.trial_duration_start, 'trial_duration_end': i.trial_duration_end, 'created_at': i.created_at}
                for i in Input.query.all()]