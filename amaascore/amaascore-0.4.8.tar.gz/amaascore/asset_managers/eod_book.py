import datetime
from amaascore.core.amaas_model import AMaaSModel

class EODBook(AMaaSModel):

    def __init__(self, asset_manager_id, book_id, utc_close_time,
                 eod_book_status='Active', *args, **kwargs):
        self.asset_manager_id = asset_manager_id
        self.book_id = book_id
        self.utc_close_time = utc_close_time.strftime('%H:%M:%S') if isinstance(utc_close_time, datetime.time) else str(utc_close_time)
        self.eod_book_status = eod_book_status
        super(EODBook, self).__init__(*args, **kwargs)