import logging

class MyLogger:

  # level e.g logging.DEBUG | logging.INFO | logging.WARNING | logging.ERROR
  def __init__(self, level, logger_name):
    # Init logger
    logging.basicConfig(level=level, format='%(name)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(logger_name)

  def log(self, message, level="info"):
    if level == "error":
      self.logger.error(message)
    elif level == "warning":
      self.logger.warning(message)
    elif level == "debug":
      self.logger.debug(message)
    else:
      self.logger.info(message)


if __name__ == '__main__':
  ml = MyLogger(logging.INFO,'MyLogger')
  ml.log("debug", "debug")
  ml.log("info")
  ml.log("warning", "warning")
  ml.log("error", "error")
