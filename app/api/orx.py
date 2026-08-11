from fastapi import APIRouter

router = APIRouter(
    prefix="/api/v1/orx",
    tags=["ORX"],
)


@router.get("")
def get_orx_identity():
    return {
        "name": "ORX",
        "symbol": "ORX",
        "network": "ORLIX",
        "type": "digital_economic_unit",
        "architecture": "centralized_ledger",
        "status": "foundation",
        "version": "0.1.0",
        "public_network_active": False,
        "legal_tender_claim": False,
    }
