import uuid
from pydantic import BaseModel


class WorkerRegister(BaseModel):
    name: str
    phone_number: str
    platform_id: str
    city: str
    zone_id: str
    income_band: str  # LOW / MID / HIGH / ULTRA 
    # about the above instead of tieing to bands why
    # not accoding to income levels needs more thinking on this
    # cause someone might be too low even for the low band
    # or too high even for the utlra band
    aadhaar_last4: str  # mock KYC last 4 digits only


class WorkerLoginRequest(BaseModel):
    phone_number: str
    otp: str  # for now mock otp


class WorkerRead(BaseModel):
    id: uuid.UUID
    name: str
    phone_number: str
    platform_id: str
    city: str
    zone_id: str
    income_band: str
    kyc_status: str

    model_config = {"from_attributes": True}
