from ..api import db

from sqlalchemy.sql import func
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, Float
from sqlalchemy.orm import relationship

class Network(db.Model):

    __tablename__ = "network"

    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class NetworkParameter(db.Model):

    __tablename__ = "network_parameter"

    network_id = Column(Integer, ForeignKey("network.id"), primary_key=True)
    name = Column(String(100), nullable=False, primary_key=True)
    value = Column(Float, nullable=False)

    network = relationship('network')