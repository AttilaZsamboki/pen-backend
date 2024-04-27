import os
from functools import partial

from dotenv import load_dotenv

from ..utils.logs import log
from ..utils.minicrm import MiniCrmClient

load_dotenv()


class MiniCRMWrapper:
    script_name = None
    minicrm_client = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minicrm_client = MiniCrmClient(
            os.environ.get("PEN_MINICRM_SYSTEM_ID"),
            os.environ.get("PEN_MINICRM_API_KEY"),
            script_name=self.script_name,
        )

        if self.script_name is None:
            self.script_name = self.__class__.__name__
        self.log = partial(log, script_name=self.script_name)
