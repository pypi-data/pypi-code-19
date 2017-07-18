import os
from tellurium import antimonyConverter
from tellurium.teconverters import saveInlineOMEX, inlineOmexImporter
from errno import EPERM, EIO, ENXIO, EACCES, EFBIG, ENOSPC, EROFS, ENAMETOOLONG

def errnoToMessage(e):
    return {
        EPERM:  'Operation not permitted',
        EIO:    'I/O error',
        ENXIO:  'No such device or address',
        EACCES: 'Permission denied',
        EFBIG:  'File too large',
        ENOSPC: 'No space left on device',
        EROFS:  'Read-only file system',
        ENAMETOOLONG: 'File name too long',
    }[e]

def convert_file_comm(comm, msg):
    """ Handles convert file requests from Tellurium.

    :param comm: The kernel Comm instance
    :param msg: The comm_open message
    """

    # def printout(s):
    #     with open('/tmp/nterout', 'a') as myfile:
    #         myfile.write(s+'\n')
    # printout('message = {}'.format(msg))
    # if 'path' in msg['content']['data']:
    #     printout('importing {}'.format(msg['content']['data']['path']))

    # Register handler for later messages
    @comm.on_msg
    def _recv(msg):
        # Use msg['content']['data'] for the data in the message
        # with open('/tmp/nterout', 'a') as myfile:
        #     myfile.write('import_file_comm _recv\n')
        pass

    def returnSource(src):
        'convert the file and send it back'
        comm.send({'content': src})
        comm.close()

    def returnError(err):
        'Report error'
        comm.send({'status': 'error', 'error': err})
        comm.close()

    if not 'target_format' in msg['content']['data']:
        # printout('import_file_comm no target_format')
        returnError('Expected "target_format" in message data payload')
    else:
        # printout('set target_format')
        target_format = msg['content']['data']['target_format']
        if 'path' in msg['content']['data']:
            # given path to file
            file_path = msg['content']['data']['path']
            if target_format == 'python':
                try:
                    with open(file_path) as f:
                        returnSource(f.read())
                except OSError as err:
                    try:
                        returnError('{}.'.format(errnoToMessage(err.errno)))
                    except:
                        returnError('Unable to import file.')
                except Exception as e:
                    returnError(str(e))
            elif target_format == 'antimony':
                module,sb = antimonyConverter().sbmlFileToAntimony(file_path)
                # Antimony pads with a newline for some reason
                returnSource(sb.rstrip())
            elif target_format == 'cellml':
                # printout('cellml format')
                module,sb = antimonyConverter().cellmlFileToAntimony(file_path)
                # Antimony pads with a newline for some reason
                returnSource(sb.rstrip())
            elif target_format == 'omex':
                # printout('target_format = omex')
                try:
                    returnSource(inlineOmexImporter.fromFile(file_path).toInlineOmex())
                except Exception as e:
                    # printout('error '+str(e))
                    returnError(str(e))
        elif 'content' in msg['content']['data']:
            # given raw content
            raw_content = msg['content']['data']['content']
            if target_format == 'antimony':
                module,sb = antimonyConverter().sbmlToAntimony(raw_content)
                returnAntimony(sb)
        else:
            # printout('import_file_comm no path or content')
            returnError('Expected "path" or "content" in message data payload')

def save_file_comm(comm, msg):
    """ Handles save file requests from Tellurium.

    :param comm: The kernel Comm instance
    :param msg: The comm_open message
    """

    # def printout(s):
    #     with open('/tmp/nterout', 'a') as myfile:
    #         myfile.write(s+'\n')
    # printout('save_file_comm')

    def returnOkay(path):
        'Report success with written file path'
        # printout('saved {}'.format(path))
        # Antimony pads with a newline for some reason
        comm.send({'status': 'okay', 'file': path})
        comm.close()

    def returnError(err):
        'Report success with written file path'
        # printout('error {}'.format(err))
        # Antimony pads with a newline for some reason
        comm.send({'status': 'error', 'error': err})
        comm.close()

    if  not 'path' in msg['content']['data'] or \
        not 'target_format' in msg['content']['data'] or \
        not 'source_format' in msg['content']['data'] or \
        not 'source_str' in msg['content']['data']:
        # printout('missing info')
        returnError('Missing data for save command')
    else:
        # printout('have info')
        source_format = msg['content']['data']['source_format']
        target_format = msg['content']['data']['target_format']
        source_str    = msg['content']['data']['source_str']
        path      = msg['content']['data']['path']
        if source_format == 'antimony':
            if target_format == 'sbml':
                target_str = antimonyConverter().antimonyToSBML(source_str)
                try:
                    with open(path, 'w') as f:
                        f.write(target_str)
                except OSError as err:
                    try:
                        returnError('{}.'.format(errnoToMessage(err.errno)))
                    except:
                        returnError('Unable to write file.')
        elif source_format == 'omex':
            # printout('src omex')
            try:
                saveInlineOMEX(source_str, path)
                returnOkay(os.path.basename(path))
            except OSError as err:
                try:
                    returnError('{}.'.format(errnoToMessage(err.errno)))
                except:
                    # Unknown OS error
                    # import traceback
                    # printout(traceback.format_exc())
                    returnError('Unable to write file.')
            except:
                # Unknown error
                # import traceback
                # printout(traceback.format_exc())
                returnError('Unable to write file.')
