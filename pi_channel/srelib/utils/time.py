from datetime import datetime
from datetime import timedelta


def get_modified_timestamp(datetime_obj, num_minutes_to_manipulate):
    """ Returns the datetime object with the manipulated time. 
    Args:
        datetime_obj(datetime): Contains the base time.
        num_minutes_to_manipulate(int): The number of minutes to add or subtract
        to the base time.  Negative minutes will be subtracted.
    Returns:
        datetime: The datetime obj with the updated time.
    """
    new_time = None    
    if(num_minutes_to_manipulate > 0):
        new_time = datetime_obj + timedelta(minutes=abs(num_minutes_to_manipulate))
    else:
        new_time = datetime_obj - timedelta(minutes=abs(num_minutes_to_manipulate))
    
    return new_time

def unix_time_millis(dt):
    """ Get epoch time for the datetime object passed in.
    Args:
        dt(datetime): The datetime object.
    Returns:
        int: The epoch time.
    """
    epoch = datetime(1970,1,1)
    return int((dt - epoch).total_seconds())


def is_in_dst_period(dt):
    """ Assumes dt is in a timezone that supports US dst. Returns
    True if the date provided is in a DST period.
    Args:
        dt(datetime): The date
    Returns:
        bool: True if date is in DST period False otherwise.
    """
    is_dst = False
    #need to find which day is second sunday in march for this year.
    #starts second sunday in march
    #cant be the first 7 days
    #start on the 8th of the month.
    start_dt = datetime.strptime(
        "03 08 {}".format(dt.year),
        '%m %d %Y'
    )
    while(start_dt.weekday() != 6):
        start_dt = get_modified_timestamp(start_dt, 60 * 24)
    
    #ends first sunday in november
    end_dt = datetime.strptime(
        "11 01 {}".format(dt.year),
        '%m %d %Y'
    )
    while(start_dt.weekday() != 6):
        end_dt = get_modified_timestamp(start_dt, 60 * 24)

    if((dt >= start_dt) and (dt < end_dt)):
        is_dst = True

    return is_dst


def is_in_previous_gmt_day(dt, tz):
    """ Returns true if the time enclosed in dt in the tz timezone
    is in the previous day GMT. For example, 3/4/2020 03:30 IST is
    actually on day 3/3/2020 if the timezone is GMT.  Therefore
    this methods would return true for this example.
    Args:
        dt(datetime): The datetime object that contains the date and time.
        tz(str): The timezone.  Valid values: "PT", "CT", "IST".
    Returns:
        bool: True if the time passed is the previous day GMT.
    """
    if(tz == "IST"):
        if((dt.hour <= 5) and (dt.minute <= 29)):
            return True
    return False

def is_in_next_gmt_day(dt, tz):
    """ Returns true if the datetime in the given timezone
    has crossed the day in GMT.
    Args:
        dt(datetime): The datetime object
        tz(str): The timezone. tz can only be
        "PT", "CT", "IST".
    Returns:
        bool: True if dt is next day in GMT, False otherwise.
    """

    test_day = dt.day
    minutes_to_manipulate = 0
    if(tz == "IST"):
        pass
    elif(tz == "PT"):
        if(is_in_dst_period(dt) == True):
            minutes_to_manipulate = (60 * 7)
        else:
            minutes_to_manipulate = (60 * 8)
    elif(tz == "CT"):
        if(is_in_dst_period(dt) == True):
            minutes_to_manipulate = (60 * 5)
        else:
            minutes_to_manipulate = (60 * 6)

    new_dt = get_modified_timestamp(dt, minutes_to_manipulate)
    new_day = new_dt.day

    if(test_day < new_day):
        #The timestamp given is new day GMT
        return True
    return False

def get_gmt_dt(dt, tz):
    """ Get a datetime object in gmt 
    for the given datime and timezone.  tz can only be
    "PT", "CT", "IST".
    Args:
        dt(datetime): The time
        tz(str): Timezone abbreviation.
    Returns:
        datetime: In UTC
    """
    #Determine if in DST
    is_dst = is_in_dst_period(dt)
    minutes_to_manipulate = 0
    if(tz == "IST"):
        minutes_to_manipulate = (-1 * 60 * 5) - 30
    elif(tz == "PT"):
        if(is_dst):
            minutes_to_manipulate = (60 * 7)
        else:
            minutes_to_manipulate = (60 * 8)
    elif(tz == "CT"):
        if(is_dst):
            minutes_to_manipulate = (60 * 5)
        else:
            minutes_to_manipulate = (60 * 6)

    modified_dt = get_modified_timestamp(dt, minutes_to_manipulate)
    #print("{} dst {}: {} to ---> {}".format(tz, is_dst, dt, modified_dt))
    return modified_dt

def get_dt_from_gmt(gmt_dt, target_tz):
    """ Transorm the given GMT datetime object to
    the target timezone.  Returns a new instance of a datetime object
    as the result.
    Args:
        gmt_dt(datetime): The datetime object that represents a GMT datetime.
        target_tz(str): The target timezone for the transformation.
    Returns:
        datetime: The datetime after the transformation from GMT to the 
        target time zone.
    """
    is_dst = False
    if(target_tz in ["PT", "CT"]):
        #TODO: Make sure that this is ok
        is_dst = is_in_dst_period(gmt_dt)
    
    minutes_to_manipulate = 0
    if(target_tz == "IST"):
        minutes_to_manipulate = (60 * 5) + 30
    elif(target_tz == "PT"):
        if(is_dst):
            minutes_to_manipulate = (-1 * 60 * 7)
        else:
            minutes_to_manipulate = (-1 * 60 * 8)
    elif(target_tz == "CT"):
        if(is_dst):
            minutes_to_manipulate = (-1 * 60 * 5)
        else:
            minutes_to_manipulate = (-1 * 60 * 6)

    modified_dt = get_modified_timestamp(gmt_dt, minutes_to_manipulate)
    return modified_dt


def get_time_in_target_tz(source_dt, source_tz, target_tz):
    """ Used to convert the datetime to the target time zone.
    Args:
        source_dt(datetime): The datetime object.
        source_tz(st): The implied timezone for the date.
        target_tz(st): The target timezone conversion.
        Valid values are "PT", "CT", "IST"
    Returns:
        datetime: The date and time in the target timezone
    """
    is_dst = False
    if(source_tz == target_tz):
        return source_dt

    if(target_tz in ["PT", "CT"]):
        is_dst = is_in_dst_period(source_dt)
    # get the gmt version of the time.
    #print("Original dt = {} {}".format(source_dt, source_tz))
    gmt_dt = get_gmt_dt(source_dt, source_tz)
    #print("GMT dt = {}".format(gmt_dt))

    minutes_to_manipulate = 0
    if(target_tz == "IST"):
        minutes_to_manipulate = (60 * 5) + 30
    elif(target_tz == "PT"):
        if(is_dst):
            minutes_to_manipulate = (-1 * 60 * 7)
        else:
            minutes_to_manipulate = (-1 * 60 * 8)
    elif(target_tz == "CT"):
        if(is_dst):
            minutes_to_manipulate = (-1 * 60 * 5)
        else:
            minutes_to_manipulate = (-1 * 60 * 6)

    modified_dt = get_modified_timestamp(gmt_dt, minutes_to_manipulate)
    #print("Modified to {} {}, dst {}".format(modified_dt, target_tz, is_dst))
    
    return modified_dt


if __name__ == "__main__":
    tz = "IST"
    dt = datetime.strptime('07 14 2020 05:29', '%m %d %Y %H:%M')
    print("Is next day = {}".format(is_in_next_gmt_day(dt, tz)))
    print("Is previous day = {}".format(is_in_previous_gmt_day(dt, tz)))
    print("{} IST = {} GMT".format(
            dt,
            get_gmt_dt(dt, tz)
        )
    )

