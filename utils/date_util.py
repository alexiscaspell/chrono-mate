import datetime

def cast_to_datetime(value):
    converted_value = None
    possible_formats = ["%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%S.%f","%Y-%m-%dT%H:%M:%S.%f%z",
                        "%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S", '%Y-%m-%d %H:%M:%S', "%Y-%m-%dT%H:%M:%SZ"]

    for possible_format in possible_formats:
        try:
            converted_value = datetime.datetime.strptime(
                str(value).lstrip().rstrip(), possible_format)
            return converted_value
        except BaseException as e:
            continue

    raise RuntimeError(f"No es posible castear {value} a datetime")

def now_iso8601_utc(utc_number:int=3):
    return to_utc(datetime.datetime.now(datetime.timezone.utc,utc_number))

def to_utc(some_date,utc_number:int=3):
    dummy = cast_to_datetime(f'2023-03-22T17:07:10.000-0{utc_number}00')
    return some_date.astimezone(dummy.tzinfo)

def between(some_date:datetime.datetime,start_date:datetime.datetime,end_date:datetime.datetime)->bool:
    return some_date.date()<=end_date.date() and some_date.date()>=start_date.date()
