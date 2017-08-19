from functools import wraps
from telegram import Bot, Update


def admin_access(admins_ids):
    def access(func):
        @wraps(func)
        def wrapped(self, bot: Bot, update: Update, *args, **kwargs):
            user = update.effective_user
            if user.id not in admins_ids:
                self.logger.info(f"Unauthorized access denied for {user}.")
                return
            return func(self, bot, update, *args, **kwargs)
        return wrapped
    return access
