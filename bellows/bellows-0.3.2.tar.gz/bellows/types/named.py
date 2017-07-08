import enum

from . import basic


class NcpResetCode(basic.uint8_t, enum.Enum):
    # Reset and Error Codes for NCP
    RESET_UNKNOWN_REASON = 0x00
    RESET_EXTERNAL = 0x01
    RESET_POWER_ON = 0x02
    RESET_WATCHDOG = 0x03
    RESET_ASSERT = 0x06
    RESET_BOOTLOADER = 0x09
    RESET_SOFTWARE = 0x0B
    ERROR_EXCEEDED_MAXIMUM_ACK_TIMEOUT_COUNT = 0x51
    ERROR_UNKNOWN_EM3XX_ERROR = 0x80


class EmberRf4ceTxOption(basic.uint8_t):
    # RF4CE transmission options.
    pass


class EmberRf4ceNodeCapabilities(basic.uint8_t):
    # The RF4CE node capabilities.
    pass


class EmberRf4ceApplicationCapabilities(basic.uint8_t):
    # The RF4CE application capabilities.
    pass


class EmberNodeId(basic.uint16_t):
    # 16-bit ZigBee network address.
    pass


class EmberPanId(basic.uint16_t):
    # 802.15.4 PAN ID.
    pass


class EmberMulticastId(basic.uint16_t):
    # 16-bit ZigBee multicast group identifier.
    pass


class EmberEUI64(basic.fixed_list(8, basic.uint8_t)):
    # EUI 64-bit ID (an IEEE address).
    @classmethod
    def deserialize(cls, data):
        r, data = super().deserialize(data)
        return cls(r[::-1]), data

    def serialize(self):
        assert self._length == len(self)
        return b''.join([i.serialize() for i in self[::-1]])

    def __repr__(self):
        return ':'.join('%02x' % i for i in self)

    def __hash__(self):
        return hash(repr(self))


class EmberLibraryStatus(basic.uint8_t):
    # The presence and status of the Ember library.
    pass


class SecureEzspSecurityType(basic.uint32_t):
    # Security type of the Secure EZSP Protocol.
    pass


class SecureEzspSecurityLevel(basic.uint8_t):
    # Security level of the Secure EZSP Protocol.
    pass


class EmberGpSecurityLevel(basic.uint8_t):
    # The security level of the GPD.
    pass


class EmberGpKeyType(basic.uint8_t):
    # The type of security key to use for the GPD.
    pass


class SecureEzspRandomNumber(basic.uint64_t):
    # Randomly generated 64-bit number.
    # Both NCP and Host contribute this number to create the Session ID,
    # which is used in the nonce.
    pass


class SecureEzspSessionId(basic.uint64_t):
    # Generated 64-bit Session ID, using random numbers from Host and NCP.
    # It is generated at each reboot (during negotiation phase).
    # Having both sides contribute to the value prevents one side from
    # choosing a number that might have been previously
    # used (either because of a bug or by malicious intent).
    pass


class Bool(basic.uint8_t, enum.Enum):
    # Boolean type with values true and false.

    false = 0x00  # An alias for zero, used for clarity.
    true = 0x01  # An alias for one, used for clarity.


class EzspConfigId(basic.uint8_t, enum.Enum):
    # Identifies a configuration value.

    # The number of packet buffers available to the stack.  When set to the
    # special value 0xFF, the NCP will allocate all remaining configuration RAM
    # towards packet buffers, such that the resulting count will be the largest
    # whole number of packet buffers that can fit into the available memory.
    CONFIG_PACKET_BUFFER_COUNT = 0x01
    # The maximum number of router neighbors the stack can keep track of. A
    # neighbor is a node within radio range.
    CONFIG_NEIGHBOR_TABLE_SIZE = 0x02
    # The maximum number of APS retried messages the stack can be transmitting
    # at any time.
    CONFIG_APS_UNICAST_MESSAGE_COUNT = 0x03
    # The maximum number of non-volatile bindings supported by the stack.
    CONFIG_BINDING_TABLE_SIZE = 0x04
    # The maximum number of EUI64 to network address associations that the
    # stack can maintain for the application. (Note, the total number of such
    # address associations maintained by the NCP is the sum of the value of
    # this setting and the value of ::CONFIG_TRUST_CENTER_ADDRESS_CACHE_SIZE).
    CONFIG_ADDRESS_TABLE_SIZE = 0x05
    # The maximum number of multicast groups that the device may be a member
    # of.
    CONFIG_MULTICAST_TABLE_SIZE = 0x06
    # The maximum number of destinations to which a node can route messages.
    # This includes both messages originating at this node and those relayed
    # for others.
    CONFIG_ROUTE_TABLE_SIZE = 0x07
    # The number of simultaneous route discoveries that a node will support.
    CONFIG_DISCOVERY_TABLE_SIZE = 0x08
    # The size of the alarm broadcast buffer.
    CONFIG_BROADCAST_ALARM_DATA_SIZE = 0x09
    # The size of the unicast alarm buffers allocated for end device children.
    CONFIG_UNICAST_ALARM_DATA_SIZE = 0x0A
    # Specifies the stack profile.
    CONFIG_STACK_PROFILE = 0x0C
    # The security level used for security at the MAC and network layers. The
    # supported values are 0 (no security) and 5 (payload is encrypted and a
    # four-byte MIC is used for authentication).
    CONFIG_SECURITY_LEVEL = 0x0D
    # The maximum number of hops for a message.
    CONFIG_MAX_HOPS = 0x10
    # The maximum number of end device children that a router will support.
    CONFIG_MAX_END_DEVICE_CHILDREN = 0x11
    # The maximum amount of time that the MAC will hold a message for indirect
    # transmission to a child.
    CONFIG_INDIRECT_TRANSMISSION_TIMEOUT = 0x12
    # The maximum amount of time that an end device child can wait between
    # polls. If no poll is heard within this timeout, then the parent removes
    # the end device from its tables.
    CONFIG_END_DEVICE_POLL_TIMEOUT = 0x13
    # The maximum amount of time that a mobile node can wait between polls. If
    # no poll is heard within this timeout, then the parent removes the mobile
    # node from its tables.
    CONFIG_MOBILE_NODE_POLL_TIMEOUT = 0x14
    # The number of child table entries reserved for use only by mobile nodes.
    CONFIG_RESERVED_MOBILE_CHILD_ENTRIES = 0x15
    # Enables boost power mode and/or the alternate transmitter output.
    CONFIG_TX_POWER_MODE = 0x17
    # 0: Allow this node to relay messages. 1: Prevent this node from relaying
    # messages.
    CONFIG_DISABLE_RELAY = 0x18
    # The maximum number of EUI64 to network address associations that the
    # Trust Center can maintain.  These address cache entries are reserved for
    # and reused by the Trust Center when processing device join/rejoin
    # authentications. This cache size limits the number of overlapping joins
    # the Trust Center can process within a narrow time window (e.g. two
    # seconds), and thus should be set to the maximum number of near
    # simultaneous joins the Trust Center is expected to accommodate. (Note,
    # the total number of such address associations maintained by the NCP is
    # the sum of the value of this setting and the value of
    # ::CONFIG_ADDRESS_TABLE_SIZE.)
    CONFIG_TRUST_CENTER_ADDRESS_CACHE_SIZE = 0x19
    # The size of the source route table.
    CONFIG_SOURCE_ROUTE_TABLE_SIZE = 0x1A
    # The units used for timing out end devices on their parents.
    CONFIG_END_DEVICE_POLL_TIMEOUT_SHIFT = 0x1B
    # The number of blocks of a fragmented message that can be sent in a single
    # window.
    CONFIG_FRAGMENT_WINDOW_SIZE = 0x1C
    # The time the stack will wait (in milliseconds) between sending blocks of
    # a fragmented message.
    CONFIG_FRAGMENT_DELAY_MS = 0x1D
    # The size of the Key Table used for storing individual link keys (if the
    # device is a Trust Center) or Application Link Keys (if the device is a
    # normal node).
    CONFIG_KEY_TABLE_SIZE = 0x1E
    # The APS ACK timeout value. The stack waits this amount of time between
    # resends of APS retried messages.
    CONFIG_APS_ACK_TIMEOUT = 0x1F
    # The duration of an active scan, in the units used by the 15.4 scan
    # parameter (((1 << duration) + 1) * 15ms). This also controls the jitter
    # used when responding to a beacon request.
    CONFIG_ACTIVE_SCAN_DURATION = 0x20
    # The time the coordinator will wait (in seconds) for a second end device
    # bind request to arrive.
    CONFIG_END_DEVICE_BIND_TIMEOUT = 0x21
    # The number of PAN id conflict reports that must be received by the
    # network manager within one minute to trigger a PAN id change.
    CONFIG_PAN_ID_CONFLICT_REPORT_THRESHOLD = 0x22
    # The timeout value in minutes for how long the Trust Center or a normal
    # node waits for the ZigBee Request Key to complete. On the Trust Center
    # this controls whether or not the device buffers the request, waiting for
    # a matching pair of ZigBee Request Key. If the value is non-zero, the
    # Trust Center buffers and waits for that amount of time. If the value is
    # zero, the Trust Center does not buffer the request and immediately
    # responds to the request.  Zero is the most compliant behavior.
    CONFIG_REQUEST_KEY_TIMEOUT = 0x24
    # This value indicates the size of the runtime modifiable certificate
    # table. Normally certificates are stored in MFG tokens but this table can
    # be used to field upgrade devices with new Smart Energy certificates.
    # This value cannot be set, it can only be queried.
    CONFIG_CERTIFICATE_TABLE_SIZE = 0x29
    # This is a bitmask that controls which incoming ZDO request messages are
    # passed to the application. The bits are defined in the
    # EmberZdoConfigurationFlags enumeration. To see if the application is
    # required to send a ZDO response in reply to an incoming message, the
    # application must check the APS options bitfield within the
    # incomingMessageHandler callback to see if the
    # APS_OPTION_ZDO_RESPONSE_REQUIRED flag is set.
    CONFIG_APPLICATION_ZDO_FLAGS = 0x2A
    # The maximum number of broadcasts during a single broadcast timeout
    # period.
    CONFIG_BROADCAST_TABLE_SIZE = 0x2B
    # The size of the MAC filter list table.
    CONFIG_MAC_FILTER_TABLE_SIZE = 0x2C
    # The number of supported networks.
    CONFIG_SUPPORTED_NETWORKS = 0x2D
    # Whether multicasts are sent to the RxOnWhenIdle=true address (0xFFFD) or
    # the sleepy broadcast address (0xFFFF). The RxOnWhenIdle=true address is
    # the ZigBee compliant destination for multicasts.
    CONFIG_SEND_MULTICASTS_TO_SLEEPY_ADDRESS = 0x2E
    # ZLL group address initial configuration.
    CONFIG_ZLL_GROUP_ADDRESSES = 0x2F
    # ZLL rssi threshold initial configuration.
    CONFIG_ZLL_RSSI_THRESHOLD = 0x30
    # The maximum number of pairings supported by the stack. Controllers
    # must support at least one pairing table entry while targets must
    # support at least five.
    CONFIG_RF4CE_PAIRING_TABLE_SIZE = 0x31
    # The maximum number of outgoing RF4CE packets supported by the stack.
    CONFIG_RF4CE_PENDING_OUTGOING_PACKET_TABLE_SIZE = 0x32
    # Toggles the mtorr flow control in the stack.
    CONFIG_MTORR_FLOW_CONTROL = 0x33
    # Setting the retry queue size.
    CONFIG_RETRY_QUEUE_SIZE = 0x34
    # Setting the new broadcast entry threshold.
    CONFIG_NEW_BROADCAST_ENTRY_THRESHOLD = 0x35
    # The length of time, in seconds, that a trust center will store a
    # transient link key that a device can use to join its network. A transient
    # key is added with a call to emberAddTransientLinkKey. After the transient
    # key is added, it will be removed once this amount of time has passed. A
    # joining device will not be able to use that key to join until it is added
    # again on the trust center. The default value is 300 seconds, i.e., 5
    # minutes.
    CONFIG_TRANSIENT_KEY_TIMEOUT_S = 0x36


class EzspValueId(basic.uint8_t, enum.Enum):
    # Identifies a value.

    # The contents of the node data stack token.
    VALUE_TOKEN_STACK_NODE_DATA = 0x00
    # The types of MAC passthrough messages that the host wishes to receive.
    VALUE_MAC_PASSTHROUGH_FLAGS = 0x01
    # The source address used to filter legacy EmberNet messages when the
    # MAC_PASSTHROUGH_EMBERNET_SOURCE flag is set in
    # VALUE_MAC_PASSTHROUGH_FLAGS.
    VALUE_EMBERNET_PASSTHROUGH_SOURCE_ADDRESS = 0x02
    # The number of available message buffers.
    VALUE_FREE_BUFFERS = 0x03
    # Selects sending synchronous callbacks in ezsp-uart.
    VALUE_UART_SYNCH_CALLBACKS = 0x04
    # The maximum incoming transfer size for the local node.
    VALUE_MAXIMUM_INCOMING_TRANSFER_SIZE = 0x05
    # The maximum outgoing transfer size for the local node.
    VALUE_MAXIMUM_OUTGOING_TRANSFER_SIZE = 0x06
    # A boolean indicating whether stack tokens are written to persistent
    # storage as they change.
    VALUE_STACK_TOKEN_WRITING = 0x07
    # A read-only value indicating whether the stack is currently performing a
    # rejoin.
    VALUE_STACK_IS_PERFORMING_REJOIN = 0x08
    # A list of EmberMacFilterMatchData values.
    VALUE_MAC_FILTER_LIST = 0x09
    # The Ember Extended Security Bitmask.
    VALUE_EXTENDED_SECURITY_BITMASK = 0x0A
    # The node short ID.
    VALUE_NODE_SHORT_ID = 0x0B
    # The descriptor capability of the local node.
    VALUE_DESCRIPTOR_CAPABILITY = 0x0C
    # The stack device request sequence number of the local node.
    VALUE_STACK_DEVICE_REQUEST_SEQUENCE_NUMBER = 0x0D
    # Enable or disable radio hold-off.
    VALUE_RADIO_HOLD_OFF = 0x0E
    # The flags field associated with the endpoint data.
    VALUE_ENDPOINT_FLAGS = 0x0F
    # Enable/disable the Mfg security config key settings.
    VALUE_MFG_SECURITY_CONFIG = 0x10
    # Retrieves the version information from the stack on the NCP.
    VALUE_VERSION_INFO = 0x11
    # This will get/set the rejoin reason noted by the host for a subsequent
    # call to emberFindAndRejoinNetwork(). After a call to
    # emberFindAndRejoinNetwork() the host's rejoin reason will be set to
    # REJOIN_REASON_NONE. The NCP will store the rejoin reason used by the
    # call to emberFindAndRejoinNetwork()
    VALUE_NEXT_HOST_REJOIN_REASON = 0x12
    # This is the reason that the last rejoin took place. This value may only
    # be retrieved, not set. The rejoin may have been initiated by the stack
    # (NCP) or the application (host). If a host initiated a rejoin the reason
    # will be set by default to REJOIN_DUE_TO_APP_EVENT_1. If the application
    # wishes to denote its own rejoin reasons it can do so by calling
    # ezspSetValue(VALUE_HOST_REJOIN_REASON, REJOIN_DUE_TO_APP_EVENT_X). X is a
    # number corresponding to one of the app events defined. If the NCP
    # initiated a rejoin it will record this value internally for retrieval by
    # ezspGetValue(VALUE_REAL_REJOIN_REASON).
    VALUE_LAST_REJOIN_REASON = 0x13
    # The next ZigBee sequence number.
    VALUE_NEXT_ZIGBEE_SEQUENCE_NUMBER = 0x14
    # CCA energy detect threshold for radio.
    VALUE_CCA_THRESHOLD = 0x15
    # The threshold value for a counter
    VALUE_SET_COUNTER_THRESHOLD = 0x17
    # Resets all counters thresholds to 0xFF
    VALUE_RESET_COUNTER_THRESHOLDS = 0x18
    # Clears all the counters
    VALUE_CLEAR_COUNTERS = 0x19
    # The device RF4CE base channel
    VALUE_RF4CE_BASE_CHANNEL = 0x1A
    # The RF4CE device types supported by the node
    VALUE_RF4CE_SUPPORTED_DEVICE_TYPES_LIST = 0x1B
    # The RF4CE profiles supported by the node
    VALUE_RF4CE_SUPPORTED_PROFILES_LIST = 0x1C
    # Setting this byte enables R21 behavior on the NCP.
    VALUE_ENABLE_R21_BEHAVIOR = 0x29
    # Configure the antenna mode(0-primary,1-secondary,2- toggle on tx ack
    # fail).
    VALUE_ANTENNA_MODE = 0x30
    # The GDP binding recipient parameters
    VALUE_RF4CE_GDP_BINDING_RECIPIENT_PARAMETERS = 0x1D
    # The GDP binding push button stimulus received pending flag
    VALUE_RF4CE_GDP_PUSH_BUTTON_STIMULUS_RECEIVED_PENDING_FLAG = 0x1E
    # The GDP originator proxy flag in the advanced binding options
    VALUE_RF4CE_GDP_BINDING_PROXY_FLAG = 0x1F
    # The GDP application specific user s join unti_VALUE_RF4CE_MSO_USER_STRING
    # 0x21 The MSO user string
    VALUE_RF4CE_GDP_APPLICATION_SPECIFIC_USER_STRING = 0x20
    # The MSO user string
    VALUE_RF4CE_MSO_USER_STRING = 0x21
    # The MSO binding recipient parameters
    VALUE_RF4CE_MSO_BINDING_RECIPIENT_PARAMETERS = 0x22
    # The NWK layer security frame counter value
    VALUE_NWK_FRAME_COUNTER = 0x23
    # The APS layer security frame counter value
    VALUE_APS_FRAME_COUNTER = 0x24
    # Sets the device type to use on the next rejoin using device type
    VALUE_RETRY_DEVICE_TYPE = 0x25
    # The device RF4CE base channel
    VALUE_RF4CE_BASE_CHANNEL2 = 0x26
    # The RF4CE device types supported by the node
    VALUE_RF4CE_SUPPORTED_DEVICE_TYPES_LIST2 = 0x27
    # The RF4CE profiles supported by the node
    VALUE_RF4CE_SUPPORTED_PROFILES_LIST2 = 0x28
    # Enable or disable packet traffic arbitration.
    VALUE_ENABLE_PTA = 0x31
    # Set packet traffic arbitration configuration options.
    VALUE_PTA_OPTIONS = 0x32
    # Configure manufacturing library options(0-non-CSMA transmits,1-CSMA transmits).
    VALUE_MFGLIB_OPTIONS = 0x33


class EzspExtendedValueId(basic.uint8_t, enum.Enum):
    # Identifies a value based on specified characteristics. Each set of
    # characteristics is unique to that value and is specified during the call
    # to get the extended value.

    # The flags field associated with the specified endpoint.
    EXTENDED_VALUE_ENDPOINT_FLAGS = 0x00
    # This is the reason for the node to leave the network as well as the
    # device that told it to leave. The leave reason is the 1st byte of the
    # value while the node ID is the 2nd and 3rd byte. If the leave was caused
    # due to an API call rather than an over the air message, the node ID will
    # be UNKNOWN_NODE_ID (0xFFFD).
    EXTENDED_VALUE_LAST_LEAVE_REASON = 0x01
    # This number of bytes of overhead required in the network frame for source
    # routing to a particular destination.
    EXTENDED_VALUE_GET_SOURCE_ROUTE_OVERHEAD = 0x02


class EzspEndpointFlags(basic.uint16_t, enum.Enum):
    # Flags associated with the endpoint data configured on the NCP.

    # Indicates that the endpoint is disabled and NOT discoverable via ZDO.
    ENDPOINT_DISABLED = 0x00
    # Indicates that the endpoint is enabled and discoverable via ZDO.
    ENDPOINT_ENABLED = 0x01


class EmberConfigTxPowerMode(basic.uint16_t, enum.Enum):
    # Values for CONFIG_TX_POWER_MODE.

    # Normal power mode and bi-directional RF transmitter output.
    TX_POWER_MODE_DEFAULT = 0x00
    # Enable boost power mode. This is a high performance radio mode which
    # offers increased receive sensitivity and transmit power at the cost of an
    # increase in power consumption.
    TX_POWER_MODE_BOOST = 0x01
    # Enable the alternate transmitter output. This allows for simplified
    # connection to an external power amplifier via the RF_TX_ALT_P and
    # RF_TX_ALT_N pins.  TX_POWER_MODE_BOOST_AND_ALTERNATE 0x03 Enable both
    # boost mode and the alternate transmitter output.
    TX_POWER_MODE_ALTERNATE = 0x02


class EzspPolicyId(basic.uint8_t, enum.Enum):
    # Identifies a policy.

    # Controls trust center behavior.
    TRUST_CENTER_POLICY = 0x00
    # Controls how external binding modification requests are handled.
    BINDING_MODIFICATION_POLICY = 0x01
    # Controls whether the Host supplies unicast replies.
    UNICAST_REPLIES_POLICY = 0x02
    # Controls whether pollHandler callbacks are generated.
    POLL_HANDLER_POLICY = 0x03
    # Controls whether the message contents are included in the
    # messageSentHandler callback.
    MESSAGE_CONTENTS_IN_CALLBACK_POLICY = 0x04
    # Controls whether the Trust Center will respond to Trust Center link key
    # requests.
    TC_KEY_REQUEST_POLICY = 0x05
    # Controls whether the Trust Center will respond to application link key
    # requests.
    APP_KEY_REQUEST_POLICY = 0x06
    # Controls whether ZigBee packets that appear invalid are automatically
    # dropped by the stack. A counter will be incremented when this occurs.
    PACKET_VALIDATE_LIBRARY_POLICY = 0x07
    # Controls whether the stack will process ZLL messages.
    ZLL_POLICY = 0x08


class EzspDecisionId(basic.uint8_t, enum.Enum):
    # Identifies a policy decision.

    # Send the network key in the clear to all joining and rejoining devices.
    ALLOW_JOINS = 0x00
    # Send the network key in the clear to all joining devices.  Rejoining
    # devices are sent the network key encrypted with their trust center link
    # key. The trust center and any rejoining device are assumed to share a
    # link key, either preconfigured or obtained under a previous policy.
    ALLOW_JOINS_REJOINS_HAVE_LINK_KEY = 0x04
    # Send the network key encrypted with the joining or rejoining device's
    # trust center link key. The trust center and any joining or rejoining
    # device are assumed to share a link key, either preconfigured or obtained
    # under a previous policy. This is the default value for the
    # TRUST_CENTER_POLICY.
    ALLOW_PRECONFIGURED_KEY_JOINS = 0x01
    # Send the network key encrypted with the rejoining device's trust center
    # link key. The trust center and any rejoining device are assumed to share
    # a link key, either preconfigured or obtained under a previous policy. No
    # new devices are allowed to join.
    ALLOW_REJOINS_ONLY = 0x02
    # Reject all unsecured join and rejoin attempts.
    DISALLOW_ALL_JOINS_AND_REJOINS = 0x03
    # Take no action on trust center rejoin attempts.
    IGNORE_TRUST_CENTER_REJOINS = 0x05
    # BINDING_MODIFICATION_POLICY default decision. Do not allow the local
    # binding table to be changed by remote nodes.
    DISALLOW_BINDING_MODIFICATION = 0x10
    # BINDING_MODIFICATION_POLICY decision.  Allow remote nodes to change
    # the local binding table.
    ALLOW_BINDING_MODIFICATION = 0x11
    # BINDING_MODIFICATION_POLICY decision.  Allows remote nodes to set local
    # binding entries only if the entries correspond to endpoints defined on
    # the device, and for output clusters bound to those endpoints.
    CHECK_BINDING_MODIFICATIONS_ARE_VALID_ENDPOINT_CLUSTERS = 0x12
    # UNICAST_REPLIES_POLICY default decision.  The NCP will automatically send
    # an empty reply (containing no payload) for every unicast received.
    HOST_WILL_NOT_SUPPLY_REPLY = 0x20
    # UNICAST_REPLIES_POLICY decision. The NCP will only send a reply if it
    # receives a sendReply command from the Host.
    HOST_WILL_SUPPLY_REPLY = 0x21
    # POLL_HANDLER_POLICY default decision. Do not inform the Host when a child
    # polls.
    POLL_HANDLER_IGNORE = 0x30
    # POLL_HANDLER_POLICY decision. Generate a pollHandler callback when a
    # child polls.
    POLL_HANDLER_CALLBACK = 0x31
    # MESSAGE_CONTENTS_IN_CALLBACK_POLICY default decision. Include only the
    # message tag in the messageSentHandler callback.
    MESSAGE_TAG_ONLY_IN_CALLBACK = 0x40
    # MESSAGE_CONTENTS_IN_CALLBACK_POLICY decision. Include both the message
    # tag and the message contents in the messageSentHandler callback.
    MESSAGE_TAG_AND_CONTENTS_IN_CALLBACK = 0x41
    # TC_KEY_REQUEST_POLICY decision. When the Trust Center receives a request
    # for a Trust Center link key, it will be ignored.
    DENY_TC_KEY_REQUESTS = 0x50
    # TC_KEY_REQUEST_POLICY decision. When the Trust Center receives a request
    # for a Trust Center link key, it will reply to it with the corresponding
    # key.
    ALLOW_TC_KEY_REQUESTS = 0x51
    # TC_KEY_REQUEST_POLICY decision. When the Trust Center receives a request
    # for a Trust Center link key, it will generate a key to send to the
    # joiner.
    GENERATE_NEW_TC_LINK_KEY = 0x52
    # APP_KEY_REQUEST_POLICY decision. When the Trust Center receives a request
    # for an application link key, it will be ignored.
    DENY_APP_KEY_REQUESTS = 0x60
    # APP_KEY_REQUEST_POLICY decision. When the Trust Center receives a request
    # for an application link key, it will randomly generate a key and send it
    # to both partners.
    ALLOW_APP_KEY_REQUESTS = 0x61
    # Indicates that packet validate library checks are enabled on the NCP.
    PACKET_VALIDATE_LIBRARY_CHECKS_ENABLED = 0x62
    # Indicates that packet validate library checks are NOT enabled on the NCP.
    PACKET_VALIDATE_LIBRARY_CHECKS_DISABLED = 0x63


class EzspMfgTokenId(basic.uint8_t, enum.Enum):
    # Manufacturing token IDs used by ezspGetMfgToken().

    # Custom version (2 bytes).
    MFG_CUSTOM_VERSION = 0x00
    # Manufacturing string (16 bytes).
    MFG_STRING = 0x01
    # Board name (16 bytes).
    MFG_BOARD_NAME = 0x02
    # Manufacturing ID (2 bytes).
    MFG_MANUF_ID = 0x03
    # Radio configuration (2 bytes).
    MFG_PHY_CONFIG = 0x04
    # Bootload AES key (16 bytes).
    MFG_BOOTLOAD_AES_KEY = 0x05
    # ASH configuration (40 bytes).
    MFG_ASH_CONFIG = 0x06
    # EZSP storage (8 bytes).
    MFG_STORAGE = 0x07
    # Radio calibration data (64 bytes). 4 bytes are stored for each of the 16
    # channels. This token is not stored in the Flash Information Area. It is
    # updated by the stack each time a calibration is performed.
    STACK_CAL_DATA = 0x08
    # Certificate Based Key Exchange (CBKE) data (92 bytes).
    MFG_CBKE_DATA = 0x09
    # Installation code (20 bytes).
    MFG_INSTALLATION_CODE = 0x0A
    # Radio channel filter calibration data (1 byte). This token is not stored
    # in the Flash Information Area. It is updated by the stack each time a
    # calibration is performed.
    STACK_CAL_FILTER = 0x0B
    # Custom EUI64 MAC address (8 bytes).
    MFG_CUSTOM_EUI_64 = 0x0C
    # CTUNE value (2 byte).
    MFG_CTUNE = 0x0D


class EzspStatus(basic.uint8_t, enum.Enum):
    # Status values used by EZSP.

    # Success.
    SUCCESS = 0x00
    # Fatal error.
    SPI_ERR_FATAL = 0x10
    # The Response frame of the current transaction indicates the NCP has
    # reset.
    SPI_ERR_NCP_RESET = 0x11
    # The NCP is reporting that the Command frame of the current transaction is
    # oversized (the length byte is too large).
    SPI_ERR_OVERSIZED_FRAME = 0x12
    # The Response frame of the current transaction indicates the previous
    # transaction was aborted (nSSEL deasserted too soon).
    SPI_ERR_ABORTED_TRANSACTION = 0x13
    # The Response frame of the current transaction indicates the frame
    # terminator is missing from the Command frame.
    SPI_ERR_MISSING_FRAME_TERMINATOR = 0x14
    # The NCP has not provided a Response within the time limit defined by
    # WAIT_SECTION_TIMEOUT.
    SPI_ERR_WAIT_SECTION_TIMEOUT = 0x15
    # The Response frame from the NCP is missing the frame terminator.
    SPI_ERR_NO_FRAME_TERMINATOR = 0x16
    # The Host attempted to send an oversized Command (the length byte is too
    # large) and the AVR's spi-protocol.c blocked the transmission.
    SPI_ERR_COMMAND_OVERSIZED = 0x17
    # The NCP attempted to send an oversized Response (the length byte is too
    # large) and the AVR's spi-protocol.c blocked the reception.
    SPI_ERR_RESPONSE_OVERSIZED = 0x18
    # The Host has sent the Command and is still waiting for the NCP to send a
    # Response.
    SPI_WAITING_FOR_RESPONSE = 0x19
    # The NCP has not asserted nHOST_INT within the time limit defined by
    # WAKE_HANDSHAKE_TIMEOUT.
    SPI_ERR_HANDSHAKE_TIMEOUT = 0x1A
    # The NCP has not asserted nHOST_INT after an NCP reset within the time
    # limit defined by STARTUP_TIMEOUT.
    SPI_ERR_STARTUP_TIMEOUT = 0x1B
    # The Host attempted to verify the SPI Protocol activity and version
    # number, and the verification failed.
    SPI_ERR_STARTUP_FAIL = 0x1C
    # The Host has sent a command with a SPI Byte that is unsupported by the
    # current mode the NCP is operating in.
    SPI_ERR_UNSUPPORTED_SPI_COMMAND = 0x1D
    # Operation not yet complete.
    ASH_IN_PROGRESS = 0x20
    # Fatal error detected by host.
    HOST_FATAL_ERROR = 0x21
    # Fatal error detected by NCP.
    ASH_NCP_FATAL_ERROR = 0x22
    # Tried to send DATA frame too long.
    DATA_FRAME_TOO_LONG = 0x23
    # Tried to send DATA frame too short.
    DATA_FRAME_TOO_SHORT = 0x24
    # No space for tx'ed DATA frame.
    NO_TX_SPACE = 0x25
    # No space for rec'd DATA frame.
    NO_RX_SPACE = 0x26
    # No receive data available.
    NO_RX_DATA = 0x27
    # Not in Connected state.
    NOT_CONNECTED = 0x28
    # The NCP received a command before the EZSP version had been set.
    ERROR_VERSION_NOT_SET = 0x30
    # The NCP received a command containing an unsupported frame ID.
    ERROR_INVALID_FRAME_ID = 0x31
    # The direction flag in the frame control field was incorrect.
    ERROR_WRONG_DIRECTION = 0x32
    # The truncated flag in the frame control field was set, indicating there
    # was not enough memory available to complete the response or that the
    # response would have exceeded the maximum EZSP frame length.
    ERROR_TRUNCATED = 0x33
    # The overflow flag in the frame control field was set, indicating one or
    # more callbacks occurred since the previous response and there was not
    # enough memory available to report them to the Host.
    ERROR_OVERFLOW = 0x34
    # Insufficient memory was available.
    ERROR_OUT_OF_MEMORY = 0x35
    # The value was out of bounds.
    ERROR_INVALID_VALUE = 0x36
    # The configuration id was not recognized.
    ERROR_INVALID_ID = 0x37
    # Configuration values can no longer be modified.
    ERROR_INVALID_CALL = 0x38
    # The NCP failed to respond to a command.
    ERROR_NO_RESPONSE = 0x39
    # The length of the command exceeded the maximum EZSP frame length.
    ERROR_COMMAND_TOO_LONG = 0x40
    # The UART receive queue was full causing a callback response to be
    # dropped.
    ERROR_QUEUE_FULL = 0x41
    # The command has been filtered out by NCP.
    ERROR_COMMAND_FILTERED = 0x42
    # EZSP Security Key is already set
    ERROR_SECURITY_KEY_ALREADY_SET = 0x43
    # EZSP Security Type is invalid
    ERROR_SECURITY_TYPE_INVALID = 0x44
    # EZSP Security Parameters are invalid
    ERROR_SECURITY_PARAMETERS_INVALID = 0x45
    # EZSP Security Parameters are already set
    ERROR_SECURITY_PARAMETERS_ALREADY_SET = 0x46
    # EZSP Security Key is not set
    ERROR_SECURITY_KEY_NOT_SET = 0x47
    # EZSP Security Parameters are not set
    ERROR_SECURITY_PARAMETERS_NOT_SET = 0x48
    # Received frame with unsupported control byte
    ERROR_UNSUPPORTED_CONTROL = 0x49
    # Received frame is unsecure, when security is established
    ERROR_UNSECURE_FRAME = 0x4A
    # Incompatible ASH version
    ASH_ERROR_VERSION = 0x50
    # Exceeded max ACK timeouts
    ASH_ERROR_TIMEOUTS = 0x51
    # Timed out waiting for RSTACK
    ASH_ERROR_RESET_FAIL = 0x52
    # Unexpected ncp reset
    ASH_ERROR_NCP_RESET = 0x53
    # Serial port initialization failed
    ERROR_SERIAL_INIT = 0x54
    # Invalid ncp processor type
    ASH_ERROR_NCP_TYPE = 0x55
    # Invalid ncp reset method
    ASH_ERROR_RESET_METHOD = 0x56
    # XON/XOFF not supported by host driver
    ASH_ERROR_XON_XOFF = 0x57
    # ASH protocol started
    ASH_STARTED = 0x70
    # ASH protocol connected
    ASH_CONNECTED = 0x71
    # ASH protocol disconnected
    ASH_DISCONNECTED = 0x72
    # Timer expired waiting for ack
    ASH_ACK_TIMEOUT = 0x73
    # Frame in progress cancelled
    ASH_CANCELLED = 0x74
    # Received frame out of sequence
    ASH_OUT_OF_SEQUENCE = 0x75
    # Received frame with CRC error
    ASH_BAD_CRC = 0x76
    # Received frame with comm error
    ASH_COMM_ERROR = 0x77
    # Received frame with bad ackNum
    ASH_BAD_ACKNUM = 0x78
    # Received frame shorter than minimum
    ASH_TOO_SHORT = 0x79
    # Received frame longer than maximum
    ASH_TOO_LONG = 0x7A
    # Received frame with illegal control byte
    ASH_BAD_CONTROL = 0x7B
    # Received frame with illegal length for its type
    ASH_BAD_LENGTH = 0x7C
    # Received ASH Ack
    ASH_ACK_RECEIVED = 0x7D
    # Sent ASH Ack
    ASH_ACK_SENT = 0x7E
    # No reset or error
    NO_ERROR = 0xFF


class EmberStatus(basic.uint8_t, enum.Enum):
    # Return type for stack functions.

    # The generic 'no error' message.
    SUCCESS = 0x00
    # The generic 'fatal error' message.
    ERR_FATAL = 0x01
    # An invalid value was passed as an argument to a function
    BAD_ARGUMENT = 0x02
    # The manufacturing and stack token format in nonvolatile memory is
    # different than what the stack expects (returned at initialization).
    EEPROM_MFG_STACK_VERSION_MISMATCH = 0x04
    # The static memory definitions in ember-staticmemory.h are incompatible
    # with this stack version.
    INCOMPATIBLE_STATIC_MEMORY_DEFINITIONS = 0x05
    # The manufacturing token format in non-volatile memory is different than
    # what the stack expects (returned at initialization).
    EEPROM_MFG_VERSION_MISMATCH = 0x06
    # The stack token format in non-volatile memory is different than what the
    # stack expects (returned at initialization).
    EEPROM_STACK_VERSION_MISMATCH = 0x07
    # There are no more buffers.
    NO_BUFFERS = 0x18
    # Specified an invalid baud rate.
    SERIAL_INVALID_BAUD_RATE = 0x20
    # Specified an invalid serial port.
    SERIAL_INVALID_PORT = 0x21
    # Tried to send too much data.
    SERIAL_TX_OVERFLOW = 0x22
    # There was not enough space to store a received character and the
    # character was dropped.
    SERIAL_RX_OVERFLOW = 0x23
    # Detected a UART framing error.
    SERIAL_RX_FRAME_ERROR = 0x24
    # Detected a UART parity error.
    SERIAL_RX_PARITY_ERROR = 0x25
    # There is no received data to process.
    SERIAL_RX_EMPTY = 0x26
    # The receive interrupt was not handled in time, and a character was
    # dropped.
    SERIAL_RX_OVERRUN_ERROR = 0x27
    # The MAC transmit queue is full.
    MAC_TRANSMIT_QUEUE_FULL = 0x39
    # MAC header FCR error on receive.
    MAC_UNKNOWN_HEADER_TYPE = 0x3A
    # The MAC can't complete this task because it is scanning.
    MAC_SCANNING = 0x3D
    # No pending data exists for device doing a data poll.
    MAC_NO_DATA = 0x31
    # Attempt to scan when we are joined to a network.
    MAC_JOINED_NETWORK = 0x32
    # Scan duration must be 0 to 14 inclusive. Attempt was made to scan with an
    # incorrect duration value.
    MAC_BAD_SCAN_DURATION = 0x33
    # emberStartScan was called with an incorrect scan type.
    MAC_INCORRECT_SCAN_TYPE = 0x34
    # emberStartScan was called with an invalid channel mask.
    MAC_INVALID_CHANNEL_MASK = 0x35
    # Failed to scan current channel because we were unable to transmit the
    # relevant MAC command.
    MAC_COMMAND_TRANSMIT_FAILURE = 0x36
    # We expected to receive an ACK following the transmission, but the MAC
    # level ACK was never received.
    MAC_NO_ACK_RECEIVED = 0x40
    # Indirect data message timed out before polled.
    MAC_INDIRECT_TIMEOUT = 0x42
    # The Simulated EEPROM is telling the application that there is at least
    # one flash page to be erased.  The GREEN status means the current page has
    # not filled above the ERASE_CRITICAL_THRESHOLD.  The application should
    # call the function halSimEepromErasePage when it can to erase a page.
    SIM_EEPROM_ERASE_PAGE_GREEN = 0x43
    # The Simulated EEPROM is telling the application that there is at least
    # one flash page to be erased.  The RED status means the current page has
    # filled above the ERASE_CRITICAL_THRESHOLD. Due to the shrinking
    # availability of write space, there is a danger of data loss. The
    # application must call the function halSimEepromErasePage as soon as
    # possible to erase a page.
    SIM_EEPROM_ERASE_PAGE_RED = 0x44
    # The Simulated EEPROM has run out of room to write any new data and the
    # data trying to be set has been lost. This error code is the result of
    # ignoring the SIM_EEPROM_ERASE_PAGE_RED error code.  The application must
    # call the function halSimEepromErasePage to make room for any further
    # calls to set a token.
    SIM_EEPROM_FULL = 0x45
    # A fatal error has occurred while trying to write data to the Flash. The
    # target memory attempting to be programmed is already programmed. The
    # flash write routines were asked to flip a bit from a 0 to 1, which is
    # physically impossible and the write was therefore inhibited. The data in
    # the flash cannot be trusted after this error.
    ERR_FLASH_WRITE_INHIBITED = 0x46
    # A fatal error has occurred while trying to write data to the Flash and
    # the write verification has failed. The data in the flash cannot be
    # trusted after this error, and it is possible this error is the result of
    # exceeding the life cycles of the flash.
    ERR_FLASH_VERIFY_FAILED = 0x47
    # Attempt 1 to initialize the Simulated EEPROM has failed. This failure
    # means the information already stored in Flash (or a lack thereof), is
    # fatally incompatible with the token information compiled into the code
    # image being run.
    SIM_EEPROM_INIT_1_FAILED = 0x48
    # Attempt 2 to initialize the Simulated EEPROM has failed. This failure
    # means Attempt 1 failed, and the token system failed to properly reload
    # default tokens and reset the Simulated EEPROM.
    SIM_EEPROM_INIT_2_FAILED = 0x49
    # Attempt 3 to initialize the Simulated EEPROM has failed. This failure
    # means one or both of the tokens TOKEN_MFG_NVDATA_VERSION or
    # TOKEN_STACK_NVDATA_VERSION were incorrect and the token system failed to
    # properly reload default tokens and reset the Simulated EEPROM.
    SIM_EEPROM_INIT_3_FAILED = 0x4A
    # A fatal error has occurred while trying to write data to the flash,
    # possibly due to write protection or an invalid address. The data in the
    # flash cannot be trusted after this error, and it is possible this error
    # is the result of exceeding the life cycles of the flash.
    ERR_FLASH_PROG_FAIL = 0x4B
    # A fatal error has occurred while trying to erase flash, possibly due to
    # write protection. The data in the flash cannot be trusted after this
    # error, and it is possible this error is the result of exceeding the life
    # cycles of the flash.
    ERR_FLASH_ERASE_FAIL = 0x4C
    # The bootloader received an invalid message (failed attempt to go into
    # bootloader).
    ERR_BOOTLOADER_TRAP_TABLE_BAD = 0x58
    # Bootloader received an invalid message (failed attempt to go into
    # bootloader).
    ERR_BOOTLOADER_TRAP_UNKNOWN = 0x59
    # The bootloader cannot complete the bootload operation because either an
    # image was not found or the image exceeded memory bounds.
    ERR_BOOTLOADER_NO_IMAGE = 0x5A
    # The APS layer attempted to send or deliver a message, but it failed.
    DELIVERY_FAILED = 0x66
    # This binding index is out of range of the current binding table.
    BINDING_INDEX_OUT_OF_RANGE = 0x69
    # This address table index is out of range for the current address table.
    ADDRESS_TABLE_INDEX_OUT_OF_RANGE = 0x6A
    # An invalid binding table index was given to a function.
    INVALID_BINDING_INDEX = 0x6C
    # The API call is not allowed given the current state of the stack.
    INVALID_CALL = 0x70
    # The link cost to a node is not known.
    COST_NOT_KNOWN = 0x71
    # The maximum number of in-flight messages (i.e.
    # APS_UNICAST_MESSAGE_COUNT) has been reached.
    MAX_MESSAGE_LIMIT_REACHED = 0x72
    # The message to be transmitted is too big to fit into a single over-the-
    # air packet.
    MESSAGE_TOO_LONG = 0x74
    # The application is trying to delete or overwrite a binding that is in
    # use.
    BINDING_IS_ACTIVE = 0x75
    # The application is trying to overwrite an address table entry that is in
    # use.
    ADDRESS_TABLE_ENTRY_IS_ACTIVE = 0x76
    # Conversion is complete.
    ADC_CONVERSION_DONE = 0x80
    # Conversion cannot be done because a request is being processed.
    ADC_CONVERSION_BUSY = 0x81
    # Conversion is deferred until the current request has been processed.
    ADC_CONVERSION_DEFERRED = 0x82
    # No results are pending.
    ADC_NO_CONVERSION_PENDING = 0x84
    # Sleeping (for a duration) has been abnormally interrupted and exited
    # prematurely.
    SLEEP_INTERRUPTED = 0x85
    # The transmit hardware buffer underflowed.
    PHY_TX_UNDERFLOW = 0x88
    # The transmit hardware did not finish transmitting a packet.
    PHY_TX_INCOMPLETE = 0x89
    # An unsupported channel setting was specified.
    PHY_INVALID_CHANNEL = 0x8A
    # An unsupported power setting was specified.
    PHY_INVALID_POWER = 0x8B
    # The packet cannot be transmitted because the physical MAC layer is
    # currently transmitting a packet.  (This is used for the MAC backoff
    # algorithm.) PHY_TX_CCA_FAIL 0x8D The transmit attempt failed because all
    # CCA attempts indicated that the channel was busy
    PHY_TX_BUSY = 0x8C
    # The software installed on the hardware doesn't recognize the hardware
    # radio type.
    PHY_OSCILLATOR_CHECK_FAILED = 0x8E
    # The expected ACK was received after the last transmission.
    PHY_ACK_RECEIVED = 0x8F
    # The stack software has completed initialization and is ready to send and
    # receive packets over the air.
    NETWORK_UP = 0x90
    # The network is not operating.
    NETWORK_DOWN = 0x91
    # An attempt to join a network failed.
    JOIN_FAILED = 0x94
    # After moving, a mobile node's attempt to re-establish contact with the
    # network failed.
    MOVE_FAILED = 0x96
    # An attempt to join as a router failed due to a ZigBee versus ZigBee Pro
    # incompatibility. ZigBee devices joining ZigBee Pro networks (or vice
    # versa) must join as End Devices, not Routers.
    CANNOT_JOIN_AS_ROUTER = 0x98
    # The local node ID has changed. The application can obtain the new node ID
    # by calling emberGetNodeId().
    NODE_ID_CHANGED = 0x99
    # The local PAN ID has changed. The application can obtain the new PAN ID
    # by calling emberGetPanId().
    PAN_ID_CHANGED = 0x9A
    # An attempt to join or rejoin the network failed because no router beacons
    # could be heard by the joining node.
    NO_BEACONS = 0xAB
    # An attempt was made to join a Secured Network using a pre-configured key,
    # but the Trust Center sent back a Network Key in-the-clear when an
    # encrypted Network Key was required.
    RECEIVED_KEY_IN_THE_CLEAR = 0xAC
    # An attempt was made to join a Secured Network, but the device did not
    # receive a Network Key.
    NO_NETWORK_KEY_RECEIVED = 0xAD
    # After a device joined a Secured Network, a Link Key was requested but no
    # response was ever received.
    NO_LINK_KEY_RECEIVED = 0xAE
    # An attempt was made to join a Secured Network without a pre-configured
    # key, but the Trust Center sent encrypted data using a pre-configured key.
    PRECONFIGURED_KEY_REQUIRED = 0xAF
    # The node has not joined a network.
    NOT_JOINED = 0x93
    # The chosen security level (the value of SECURITY_LEVEL) is not supported
    # by the stack.
    INVALID_SECURITY_LEVEL = 0x95
    # A message cannot be sent because the network is currently overloaded.
    NETWORK_BUSY = 0xA1
    # The application tried to send a message using an endpoint that it has not
    # defined.
    INVALID_ENDPOINT = 0xA3
    # The application tried to use a binding that has been remotely modified
    # and the change has not yet been reported to the application.
    BINDING_HAS_CHANGED = 0xA4
    # An attempt to generate random bytes failed because of insufficient random
    # data from the radio.
    INSUFFICIENT_RANDOM_DATA = 0xA5
    # There was an error in trying to encrypt at the APS Level. This could
    # result from either an inability to determine the long address of the
    # recipient from the short address (no entry in the binding table) or there
    # is no link key entry in the table associated with the destination, or
    # there was a failure to load the correct key into the encryption core.
    # TRUST_CENTER_MASTER_KEY_NOT_SET 0xA7 There was an attempt to form a
    # network using commercial security without setting the Trust Center master
    # key first.
    APS_ENCRYPTION_ERROR = 0xA6
    # There was an attempt to form or join a network with security without
    # calling emberSetInitialSecurityState() first.
    SECURITY_STATE_NOT_SET = 0xA8
    # There was an attempt to set an entry in the key table using an invalid
    # long address. An entry cannot be set using either the local device's or
    # Trust Center's IEEE address. Or an entry already exists in the table with
    # the same IEEE address. An Address of all zeros or all F's are not valid
    # addresses in 802.15.4.
    KEY_TABLE_INVALID_ADDRESS = 0xB3
    # There was an attempt to set a security configuration that is not valid
    # given the other security settings.
    SECURITY_CONFIGURATION_INVALID = 0xB7
    # There was an attempt to broadcast a key switch too quickly after
    # broadcasting the next network key. The Trust Center must wait at least a
    # period equal to the broadcast timeout so that all routers have a chance
    # to receive the broadcast of the new network key.
    TOO_SOON_FOR_SWITCH_KEY = 0xB8
    # The message could not be sent because the link key corresponding to the
    # destination is not authorized for use in APS data messages. APS Commands
    # (sent by the stack) are allowed. To use it for encryption of APS data
    # messages it must be authorized using a key agreement protocol (such as
    # CBKE).
    KEY_NOT_AUTHORIZED = 0xBB
    # The security data provided was not valid, or an integrity check failed.
    SECURITY_DATA_INVALID = 0xBD
    # A ZigBee route error command frame was received indicating that a source
    # routed message from this node failed en route.
    SOURCE_ROUTE_FAILURE = 0xA9
    # A ZigBee route error command frame was received indicating that a message
    # sent to this node along a many-to-one route failed en route. The route
    # error frame was delivered by an ad-hoc search for a functioning route.
    MANY_TO_ONE_ROUTE_FAILURE = 0xAA
    # A critical and fatal error indicating that the version of the stack
    # trying to run does not match with the chip it is running on. The software
    # (stack) on the chip must be replaced with software that is compatible
    # with the chip.
    STACK_AND_HARDWARE_MISMATCH = 0xB0
    # An index was passed into the function that was larger than the valid
    # range.
    INDEX_OUT_OF_RANGE = 0xB1
    # There are no empty entries left in the table.
    TABLE_FULL = 0xB4
    # The requested table entry has been erased and contains no valid data.
    TABLE_ENTRY_ERASED = 0xB6
    # The requested function cannot be executed because the library that
    # contains the necessary functionality is not present.
    LIBRARY_NOT_PRESENT = 0xB5
    # The stack accepted the command and is currently processing the request.
    # The results will be returned via an appropriate handler.
    OPERATION_IN_PROGRESS = 0xBA
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_0 = 0xF0
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_1 = 0xF1
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_2 = 0xF2
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_3 = 0xF3
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_4 = 0xF4
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_5 = 0xF5
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_6 = 0xF6
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_7 = 0xF7
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_8 = 0xF8
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_9 = 0xF9
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_10 = 0xFA
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_11 = 0xFB
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_12 = 0xFC
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_13 = 0xFD
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_14 = 0xFE
    # This error is reserved for customer application use.  This will never be
    # returned from any portion of the network stack or HAL.
    APPLICATION_ERROR_15 = 0xFF


class EmberEventUnits(basic.uint8_t, enum.Enum):
    # Either marks an event as inactive or specifies the units for the event
    # execution time.

    # The event is not scheduled to run.
    EVENT_INACTIVE = 0x00
    # The execution time is in approximate milliseconds.
    EVENT_MS_TIME = 0x01
    # The execution time is in 'binary' quarter seconds (256 approximate
    # milliseconds each).
    EVENT_QS_TIME = 0x02
    # The execution time is in 'binary' minutes (65536 approximate milliseconds
    # each).
    EVENT_MINUTE_TIME = 0x03


class EmberNodeType(basic.uint8_t, enum.Enum):
    # The type of the node.

    # Device is not joined.
    UNKNOWN_DEVICE = 0x00
    # Will relay messages and can act as a parent to other nodes.
    COORDINATOR = 0x01
    # Will relay messages and can act as a parent to other nodes.
    ROUTER = 0x02
    # Communicates only with its parent and will not relay messages.
    END_DEVICE = 0x03
    # An end device whose radio can be turned off to save power. The
    # application must poll to receive messages.
    SLEEPY_END_DEVICE = 0x04
    # A sleepy end device that can move through the network.
    MOBILE_END_DEVICE = 0x05


class EmberNetworkStatus(basic.uint8_t, enum.Enum):
    # The possible join states for a node.

    # The node is not associated with a network in any way.
    NO_NETWORK = 0x00
    # The node is currently attempting to join a network.
    JOINING_NETWORK = 0x01
    # The node is joined to a network.
    JOINED_NETWORK = 0x02
    # The node is an end device joined to a network but its parent is not
    # responding.
    JOINED_NETWORK_NO_PARENT = 0x03
    # The node is in the process of leaving its current network.
    LEAVING_NETWORK = 0x04


class EmberIncomingMessageType(basic.uint8_t, enum.Enum):
    # Incoming message types.

    # Unicast.
    INCOMING_UNICAST = 0x00
    # Unicast reply.
    INCOMING_UNICAST_REPLY = 0x01
    # Multicast.
    INCOMING_MULTICAST = 0x02
    # Multicast sent by the local device.
    INCOMING_MULTICAST_LOOPBACK = 0x03
    # Broadcast.
    INCOMING_BROADCAST = 0x04
    # Broadcast sent by the local device.
    INCOMING_BROADCAST_LOOPBACK = 0x05
    # Many to one route request.
    INCOMING_MANY_TO_ONE_ROUTE_REQUEST = 0x06


class EmberOutgoingMessageType(basic.uint8_t, enum.Enum):
    # Outgoing message types.

    # Unicast sent directly to an EmberNodeId.
    OUTGOING_DIRECT = 0x00
    # Unicast sent using an entry in the address table.
    OUTGOING_VIA_ADDRESS_TABLE = 0x01
    # Unicast sent using an entry in the binding table.
    OUTGOING_VIA_BINDING = 0x02
    # Multicast message. This value is passed to emberMessageSentHandler()
    # only. It may not be passed to emberSendUnicast().
    OUTGOING_MULTICAST = 0x03
    # Aliased multicast message. This value is passed to emberMessageSentHandler() only.
    # It may not be passed to emberSendUnicast().
    OUTGOING_MULTICAST_WITH_ALIAS = 0x04
    # Aliased Broadcast message.  This value is passed to emberMessageSentHandler() only.
    # It may not be passed to emberSendUnicast().
    OUTGOING_BROADCAST_WITH_ALIAS = 0x05
    # Broadcast message. This value is passed to emberMessageSentHandler()
    # only. It may not be passed to emberSendUnicast().
    OUTGOING_BROADCAST = 0x06


class EmberMacPassthroughType(basic.uint8_t, enum.Enum):
    # MAC passthrough message type flags.

    # No MAC passthrough messages.
    MAC_PASSTHROUGH_NONE = 0x00
    # SE InterPAN messages.
    MAC_PASSTHROUGH_SE_INTERPAN = 0x01
    # Legacy EmberNet messages.
    MAC_PASSTHROUGH_EMBERNET = 0x02
    # Legacy EmberNet messages filtered by their source address.
    MAC_PASSTHROUGH_EMBERNET_SOURCE = 0x04
    MAC_PASSTHROUGH_APPLICATION = 0x08
    MAC_PASSTHROUGH_CUSTOM = 0x10
    MAC_PASSTHROUGH_INTERNAL = 0x80


class EmberBindingType(basic.uint8_t, enum.Enum):
    # Binding types.

    # A binding that is currently not in use.
    UNUSED_BINDING = 0x00
    # A unicast binding whose 64-bit identifier is the destination EUI64.
    UNICAST_BINDING = 0x01
    # A unicast binding whose 64-bit identifier is the aggregator EUI64.
    MANY_TO_ONE_BINDING = 0x02
    # A multicast binding whose 64-bit identifier is the group address. A
    # multicast binding can be used to send messages to the group and to
    # receive messages sent to the group.
    MULTICAST_BINDING = 0x03


class EmberApsOption(basic.uint16_t):
    # Options to use when sending a message.

    # No options.
    APS_OPTION_NONE = 0x0000
    # UNKNOWN: Discovered while receiving data
    APS_OPTION_UNKNOWN = 0x0008
    # Send the message using APS Encryption, using the Link Key shared with the
    # destination node to encrypt the data at the APS Level.
    APS_OPTION_ENCRYPTION = 0x0020
    # Resend the message using the APS retry mechanism.
    APS_OPTION_RETRY = 0x0040
    # Causes a route discovery to be initiated if no route to the destination
    # is known.
    APS_OPTION_ENABLE_ROUTE_DISCOVERY = 0x0100
    # Causes a route discovery to be initiated even if one is known.
    APS_OPTION_FORCE_ROUTE_DISCOVERY = 0x0200
    # Include the source EUI64 in the network frame.
    APS_OPTION_SOURCE_EUI64 = 0x0400
    # Include the destination EUI64 in the network frame.
    APS_OPTION_DESTINATION_EUI64 = 0x0800
    # Send a ZDO request to discover the node ID of the destination, if it is
    # not already know.
    APS_OPTION_ENABLE_ADDRESS_DISCOVERY = 0x1000
    # Reserved.
    APS_OPTION_POLL_RESPONSE = 0x2000
    # This incoming message is a ZDO request not handled by the EmberZNet
    # stack, and the application is responsible for sending a ZDO response.
    # This flag is used only when the ZDO is configured to have requests
    # handled by the application. See the CONFIG_APPLICATION_ZDO_FLAGS
    # configuration parameter for more information.
    APS_OPTION_ZDO_RESPONSE_REQUIRED = 0x4000
    # This message is part of a fragmented message. This option may only be set
    # for unicasts. The groupId field gives the index of this fragment in the
    # low-order byte. If the low-order byte is zero this is the first fragment
    # and the high-order byte contains the number of fragments in the message.
    APS_OPTION_FRAGMENT = 0x8000


class EzspNetworkScanType(basic.uint8_t, enum.Enum):
    # Network scan types.

    # An energy scan scans each channel for its RSSI value.
    ENERGY_SCAN = 0x00
    # An active scan scans each channel for available networks.
    ACTIVE_SCAN = 0x01


class EmberJoinDecision(basic.uint8_t, enum.Enum):
    # Decision made by the trust center when a node attempts to join.

    # Allow the node to join. The joining node should have a pre-configured
    # key. The security data sent to it will be encrypted with that key.
    USE_PRECONFIGURED_KEY = 0x00
    # Allow the node to join. Send the necessary key (the Network Key in
    # Standard Security mode, the Trust Center Master in High Security mode)
    # in-the-clear to the joining device.
    SEND_KEY_IN_THE_CLEAR = 0x01
    # Deny join.
    DENY_JOIN = 0x02
    # Take no action.
    NO_ACTION = 0x03


class EmberInitialSecurityBitmask(basic.uint16_t):
    # This is the Initial Security Bitmask that controls the use of various
    # security features.

    # This enables ZigBee Standard Security on the node.
    STANDARD_SECURITY_MODE = 0x0000
    # This enables Distributed Trust Center Mode for the device forming the
    # network. (Previously known as NO_TRUST_CENTER_MODE)
    DISTRIBUTED_TRUST_CENTER_MODE = 0x0002
    # This enables a Global Link Key for the Trust Center. All nodes will share
    # the same Trust Center Link Key.
    TRUST_CENTER_GLOBAL_LINK_KEY = 0x0004
    # This enables devices that perform MAC Association with a pre-configured
    # Network Key to join the network. It is only set on the Trust Center.
    PRECONFIGURED_NETWORK_KEY_MODE = 0x0008
    # This denotes that the preconfiguredKey is not the actual Link Key but a
    # Secret Key known only to the Trust Center.  It is hashed with the IEEE
    # Address of the destination device in order to create the actual Link Key
    # used in encryption. This is bit is only used by the Trust Center. The
    # joining device need not set this.
    TRUST_CENTER_USES_HASHED_LINK_KEY = 0x0084
    # This denotes that the preconfiguredKey element has valid data that should
    # be used to configure the initial security state.
    HAVE_PRECONFIGURED_KEY = 0x0100
    # This denotes that the networkKey element has valid data that should be
    # used to configure the initial security state.
    HAVE_NETWORK_KEY = 0x0200
    # This denotes to a joining node that it should attempt to acquire a Trust
    # Center Link Key during joining. This is only necessary if the device does
    # not have a pre-configured key.
    GET_LINK_KEY_WHEN_JOINING = 0x0400
    # This denotes that a joining device should only accept an encrypted
    # network key from the Trust Center (using its preconfigured key). A key
    # sent in-the-clear by the Trust Center will be rejected and the join will
    # fail. This option is only valid when utilizing a pre-configured key.
    REQUIRE_ENCRYPTED_KEY = 0x0800
    # This denotes whether the device should NOT reset its outgoing frame
    # counters (both NWK and APS) when ::emberSetInitialSecurityState() is
    # called. Normally it is advised to reset the frame counter before joining
    # a new network. However in cases where a device is joining to the same
    # network a again (but not using ::emberRejoinNetwork()) it should keep the
    # NWK and APS frame counters stored in its tokens.
    NO_FRAME_COUNTER_RESET = 0x1000
    # This denotes that the device should obtain its preconfigured key from an
    # installation code stored in the manufacturing token. The token contains a
    # value that will be hashed to obtain the actual preconfigured key. If that
    # token is not valid, then the call to emberSetInitialSecurityState() will
    # fail.
    GET_PRECONFIGURED_KEY_FROM_INSTALL_CODE = 0x2000
    # This denotes that the
    # ::EmberInitialSecurityState::preconfiguredTrustCenterEui64 has a value in
    # it containing the trust center EUI64. The device will only join a network
    # and accept commands from a trust center with that EUI64. Normally this
    # bit is NOT set, and the EUI64 of the trust center is learned during the
    # join process. When commissioning a device to join onto an existing
    # network, which is using a trust center, and without sending any messages,
    # this bit must be set and the field
    # ::EmberInitialSecurityState::preconfiguredTrustCenterEui64 must be
    # populated with the appropriate EUI64.
    HAVE_TRUST_CENTER_EUI64 = 0x0040


class EmberCurrentSecurityBitmask(basic.uint16_t):
    # This is the Current Security Bitmask that details the use of various
    # security features.

    # This denotes that the device is running in a network with ZigBee Standard
    # Security.
    STANDARD_SECURITY_MODE = 0x0000
    # This denotes that the device is running in a network with ZigBee High
    # Security.
    HIGH_SECURITY_MODE = 0x0001
    # This denotes that the device is running in a network without a
    # centralized Trust Center.
    DISTRIBUTED_TRUST_CENTER_MODE = 0x0002
    # This denotes that the device has a Global Link Key. The Trust Center Link
    # Key is the same across multiple nodes.
    GLOBAL_LINK_KEY = 0x0004
    # This denotes that the node has a Trust Center Link Key.
    HAVE_TRUST_CENTER_LINK_KEY = 0x0010
    # This denotes that the Trust Center is using a Hashed Link Key.
    TRUST_CENTER_USES_HASHED_LINK_KEY = 0x0084


class EmberKeyType(basic.uint8_t, enum.Enum):
    # Describes the type of ZigBee security key.

    # A shared key between the Trust Center and a device.
    TRUST_CENTER_LINK_KEY = 0x01
    # A shared secret used for deriving keys between the Trust Center and a
    # device
    TRUST_CENTER_MASTER_KEY = 0x02
    # The current active Network Key used by all devices in the network.
    CURRENT_NETWORK_KEY = 0x03
    # The alternate Network Key that was previously in use, or the newer key
    # that will be switched to.
    NEXT_NETWORK_KEY = 0x04
    # An Application Link Key shared with another (non-Trust Center) device.
    APPLICATION_LINK_KEY = 0x05
    # An Application Master Key shared secret used to derive an Application
    # Link Key.
    APPLICATION_MASTER_KEY = 0x06


class EmberKeyStructBitmask(basic.uint16_t):
    # Describes the presence of valid data within the EmberKeyStruct structure.

    # The key has a sequence number associated with it.
    KEY_HAS_SEQUENCE_NUMBER = 0x0001
    # The key has an outgoing frame counter associated with it.
    KEY_HAS_OUTGOING_FRAME_COUNTER = 0x0002
    # The key has an incoming frame counter associated with it.
    KEY_HAS_INCOMING_FRAME_COUNTER = 0x0004
    # The key has a Partner IEEE address associated with it.
    KEY_HAS_PARTNER_EUI64 = 0x0008


class EmberDeviceUpdate(basic.uint8_t, enum.Enum):
    # The status of the device update.

    STANDARD_SECURITY_SECURED_REJOIN = 0x0
    STANDARD_SECURITY_UNSECURED_JOIN = 0x1
    DEVICE_LEFT = 0x2
    STANDARD_SECURITY_UNSECURED_REJOIN = 0x3
    HIGH_SECURITY_SECURED_REJOIN = 0x4
    HIGH_SECURITY_UNSECURED_JOIN = 0x5
    HIGH_SECURITY_UNSECURED_REJOIN = 0x7


class EmberKeyStatus(basic.uint8_t, enum.Enum):
    # The status of the attempt to establish a key.

    APP_LINK_KEY_ESTABLISHED = 0x01
    APP_MASTER_KEY_ESTABLISHED = 0x02
    TRUST_CENTER_LINK_KEY_ESTABLISHED = 0x03
    KEY_ESTABLISHMENT_TIMEOUT = 0x04
    KEY_TABLE_FULL = 0x05
    TC_RESPONDED_TO_KEY_REQUEST = 0x06
    TC_APP_KEY_SENT_TO_REQUESTER = 0x07
    TC_RESPONSE_TO_KEY_REQUEST_FAILED = 0x08
    TC_REQUEST_KEY_TYPE_NOT_SUPPORTED = 0x09
    TC_NO_LINK_KEY_FOR_REQUESTER = 0x0A
    TC_REQUESTER_EUI64_UNKNOWN = 0x0B
    TC_RECEIVED_FIRST_APP_KEY_REQUEST = 0x0C
    TC_TIMEOUT_WAITING_FOR_SECOND_APP_KEY_REQUEST = 0x0D
    TC_NON_MATCHING_APP_KEY_REQUEST_RECEIVED = 0x0E
    TC_FAILED_TO_SEND_APP_KEYS = 0x0F
    TC_FAILED_TO_STORE_APP_KEY_REQUEST = 0x10
    TC_REJECTED_APP_KEY_REQUEST = 0x11


class EmberCounterType(basic.uint8_t, enum.Enum):
    # Defines the events reported to the application by the
    # readAndClearCounters command.

    # The MAC received a broadcast.
    COUNTER_MAC_RX_BROADCAST = 0
    # The MAC transmitted a broadcast.
    COUNTER_MAC_TX_BROADCAST = 1
    # The MAC received a unicast.
    COUNTER_MAC_RX_UNICAST = 2
    # The MAC successfully transmitted a unicast.
    COUNTER_MAC_TX_UNICAST_SUCCESS = 3
    # The MAC retried a unicast.
    COUNTER_MAC_TX_UNICAST_RETRY = 4
    # The MAC unsuccessfully transmitted a unicast.
    COUNTER_MAC_TX_UNICAST_FAILED = 5
    # The APS layer received a data broadcast.
    COUNTER_APS_DATA_RX_BROADCAST = 6
    # The APS layer transmitted a data broadcast.
    COUNTER_APS_DATA_TX_BROADCAST = 7
    # The APS layer received a data unicast.
    COUNTER_APS_DATA_RX_UNICAST = 8
    # The APS layer successfully transmitted a data unicast.
    COUNTER_APS_DATA_TX_UNICAST_SUCCESS = 9
    # The APS layer retried a data unicast.
    COUNTER_APS_DATA_TX_UNICAST_RETRY = 10
    # The APS layer unsuccessfully transmitted a data unicast.
    COUNTER_APS_DATA_TX_UNICAST_FAILED = 11
    # The network layer successfully submitted a new route discovery to the
    # MAC.
    COUNTER_ROUTE_DISCOVERY_INITIATED = 12
    # An entry was added to the neighbor table.
    COUNTER_NEIGHBOR_ADDED = 13
    # An entry was removed from the neighbor table.
    COUNTER_NEIGHBOR_REMOVED = 14
    # A neighbor table entry became stale because it had not been heard from.
    COUNTER_NEIGHBOR_STALE = 15
    # A node joined or rejoined to the network via this node.
    COUNTER_JOIN_INDICATION = 16
    # An entry was removed from the child table.
    COUNTER_CHILD_REMOVED = 17
    # EZSP-UART only. An overflow error occurred in the UART.
    COUNTER_ASH_OVERFLOW_ERROR = 18
    # EZSP-UART only. A framing error occurred in the UART.
    COUNTER_ASH_FRAMING_ERROR = 19
    # EZSP-UART only. An overrun error occurred in the UART.
    COUNTER_ASH_OVERRUN_ERROR = 20
    # A message was dropped at the network layer because the NWK frame counter
    # was not higher than the last message seen from that source.
    COUNTER_NWK_FRAME_COUNTER_FAILURE = 21
    # A message was dropped at the APS layer because the APS frame counter was
    # not higher than the last message seen from that source.
    COUNTER_APS_FRAME_COUNTER_FAILURE = 22
    # Utility counter for general debugging use.
    COUNTER_UTILITY = 23
    # A message was dropped at the APS layer because it had APS encryption but
    # the key associated with the sender has not been authenticated, and thus
    # the key is not authorized for use in APS data messages.
    COUNTER_APS_LINK_KEY_NOT_AUTHORIZED = 24
    # A NWK encrypted message was received but dropped because decryption
    # failed.
    COUNTER_NWK_DECRYPTION_FAILURE = 25
    # An APS encrypted message was received but dropped because decryption
    # failed.
    COUNTER_APS_DECRYPTION_FAILURE = 26
    # The number of times we failed to allocate a set of linked packet buffers.
    # This doesn't necessarily mean that the packet buffer count was 0 at the
    # time, but that the number requested was greater than the number free.
    COUNTER_ALLOCATE_PACKET_BUFFER_FAILURE = 27
    # The number of relayed unicast packets.
    COUNTER_RELAYED_UNICAST = 28
    # The number of times we dropped a packet due to reaching
    # the preset PHY to MAC queue limit (emMaxPhyToMacQueueLength).
    COUNTER_PHY_TO_MAC_QUEUE_LIMIT_REACHED = 29
    # The number of times we dropped a packet due to the
    # packet-validate library checking a packet and rejecting it
    # due to length or other formatting problems.
    COUNTER_PACKET_VALIDATE_LIBRARY_DROPPED_COUNT = 30
    # The number of times the NWK retry queue is full and a
    # new message failed to be added.
    COUNTER_TYPE_NWK_RETRY_OVERFLOW = 31
    # The number of times the PHY layer was unable to transmit
    # due to a failed CCA.
    COUNTER_PHY_CCA_FAIL_COUNT = 32
    # The number of times a NWK broadcast was dropped because
    # the broadcast table was full.
    COUNTER_BROADCAST_TABLE_FULL = 33
    # The number of low priority packet traffic arbitration requests.
    COUNTER_PTA_LO_PRI_REQUESTED = 34
    # The number of high priority packet traffic arbitration requests.
    COUNTER_PTA_HI_PRI_REQUESTED = 35
    # The number of low priority packet traffic arbitration requests denied.
    COUNTER_PTA_LO_PRI_DENIED = 36
    # The number of high priority packet traffic arbitration requests denied.
    COUNTER_PTA_HI_PRI_DENIED = 37
    # The number of aborted low priority packet traffic arbitration transmissions.
    COUNTER_PTA_LO_PRI_TX_ABORTED = 38
    # The number of aborted high priority packet traffic arbitration transmissions.
    COUNTER_PTA_HI_PRI_TX_ABORTED = 39
    # A placeholder giving the number of Ember counter types.
    COUNTER_TYPE_COUNT = 40


class EmberJoinMethod(basic.uint8_t, enum.Enum):
    # The type of method used for joining.

    # Normally devices use MAC Association to join a network, which respects
    # the "permit joining" flag in the MAC Beacon. For mobile nodes this value
    # causes the device to use an Ember Mobile Node Join, which is functionally
    # equivalent to a MAC association. This value should be used by default.
    USE_MAC_ASSOCIATION = 0x0
    # For those networks where the "permit joining" flag is never turned on,
    # they will need to use a ZigBee NWK Rejoin. This value causes the rejoin
    # to be sent without NWK security and the Trust Center will be asked to
    # send the NWK key to the device. The NWK key sent to the device can be
    # encrypted with the device's corresponding Trust Center link key. That is
    # determined by the ::EmberJoinDecision on the Trust Center returned by the
    # ::emberTrustCenterJoinHandler(). For a mobile node this value will cause
    # it to use an Ember Mobile node rejoin, which is functionally equivalent.
    USE_NWK_REJOIN = 0x1
    # For those networks where the "permit joining" flag is never turned on,
    # they will need to use a NWK Rejoin. If those devices have been
    # preconfigured with the NWK key (including sequence number) they can use a
    # secured rejoin. This is only necessary for end devices since they need a
    # parent. Routers can simply use the ::USE_NWK_COMMISSIONING join method
    # below.
    USE_NWK_REJOIN_HAVE_NWK_KEY = 0x2
    # For those networks where all network and security information is known
    # ahead of time, a router device may be commissioned such that it does not
    # need to send any messages to begin communicating on the network.
    USE_NWK_COMMISSIONING = 0x3


class EmberZdoConfigurationFlags(basic.uint8_t, enum.Enum):
    # Flags for controlling which incoming ZDO requests are passed to the
    # application. To see if the application is required to send a ZDO response
    # to an incoming message, the application must check the APS options
    # bitfield within the incomingMessageHandler callback to see if the
    # APS_OPTION_ZDO_RESPONSE_REQUIRED flag is set.

    # Set this flag in order to receive supported ZDO request messages via the
    # incomingMessageHandler callback. A supported ZDO request is one that is
    # handled by the EmberZNet stack. The stack will continue to handle the
    # request and send the appropriate ZDO response even if this configuration
    # option is enabled.
    APP_RECEIVES_SUPPORTED_ZDO_REQUESTS = 0x01
    # Set this flag in order to receive unsupported ZDO request messages via
    # the incomingMessageHandler callback. An unsupported ZDO request is one
    # that is not handled by the EmberZNet stack, other than to send a 'not
    # supported' ZDO response. If this configuration option is enabled, the
    # stack will no longer send any ZDO response, and it is the application's
    # responsibility to do so.
    APP_HANDLES_UNSUPPORTED_ZDO_REQUESTS = 0x02
    # Set this flag in order to receive the following ZDO request messages via
    # the incomingMessageHandler callback: SIMPLE_DESCRIPTOR_REQUEST,
    # MATCH_DESCRIPTORS_REQUEST, and ACTIVE_ENDPOINTS_REQUEST. If this
    # configuration option is enabled, the stack will no longer send any ZDO
    # response for these requests, and it is the application's responsibility
    # to do so.
    APP_HANDLES_ZDO_ENDPOINT_REQUESTS = 0x04
    # Set this flag in order to receive the following ZDO request messages via
    # the incomingMessageHandler callback: BINDING_TABLE_REQUEST, BIND_REQUEST,
    # and UNBIND_REQUEST. If this configuration option is enabled, the stack
    # will no longer send any ZDO response for these requests, and it is the
    # application's responsibility to do so.
    APP_HANDLES_ZDO_BINDING_REQUESTS = 0x08


class EmberConcentratorType(basic.uint16_t, enum.Enum):
    # Type of concentrator.

    # A concentrator with insufficient memory to store source routes for the
    # entire network. Route records are sent to the concentrator prior to every
    # inbound APS unicast.
    LOW_RAM_CONCENTRATOR = 0xFFF8
    # A concentrator with sufficient memory to store source routes for the
    # entire network. Remote nodes stop sending route records once the
    # concentrator has successfully received one.
    HIGH_RAM_CONCENTRATOR = 0xFFF9


class EmberZllState(basic.uint16_t, enum.Enum):
    # ZLL device state identifier.

    # No state.
    ZLL_STATE_NONE = 0x0000
    # The device is factory new.
    ZLL_STATE_FACTORY_NEW = 0x0001
    # The device is capable of assigning addresses to other devices.
    ZLL_STATE_ADDRESS_ASSIGNMENT_CAPABLE = 0x0002
    # The device is initiating a link operation.
    ZLL_STATE_LINK_INITIATOR = 0x0010
    # The device is requesting link priority.
    ZLL_STATE_LINK_PRIORITY_REQUEST = 0x0020
    # The device is on a non-ZLL network.
    ZLL_STATE_NON_ZLL_NETWORK = 0x0100


class EmberZllKeyIndex(basic.uint8_t, enum.Enum):
    # ZLL key encryption algorithm enumeration.

    # Key encryption algorithm for use during development.
    ZLL_KEY_INDEX_DEVELOPMENT = 0x00
    # Key encryption algorithm shared by all certified devices.
    ZLL_KEY_INDEX_MASTER = 0x04
    # Key encryption algorithm for use during development and certification.
    ZLL_KEY_INDEX_CERTIFICATION = 0x0F


class EzspZllNetworkOperation(basic.uint8_t, enum.Enum):
    # Differentiates among ZLL network operations.

    ZLL_FORM_NETWORK = 0x00  # ZLL form network command.
    ZLL_JOIN_TARGET = 0x01  # ZLL join target command.


class EzspSourceRouteOverheadInformation(basic.uint8_t, enum.Enum):
    # Validates Source Route Overhead Information cached.

    # Ezsp source route overhead unknown
    SOURCE_ROUTE_OVERHEAD_UNKNOWN = 0xFF


class EmberNetworkInitBitmask(basic.uint16_t):
    # Bitmask options for emberNetworkInit().

    # No options for Network Init
    NETWORK_INIT_NO_OPTIONS = 0x0000
    # Save parent info (node ID and EUI64) in a token during joining/rejoin,
    # and restore on reboot.
    NETWORK_INIT_PARENT_INFO_IN_TOKEN = 0x0001
