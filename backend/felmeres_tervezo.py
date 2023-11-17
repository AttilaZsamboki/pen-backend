from .utils.google_maps import calculate_distance
from .models import MiniCrmAdatlapok
from django.db.models import DateTimeField
from django.db.models.functions import Cast, TruncDate
import datetime


def main(felmeres_adatlap):
    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=23, FelmeresIdopontja2__isnull=False
    ).exclude(StatusId__in=["2927", "3084", "3086", "2929"])

    adatlapok = adatlapok.annotate(
        FelmeresIdopontja2_datetime=Cast("FelmeresIdopontja2", DateTimeField())
    )

    distinct_dates = (
        adatlapok.annotate(date=TruncDate("FelmeresIdopontja2_datetime"))
        .values("date")
        .distinct()
    )

    open_slots = []
    for date in distinct_dates:
        for felmero in adatlapok.values("Felmero2").distinct():
            adatlap_filter = adatlapok.filter(
                FelmeresIdopontja2__date=date["date"],
                Felmero2=felmero["Felmero2"],
            ).order_by("FelmeresIdopontja2")
            for i in range(len(adatlap_filter) - 1):
                distance_from = calculate_distance(
                    start=get_address(adatlap_filter[i]),
                    end=get_address(felmeres_adatlap),
                    mode="driving",
                )
                distance_to = calculate_distance(
                    start=get_address(felmeres_adatlap),
                    end=get_address(adatlap_filter[i + 1]),
                    mode="driving",
                )

                time_between_next = (
                    adatlap_filter[i + 1].FelmeresIdopontja2_datetime
                    - adatlap_filter[i].FelmeresIdopontja2_datetime
                )

                if (
                    time_between_next.total_seconds()
                    - (
                        # Felmérések ideje
                        3600
                        # Út a következő felmérésre
                        + distance_from["duration"]
                        + distance_to["duration"]
                    )
                    < 3600
                ):
                    print(distance_from["duration"], distance_to["duration"])
                    print("Nincs elég idő a felmérésre")
                else:
                    distance_between = calculate_distance(
                        start=get_address(adatlap_filter[i]),
                        end=get_address(adatlap_filter[i + 1]),
                        mode="driving",
                    )
                    open_slots.append(
                        {
                            "at": adatlap_filter[i].FelmeresIdopontja2_datetime
                            + datetime.timedelta(
                                seconds=3600 + distance_to["duration"]
                            ),
                            "felmero": felmero["Felmero2"],
                            "diff": distance_from["duration"]
                            + distance_to["duration"]
                            - distance_between["duration"],
                        }
                    )
                    print("Van elég idő a felmérésre")

    print(open_slots)
    return open_slots


def get_address(adatlap):
    return (
        f"{adatlap.Cim2} {adatlap.Telepules}, {adatlap.Iranyitoszam} {adatlap.Orszag}"
    )


main(MiniCrmAdatlapok.objects.get(Id="43953"))
