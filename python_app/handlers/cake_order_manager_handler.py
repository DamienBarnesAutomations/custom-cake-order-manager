import logging
from fastapi import APIRouter, HTTPException, Request
from utils.cake_order_validator import validate_cake_order

# 1. Setup Logger
# This creates a logger specific to this module
logger = logging.getLogger("cake_order_service")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)



router = APIRouter(
    prefix="/api/cakeOrder",
    tags=["cakeOrder"]
)


@router.post("/validate")
async def validate_order(request: Request):
    try:
        body = await request.json()
        logger.info(f"Received request for order validation")
        logger.info(f"Body: {body}")
        old_selection = body.get("old_selection", {})
        new_extraction = body.get("new_extraction", {})
        config = body.get("config", {})
        logger.info(f"Config: {config}")    
        validation_result = validate_cake_order(old_selection, new_extraction, config)
        return validation_result
    except Exception as e:
        logger.error(f"Error validating cake order: {str(e)}", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))



