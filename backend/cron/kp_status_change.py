from ..services.minicrm import MiniCRMWrapper, Systems


class Main(MiniCRMWrapper):
    script_name = "pen_kp_status_change"

    def main(self):
        self.log(
            "Elkeződött a készpénzes adatlapok ellenőrzése",
            "INFO",
        )

        adatlapok = self.get_adatlapok(
            CategoryIdStr="Felmérés",
            StatusIdStr="Felmérés előkészítés",
            DijbekeroSzama2__isnull=True,
            FizetesiMod2="Készpénz",
        ).values("Id")
        for adatlap in adatlapok:
            self.minicrm_client.update_adatlap_fields(
                adatlap["Id"], {"StatusId": "Felmérésre vár"}
            )
        self.log(
            "Készpénzes adatlapok átállítva 'Felmérésre vár' státuszra",
            "INFO",
        )


if __name__ == "__main__":
    for system in Systems.objects.all():
        Main(system).main()
