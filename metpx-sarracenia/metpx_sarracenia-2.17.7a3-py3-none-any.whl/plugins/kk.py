
import os,stat,time
import calendar

class DOWNLOAD_REWRITE(object): 

      import urllib.parse

      def __init__(self,parent):
          if not hasattr( parent, "msg_download_threshold" ):
             parent.msg_download_threshold = [ "10M" ]

          if not hasattr( parent, "msg_download_protocol" ):
             parent.msg_download_protocol = [ "http" ]
          
      def perform(self,parent):
          logger = parent.logger
          msg    = parent.msg

          if type(parent.msg_download_threshold) is list:
             parent.msg_download_threshold = parent.chunksize_from_str( parent.msg_download_threshold[0] )

          parts = msg.partstr.split(',')
          if parts[0] == '1':
              sz=int(parts[1])
          else:
              sz=int(parts[1])*int(parts[2])

          logger.debug("msg_download sz: %d, threshold: %d download: %s to %s, " % ( \
                sz, parent.msg_download_threshold, parent.msg.urlstr, msg.local_file ) )
          if sz > parent.msg_download_threshold :
              for p in parent.msg_download_protocol :
                  parent.msg.urlstr = msg.urlstr.replace(p,"download")

              parent.msg.url = urllib.parse.urlparse(msg.urlstr)
              logger.info("msg_download triggering alternate method for: %s to %s, " % (parent.msg.urlstr, msg.local_file))

          return True

dnld_rewrite = DOWNLOAD_REWRITE(self)
self.on_message = dnld_rewrite.perform

