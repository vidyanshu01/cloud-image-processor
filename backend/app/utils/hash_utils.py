import hashlib
import json

from app.core.logging import logger
from app.schemas.transformation import TransformationRequest


logger.info("Hash utils loaded")


def create_transformation_hash(
    transformations: TransformationRequest,
) -> str:

    logger.info(
        "Creating transformation hash"
    )

    transformation_data = (
        transformations.model_dump(
            exclude_none=True
        )
    )

    normalized_data = json.dumps(
        transformation_data,
        sort_keys=True,
        separators=(",", ":"),
    )

    transformation_hash = hashlib.sha3_256(
        normalized_data.encode("utf-8")
    ).hexdigest()

    logger.info(
        "Transformation hash created"
    )

    return transformation_hash