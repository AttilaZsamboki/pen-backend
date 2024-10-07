from ..services.minicrm import MiniCRMWrapper
from ..models import MiniCrmAdatlapok, Systems


class Main(MiniCRMWrapper):
    script_name = "pen_order_webhook_chceck"

    def main(self):
        order_category_id = self.get_setting(
            type="CategoryId", label="Megrendelés"
        ).value
        in_progress_status_id = self.get_setting(
            type="StatusId", label="Folyamatban"
        ).value
        adatlapok = self.minicrm_client.get_adatlap(
            order_category_id, in_progress_status_id
        )
        db_adatlapok = self.get_adatlapok(
            CategoryIdStr="Megrendelés",
            Id__in=[i.Id for i in adatlapok],
        ).exclude(StatusIdStr="Folyamatban")
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


if __name__ == "__main__":
    for i in Systems.objects.all():
        Main(i).main()
