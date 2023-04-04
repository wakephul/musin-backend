from ..api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship
  
class Input(db.Model):
    
    __tablename__ = "input"

    id = Column(Integer, primary_key=True, index=True)
    rate_start = Column(Float, nullable=False)
    rate_end = Column(Float, nullable=False)
    first_spike_latency_start = Column(Float, nullable=False)
    first_spike_latency_end = Column(Float, nullable=False)
    number_of_neurons_start = Column(Integer, nullable=False)
    number_of_neurons_end = Column(Integer, nullable=False)
    trial_duration_start = Column(Integer, nullable=False)
    trial_duration_end = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __init__(self, rate_start: float, rate_end: float, first_spike_latency_start: float, first_spike_latency_end: float, number_of_neurons_start: int, number_of_neurons_end: int, trial_duration_start: int, trial_duration_end: int):
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
        to_create = Input(rate_start, rate_end, first_spike_latency_start, first_spike_latency_end, number_of_neurons_start, number_of_neurons_end, trial_duration_start, trial_duration_end)
        db.session.add(to_create)
        db.session.commit()

    @staticmethod
    def get():
        return [{'id': i.id, 'rate_start': i.rate_start, 'rate_end': i.rate_end, 'first_spike_latency_start': i.first_spike_latency_start, 'first_spike_latency_end': i.first_spike_latency_end, 'number_of_neurons_start': i.number_of_neurons_start, 'number_of_neurons_end': i.number_of_neurons_end, 'trial_duration_start': i.trial_duration_start, 'trial_duration_end': i.trial_duration_end, 'created_at': i.created_at}
                for i in Input.query.order_by('id').all()]