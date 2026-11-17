"""Options Pricing & Risk Toolkit - FastAPI service."""
from __future__ import annotations

from dataclasses import asdict
from typing import Literal

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from basis.options import price_option, implied_volatility

app = FastAPI(title="Options Pricing & Risk Toolkit", version="1.0.0",
    docs_url="/api/docs", openapi_url="/api/openapi.json",
    description="Black-Scholes and Monte Carlo option pricing with Greeks.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
router = APIRouter(prefix="/api")


@router.get("/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok", "service": "basis-options"}


class OptionRequest(BaseModel):
    S: float = Field(100, gt=0)
    K: float = Field(100, gt=0)
    T: float = Field(1.0, gt=0, le=30)
    r: float = Field(0.05, ge=-0.1, le=0.5)
    sigma: float = Field(0.20, gt=0, le=3)
    q: float = Field(0.0, ge=0, le=0.5)
    option_type: Literal["call", "put"] = "call"
    n_sims: int = Field(100_000, ge=1000, le=1_000_000)


class ImpliedVolRequest(BaseModel):
    price: float = Field(..., gt=0)
    S: float = Field(100, gt=0)
    K: float = Field(100, gt=0)
    T: float = Field(1.0, gt=0, le=30)
    r: float = Field(0.05, ge=-0.1, le=0.5)
    q: float = Field(0.0, ge=0, le=0.5)
    option_type: Literal["call", "put"] = "call"


@router.post("/options/price", tags=["pricing"])
def options_price(req: OptionRequest) -> dict:
    return asdict(price_option(**req.model_dump()))


@router.post("/options/implied-vol", tags=["pricing"])
def options_iv(req: ImpliedVolRequest) -> dict:
    return {"implied_volatility": implied_volatility(**req.model_dump()), "inputs": req.model_dump()}

app.include_router(router)
