
from enum import Enum
from pydantic import model_validator
from pydantic import BaseModel, ConfigDict, Field


class Priority(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class ResolutionCategory(str, Enum):
    DATA = "Data"
    SELF_HEALED = "Self-healed"
    VENDOR_SUPPORT = "Vendor Support"
    USER_EDUCATION = "User Education"
    VIA_CHANGE = "Via Change"
    CONFIGURATION = "Configuration"
    INTEGRATION_FAILURE = "Integration Failure"
    OTHER = "Other"


class Incident(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    incident_id: str = Field(min_length=1)

    short_description: str = Field(min_length=3)

    description: str = Field(min_length=5)

    resolution_notes: str = Field(min_length=5)

    priority: Priority

    resolution_category: ResolutionCategory

    resolution_time_hours: float | None = Field(
        default=None,
        ge=0
    )

    sla_breached: bool | None = None


class IncidentUpdate(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra="forbid"
    )

    short_description: str | None = Field(
        default=None,
        min_length=3
    )

    description: str | None = Field(
        default=None,
        min_length=5
    )

    resolution_notes: str | None = Field(
        default=None,
        min_length=5
    )

    priority: Priority | None = None

    resolution_category: ResolutionCategory | None = None

    resolution_time_hours: float | None = Field(
        default=None,
        ge=0
    )

    sla_breached: bool | None = None

    @model_validator(mode="after")
    def validate_non_nullable_fields(self):
        non_nullable_fields = {
            "short_description",
            "description",
            "resolution_notes",
            "priority",
            "resolution_category"
        }

        for field in non_nullable_fields:
            if field in self.model_fields_set:
                if getattr(self, field) is None:
                    raise ValueError(
                        f"{field} cannot be null"
                    )

        return self
