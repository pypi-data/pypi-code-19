# coding: utf-8

import logging
import os
import glob


logger = logging.getLogger(__name__)  # pylint: disable=C0103


def search_backup(path, customer_id):
    """Searches the best matching backup fot the given client id in te path
    :param path: Path where the backups are stored
    :param customer_id: Unique customer identifier
    :return: Returns the best matching backup (full path)
    """
    logger.info('Searching backup for %s in "%s"',
                customer_id, os.path.abspath(path))
    files = sorted(glob.glob(os.path.join(
        path, u'{cid}*'.format(cid=customer_id))), key=unicode.lower)
    logger.info('Available backups: %s', str(files))
    if files:
        logger.info('Will use: %s', str(files[-1]))
        return files[-1]
    return None
