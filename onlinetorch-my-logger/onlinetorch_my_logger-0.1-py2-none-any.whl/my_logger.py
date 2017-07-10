import logging

class MyLogger:

  def __init__(self, logger_name):
    # Init logger
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    self.logger = logging.getLogger(logger_name)

  def log(self, message, level="info"):
    if level == "error":
      self.logger.error(message)
    elif level == "warning":
      self.logger.warning(message)
    else:
      self.logger.info(message)


if __name__ == '__main__':
  ml = MyLogger('MyLogger')
  ml.log("hallo welt", "error")
