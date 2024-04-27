from ..services.minicrm import MiniCRMWrapper
from ..utils.logs import log
from ..models import MiniCrmAdatlapok


class Main(MiniCRMWrapper):
    script_name = "pen_order_webhook_chceck"

    def main(self):
        adatlapok = self.minicrm_client.get_adatlap(29, "3008")
        db_adatlapok = MiniCrmAdatlapok.objects.filter(
            CategoryId="29", Id__in=list(map(lambda adatlap: adatlap.Id, adatlapok))
        ).exclude(StatusId="3008")
        for adatlap in db_adatlapok:
            adatlap = self.minicrm_client.get_adatlap_details(adatlap.Id)
            valid_fields = {f.name for f in MiniCrmAdatlapok._meta.get_fields()}
            filtered_data = {
                k: v
                for k, v in adatlap.items()
                if k in valid_fields
                and k
                not in [
                    "ProjectHash",
                    "ProjectEmail",
                    "UserId",
                    "CreatedBy",
                    "UpdatedBy",
                    "LezarasOka",
                    "MiertMentunkKiFeleslegesen",
                    "ElutasitasOka",
                ]
            }
            MiniCrmAdatlapok(
                StatusId=[i.StatusId for i in adatlapok if i.Id == adatlap.Id][0],
                MainContacId=[i.BusinessId for i in adatlapok if i.Id == adatlap.Id][0],
                **filtered_data
            ).save()


Main().main()
