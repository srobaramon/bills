class Call:
    main_time_start=(8,0)
    main_time_end=(16,0)
    main_time_price=1
    other_time_price=0.5
    bonus_minutes=5
    bonus_minutes_price=0.2

    def __init__(self, start_time, end_time):
        self.start_time = start_time
        self.end_time = end_time
        self.duration = start_time-end_time

    def get_main_minutes():
        pass

    def get_other_minutes():
        pass

    def get_total_minutes():
        return end_time-start_time
    