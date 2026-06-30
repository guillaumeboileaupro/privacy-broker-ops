from __future__ import annotations

from enum import StrEnum
from typing import Literal

from pydantic import BaseModel, Field, HttpUrl


class ExposureStatus(StrEnum):
    A_VERIFIER = "A_VERIFIER"
    HOMONYME = "HOMONYME"
    CONFIRME = "CONFIRME"
    DEMANDE_PREPAREE = "DEMANDE_PREPAREE"
    ENVOYE = "ENVOYE"
    REPONSE_RECUE = "REPONSE_RECUE"
    SUPPRESSION_CONFIRMEE = "SUPPRESSION_CONFIRMEE"
    REFUS = "REFUS"
    JUSTIFICATIF_DEMANDE = "JUSTIFICATIF_DEMANDE"
    RELANCE_A_FAIRE = "RELANCE_A_FAIRE"
    CNIL_A_ENVISAGER = "CNIL_A_ENVISAGER"
    CLOS = "CLOS"


class Broker(BaseModel):
    id: str
    name: str
    category: str
    country: str = ""
    request_channel: str
    optout_url: str = ""
    contact_email: str = ""
    notes: str = ""


class Person(BaseModel):
    full_name: str
    email: str
    postal_address: str = ""
    phone: str = ""
    proof_identity: str = ""


class ExposureCreate(BaseModel):
    broker_id: str
    url: str
    status: ExposureStatus = ExposureStatus.A_VERIFIER
    data_type: str = ""
    note: str = ""


class Exposure(BaseModel):
    id: int
    broker_id: str
    url: str
    status: ExposureStatus
    data_type: str = ""
    note: str = ""
    discovered_at: str
    last_contact_at: str | None = None


class AgentDecision(BaseModel):
    exposure_id: int
    broker_id: str
    current_status: ExposureStatus
    recommended_status: ExposureStatus
    reason: str
    urgency: Literal["ok", "soon", "urgent"] = "ok"
    days_since_last_contact: int | None = Field(default=None, ge=0)
