
INVALID_HANDLE_VALUE = -1

ERROR_NO_MORE_ITEMS = 259
ERROR_MORE_DATA = 234
ERROR_BAD_COMMAND = 22
ERROR_INSUFFICIENT_BUFFER = 122
ERROR_INVALID_FLAGS = 1004
ERROR_INVALID_HANDLE = 6
ERROR_INVALID_DATA = 13
ERROR_INVALID_USER_BUFFER = 1784
ERROR_NO_SUCH_DEVINST = 523
ERROR_NOT_ENOUGH_MEMORY = 9
ERROR_NOT_FOUND = 1168
ERROR_ACCESS_DENIED = 5
SDDL_REVISION_1 = 1

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
GENERIC_EXECUTE = 0x20000000
GENERIC_ALL = 0x10000000

FILE_SHARE_READ = 0x00000001
FILE_SHARE_WRITE = 0x00000002
FILE_SHARE_NONE = 0x00000000
FILE_SHARE_DELETE = 0x00000004

CREATE_NEW = 1
CREATE_ALWAYS = 2
OPEN_EXISTING = 3
OPEN_ALWAYS = 4
TRUNCATE_EXISTING = 5

FILE_FLAG_OVERLAPPED = 0x40000000

# Taken from
# C:\Program Files\Microsoft SDKs\Windows\v6.0A\Include\WinIoCtl.h

IOCTL_STORAGE_BASE = 45
IOCTL_STORAGE_CHECK_VERIFY = 2967552
IOCTL_STORAGE_CHECK_VERIFY2 = 2951168
IOCTL_STORAGE_MEDIA_REMOVAL = 2967556
IOCTL_STORAGE_EJECT_MEDIA = 2967560
IOCTL_STORAGE_LOAD_MEDIA = 2967564
IOCTL_STORAGE_LOAD_MEDIA2 = 2951180
IOCTL_STORAGE_RESERVE = 2967568
IOCTL_STORAGE_RELEASE = 2967572
IOCTL_STORAGE_FIND_NEW_DEVICES = 2967576
IOCTL_STORAGE_EJECTION_CONTROL = 2951488
IOCTL_STORAGE_MCN_CONTROL = 2951492
IOCTL_STORAGE_GET_MEDIA_TYPES = 2952192
IOCTL_STORAGE_GET_MEDIA_TYPES_EX = 2952196
IOCTL_STORAGE_GET_MEDIA_SERIAL_NUMBER = 2952208
IOCTL_STORAGE_GET_HOTPLUG_INFO = 2952212
IOCTL_STORAGE_SET_HOTPLUG_INFO = 3001368
IOCTL_STORAGE_RESET_BUS = 2969600
IOCTL_STORAGE_RESET_DEVICE = 2969604
IOCTL_STORAGE_BREAK_RESERVATION = 2969620
IOCTL_STORAGE_PERSISTENT_RESERVE_IN = 2969624
IOCTL_STORAGE_PERSISTENT_RESERVE_OUT = 3002396
IOCTL_STORAGE_GET_DEVICE_NUMBER = 2953344
IOCTL_STORAGE_PREDICT_FAILURE = 2953472
IOCTL_STORAGE_READ_CAPACITY = 2969920
IOCTL_STORAGE_QUERY_PROPERTY = 2954240
IOCTL_STORAGE_GET_BC_PROPERTIES = 2971648
IOCTL_STORAGE_ALLOCATE_BC_STREAM = 3004420
IOCTL_STORAGE_FREE_BC_STREAM = 3004424
IOCTL_STORAGE_CHECK_PRIORITY_HINT_SUPPORT = 2955392
IOCTL_STORAGE_BC_VERSION = 1
IOCTL_DISK_BASE = 7
IOCTL_DISK_GET_DISK_ATTRIBUTES = 458992
IOCTL_DISK_SET_DISK_ATTRIBUTES = 508148
IOCTL_DISK_GET_SAN_SETTINGS = 475648
IOCTL_DISK_SET_SAN_SETTINGS = 508420
IOCTL_DISK_IS_CLUSTERED = 459000
IOCTL_DISK_GET_DRIVE_GEOMETRY = 458752
IOCTL_DISK_GET_PARTITION_INFO = 475140
IOCTL_DISK_SET_PARTITION_INFO = 507912
IOCTL_DISK_GET_DRIVE_LAYOUT = 475148
IOCTL_DISK_SET_DRIVE_LAYOUT = 507920
IOCTL_DISK_VERIFY = 458772
IOCTL_DISK_FORMAT_TRACKS = 507928
IOCTL_DISK_REASSIGN_BLOCKS = 507932
IOCTL_DISK_PERFORMANCE = 458784
IOCTL_DISK_IS_WRITABLE = 458788
IOCTL_DISK_LOGGING = 458792
IOCTL_DISK_FORMAT_TRACKS_EX = 507948
IOCTL_DISK_HISTOGRAM_STRUCTURE = 458800
IOCTL_DISK_HISTOGRAM_DATA = 458804
IOCTL_DISK_HISTOGRAM_RESET = 458808
IOCTL_DISK_REQUEST_STRUCTURE = 458812
IOCTL_DISK_REQUEST_DATA = 458816
IOCTL_DISK_PERFORMANCE_OFF = 458848
IOCTL_DISK_CONTROLLER_NUMBER = 458820
IOCTL_DISK_GET_PARTITION_INFO_EX = 458824
IOCTL_DISK_SET_PARTITION_INFO_EX = 507980
IOCTL_DISK_GET_DRIVE_LAYOUT_EX = 458832
IOCTL_DISK_SET_DRIVE_LAYOUT_EX = 507988
IOCTL_DISK_CREATE_DISK = 507992
IOCTL_DISK_GET_LENGTH_INFO = 475228
IOCTL_DISK_GET_DRIVE_GEOMETRY_EX = 458912
IOCTL_DISK_REASSIGN_BLOCKS_EX = 508068
IOCTL_DISK_UPDATE_DRIVE_SIZE = 508104
IOCTL_DISK_GROW_PARTITION = 508112
IOCTL_DISK_GET_CACHE_INFORMATION = 475348
IOCTL_DISK_SET_CACHE_INFORMATION = 508120
IOCTL_DISK_DELETE_DRIVE_LAYOUT = 508160
IOCTL_DISK_UPDATE_PROPERTIES = 459072
IOCTL_DISK_FORMAT_DRIVE = 508876
IOCTL_DISK_SENSE_DEVICE = 459744
IOCTL_DISK_CHECK_VERIFY = 477184
IOCTL_DISK_MEDIA_REMOVAL = 477188
IOCTL_DISK_EJECT_MEDIA = 477192
IOCTL_DISK_LOAD_MEDIA = 477196
IOCTL_DISK_RESERVE = 477200
IOCTL_DISK_RELEASE = 477204
IOCTL_DISK_FIND_NEW_DEVICES = 477208
IOCTL_DISK_GET_MEDIA_TYPES = 461824
IOCTL_CHANGER_BASE = 48
IOCTL_CHANGER_GET_PARAMETERS = 3162112
IOCTL_CHANGER_GET_STATUS = 3162116
IOCTL_CHANGER_GET_PRODUCT_DATA = 3162120
IOCTL_CHANGER_SET_ACCESS = 3194896
IOCTL_CHANGER_GET_ELEMENT_STATUS = 3194900
IOCTL_CHANGER_INITIALIZE_ELEMENT_STATUS = 3162136
IOCTL_CHANGER_SET_POSITION = 3162140
IOCTL_CHANGER_EXCHANGE_MEDIUM = 3162144
IOCTL_CHANGER_MOVE_MEDIUM = 3162148
IOCTL_CHANGER_REINITIALIZE_TRANSPORT = 3162152
IOCTL_CHANGER_QUERY_VOLUME_TAGS = 3194924
IOCTL_SERIAL_LSRMST_INSERT = 1769596
IOCTL_SERENUM_EXPOSE_HARDWARE = 3604992
IOCTL_SERENUM_REMOVE_HARDWARE = 3604996
IOCTL_SERENUM_PORT_DESC = 3605000
IOCTL_SERENUM_GET_PORT_NAME = 3605004
IOCTL_VOLUME_BASE = 86
IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = 5636096
IOCTL_VOLUME_IS_CLUSTERED = 5636144
IOCTL_SMARTCARD_POWER = 3211268
IOCTL_SMARTCARD_GET_ATTRIBUTE = 3211272
IOCTL_SMARTCARD_SET_ATTRIBUTE = 3211276
IOCTL_SMARTCARD_CONFISCATE = 3211280
IOCTL_SMARTCARD_TRANSMIT = 3211284
IOCTL_SMARTCARD_EJECT = 3211288
IOCTL_SMARTCARD_SWALLOW = 3211292
IOCTL_SMARTCARD_IS_PRESENT = 3211304
IOCTL_SMARTCARD_IS_ABSENT = 3211308
IOCTL_SMARTCARD_SET_PROTOCOL = 3211312
IOCTL_SMARTCARD_GET_STATE = 3211320
IOCTL_SMARTCARD_GET_LAST_ERROR = 3211324
IOCTL_SMARTCARD_GET_PERF_CNTR = 3211328
IOCTL_SCSI_BASE = 4
IOCTL_SCSI_PASS_THROUGH = 315396
IOCTL_SCSI_MINIPORT = 315400
IOCTL_SCSI_GET_INQUIRY_DATA = 266252
IOCTL_SCSI_GET_CAPABILITIES = 266256
IOCTL_SCSI_PASS_THROUGH_DIRECT = 315412
IOCTL_SCSI_GET_ADDRESS = 266264
IOCTL_SCSI_RESCAN_BUS = 266268
IOCTL_SCSI_GET_DUMP_POINTERS = 266272
IOCTL_SCSI_FREE_DUMP_POINTERS = 266276
IOCTL_IDE_PASS_THROUGH = 315432
IOCTL_ATA_PASS_THROUGH = 315436
IOCTL_ATA_PASS_THROUGH_DIRECT = 315440
IOCTL_ATA_MINIPORT = 315444
IOCTL_SCSI_MINIPORT_NVCACHE = 1771008
IOCTL_MOUNTDEV_LINK_CREATED = 5095440
IOCTL_MOUNTDEV_LINK_DELETED = 5095444
IOCTL_MOUNTDEV_QUERY_DEVICE_NAME = 5046280
IOCTL_MOUNTDEV_QUERY_STABLE_GUID = 5046296
IOCTL_MOUNTDEV_QUERY_SUGGESTED_LINK_NAME = 5046284
IOCTL_MOUNTDEV_QUERY_UNIQUE_ID = 5046272
IOCTL_MOUNTMGR_AUTO_DL_ASSIGNMENTS = 7192596
IOCTL_MOUNTMGR_BOOT_DL_ASSIGNMENT = 7192644
IOCTL_MOUNTMGR_CHANGE_NOTIFY = 7159840
IOCTL_MOUNTMGR_CHECK_UNPROCESSED_VOLUMES = 7159848
IOCTL_MOUNTMGR_CREATE_POINT = 7192576
IOCTL_MOUNTMGR_DELETE_POINTS = 7192580
IOCTL_MOUNTMGR_DELETE_POINTS_DBONLY = 7192588
IOCTL_MOUNTMGR_KEEP_LINKS_WHEN_OFFLINE = 7192612
IOCTL_MOUNTMGR_NEXT_DRIVE_LETTER = 7192592
IOCTL_MOUNTMGR_QUERY_AUTO_MOUNT = 7143484
IOCTL_MOUNTMGR_QUERY_DOS_VOLUME_PATH = 7143472
IOCTL_MOUNTMGR_QUERY_DOS_VOLUME_PATHS = 7143476
IOCTL_MOUNTMGR_QUERY_POINTS = 7143432
IOCTL_MOUNTMGR_SCRUB_REGISTRY = 7192632
IOCTL_MOUNTMGR_SET_AUTO_MOUNT = 7192640
IOCTL_MOUNTMGR_TRACELOG_CACHE = 7159880
IOCTL_MOUNTMGR_VOLUME_ARRIVAL_NOTIFICATION = 7159852
IOCTL_MOUNTMGR_VOLUME_MOUNT_POINT_CREATED = 7192600
IOCTL_MOUNTMGR_VOLUME_MOUNT_POINT_DELETED = 7192604
IOCTL_VOLUME_ALLOCATE_BC_STREAM = 5685312
IOCTL_VOLUME_FREE_BC_STREAM = 5685316
IOCTL_VOLUME_GET_BC_PROPERTIES = 5652540
IOCTL_VOLUME_GET_GPT_ATTRIBUTES = 5636152
IOCTL_VOLUME_GET_VOLUME_DISK_EXTENTS = 5636096
IOCTL_VOLUME_IS_CLUSTERED = 5636144
IOCTL_VOLUME_IS_DYNAMIC = 5636168
IOCTL_VOLUME_IS_IO_CAPABLE = 5636116
IOCTL_VOLUME_IS_OFFLINE = 5636112
IOCTL_VOLUME_IS_PARTITION = 5636136
IOCTL_VOLUME_LOGICAL_TO_PHYSICAL = 5636128
IOCTL_VOLUME_OFFLINE = 5685260
IOCTL_VOLUME_ONLINE = 5685256
IOCTL_VOLUME_PHYSICAL_TO_LOGICAL = 5636132
IOCTL_VOLUME_PREPARE_FOR_CRITICAL_IO = 5685324
IOCTL_VOLUME_PREPARE_FOR_SHRINK = 5685340
IOCTL_VOLUME_QUERY_ALLOCATION_HINT = 5652562
IOCTL_VOLUME_QUERY_FAILOVER_SET = 5636120
IOCTL_VOLUME_QUERY_MINIMUM_SHRINK_SIZE = 5652568
IOCTL_VOLUME_QUERY_VOLUME_NUMBER = 5636124
IOCTL_VOLUME_READ_PLEX = 5652526
IOCTL_VOLUME_SET_GPT_ATTRIBUTES = 5636148
IOCTL_VOLUME_SUPPORTS_ONLINE_OFFLINE = 5636100
IOCTL_VOLUME_UPDATE_PROPERTIES = 5636180
FSCTL_EXTEND_VOLUME = 590064
