from .utils.google_maps import calculate_distance
from .models import MiniCrmAdatlapok, Cimek, OpenSlots
from .utils.utils import round_to_closest_hour
from django.db.models import DateTimeField
from django.db.models.functions import Cast, TruncDate
import datetime
from django.utils import timezone
from .utils.logs import log


def main(felmeres_adatlap):
    OpenSlots.objects.filter(adatlap_id=felmeres_adatlap.Id).delete()
    adatlapok = MiniCrmAdatlapok.objects.filter(
        CategoryId=23,
        FelmeresIdopontja2__isnull=False,
        FelmeresIdopontja2__gte=timezone.now(),
    ).exclude(StatusId__in=["2927", "3084", "3086", "2929"])

    next_30_days = [
        datetime.datetime.today() + datetime.timedelta(days=i)
        for i in range(1, 31)
        if (datetime.datetime.today() + datetime.timedelta(days=i)).weekday() < 5
    ]

    for date in next_30_days:
        for felmero in Cimek.objects.all().values("Felmero2").distinct():
            adatlap_filter = adatlapok.filter(
                FelmeresIdopontja2__date=date,
                Felmero2=felmero["Felmero2"],
            ).order_by("FelmeresIdopontja2")
            if not adatlap_filter:
                OpenSlots(
                    adatlap_id=felmeres_adatlap.Id,
                    at=date.replace(
                        hour=9,
                        minute=0,
                        second=0,
                        microsecond=0,
                    ),
                    group=felmero,
                    diff=calculate_distance(
                        start=Cimek.objects.get(name=felmero["Felmero2"]).address,
                        end=get_address(felmeres_adatlap),
                    )["duration"],
                ).save()
                continue

            distance_home = calculate_distance(
                start=get_address(adatlap_filter.last()),
                end=Cimek.objects.get(name=felmero["Felmero2"]).address,
                mode="driving",
            )
            distance_home_from_destination = calculate_distance(
                start=get_address(adatlap_filter.last()),
                end=Cimek.objects.get(name=felmero["Felmero2"]).address,
                mode="driving",
                waypoints=get_address(felmeres_adatlap),
            )

            workhours_left = (
                8 * 3600
                - (
                    (
                        adatlap_filter.last().FelmeresIdopontja2
                        + datetime.timedelta(seconds=3600)
                        + datetime.timedelta(seconds=distance_home["duration"])
                    )
                    - (
                        adatlap_filter.first().FelmeresIdopontja2
                        - datetime.timedelta(
                            seconds=calculate_distance(
                                start=Cimek.objects.get(
                                    name=felmero["Felmero2"],
                                ).address,
                                end=get_address(adatlap_filter[0]),
                                mode="driving",
                            )["duration"]
                        )
                    )
                ).total_seconds()
            )
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
                    adatlap_filter[i + 1].FelmeresIdopontja2
                    - adatlap_filter[i].FelmeresIdopontja2
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
                    continue
                else:
                    distance_between = calculate_distance(
                        start=get_address(adatlap_filter[i]),
                        end=get_address(adatlap_filter[i + 1]),
                        mode="driving",
                    )
                    OpenSlots(
                        adatlap_id=felmeres_adatlap.Id,
                        at=round_to_closest_hour(
                            adatlap_filter[i].FelmeresIdopontja2_datetime
                            + datetime.timedelta(seconds=3600 + distance_to["duration"])
                        ),
                        group=felmero["Felmero2"],
                        diff=distance_from["duration"]
                        + distance_to["duration"]
                        - distance_between["duration"],
                    ).save()
            if workhours_left > 3600:
                time_from_last = calculate_distance(
                    start=get_address(adatlap_filter.last()),
                    end=get_address(felmeres_adatlap),
                    mode="driving",
                )
                if workhours_left - time_from_last["duration"] > 3600:
                    log(
                        "A felmérést a nap végére terveztük.",
                        "INFO",
                        "pen_felmeres_tervezo",
                        "Adatlap Id: "
                        + str(adatlap_filter.last().Id)
                        + ". Az utolsótól való távolság: "
                        + str(time_from_last["duration"])
                        + " másodperc."
                        + " A munkaidő végéig hátralévő idő: "
                        + str(workhours_left)
                        + " másodperc."
                        + " Az utolsó felmérés időpontja: "
                        + str(adatlap_filter.last().FelmeresIdopontja2),
                    )

                    OpenSlots(
                        adatlap_id=felmeres_adatlap.Id,
                        at=round_to_closest_hour(
                            adatlap_filter.last().FelmeresIdopontja2
                            + datetime.timedelta(
                                seconds=(3600 + time_from_last["duration"])
                            )
                        ),
                        group=felmero["Felmero2"],
                        diff=distance_home_from_destination["duration"]
                        - distance_home["duration"],
                    ).save()


def get_address(adatlap):
    return (
        f"{adatlap.Cim2} {adatlap.Telepules}, {adatlap.Iranyitoszam} {adatlap.Orszag}"
    )


main(MiniCrmAdatlapok.objects.get(Id="43151"))
