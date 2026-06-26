import os
import json
import logging
from datetime import datetime
from pydantic import ValidationError

# Setup Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def validate_records(records, model_class, resource_name):
    """
    Validates a list of dictionaries against a Pydantic model.
    Splits records into validated and quarantined.
    """
    validated = []
    quarantined = []

    for idx, raw_record in enumerate(records):
        try:
            # Pydantic validation handles parsing and coercion (e.g. string to datetime)
            model_instance = model_class(**raw_record)
            validated.append(model_instance.model_dump())
        except ValidationError as e:
            logging.warning(f"Validation failed for {resource_name} index {idx}: {e.errors()}")
            quarantined.append({
                "record": raw_record,
                "errors": e.errors(),
                "timestamp": datetime.utcnow().isoformat()
            })
        except Exception as e:
            logging.error(f"Unexpected validation error for {resource_name} index {idx}: {e}")
            quarantined.append({
                "record": raw_record,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            })

    # Save quarantined records if any exist
    if quarantined:
        quarantine_dir = "data/quarantine"
        os.makedirs(quarantine_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"{quarantine_dir}/{resource_name}_failed_{timestamp}.json"
        with open(filepath, "w") as f:
            json.dump(quarantined, f, indent=4, default=str)
        logging.warning(f"Quarantined {len(quarantined)} records for {resource_name} in {filepath}")
        print(f"Quarantined {len(quarantined)} invalid {resource_name} records.")

    logging.info(f"{resource_name} validation result: {len(validated)} valid, {len(quarantined)} quarantined.")
    return validated
