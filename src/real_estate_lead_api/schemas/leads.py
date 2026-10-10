"""Pydantic models for lead API data."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

LeadStatus = Literal["new", "contacted", "qualified"]
NonEmptyText = Annotated[str, Field(min_length=1)]
PositiveBudget = Annotated[int, Field(strict=True, gt=0)]


class LeadRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")


class LeadCreate(LeadRequest):
    name: NonEmptyText
    phone: NonEmptyText
    city: NonEmptyText
    budget: PositiveBudget
    status: LeadStatus = "new"


class LeadUpdate(LeadRequest):
    name: NonEmptyText | None = None
    phone: NonEmptyText | None = None
    city: NonEmptyText | None = None
    budget: PositiveBudget | None = None
    status: LeadStatus | None = None

    @field_validator("name", "phone", "city", "budget", "status", mode="before")
    @classmethod
    def reject_null_values(cls, value: object) -> object:
        if value is None:
            raise ValueError("null is not a valid update value")
        return value

    @model_validator(mode="after")
    def require_at_least_one_field(self) -> Self:
        if not self.model_fields_set:
            raise ValueError("at least one field must be provided")
        return self


class LeadResponse(BaseModel):
    id: int
    name: NonEmptyText
    phone: NonEmptyText
    city: NonEmptyText
    budget: PositiveBudget
    status: LeadStatus