import json
import os
import logging
from typing import Union

logger = logging.getLogger(__name__)


def vehicle_database(car_name: str) -> Union[dict, str]:
    """
    Search for car information in the local car_Data.json file based on the user's query.

    Args:
        car_name (str): The make, model, or partial name of the car.

    Returns:
        Union[dict, str]:
            A dictionary containing the car's detailed information if found,
            or an error message string if not found or if an issue occurs.
    """
    file_path = "data/car_Data.json"

    if not os.path.exists(file_path):
        logger.error("Car database file not found at %s", file_path)
        return {"error": "Car database file not found."}

    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except json.JSONDecodeError as e:
        logger.exception("Failed to parse car database: %s", e)
        return {"error": "Failed to parse car database."}

    car_list = data.get("Sheet1", [])
    search_term = car_name.lower().strip()

    for car in car_list:
        make = car.get("make", "").lower()
        model = car.get("model", "").lower()
        full_name = f"{make} {model}".strip()

        if search_term in model or search_term in make or search_term in full_name:
            logger.info("Match found for '%s': %s %s", car_name, make.title(), model.title())
            return {
                "make": car.get("make"),
                "model": car.get("model"),
                "year": car.get("year"),
                "price": f"${car.get('retail_price')}",
                "body_type": car.get("body_type"),
                "fuel_type": car.get("fuel_type"),
                "drivetrain": car.get("drivetrain"),
                "interior": car.get("interior"),
                "exterior": car.get("exterior"),
                "vehicle_type": car.get("vehicle_type"),
                "description": (
                    f"{car.get('year')} {car.get('make')} {car.get('model')} "
                    f"({car.get('trim')}), {car.get('body_type')}, "
                    f"{car.get('fuel_type')} with {car.get('drivetrain')} drivetrain. "
                    f"Interior: {car.get('interior')}, Exterior: {car.get('exterior')}."
                )
            }

    logger.warning("No match found for car name: %s", car_name)
    return {"error": f"Sorry, we couldn't find any vehicle matching '{car_name}'."}