from ..api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

class ExecutionType(db.Model):

    __tablename__ = "execution_type"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    input = Column(String(128), ForeignKey("input.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    input = relationship('input')
    
class Input(db.Model):
    
    __tablename__ = "input"

    id = Column(Integer, primary_key=True)
    rate_start = Column(Float, nullable=False)
    rate_end = Column(Float, nullable=False)
    first_spike_latency_start = Column(Float, nullable=False)
    first_spike_latency_end = Column(Float, nullable=False)
    number_of_neurons = Column(Integer, nullable=False)
    number_of_neurons_start = Column(Integer, nullable=False)
    number_of_neurons_end = Column(Integer, nullable=False)
    trial_duration = Column(Integer, nullable=False)
    trial_duration_start = Column(Integer, nullable=False)
    trial_duration_end = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Execution(db.Model):

    __tablename__ = "execution"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ExecutionTypesRelation(db.Model):

    __tablename__ = "execution_types_relation"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    execution_type_id = Column(Integer, ForeignKey("execution_type.id"), primary_key=True)

    execution = relationship('execution')
    execution_type = relationship('execution_type')

class ExecutionInputRelation(db.Model):

    __tablename__ = "execution_input_relation"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    input_id = Column(Integer, ForeignKey("input.id"), primary_key=True)

    execution = relationship('execution')
    input = relationship('input')

class ExecutionNetworksRelation(db.Model):

    __tablename__ = "execution_networks_relation"

    execution_id = Column(Integer, ForeignKey("execution.id"), primary_key=True)
    network_id = Column(Integer, ForeignKey("network.id"), primary_key=True)

    execution = relationship('execution')
    execution_type = relationship('network')