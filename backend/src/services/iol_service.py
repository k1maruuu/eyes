from __future__ import annotations
import math
from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.models.iol_calc import IOLCalculation
from src.schemas.iol_calc import IOLCalcIn


def _avg_k(k1: float, k2: float) -> float:
    return (k1 + k2) / 2.0


def srk_t_iol_power(al_mm: float, k_d: float, a_const: float, reft: float) -> float:
    """
    SRK/T (возвращает IOL power для target refraction reft).
    Реализация по открытой реализации (Python-for-ophthalmologist). :contentReference[oaicite:3]{index=3}
    """
    # retinal thickness correction
    rethick = 0.65696 - 0.02029 * al_mm

    # corrected axial length
    if al_mm <= 24.2:
        lc = al_mm
    else:
        lc = (-3.446 + (1.716 * al_mm) - (0.0237 * al_mm**2))

    # convert K to radius (mm)
    rmm = 337.5 / k_d

    c1 = -5.40948 + 0.58412 * lc + 0.098 * k_d
    rc = rmm**2 - (c1**2) / 4.0
    if rc < 0:
        rc = 0.0

    c2 = rmm - math.sqrt(rc)

    # ACD estimate from A-constant
    acd = 0.62467 * a_const - 68.74709
    acde = c2 + acd - 3.3357

    n1 = 1.336
    n2 = 0.333

    l0 = al_mm + rethick

    s1 = l0 - acde
    s2 = n1 * rmm - n2 * acde
    s3 = n1 * rmm - n2 * l0
    s4 = 12.0 * s3 + l0 * rmm
    s5 = 12.0 * s2 + acde * rmm

    # note: 1336 and 0.001 keep mm units consistent
    iol_for_tgt = (1336.0 * (s3 - 0.001 * reft * s4)) / (s1 * (s2 - 0.001 * reft * s5))
    return float(iol_for_tgt)


def haigis_iol_power(k_d: float, acd_mm: float, al_mm: float, a_const: float, rx: float,
                     a0: float | None, a1: float, a2: float) -> float:
    """
    Haigis thin-lens implementation (возвращает IOL power).
    ELP(d) = a0 + a1*ACD + a2*AL (классическая идея). :contentReference[oaicite:4]{index=4}
    Реализация по открытой реализации (Python-for-ophthalmologist). :contentReference[oaicite:5]{index=5}
    """
    # If a0 not provided, derive from A-constant as in open implementation
    if a0 is None:
        a0 = 0.62467 * a_const - 72.434

    # constants used in that implementation
    n = 1.336
    nc = 1.3315
    dx = 12.0 / 1000.0  # vertex distance (m)

    # Convert mm -> m for radii/lengths
    # Convert K (D) -> corneal radius (mm): R(mm) = 337.5 / K
    r_mm = 337.5 / k_d
    r = r_mm / 1000.0
    ac = acd_mm / 1000.0
    l = al_mm / 1000.0

    # Predict ELP (d) in mm then to meters
    # (open impl has alternate branch for AC==0; we don't need it here)
    d_mm = a0 + a1 * acd_mm + a2 * al_mm
    d = d_mm / 1000.0

    # corneal power from radius
    dc = (nc - 1.0) / r

    # z is effective corneal power including target refraction at spectacle plane
    z = dc + rx / (1.0 - rx * dx)

    dl = n / (l - d) - n / (n / z - d)
    return float(dl)


def round_iol(power: float, step: float = 0.5) -> float:
    # обычно линзы идут шагом 0.5D (иногда 0.25)
    return round(power / step) * step


def calculate_iol(db: Session, patient_id: int, data: IOLCalcIn) -> IOLCalculation:
    k = _avg_k(data.k1, data.k2)
    target = float(data.target_refraction)

    if data.formula == "SRKT":
        if data.a_constant is None:
            raise HTTPException(400, "a_constant is required for SRKT")
        result = srk_t_iol_power(
            al_mm=float(data.axial_length),
            k_d=float(k),
            a_const=float(data.a_constant),
            reft=target,
        )
    elif data.formula == "HAIGIS":
        if data.a_constant is None:
            # можно разрешить, но тогда a0 MUST быть задан
            if data.haigis_a0 is None:
                raise HTTPException(400, "Either a_constant or haigis_a0 is required for Haigis")
        result = haigis_iol_power(
            k_d=float(k),
            acd_mm=float(data.acd),
            al_mm=float(data.axial_length),
            a_const=float(data.a_constant or 118.0),
            rx=target,
            a0=data.haigis_a0,
            a1=float(data.haigis_a1),
            a2=float(data.haigis_a2),
        )
    else:
        raise HTTPException(400, "Unknown formula")

    result = round_iol(result, step=0.5)

    calc = IOLCalculation(
        patient_id=patient_id,
        checklist_item_id=data.checklist_item_id,
        formula=data.formula,
        k1=data.k1,
        k2=data.k2,
        acd=data.acd,
        axial_length=data.axial_length,
        a_constant=data.a_constant,
        result_d=result,
    )
    db.add(calc)
    db.commit()
    db.refresh(calc)
    return calc 