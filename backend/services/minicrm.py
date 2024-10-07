import os
from functools import partial

from dotenv import load_dotenv

from ..utils.logs import log
from ..utils.minicrm import MiniCrmClient
from ..models import (
    Systems,
    MiniCrmAdatlapok,
    Orders,
    SystemSettings,
    MiniCrmTodos,
    Felmeresek,
)


load_dotenv()


class MiniCRMWrapper:
    script_name = None
    minicrm_client = None

    def __init__(self, system: Systems, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.minicrm_client = MiniCrmClient(
            system_id=system.system_id,
            api_key=system.api_key,
            script_name=self.script_name,
        )

        if self.script_name is None:
            self.script_name = self.__class__.__name__
        self.log = partial(
            log, script_name=self.script_name, system_id=system.system_id
        )
        self.get_adatlapok = partial(
            MiniCrmAdatlapok.objects.filter, SystemId=system.system_id
        )
        self.get_todos = partial(MiniCrmTodos.objects.filter, system=system)

        self.get_orders = partial(Orders.objects.filter, system=system)
        self.get_setting = partial(SystemSettings.objects.get, system=system)

        self.system = system
        self.save_todo = partial(
            MiniCrmTodos.objects.create,
            system=system,
        )

        self.get_felmeres = partial(Felmeresek.objects.get, system=system)
