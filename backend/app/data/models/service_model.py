from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship
from app.data.models.base import Base


class ServiceModel(Base):
    """Model for t_service table - Reference table for medical services"""
    __tablename__ = "t_service"

    service_id = Column(Integer, primary_key=True)
    nom = Column(String(120), nullable=False)
    organisation_id = Column(Integer, ForeignKey("t_organisation.organisation_id", ondelete="CASCADE"), nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    # Relationships
    organisation = relationship("OrganisationModel", back_populates="services")
    patients = relationship("PatientModel", back_populates="service_ref")

    def __repr__(self):
        return f"<ServiceModel(service_id={self.service_id}, nom={self.nom}, org_id={self.organisation_id})>"
