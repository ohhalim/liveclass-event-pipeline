import logging

from db import setup_database
from event_generator import run as generate_and_save

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

if __name__ == "__main__":
    setup_database()
    generate_and_save()
