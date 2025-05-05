from loguru import logger
from pretty_json_loguru import setup_json_loguru


def test():
    logger.info("Simple message")
    logger.info("Message with extra", foo="bar")

    try:
        raise ValueError("This is an exception")
    except ValueError:
        logger.exception("Exception caught")


if __name__ == "__main__":
    setup_json_loguru()
    test()
