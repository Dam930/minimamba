import os
import random
import string
from datetime import datetime


def generate_log_name() -> str:
    """Generate logname concatenating timestamp, username and a random string.

    Returns
    -------
    str
        The generated logname.
    """
    # concatenate timestamp, username and random code
    return (
        "_".join(
            [
                (
                    str(datetime.now())
                    .split(".", maxsplit=1)[0]
                    .replace(":", ".")
                    .replace(" ", "_")
                ),
                os.path.split(os.path.expanduser("~"))[-1],
                "".join(
                    random.choice(string.ascii_uppercase + string.digits)
                    for _ in range(6)
                ),
            ]
        )
        + ".log"
    )
