import os
from .utils import _logger


def get_attachment_path(request, attachments_dir, message_id, name):
    # creating directory for loaded attachment, if it doesn't exists
    attachment_dir = '{}/attachments'.format(attachments_dir)
    if not os.path.exists(attachment_dir):
        os.makedirs(attachment_dir)
    attachment = '{}/{}_{}'.format(attachment_dir, message_id, name)
    with open(attachment, 'wb') as attached_file:
        attached_file.write(request.content)
    _logger.info('Attachment successfully saved')
    return os.path.abspath(attachment)
