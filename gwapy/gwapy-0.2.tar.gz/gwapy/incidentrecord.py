from xml.dom.minidom import getDOMImplementation, parseString

from wa_fields import WaField, WaFft

impl = getDOMImplementation()

SWORD_HIDDENDUMMYIR = 'SZZZZ'
SWORD_TITLE = 'S0E0F'
SWORD_DESCRIPTION = 'S0E01'
SWORD_STATUSTEXT = 'S0E02'
SWORD_ASSIGNEEGROUP = 'S0B9C'
SWORD_ASSIGNEENAME = 'S0B5A'
SWORD_ASSIGNEEPHONE = 'S0B2E'
SWORD_RECORDID = 'S0000'
SWORD_TYPE = 'S0C09'
SWORD_COMPONENT = 'S81FF'
SWORD_SUBCOMPONENT = 'S8778'
SWORD_SEVERITY = 'S0BE7'
SWORD_STATUS = 'S0BEE'
SWORD_URGENCYCODE = 'S8048'
SWORD_CLASSENTERED = 'S0BB1'
SWORD_EXTERNALCREATION = 'S8E6B'
SWORD_MASTERRECORD = 'S88F8'
SWORD_ASYSCATEGORY = 'S88CC'
SWORD_SYSTEM = 'S81AB'
SWORD_RESPONSIBLEGROUP = 'S88C9'
SWORD_RESPONSIBLENAME = 'S88CA'
SWORD_RESPONSIBLEPHONE = 'S88CB'
SWORD_SERVICE = 'S8B51'
SWORD_SERVICECATEGORY = 'S8B52'
SWORD_SUBSTATUS = 'S8EC0'
SWORD_OWNERGROUP = 'S8A42'
SWORD_ONWERNAME = 'S8B28'
SWORD_OWNERPHONE = 'S8B5E'
SWORD_WISHDATE = 'S8A5F'
SWORD_WISHDATE = 'S8A60'
SWORD_DUMMYFIELDFORIWAVETOQF = 'S0E05'
SWORD_OWNER_CAT = 'S8EDC'
SWORD_DETECTIONDATE = 'S8CFA'
SWORD_DETECTIONTIME = 'S8CFB'
SWORD_LOADEDDATE = 'S0C41'
SWORD_LOADEDTIME = 'S0C70'
SWORD_SELECT_OWNER_GROUP_PRD = 'S8EDD'
SWORD_SELECT_OWNER_GROUP_TST = 'S8EDE'
SWORD_PLANNEDLOADDATE = 'S8D45'
SWORD_PLANNEDLOADTIME = 'S8D46'
SWORD_ACCOUNTID = 'S8D54'
SWORD_LOGGERGROUP = 'S0B9E'
SWORD_LOGGERNAME = 'S0B5C'
SWORD_LOGGERPHONE = 'S0B30'
SWORD_LOCATION = 'S800D'
SWORD_CONTACTID = 'S8A88'
SWORD_REPORTERGROUP = 'S0B9B'
SWORD_REPORTERNAME = 'S0B59'
SWORD_REPORTERPHONE = 'S0B2D'
SWORD_MASTERID = 'S8A6B'
SWORD_PTRREFNO1 = 'S0CD3'
SWORD_BYPASSDATE = 'S8200'
SWORD_RECOVERYTIME = 'S8201'
SWORD_LASTMODIFYDATE = 'S0C35'
SWORD_LASTMODIFYTIME = 'S0C62'
SWORD_LASTMODIFYUSER = 'S0B5E'
SWORD_CLOSEDDATE = 'S0C38'
SWORD_CLOSEDTIME = 'S0C65'
SWORD_HIDDENRECORD = 'S8EBF'
SWORD_OCCURRENCEDATE = 'S0C3D'
SWORD_OCCURRENCETIME = 'S0C6A'
SWORD_SVAFFREQUIRED = 'S895D'
SWORD_REVIEWDATE = 'S0C42'
SWORD_REVIEWTIME = 'S0C6F'
SWORD_ACKDATE = 'S8A4E'
SWORD_ACKTIME = 'S8A4F'
SWORD_REPLICATEDTOBA = 'S8A38'
SWORD_REPLLICATEDTOQF = 'S8A26'
SWORD_CAUSECI = 'S8B69'
SWORD_REJECTREASON = 'S82D6'
SWORD_COMMSSOFTWARE = 'S82D5'
SWORD_NOTESLINK = 'S8AAE'
SWORD_KNOWLEDGEBASE = 'S8A62'
SWORD_GLOBALOPSCAT1 = 'S8B66'
SWORD_GLOBALOPSCAT2 = 'S8B67'
SWORD_GLOBALOPSCAT3 = 'S8B68'
SWORD_SLAID = 'S8A5A'
SWORD_SLAACCEPTDATE = 'S8A5B'
SWORD_SLAACCEPTTIME = 'S8A5C'
SWORD_SLARECOVERYDATE = 'S8A5D'
SWORD_SLARECOVERYTIME = 'S8A5E'
SWORD_SLAPENALTY = 'S8CEC'
SWORD_LASTOKDATE = 'S8D7B'
SWORD_LASTOKTIME = 'S8D7C'
SWORD_IRCHILDINCIDENTEXISTS = 'S8D40'
SWORD_CIREFERENCEEN = 'S8B4B'
SWORD_LOCKDURATION = 'S8D0A'
SWORD_CLOCKDURATION = 'S8D0B'
SWORD_SYMPTOM = 'S8AB9'
SWORD_LOADINFO = 'S0E10'
SWORD_FULLEXECSUMMARY = 'S8EA1'
SWORD_LINK1PARTNERID = 'S8CFF'
SWORD_LINK1EXTERNALID = 'S8D00'
SWORD_LINK1EXTERNALREF = 'S8D01'
SWORD_LINK2PARTNERID = 'S8D02'
SWORD_LINK2EXTERNALID = 'S8D03'
SWORD_LINK2EXTERNALREF = 'S8D04'
SWORD_LINK1EXTERNALNUMBER = 'S8EBB'
SWORD_LINK2EXTERNALNUMBER = 'S8EBC'
SWORD_HOTELCODE = 'S8EBD'
SWORD_VENDORCATEGORY = 'S8B0F'
SWORD_VENDOR = 'S8003'
SWORD_VENDORNAME = 'S8023'
SWORD_VENDORPHONE = 'S8024'
SWORD_VENDORREFERENCE = 'S0D11'
SWORD_AIRWCOMPLIANCE = 'S8AFC'
SWORD_HIERESCALATION = 'S8B85'
SWORD_TOPXERRORCODE = 'S8C8E'
SWORD_TECHNICALISSUE = 'S8C9F'
SWORD_EXECUTIVESUMMARY = 'S8AA0'
SWORD_ORIGINATORGROUPID = 'S8CFC'
SWORD_ORIGINATORUSERID = 'S8CFD'
SWORD_ORIGINATORTELEPHONE = 'S8CFE'
SWORD_IMPACTSFLIGHTSAFETY = 'S8DE1'
SWORD_CONFCALLNUMBER = 'S0C0D'
SWORD_RESOLUTIONCAUSE = 'S88F7'
SWORD_SOLVEDTIME = 'S801E'
SWORD_SOLVEDDATE = 'S801F'
SWORD_AREA = 'S816B'
SWORD_BAPMXRNID = 'S899F'
SWORD_BACOUNTRY = 'S8A0D'
SWORD_BALOCATION = 'S8A09'
SWORD_BALOCATIONDESC1 = 'S8A0A'
SWORD_BALOCATIONDESC2 = 'S8A0B'
SWORD_BALOCATIONDESC3 = 'S8A0C'
SWORD_BATICKETTYPE = 'S88F6'
SWORD_BAEXTERNALID = 'S8A47'
SWORD_QFSEVERITY = 'S8A17'
SWORD_QFCOVERAGEDATE = 'S8A27'
SWORD_QFCOVERAGETIME = 'S8A28'
SWORD_QFREFNO1 = 'S8A29'
SWORD_QFREFNO2 = 'S8A2A'
SWORD_QFREFNO3 = 'S8A2B'
SWORD_QFREFNO4 = 'S8A2C'
SWORD_QFREFNO5 = 'S8A2D'
SWORD_QFREFNO6 = 'S8A2E'
SWORD_FLIGHTDELAY = 'S8A16'
SWORD_QFEXTERNALID = 'S899F'
SWORD_QFFLIGHTDELAY = 'S8A2F'
SWORD_OWNEDBYQF = 'S8A36'
SWORD_QFMAXIMORNID = 'S8A39'
SWORD_SIEBELROWID = 'S8B1B'
SWORD_SIEBELID = 'S8B1C'
SWORD_GSSESCALATIONRANKING = 'S8EE1'
SWORD_SIEBELCATA = 'S8B21'
SWORD_SIEBELCATB = 'S8B22'
SWORD_SIEBELCATC = 'S8B23'
SWORD_SIEBELCATD = 'S8B24'
SWORD_SIEBELCATE = 'S8B25'
SWORD_COUNTRYCODE = 'S825C'
SWORD_OFFICEID = 'S82CA'
SWORD_PRODPLANCATEGORY = 'S8997'
SWORD_AMAPROVERSION2 = 'S82CC'
SWORD_TERMINALADDRESS = 'S81B0'
SWORD_OPERSYSTEMNAME = 'S82C9'
SWORD_OPERSYSTEMVERSION = 'S82DD'
SWORD_ATID = 'S8721'
SWORD_FIXEDINRELEASE = 'S8D47'
SWORD_FOCUS = 'S8EC3'
SWORD_CAUSE = 'S8188'
SWORD_USERREMARKS = 'S8243'
SWORD_URLALF = 'S8E33'
SWORD_URLSENTINEL = 'S8E34'
SWORD_IRLONELINK = 'S8E35'
SWORD_TRACKERGROUP5 = 'S8101'
SWORD_LHPSCID = 'S8C68'
SWORD_PROJECT = 'S8996'
SWORD_EXPLORERLANGUAGE = 'S8B13'
SWORD_EXPLORERSERVPACK = 'S8B14'
SWORD_OSSERVICEPACK = 'S8B12'
SWORD_LUFTHANSAID = 'S8B3A'
SWORD_RATINGBYCUSTOMER = 'S8E42'
SWORD_SEVERITYONEACK = 'S8ABA'
SWORD_SIEBELCOMPROWID = 'S8B5F'
SWORD_SIEBELCONTROWID = 'S8B60'
SWORD_ERRORMESSAGE = 'S8E28'
SWORD_KNOWLEDGEBASEURL = 'S8EDB'
SWORD_LASTEVERBRIDGESENTDATE = 'S8EEC'
SWORD_LASTEVERBRIDGESENTTIME = 'S8EED'
SWORD_AFFSERVICEFLIGHTDELC = 'S8C9B'
SWORD_AFFSERVICEFLIGHTDELA = 'S8C9A'
SWORD_AFFSERVICELASTDATE = 'S895E'
SWORD_AFFSERVICELASTTIME = 'S895F'
SWORD_AFFSERVICELASTUSER = 'S8960'
SWORD_UPDATEDINBA = 'S89A0'
SWORD_UPDATEDINQF = 'S8A10'
SWORD_CLOSEDBY = 'S802A'
SWORD_SEVATFIRSTACKID = 'S8D53'
SWORD_ACCESSEDDATE = 'S8A4C'
SWORD_ACCESSEDTIME = 'S8A4D'
SWORD_ACKDATE = 'S8A4E'
SWORD_ACKTIME = 'S8A4F'
SWORD_ACKDATEEXT = 'S8AB7'
SWORD_ACKTIMEEXT = 'S8AB8'
SWORD_IWAVEERRORBA = 'S88D8'
SWORD_IWAVEERRORQF = 'S8A14'
SWORD_AIRFRANCEID = 'S8C9D'
SWORD_LHIMVIEWID = 'S8B84'
SWORD_MAXSEVERITY = 'S8A68'
SWORD_COMMUNITYACCESS = 'S8B26'
SWORD_COMMUNITYOWNER = 'S8B27'
SWORD_IMLASTUPDATE = 'S8C3D'
SWORD_IMSERVICE = 'S8C3E'
SWORD_IMMARKETS = 'S8C3F'
SWORD_IMSINCE = 'S8C40'
SWORD_IMCAUSE = 'S8C41'
SWORD_IM_STATUS = 'S8C42'
SWORD_IMRECOVERY = 'S8C43'
SWORD_IMEMAIL = 'S8C44'
SWORD_IMEXTERNALSTATUS = 'S8CD3'
SWORD_IMUPGRADETIME = 'S8CD4'
SWORD_CUSTOMERINFO = 'S804C'
SWORD_CUSTOMERNOTE = 'S8EB5'
SWORD_PREVSTATUSMAIL = 'S8E97'
SWORD_REPORTREQUESTED = 'S8CE1'
SWORD_REPORTFORAIRLINES = 'S8CE2'
SWORD_CIREFERENCEEN = 'S8B4C'
SWORD_SOLVERGROUP2 = 'S8241'
SWORD_RECOVERYACTION = 'S8AAD'
SWORD_TRREFERENCE = 'S84A7'
SWORD_CRCPREFNO1 = 'S0CD1'
SWORD_CRCPREFNO2 = 'S0CD2'
SWORD_RESOLUTION = 'S0E03'
SWORD_CAUSEDCR = 'S8999'
SWORD_CAUSEDWO = 'S8B00'
SWORD_LRREFERENCE = 'S84A8'
SWORD_OSLANGUAGE = 'S8B11'
SWORD_SOLUTIONXREF = 'S8B63'
SWORD_PTRREFNO2 = 'S81F3'
SWORD_PTRREFNO3 = 'S81F4'
SWORD_WORKAROUNDAVAIL = 'S8C86'
SWORD_REOCCURANCE = 'S8C85'
SWORD_PTRREFNO4 = 'S81F5'
SWORD_CINOTFOUND = 'S8C58'
SWORD_CINOTFOUNDREASON = 'S8C59'
SWORD_CINOTFOUNDLIST = 'S8C5E'
SWORD_CRIMPLEMENTATION = 'S8CED'
SWORD_PTRREFNO0 = 'S81F6'
SWORD_LOCALMASTER = 'S8CBE'
SWORD_MARKEDASMIRDATE = 'S8CC2'
SWORD_MARKEDASMIRTIME = 'S8CC3'
SWORD_DIAGNOSEDDATE = 'S8CC4'
SWORD_DIAGNOSEDTIME = 'S8CC5'
SWORD_ENTEREDDATE = 'S0C34'
SWORD_ENTEREDTIME = 'S0C61'
SWORD_TEMPLATEID = 'S8A55'
SWORD_QFLASTGROUP = 'S8A31'
SWORD_QFLASTUSER = 'S8A30'
SWORD_QFLASTTEL = 'S8A32'
SWORD_AMAACKSEV = 'S8CD5'
SWORD_IWAVEBAMODE = 'S89A1'
SWORD_BACATEGORY = 'S8A51'
SWORD_BASUBCATEGORY = 'S8A52'
SWORD_BAPRODUCT = 'S8A53'
SWORD_BAPROBLEMTYPE = 'S8A54'
SWORD_QFMSSTATUS = 'S8A64'
SWORD_CRISISACTIVATION = 'S8CE7'
SWORD_CRISISACTIVATION = 'S8CE8'
SWORD_IMSTART = 'S8CE3'
SWORD_IMSTART = 'S8CE4'
SWORD_REJECTDATE = 'S8CE9'
SWORD_REJECTDATE_2 = 'S8CEA'
SWORD_DIAGNOSEDGROUPID = 'S8CEB'
SWORD_LOGGEDTOOL = 'S8CF1'
SWORD_RECTYPEID = 'S8CF3'
SWORD_SERVMANINVOLVEDDATE = 'S8D0F'
SWORD_SERVMANINVOLVEDTIME = 'S8D10'
SWORD_CREATEDBYTOOL = 'S8D11'
SWORD_LOGGERUSERID = 'S8D12'
SWORD_ACKSMCGROUP = 'S8D74'
SWORD_ACKSMCUSER = 'S8D75'
SWORD_MAXSEVSETDATE = 'S8D76'
SWORD_MAXSEVSETTIME = 'S8D77'
SWORD_SERVICEIMPACTINDEX = 'S8D9B'
SWORD_SEV1SETDATE = 'S8E43'
SWORD_SEV2SETDATE = 'S8E44'
SWORD_SEV3SETDATE = 'S8E45'
SWORD_SEV4SETDATE = 'S8E46'
SWORD_SOAINVOLVEDDATE = 'S8E40'
SWORD_SOAINVOLVEDTIME = 'S8E41'
SWORD_PTRIRREFERENCE = 'S8E1B'
SWORD_CHASEUPTEXT = 'S0E11'
SWORD_CHASEUPGROUPS = 'S8D7E'
SWORD_CLAIMPROVIDERCODE = 'S8CC7'
SWORD_CLAIMAMOUNTREQ = 'S8CC8'
SWORD_CLAIMAMOUNTREFUND = 'S8CC9'
SWORD_CLAIMRESPONSIBLE = 'S8CCA'
SWORD_CLAIMREASON = 'S8CCB'
SWORD_IWAVEBACLOSUREFLAG = 'S8A4B'
SWORD_ADMSOURCE = 'S8CE5'
SWORD_PAYMENTAPPROVED = 'S8CE6'
SWORD_CAUSEDCR = 'S8999'
SWORD_HIERESCALATION = 'S8B85'
SWORD_MIRDETECTEDBY = 'S8EA8'
SWORD_PARALLELINVESTOPEN = 'S8CBF'
SWORD_FIRSTCIRAUTOMATIONDATE = 'S8EAA'
SWORD_FIRSTCIRAUTOMATIONTIME = 'S8EAB'
SWORD_FIRSTCIRCUSTOMERDATE = 'S8EAC'
SWORD_FIRSTCIRCUSTOMERTIME = 'S8EAD'
SWORD_FIRSTCIRAMADEUSDATE = 'S8EAE'
SWORD_FIRSTCIRAMADEUSTIME = 'S8EAF'
SWORD_ORANGECRISISTRIGGERED = 'S8EC5'
SWORD_IRPRIORITY = 'S8D87'
SWORD_IRPRIORITYACCEPTDATE = 'S8D88'
SWORD_IRPRIORITYACCEPTTIME = 'S8D89'
SWORD_TARGETDATE = 'S82FB'
SWORD_TARGETTIME = 'S8D8B'
SWORD_USAGE = 'S8D8C'
SWORD_PRIOSEV1 = 'S8E21'
SWORD_PRIOSEV2U = 'S8E22'
SWORD_PRIOSEV2 = 'S8E23'
SWORD_PRIOSEV3U = 'S8E24'
SWORD_PRIOSEV3 = 'S8E25'
SWORD_PRIOSEV4U = 'S8E26'
SWORD_PRIOSEV4 = 'S8E27'
SWORD_RECOVDATEINT = 'S8E50'
SWORD_RECOVDATEINT = 'S8E51'
SWORD_NRCOMMONCIS = 'S8E52'
SWORD_TAGCI1 = 'S8E5B'
SWORD_TAGCI2 = 'S8E5C'
SWORD_TAGCI3 = 'S8E5D'
SWORD_TAGCI4 = 'S8E5E'
SWORD_TAGMORECOMMON_CIS = 'S8E5F'
SWORD_TAGALLCIS = 'S8E60'
SWORD_FOUNDCIS = 'S8E53'
SWORD_RELATEDBYTAG = 'S8E61'
SWORD_TAGLIMIT = 'S8E55'
SWORD_TAGOFFSET = 'S8E54'
SWORD_TAGRECORDTYPES = 'S8E56'
SWORD_TAGSTARTTIME = 'S8E57'
SWORD_TAGSTARTTIMEUNIT = 'S8E58'
SWORD_TAGENDTIME = 'S8E59'
SWORD_TAGENDTIMEUNIT = 'S8E5A'
SWORD_TAGSTARTDATEABS = 'S8E6F'
SWORD_TAGSTARTTIMEABS = 'S8E70'
SWORD_TAGENDDATEABS = 'S8E71'
SWORD_TAGENDTIMEABS = 'S8E72'
SWORD_TAGTIMEMODE = 'S8E73'
SWORD_TAGSTARTTIMEREL = 'S8E77'
SWORD_TAGSTARTTIMEUNITREL = 'S8E78'
SWORD_TAGENDTIMEREL = 'S8E79'
SWORD_TAGENDTIMEUNITREL = 'S8E7A'
SWORD_DISPATCHGROUPCODE = 'S8E62'
SWORD_DISPATCHGROUPNAME = 'S8E68'
SWORD_DISPATCHRELEVANCE = 'S8E69'
SWORD_PMRSEACHFOR = 'S8E74'
SWORD_PMRID = 'S8E75'
SWORD_PMRSEACHIN = 'S8E7B'
SWORD_RELATEDPMRS = 'S8E76'
SWORD_TREXIST = 'S8AAB'
SWORD_NOTENGINE_URL = 'S8EF1'
SWORD_NOTIFICATION_SENT = 'S8EF2'
SWORD_CIR_1STG_SERVICE = 'S8EF3'

IncidentRecordFields = [
    WaField(SWORD_TITLE, 'TITL', 'Title', 'Y'),
    WaField(SWORD_ASSIGNEEGROUP, 'GROA', 'AssigneeGroup', 'Y'),
    WaField(SWORD_ASSIGNEENAME, 'PERA', 'AssigneeName', 'N'),
    WaField(SWORD_ASSIGNEEPHONE, 'PH', 'AssigneePhone', 'N'),
    WaField(SWORD_RECORDID, 'RNID', 'RecordID', 'N'),
    WaField(SWORD_TYPE, 'TYPE', 'Type', 'Y'),
    WaField(SWORD_COMPONENT, 'COID', 'Component', 'Y'),
    WaField(SWORD_SUBCOMPONENT, 'SUBC', 'Subcomponent', 'N'),
    WaField(SWORD_SEVERITY, 'PRIO', 'Severity', 'Y'),
    WaField(SWORD_STATUS, 'STAC', 'Status', 'Y'),
    WaField(SWORD_URGENCYCODE, 'URGE', 'UrgencyCode', 'N'),
    WaField(SWORD_CLASSENTERED, '', 'ClassEntered', 'N'),
    WaField(SWORD_EXTERNALCREATION, 'EXTC', 'ExternalCreation', 'N'),
    WaField(SWORD_MASTERRECORD, 'MAST', 'MasterRecord', 'N'),
    WaField(SWORD_ASYSCATEGORY, 'ASPT', 'AsysCategory', 'Y'),
    WaField(SWORD_SYSTEM, 'ASYS', 'System', 'N'),
    WaField(SWORD_RESPONSIBLEGROUP, 'OWNG', 'ResponsibleGroup', 'N'),
    WaField(SWORD_RESPONSIBLENAME, 'OWNN', 'ResponsibleName', 'N'),
    WaField(SWORD_RESPONSIBLEPHONE, 'OWNP', 'ResponsiblePhone', 'N'),
    WaField(SWORD_SERVICE, 'IS1', 'Service', 'N'),
    WaField(SWORD_SERVICECATEGORY, 'IS2', 'ServiceCategory', 'N'),
    WaField(SWORD_SUBSTATUS, 'SSTA', 'SubStatus', 'N'),
    WaField(SWORD_OWNERGROUP, 'OGRP', 'OwnerGroup', 'N'),
    WaField(SWORD_ONWERNAME, 'ONAM', 'OnwerName', 'N'),
    WaField(SWORD_OWNERPHONE, 'ICOT', 'OwnerPhone', 'N'),
    WaField(SWORD_WISHDATE, 'DAWI', 'WishDate', 'N'),
    WaField(SWORD_WISHDATE, 'TIWI', 'WishDate', 'N'),
    WaField(SWORD_OWNER_CAT, '', 'OwnerCat', 'N'),
    WaField(SWORD_DETECTIONDATE, 'DADT', 'DetectionDate', 'N'),
    WaField(SWORD_DETECTIONTIME, 'TIDT', 'DetectionTime', 'N'),
    WaField(SWORD_LOADEDDATE, 'DATP', 'LoadedDate', 'N'),
    WaField(SWORD_LOADEDTIME, 'TIMP', 'LoadedTime', 'N'),
    WaField(SWORD_SELECT_OWNER_GROUP_PRD, '', 'SELECT_OWNER_GROUP_Prd', 'N'),
    WaField(SWORD_SELECT_OWNER_GROUP_TST, '', 'SELECT_OWNER_GROUP_Tst', 'N'),
    WaField(SWORD_PLANNEDLOADDATE, 'PLDA', 'PlannedLoadDate', 'N'),
    WaField(SWORD_PLANNEDLOADTIME, 'PLTI', 'PlannedLoadTime', 'N'),
    WaField(SWORD_ACCOUNTID, 'ACID', 'AccountId', 'N'),
    WaField(SWORD_LOGGERGROUP, 'GROC', 'LoggerGroup', 'Y'),
    WaField(SWORD_LOGGERNAME, 'PERC', 'LoggerName', 'Y'),
    WaField(SWORD_LOGGERPHONE, 'PH', 'LoggerPhone', 'N'),
    WaField(SWORD_LOCATION, 'LOC1', 'Location', 'Y'),
    WaField(SWORD_CONTACTID, 'CUID', 'ContactID', 'N'),
    WaField(SWORD_REPORTERGROUP, 'AGEN', 'ReporterGroup', 'N'),
    WaField(SWORD_REPORTERNAME, 'PERS', 'ReporterName', 'N'),
    WaField(SWORD_REPORTERPHONE, 'PH', 'ReporterPhone', 'N'),
    WaField(SWORD_MASTERID, 'MAID', 'MasterID', 'N'),
    WaField(SWORD_PTRREFNO1, 'OPRO', 'PtrRefNo1', 'N'),
    WaField(SWORD_BYPASSDATE, 'BYPD', 'BypassDate', 'N'),
    WaField(SWORD_RECOVERYTIME, 'BYPT', 'RecoveryTime', 'N'),
    WaField(SWORD_LASTMODIFYDATE, 'DATM', 'LastModifyDate', 'N'),
    WaField(SWORD_LASTMODIFYTIME, 'TIMM', 'LastModifyTime', 'N'),
    WaField(SWORD_LASTMODIFYUSER, 'USER', 'LastModifyUser', 'N'),
    WaField(SWORD_CLOSEDDATE, 'DATR', 'ClosedDate', 'N'),
    WaField(SWORD_CLOSEDTIME, 'TIMR', 'ClosedTime', 'N'),
    WaField(SWORD_HIDDENRECORD, '', 'HiddenRecord', 'N'),
    WaField(SWORD_OCCURRENCEDATE, 'DATO', 'OccurrenceDate', 'N'),
    WaField(SWORD_OCCURRENCETIME, 'TIMO', 'OccurrenceTime', 'N'),
    WaField(SWORD_SVAFFREQUIRED, 'SVCS', 'SvAffRequired', 'N'),
    WaField(SWORD_REVIEWDATE, 'DATT', 'ReviewDate', 'N'),
    WaField(SWORD_REVIEWTIME, 'TIMT', 'ReviewTime', 'N'),
    WaField(SWORD_ACKDATE, 'DACK', 'AckDate', 'N'),
    WaField(SWORD_ACKTIME, 'TACK', 'AckTime', 'N'),
    WaField(SWORD_REPLICATEDTOBA, 'BAID', 'ReplicatedToBA', 'N'),
    WaField(SWORD_REPLLICATEDTOQF, 'QFID', 'RepllicatedToQF', 'N'),
    WaField(SWORD_CAUSECI, 'CIX3', 'CauseCI', 'N'),
    WaField(SWORD_REJECTREASON, 'TPHW', 'RejectReason', 'N'),
    WaField(SWORD_COMMSSOFTWARE, 'TCSW', 'COMMSSoftware', 'N'),
    WaField(SWORD_NOTESLINK, '', 'NotesLink', 'N'),
    WaField(SWORD_KNOWLEDGEBASE, 'SOLC', 'KnowledgeBase', 'N'),
    WaField(SWORD_GLOBALOPSCAT1, 'IO1', 'GlobalOpsCat1', 'N'),
    WaField(SWORD_GLOBALOPSCAT2, 'IO2', 'GlobalOpsCat2', 'N'),
    WaField(SWORD_GLOBALOPSCAT3, 'IO3', 'GlobalOpsCat3', 'N'),
    WaField(SWORD_SLAID, 'SLAI', 'SLAID', 'N'),
    WaField(SWORD_SLAACCEPTDATE, 'SLD1', 'SLAAcceptDate', 'N'),
    WaField(SWORD_SLAACCEPTTIME, 'SLT1', 'SLAAcceptTime', 'N'),
    WaField(SWORD_SLARECOVERYDATE, 'SLD2', 'SLARecoveryDate', 'N'),
    WaField(SWORD_SLARECOVERYTIME, 'SLT2', 'SLARecoveryTime', 'N'),
    WaField(SWORD_SLAPENALTY, 'SLAP', 'SlaPenalty', 'N'),
    WaField(SWORD_LASTOKDATE, 'WOOD', 'LastOKDate', 'N'),
    WaField(SWORD_LASTOKTIME, 'TIDT', 'LastOKTime', 'N'),
    WaField(SWORD_IRCHILDINCIDENTEXISTS, '', 'IrChildIncidentExists', 'N'),
    WaField(SWORD_CIREFERENCEEN, 'CIX1', 'CIReferenceEn', 'N'),
    WaField(SWORD_LOCKDURATION, 'LKDU', 'LockDuration', 'N'),
    WaField(SWORD_CLOCKDURATION, 'CKDU', 'ClockDuration', 'N'),
    WaField(SWORD_SYMPTOM, 'SYMP', 'Symptom', 'N'),
    WaField(SWORD_LINK1PARTNERID, 'L1PD', 'Link1PartnerId', 'N'),
    WaField(SWORD_LINK1EXTERNALID, 'L1ED', 'Link1ExternalId', 'N'),
    WaField(SWORD_LINK1EXTERNALREF, 'L1RE', 'Link1ExternalRef', 'N'),
    WaField(SWORD_LINK2PARTNERID, 'L2PD', 'Link2PartnerId', 'N'),
    WaField(SWORD_LINK2EXTERNALID, 'L2ED', 'Link2ExternalId', 'N'),
    WaField(SWORD_LINK2EXTERNALREF, 'L2RE', 'Link2ExternalRef', 'N'),
    WaField(SWORD_LINK1EXTERNALNUMBER, 'L1EN', 'Link1ExternalNumber', 'N'),
    WaField(SWORD_LINK2EXTERNALNUMBER, 'L2EN', 'Link2ExternalNumber', 'N'),
    WaField(SWORD_HOTELCODE, 'HOCO', 'HotelCode', 'N'),
    WaField(SWORD_VENDORCATEGORY, 'VECA', 'VendorCategory', 'N'),
    WaField(SWORD_VENDOR, 'AVEN', 'Vendor', 'N'),
    WaField(SWORD_VENDORNAME, 'VENC', 'VendorName', 'N'),
    WaField(SWORD_VENDORPHONE, 'VENP', 'VendorPhone', 'N'),
    WaField(SWORD_VENDORREFERENCE, 'NUMV', 'VendorReference', 'N'),
    WaField(SWORD_AIRWCOMPLIANCE, 'CMPL', 'AirwCompliance', 'N'),
    WaField(SWORD_HIERESCALATION, 'HESC', 'HierEscalation', 'N'),
    WaField(SWORD_TOPXERRORCODE, 'ERCO', 'TopXErrorCode', 'N'),
    WaField(SWORD_TECHNICALISSUE, 'TECI', 'TechnicalIssue', 'N'),
    WaField(SWORD_ORIGINATORGROUPID, 'REPG', 'OriginatorGroupid', 'N'),
    WaField(SWORD_ORIGINATORUSERID, 'REPN', 'OriginatorUserid', 'N'),
    WaField(SWORD_ORIGINATORTELEPHONE, 'REPT', 'OriginatorTelephone', 'N'),
    WaField(SWORD_IMPACTSFLIGHTSAFETY, 'FSTY', 'ImpactsFlightSafety', 'N'),
    WaField(SWORD_CONFCALLNUMBER, '', 'ConfCallNumber', 'N'),
    WaField(SWORD_RESOLUTIONCAUSE, 'RECA', 'ResolutionCause', 'N'),
    WaField(SWORD_SOLVEDTIME, 'OCET', 'SolvedTime', 'N'),
    WaField(SWORD_SOLVEDDATE, 'OCED', 'SolvedDate', 'N'),
    WaField(SWORD_AREA, 'PRAR', 'Area', 'N'),
    WaField(SWORD_BAPMXRNID, 'EXID', 'BaPmxRnid', 'N'),
    WaField(SWORD_BACOUNTRY, '', 'BACountry', 'N'),
    WaField(SWORD_BALOCATION, '', 'BALocation', 'N'),
    WaField(SWORD_BALOCATIONDESC1, '', 'BALocationDesc1', 'N'),
    WaField(SWORD_BALOCATIONDESC2, '', 'BALocationDesc2', 'N'),
    WaField(SWORD_BALOCATIONDESC3, '', 'BALocationDesc3', 'N'),
    WaField(SWORD_BATICKETTYPE, 'TICK', 'BATicketType', 'N'),
    WaField(SWORD_BAEXTERNALID, 'EXID', 'BAExternalID', 'N'),
    WaField(SWORD_QFSEVERITY, 'QSEV', 'QFSeverity', 'N'),
    WaField(SWORD_QFCOVERAGEDATE, 'DAQF', 'QFCoverageDate', 'N'),
    WaField(SWORD_QFCOVERAGETIME, 'TIQF', 'QFCoverageTime', 'N'),
    WaField(SWORD_QFREFNO1, 'QFCH', 'QFRefNo1', 'N'),
    WaField(SWORD_QFREFNO2, 'QFCH', 'QFRefNo2', 'N'),
    WaField(SWORD_QFREFNO3, 'QFCH', 'QFRefNo3', 'N'),
    WaField(SWORD_QFREFNO4, 'QFCH', 'QFRefNo4', 'N'),
    WaField(SWORD_QFREFNO5, 'QFCH', 'QFRefNo5', 'N'),
    WaField(SWORD_QFREFNO6, 'QFCH', 'QFRefNo6', 'N'),
    WaField(SWORD_QFEXTERNALID, 'EXID', 'QFExternalID', 'N'),
    WaField(SWORD_QFFLIGHTDELAY, 'QFFD', 'QFFlightDelay', 'N'),
    WaField(SWORD_OWNEDBYQF, '', 'OwnedByQF', 'N'),
    WaField(SWORD_QFMAXIMORNID, 'QFMA', 'QfMaximoRnid', 'N'),
    WaField(SWORD_SIEBELROWID, 'SIID', 'SiebelRowID', 'N'),
    WaField(SWORD_SIEBELID, 'SIRO', 'SiebelID', 'N'),
    WaField(SWORD_GSSESCALATIONRANKING, 'GESR', 'GSSEscalationRanking', 'N'),
    WaField(SWORD_SIEBELCATA, 'SICA', 'SiebelCatA', 'N'),
    WaField(SWORD_SIEBELCATB, 'SICB', 'SiebelCatB', 'N'),
    WaField(SWORD_SIEBELCATC, 'SICC', 'SiebelCatC', 'N'),
    WaField(SWORD_SIEBELCATD, 'SICD', 'SiebelCatD', 'N'),
    WaField(SWORD_SIEBELCATE, 'SICE', 'SiebelCatE', 'N'),
    WaField(SWORD_COUNTRYCODE, 'UENT', 'CountryCode', 'N'),
    WaField(SWORD_OFFICEID, 'TOID', 'OfficeID', 'N'),
    WaField(SWORD_PRODPLANCATEGORY, 'PCAT', 'ProdPlanCategory', 'N'),
    WaField(SWORD_AMAPROVERSION2, 'TVER', 'AmaProVersion2', 'N'),
    WaField(SWORD_TERMINALADDRESS, '', 'TerminalAddress', 'N'),
    WaField(SWORD_OPERSYSTEMNAME, 'TOSY', 'OperSystemName', 'N'),
    WaField(SWORD_OPERSYSTEMVERSION, 'TOSV', 'OperSystemVersion', 'N'),
    WaField(SWORD_ATID, 'ATID', 'AtID', 'N'),
    WaField(SWORD_FIXEDINRELEASE, 'FIRE', 'FixedInRelease', 'N'),
    WaField(SWORD_FOCUS, 'FOCU', 'Focus', 'N'),
    WaField(SWORD_CAUSE, 'CAUS', 'Cause', 'N'),
    WaField(SWORD_USERREMARKS, 'UREM', 'UserRemarks', 'N'),
    WaField(SWORD_URLALF, '', 'UrlAlf', 'N'),
    WaField(SWORD_URLSENTINEL, '', 'UrlSentinel', 'N'),
    WaField(SWORD_IRLONELINK, '', 'IrlOneLink', 'N'),
    WaField(SWORD_TRACKERGROUP5, 'GROT', 'TrackerGroup5', 'N'),
    WaField(SWORD_LHPSCID, 'LHSX', 'LHPscID', 'N'),
    WaField(SWORD_PROJECT, 'PROJ', 'project', 'N'),
    WaField(SWORD_EXPLORERLANGUAGE, 'EXPL', 'ExplorerLanguage', 'N'),
    WaField(SWORD_EXPLORERSERVPACK, 'EXPS', 'ExplorerServPack', 'N'),
    WaField(SWORD_OSSERVICEPACK, 'OSSE', 'OSSErvicePack', 'N'),
    WaField(SWORD_LUFTHANSAID, 'LHID', 'LufthansaID', 'N'),
    WaField(SWORD_RATINGBYCUSTOMER, 'RBYC', 'RatingByCustomer', 'N'),
    WaField(SWORD_SEVERITYONEACK, 'SEAK', 'SeverityOneAck', 'N'),
    WaField(SWORD_SIEBELCOMPROWID, 'SICP', 'SiebelCompRowID', 'N'),
    WaField(SWORD_SIEBELCONTROWID, 'SICT', 'SiebelContRowID', 'N'),
    WaField(SWORD_ERRORMESSAGE, 'ERRM', 'ErrorMessage', 'N'),
    WaField(SWORD_KNOWLEDGEBASEURL, '', 'KnowledgeBaseUrl', 'N'),
    WaField(SWORD_LASTEVERBRIDGESENTDATE, '', 'LastEverbridgeSentDate', 'N'),
    WaField(SWORD_LASTEVERBRIDGESENTTIME, '', 'LastEverbridgeSentTime', 'N'),
    WaField(SWORD_AFFSERVICEFLIGHTDELC, 'DSAF', 'AffServiceFlightDelC', 'N'),
    WaField(SWORD_AFFSERVICEFLIGHTDELA, '', 'AffServiceFlightDelA', 'N'),
    WaField(SWORD_AFFSERVICELASTDATE, 'DSAF', 'AffServiceLastDate', 'N'),
    WaField(SWORD_AFFSERVICELASTTIME, 'TSAF', 'AffServiceLastTime', 'N'),
    WaField(SWORD_AFFSERVICELASTUSER, 'USAF', 'AffServiceLastUser', 'N'),
    WaField(SWORD_UPDATEDINBA, 'UFLG', 'UpdatedInBA', 'N'),
    WaField(SWORD_UPDATEDINQF, 'UFLG', 'UpdatedInQF', 'N'),
    WaField(SWORD_CLOSEDBY, 'CLNA', 'ClosedBy', 'N'),
    WaField(SWORD_SEVATFIRSTACKID, 'A1SE', 'SevAtFirstAckid', 'N'),
    WaField(SWORD_ACCESSEDDATE, 'DACC', 'AccessedDate', 'N'),
    WaField(SWORD_ACCESSEDTIME, 'TACC', 'AccessedTime', 'N'),
    WaField(SWORD_ACKDATE, 'DACK', 'AckDate', 'N'),
    WaField(SWORD_ACKTIME, 'TACK', 'AckTime', 'N'),
    WaField(SWORD_ACKDATEEXT, 'DAKK', 'AckDateExt', 'N'),
    WaField(SWORD_ACKTIMEEXT, 'TAKK', 'AckTimeExt', 'N'),
    WaField(SWORD_IWAVEERRORBA, 'ERRN', 'IwaveErrorBA', 'N'),
    WaField(SWORD_IWAVEERRORQF, 'ERRN', 'IwaveErrorQF', 'N'),
    WaField(SWORD_AIRFRANCEID, 'AFSX', 'AirFranceId', 'N'),
    WaField(SWORD_LHIMVIEWID, 'LHTR', 'LHIMViewID', 'N'),
    WaField(SWORD_MAXSEVERITY, 'MSEV', 'MaxSeverity', 'N'),
    WaField(SWORD_COMMUNITYACCESS, 'ASEC', 'CommunityAccess', 'N'),
    WaField(SWORD_COMMUNITYOWNER, 'OCOM', 'CommunityOwner', 'N'),
    WaField(SWORD_IMLASTUPDATE, '', 'IMLastUpdate', 'N'),
    WaField(SWORD_IMSERVICE, '', 'IMService', 'N'),
    WaField(SWORD_IMMARKETS, '', 'IMMarkets', 'N'),
    WaField(SWORD_IMSINCE, '', 'IMSince', 'N'),
    WaField(SWORD_IMCAUSE, '', 'IMCause', 'N'),
    WaField(SWORD_IMRECOVERY, '', 'IMRecovery', 'N'),
    WaField(SWORD_IMEMAIL, '', 'IMEmail', 'N'),
    WaField(SWORD_IMEXTERNALSTATUS, '', 'IMExternalStatus', 'N'),
    WaField(SWORD_IMUPGRADETIME, '', 'IMUpgradeTime', 'N'),
    WaField(SWORD_CUSTOMERNOTE, 'CUNO', 'CustomerNote', 'N'),
    WaField(SWORD_REPORTREQUESTED, 'FDRR', 'ReportRequested', 'N'),
    WaField(SWORD_REPORTFORAIRLINES, 'FDRL', 'ReportForAirlines', 'N'),
    WaField(SWORD_CIREFERENCEEN, 'CIX2', 'CIReferenceEn', 'N'),
    WaField(SWORD_SOLVERGROUP2, 'GROE', 'SolverGroup2', 'N'),
    WaField(SWORD_RECOVERYACTION, 'RATO', 'RecoveryAction', 'N'),
    WaField(SWORD_TRREFERENCE, 'CREC', 'TRReference', 'N'),
    WaField(SWORD_CRCPREFNO1, 'CREC', 'CrCpRefNo1', 'N'),
    WaField(SWORD_CRCPREFNO2, 'CREC', 'CrCpRefNo2', 'N'),
    WaField(SWORD_CAUSEDCR, 'CREC', 'CausedCR', 'N'),
    WaField(SWORD_CAUSEDWO, 'OWOK', 'CausedWO', 'N'),
    WaField(SWORD_LRREFERENCE, 'CREC', 'LRReference', 'N'),
    WaField(SWORD_OSLANGUAGE, 'OSSL', 'OSLanguage', 'N'),
    WaField(SWORD_SOLUTIONXREF, 'SOLX', 'SolutionXRef', 'N'),
    WaField(SWORD_PTRREFNO2, 'OPRO', 'PtrRefNo2', 'N'),
    WaField(SWORD_PTRREFNO3, 'OPRO', 'PtrRefNo3', 'N'),
    WaField(SWORD_WORKAROUNDAVAIL, 'WOAV', 'WorkAroundAvail', 'N'),
    WaField(SWORD_REOCCURANCE, 'REOC', 'ReOccurance', 'N'),
    WaField(SWORD_PTRREFNO4, 'OPRO', 'PtrRefNo4', 'N'),
    WaField(SWORD_CINOTFOUND, 'CINO', 'CiNotFound', 'N'),
    WaField(SWORD_CINOTFOUNDREASON, 'CINC', 'CiNotFoundReason', 'N'),
    WaField(SWORD_CINOTFOUNDLIST, 'DIAT', 'CiNotFoundList', 'N'),
    WaField(SWORD_CRIMPLEMENTATION, 'CRIM', 'CrImplementation', 'N'),
    WaField(SWORD_PTRREFNO0, 'OPRO', 'PtrRefNo0', 'N'),
    WaField(SWORD_LOCALMASTER, 'LMAS', 'LocalMaster', 'N'),
    WaField(SWORD_MARKEDASMIRDATE, 'MIRD', 'MarkedAsMIRDate', 'N'),
    WaField(SWORD_MARKEDASMIRTIME, 'MIRT', 'MarkedAsMIRTime', 'N'),
    WaField(SWORD_DIAGNOSEDDATE, '', 'DiagnosedDate', 'N'),
    WaField(SWORD_DIAGNOSEDTIME, 'CINL', 'DiagnosedTime', 'N'),
    WaField(SWORD_ENTEREDDATE, 'DATE', 'EnteredDate', 'N'),
    WaField(SWORD_ENTEREDTIME, 'TIME', 'EnteredTime', 'N'),
    WaField(SWORD_TEMPLATEID, 'TPID', 'TemplateID', 'N'),
    WaField(SWORD_QFLASTGROUP, '', 'QFLastGroup', 'N'),
    WaField(SWORD_QFLASTUSER, '', 'QFLastUser', 'N'),
    WaField(SWORD_QFLASTTEL, '', 'QFLastTel', 'N'),
    WaField(SWORD_AMAACKSEV, 'ACSE', 'AmaAckSev', 'N'),
    WaField(SWORD_IWAVEBAMODE, '', 'IWaveBAMode', 'N'),
    WaField(SWORD_BACATEGORY, '', 'BACategory', 'N'),
    WaField(SWORD_BASUBCATEGORY, '', 'BASubCategory', 'N'),
    WaField(SWORD_BAPRODUCT, '', 'BAProduct', 'N'),
    WaField(SWORD_BAPROBLEMTYPE, '', 'BAProblemType', 'N'),
    WaField(SWORD_QFMSSTATUS, '', 'QFMSStatus', 'N'),
    WaField(SWORD_CRISISACTIVATION, 'CRED', 'CrisisActivation', 'N'),
    WaField(SWORD_CRISISACTIVATION, 'CRET', 'CrisisActivation', 'N'),
    WaField(SWORD_IMSTART, 'IMSD', 'ImStart', 'N'),
    WaField(SWORD_IMSTART, 'IMSS', 'ImStart', 'N'),
    WaField(SWORD_REJECTDATE, 'REJD', 'RejectDate', 'N'),
    WaField(SWORD_REJECTDATE_2, 'REJT', 'RejectDate', 'N'),
    WaField(SWORD_DIAGNOSEDGROUPID, 'DIAG', 'DiagnosedGroupid', 'N'),
    WaField(SWORD_LOGGEDTOOL, 'CRTO', 'LoggedTool', 'N'),
    WaField(SWORD_RECTYPEID, '', 'RecTypeId', 'N'),
    WaField(SWORD_SERVMANINVOLVEDDATE, 'DATS', 'ServManInvolvedDate', 'N'),
    WaField(SWORD_SERVMANINVOLVEDTIME, 'TIMS', 'ServManInvolvedTime', 'N'),
    WaField(SWORD_CREATEDBYTOOL, 'UPTO', 'CreatedByTool', 'N'),
    WaField(SWORD_LOGGERUSERID, 'LOID', 'LoggerUserid', 'N'),
    WaField(SWORD_ACKSMCGROUP, 'GACC', 'AckSMCGroup', 'N'),
    WaField(SWORD_ACKSMCUSER, 'UACC', 'AckSMCUser', 'N'),
    WaField(SWORD_MAXSEVSETDATE, 'MSSD', 'MaxSevSetDate', 'N'),
    WaField(SWORD_MAXSEVSETTIME, 'MSST', 'MaxSevSetTime', 'N'),
    WaField(SWORD_SERVICEIMPACTINDEX, 'ISIV', 'ServiceImpactIndex', 'N'),
    WaField(SWORD_SEV1SETDATE, '', 'Sev1SetDate', 'N'),
    WaField(SWORD_SEV2SETDATE, '', 'Sev2SetDate', 'N'),
    WaField(SWORD_SEV3SETDATE, '', 'Sev3SetDate', 'N'),
    WaField(SWORD_SEV4SETDATE, '', 'Sev4SetDate', 'N'),
    WaField(SWORD_SOAINVOLVEDDATE, 'SOAD', 'SOAInvolvedDate', 'N'),
    WaField(SWORD_SOAINVOLVEDTIME, 'SOAT', 'SOAInvolvedTime', 'N'),
    WaField(SWORD_PTRIRREFERENCE, 'CREC', 'PTRIRReference', 'N'),
    WaField(SWORD_CHASEUPGROUPS, '', 'ChaseUpGroups', 'N'),
    WaField(SWORD_CLAIMPROVIDERCODE, 'CLPC', 'ClaimProviderCode', 'N'),
    WaField(SWORD_CLAIMAMOUNTREQ, 'CLAR', 'ClaimAmountReq', 'N'),
    WaField(SWORD_CLAIMAMOUNTREFUND, 'CLAF', 'ClaimAmountRefund', 'N'),
    WaField(SWORD_CLAIMRESPONSIBLE, 'CLRE', 'ClaimResponsible', 'N'),
    WaField(SWORD_CLAIMREASON, 'CLRS', 'ClaimReason', 'N'),
    WaField(SWORD_IWAVEBACLOSUREFLAG, 'CLOS', 'IWaveBAClosureFlag', 'N'),
    WaField(SWORD_ADMSOURCE, 'ADMS', 'AdmSource', 'N'),
    WaField(SWORD_PAYMENTAPPROVED, 'CLMP', 'PaymentApproved', 'N'),
    WaField(SWORD_CAUSEDCR, 'CREC', 'CausedCR', 'N'),
    WaField(SWORD_HIERESCALATION, 'HESC', 'HierEscalation', 'N'),
    WaField(SWORD_MIRDETECTEDBY, 'DETB', 'MIRDetectedBy', 'N'),
    WaField(SWORD_PARALLELINVESTOPEN, '', 'ParallelInvestOpen', 'N'),
    WaField(SWORD_FIRSTCIRAUTOMATIONDATE, 'DTAD', 'FirstCIRAutomationDate', 'N'),
    WaField(SWORD_FIRSTCIRAUTOMATIONTIME, 'DTAT', 'FirstCIRAutomationTime', 'N'),
    WaField(SWORD_FIRSTCIRCUSTOMERDATE, 'DTCD', 'FirstCIRCustomerDate', 'N'),
    WaField(SWORD_FIRSTCIRCUSTOMERTIME, 'DTCT', 'FirstCIRCustomerTime', 'N'),
    WaField(SWORD_FIRSTCIRAMADEUSDATE, 'DT1D', 'FirstCIRAmadeusDate', 'N'),
    WaField(SWORD_FIRSTCIRAMADEUSTIME, 'DT1T', 'FirstCIRAmadeusTime', 'N'),
    WaField(SWORD_ORANGECRISISTRIGGERED, '', 'OrangeCrisisTriggered', 'N'),
    WaField(SWORD_IRPRIORITY, 'IPRO', 'IRPriority', 'N'),
    WaField(SWORD_IRPRIORITYACCEPTDATE, 'IPDT', 'IRPriorityAcceptDate', 'N'),
    WaField(SWORD_IRPRIORITYACCEPTTIME, 'IPTI', 'IRPriorityAcceptTime', 'N'),
    WaField(SWORD_TARGETDATE, 'DAIP', 'TargetDate', 'N'),
    WaField(SWORD_TARGETTIME, 'DLTI', 'TargetTime', 'N'),
    WaField(SWORD_USAGE, 'PUSE', 'Usage', 'N'),
    WaField(SWORD_PRIOSEV1, '', 'PrioSev1', 'N'),
    WaField(SWORD_PRIOSEV2U, '', 'PrioSev2U', 'N'),
    WaField(SWORD_PRIOSEV2, '', 'PrioSev2', 'N'),
    WaField(SWORD_PRIOSEV3U, '', 'PrioSev3U', 'N'),
    WaField(SWORD_PRIOSEV3, '', 'PrioSev3', 'N'),
    WaField(SWORD_PRIOSEV4U, '', 'PrioSev4U', 'N'),
    WaField(SWORD_PRIOSEV4, '', 'PrioSev4', 'N'),
    WaField(SWORD_RECOVDATEINT, '', 'RecovDateInt', 'N'),
    WaField(SWORD_RECOVDATEINT, '', 'RecovDateInt', 'N'),
    WaField(SWORD_NRCOMMONCIS, '', 'NrCommonCis', 'N'),
    WaField(SWORD_TAGCI1, '', 'TagCI1', 'N'),
    WaField(SWORD_TAGCI2, '', 'TagCI2', 'N'),
    WaField(SWORD_TAGCI3, '', 'TagCI3', 'N'),
    WaField(SWORD_TAGCI4, '', 'TagCI4', 'N'),
    WaField(SWORD_TAGMORECOMMON_CIS, '', 'TagMoreCommon CIs', 'N'),
    WaField(SWORD_TAGALLCIS, '', 'TagAllCIs', 'N'),
    WaField(SWORD_FOUNDCIS, '', 'FoundCIs', 'N'),
    WaField(SWORD_RELATEDBYTAG, '', 'RelatedbyTag', 'N'),
    WaField(SWORD_TAGLIMIT, '', 'TagLimit', 'N'),
    WaField(SWORD_TAGOFFSET, '', 'TagOffset', 'N'),
    WaField(SWORD_TAGRECORDTYPES, '', 'TagRecordTypes', 'N'),
    WaField(SWORD_TAGSTARTTIME, '', 'TagStartTime', 'N'),
    WaField(SWORD_TAGSTARTTIMEUNIT, '', 'TagStartTimeUnit', 'N'),
    WaField(SWORD_TAGENDTIME, '', 'TagEndTime', 'N'),
    WaField(SWORD_TAGENDTIMEUNIT, '', 'TagEndTimeUnit', 'N'),
    WaField(SWORD_TAGSTARTDATEABS, '', 'TagStartDateAbs', 'N'),
    WaField(SWORD_TAGSTARTTIMEABS, '', 'TagStartTimeAbs', 'N'),
    WaField(SWORD_TAGENDDATEABS, '', 'TagEndDateAbs', 'N'),
    WaField(SWORD_TAGENDTIMEABS, '', 'TagEndTimeAbs', 'N'),
    WaField(SWORD_TAGTIMEMODE, '', 'TagTimeMode', 'N'),
    WaField(SWORD_TAGSTARTTIMEREL, '', 'TagStartTimeRel', 'N'),
    WaField(SWORD_TAGSTARTTIMEUNITREL, '', 'TagStartTimeUnitRel', 'N'),
    WaField(SWORD_TAGENDTIMEREL, '', 'TagEndTimeRel', 'N'),
    WaField(SWORD_TAGENDTIMEUNITREL, '', 'TagEndTimeUnitRel', 'N'),
    WaField(SWORD_DISPATCHGROUPCODE, '', 'DispatchGroupCode', 'N'),
    WaField(SWORD_DISPATCHGROUPNAME, '', 'DispatchGroupName', 'N'),
    WaField(SWORD_DISPATCHRELEVANCE, '', 'DispatchRelevance', 'N'),
    WaField(SWORD_PMRSEACHFOR, '', 'PMRSeachFor', 'N'),
    WaField(SWORD_PMRID, '', 'PMRId', 'N'),
    WaField(SWORD_PMRSEACHIN, '', 'PMRSeachIn', 'N'),
    WaField(SWORD_RELATEDPMRS, '', 'RelatedPMRs', 'N'),
    WaField(SWORD_TREXIST, 'TREX', 'TRExist', 'N'),
    WaField(SWORD_NOTENGINE_URL, '', 'NotEngine URL', 'N'),
    WaField(SWORD_NOTIFICATION_SENT, '', 'Notification Sent', 'N'),
    WaField(SWORD_CIR_1STG_SERVICE, '', 'CIR 1stg Service', 'N'),
]
IncidentRecordFft = [
    WaFft(SWORD_HIDDENDUMMYIR, '', 'HiddenDummyIR', 'N'),
    WaFft(SWORD_DESCRIPTION, '', 'Description', 'Y'),
    WaFft(SWORD_STATUSTEXT, '', 'StatusText', 'N'),
    WaFft(SWORD_DUMMYFIELDFORIWAVETOQF, '', 'DummyFieldForIwaveToQF', 'N'),
    WaFft(SWORD_LOADINFO, '', 'LoadInfo', 'N'),
    WaFft(SWORD_FULLEXECSUMMARY, '', 'FullExecSummary', 'N'),
    WaFft(SWORD_EXECUTIVESUMMARY, '', 'ExecutiveSummary', 'N'),
    WaFft(SWORD_FLIGHTDELAY, '', 'FlightDelay', 'N'),
    WaFft(SWORD_IM_STATUS, '', 'IM Status', 'N'),
    WaFft(SWORD_CUSTOMERINFO, '', 'CustomerInfo', 'N'),
    WaFft(SWORD_PREVSTATUSMAIL, '', 'PrevStatusMail', 'N'),
    WaFft(SWORD_RESOLUTION, '', 'Resolution', 'N'),
    WaFft(SWORD_CHASEUPTEXT, '', 'ChaseUpText', 'N'),
]


class IncidentRecord:
    def __init__(self):
        self.IncidentRecordMap = {
            f.sword: f for f in IncidentRecordFields
        }
        self.IncidentRecordListMap = {
            f.sword: f for f in IncidentRecordFft
        }
        self.id = ''

    def parseXml(self, xmlstr):
        dom = parseString(xmlstr)
        tags = dom.getElementsByTagName('field')
        for tag in tags:
            sword = tag.attributes['sword'].value
            value = tag.firstChild.nodeValue
            self.IncidentRecordMap[sword].set(value)
        ffts = dom.getElementsByTagName('fft')
        for fft in ffts:
            sword = fft.attributes['sword'].value
            # if sword == SWORD_OVERVIEW:
            for lines in fft.childNodes:
                for node in lines.childNodes:
                    if node.nodeType == node.TEXT_NODE:
                        self.IncidentRecordListMap[sword].add(node.data)

    def __str__(self):
        doc = impl.createDocument(None, 'wa-records', None)
        warecord = doc.documentElement
        record = doc.createElement('record')
        warecord.appendChild(record)
        record.setAttribute('type', 'IR')
        record.setAttribute('database', 'prd')
        if self.id:
            record.setAttribute('id', self.id)
        for field in self.IncidentRecordMap:
            if self.IncidentRecordMap[field].isValueSet():
                sword = self.IncidentRecordMap[field].sword
                name = self.IncidentRecordMap[field].name
                valueStr = self.IncidentRecordMap[field].value
                field = doc.createElement('field')
                value = doc.createTextNode(valueStr)
                field.appendChild(value)
                field.setAttribute('sword', sword)
                field.setAttribute('name', name)
                record.appendChild(field)
            elif self.IncidentRecordMap[field].mandatory:
                raise ValueError("This field is mandatory: " + self.IncidentRecordMap[field].name + " sword: " +
                                 self.IncidentRecordMap[field].sword)
        for field in self.IncidentRecordListMap:
            sword = self.IncidentRecordListMap[field].sword
            name = self.IncidentRecordListMap[field].name
            fft = doc.createElement('fft')
            fft.setAttribute('sword', sword)
            fft.setAttribute('name', name)
            for lineStr in self.IncidentRecordListMap[field].lines:
                line = doc.createElement('line')
                line.appendChild(doc.createTextNode(lineStr))
                fft.appendChild(line)
            record.appendChild(fft)
        return doc.toprettyxml()

    def hiddenDummyIR(self, value):
        self.IncidentRecordListMap[SWORD_HIDDENDUMMYIR].add(value)
        return self

    def getHiddenDummyIRs(self):
        return self.IncidentRecordListMap[SWORD_HIDDENDUMMYIR].getValues()

    def getHiddenDummyIRAt(self, index):
        return self.IncidentRecordListMap[SWORD_HIDDENDUMMYIR].getValue(index)

    def title(self, value):
        self.IncidentRecordMap[SWORD_TITLE].set(value)
        return self

    def getTitle(self):
        return self.IncidentRecordMap[SWORD_TITLE].getValue()

    def description(self, value):
        self.IncidentRecordListMap[SWORD_DESCRIPTION].add(value)
        return self

    def getDescriptions(self):
        return self.IncidentRecordListMap[SWORD_DESCRIPTION].getValues()

    def getDescriptionAt(self, index):
        return self.IncidentRecordListMap[SWORD_DESCRIPTION].getValue(index)

    def statusText(self, value):
        self.IncidentRecordListMap[SWORD_STATUSTEXT].add(value)
        return self

    def getStatusTexts(self):
        return self.IncidentRecordListMap[SWORD_STATUSTEXT].getValues()

    def getStatusTextAt(self, index):
        return self.IncidentRecordListMap[SWORD_STATUSTEXT].getValue(index)

    def assigneeGroup(self, value):
        self.IncidentRecordMap[SWORD_ASSIGNEEGROUP].set(value)
        return self

    def getAssigneeGroup(self):
        return self.IncidentRecordMap[SWORD_ASSIGNEEGROUP].getValue()

    def assigneeName(self, value):
        self.IncidentRecordMap[SWORD_ASSIGNEENAME].set(value)
        return self

    def getAssigneeName(self):
        return self.IncidentRecordMap[SWORD_ASSIGNEENAME].getValue()

    def assigneePhone(self, value):
        self.IncidentRecordMap[SWORD_ASSIGNEEPHONE].set(value)
        return self

    def getAssigneePhone(self):
        return self.IncidentRecordMap[SWORD_ASSIGNEEPHONE].getValue()

    def recordID(self, value):
        self.IncidentRecordMap[SWORD_RECORDID].set(value)
        self.id = value
        return self

    def getRecordID(self):
        return self.IncidentRecordMap[SWORD_RECORDID].getValue()

    def setType(self, value):
        self.IncidentRecordMap[SWORD_TYPE].set(value)
        return self

    def getType(self):
        return self.IncidentRecordMap[SWORD_TYPE].getValue()

    def component(self, value):
        self.IncidentRecordMap[SWORD_COMPONENT].set(value)
        return self

    def getComponent(self):
        return self.IncidentRecordMap[SWORD_COMPONENT].getValue()

    def subcomponent(self, value):
        self.IncidentRecordMap[SWORD_SUBCOMPONENT].set(value)
        return self

    def getSubcomponent(self):
        return self.IncidentRecordMap[SWORD_SUBCOMPONENT].getValue()

    def severity(self, value):
        self.IncidentRecordMap[SWORD_SEVERITY].set(value)
        return self

    def getSeverity(self):
        return self.IncidentRecordMap[SWORD_SEVERITY].getValue()

    def status(self, value):
        self.IncidentRecordMap[SWORD_STATUS].set(value)
        return self

    def getStatus(self):
        return self.IncidentRecordMap[SWORD_STATUS].getValue()

    def urgencyCode(self, value):
        self.IncidentRecordMap[SWORD_URGENCYCODE].set(value)
        return self

    def getUrgencyCode(self):
        return self.IncidentRecordMap[SWORD_URGENCYCODE].getValue()

    def classEntered(self, value):
        self.IncidentRecordMap[SWORD_CLASSENTERED].set(value)
        return self

    def getClassEntered(self):
        return self.IncidentRecordMap[SWORD_CLASSENTERED].getValue()

    def externalCreation(self, value):
        self.IncidentRecordMap[SWORD_EXTERNALCREATION].set(value)
        return self

    def getExternalCreation(self):
        return self.IncidentRecordMap[SWORD_EXTERNALCREATION].getValue()

    def masterRecord(self, value):
        self.IncidentRecordMap[SWORD_MASTERRECORD].set(value)
        return self

    def getMasterRecord(self):
        return self.IncidentRecordMap[SWORD_MASTERRECORD].getValue()

    def asysCategory(self, value):
        self.IncidentRecordMap[SWORD_ASYSCATEGORY].set(value)
        return self

    def getAsysCategory(self):
        return self.IncidentRecordMap[SWORD_ASYSCATEGORY].getValue()

    def system(self, value):
        self.IncidentRecordMap[SWORD_SYSTEM].set(value)
        return self

    def getSystem(self):
        return self.IncidentRecordMap[SWORD_SYSTEM].getValue()

    def responsibleGroup(self, value):
        self.IncidentRecordMap[SWORD_RESPONSIBLEGROUP].set(value)
        return self

    def getResponsibleGroup(self):
        return self.IncidentRecordMap[SWORD_RESPONSIBLEGROUP].getValue()

    def responsibleName(self, value):
        self.IncidentRecordMap[SWORD_RESPONSIBLENAME].set(value)
        return self

    def getResponsibleName(self):
        return self.IncidentRecordMap[SWORD_RESPONSIBLENAME].getValue()

    def responsiblePhone(self, value):
        self.IncidentRecordMap[SWORD_RESPONSIBLEPHONE].set(value)
        return self

    def getResponsiblePhone(self):
        return self.IncidentRecordMap[SWORD_RESPONSIBLEPHONE].getValue()

    def service(self, value):
        self.IncidentRecordMap[SWORD_SERVICE].set(value)
        return self

    def getService(self):
        return self.IncidentRecordMap[SWORD_SERVICE].getValue()

    def serviceCategory(self, value):
        self.IncidentRecordMap[SWORD_SERVICECATEGORY].set(value)
        return self

    def getServiceCategory(self):
        return self.IncidentRecordMap[SWORD_SERVICECATEGORY].getValue()

    def subStatus(self, value):
        self.IncidentRecordMap[SWORD_SUBSTATUS].set(value)
        return self

    def getSubStatus(self):
        return self.IncidentRecordMap[SWORD_SUBSTATUS].getValue()

    def ownerGroup(self, value):
        self.IncidentRecordMap[SWORD_OWNERGROUP].set(value)
        return self

    def getOwnerGroup(self):
        return self.IncidentRecordMap[SWORD_OWNERGROUP].getValue()

    def onwerName(self, value):
        self.IncidentRecordMap[SWORD_ONWERNAME].set(value)
        return self

    def getOnwerName(self):
        return self.IncidentRecordMap[SWORD_ONWERNAME].getValue()

    def ownerPhone(self, value):
        self.IncidentRecordMap[SWORD_OWNERPHONE].set(value)
        return self

    def getOwnerPhone(self):
        return self.IncidentRecordMap[SWORD_OWNERPHONE].getValue()

    def wishDate(self, value):
        self.IncidentRecordMap[SWORD_WISHDATE].set(value)
        return self

    def getWishDate(self):
        return self.IncidentRecordMap[SWORD_WISHDATE].getValue()

    def wishDate(self, value):
        self.IncidentRecordMap[SWORD_WISHDATE].set(value)
        return self

    def getWishDate(self):
        return self.IncidentRecordMap[SWORD_WISHDATE].getValue()

    def dummyFieldForIwaveToQF(self, value):
        self.IncidentRecordListMap[SWORD_DUMMYFIELDFORIWAVETOQF].add(value)
        return self

    def getDummyFieldForIwaveToQFs(self):
        return self.IncidentRecordListMap[SWORD_DUMMYFIELDFORIWAVETOQF].getValues()

    def getDummyFieldForIwaveToQFAt(self, index):
        return self.IncidentRecordListMap[SWORD_DUMMYFIELDFORIWAVETOQF].getValue(index)

    def OwnerCat(self, value):
        self.IncidentRecordMap[SWORD_OWNER_CAT].set(value)
        return self

    def getOwnerCat(self):
        return self.IncidentRecordMap[SWORD_OWNER_CAT].getValue()

    def detectionDate(self, value):
        self.IncidentRecordMap[SWORD_DETECTIONDATE].set(value)
        return self

    def getDetectionDate(self):
        return self.IncidentRecordMap[SWORD_DETECTIONDATE].getValue()

    def detectionTime(self, value):
        self.IncidentRecordMap[SWORD_DETECTIONTIME].set(value)
        return self

    def getDetectionTime(self):
        return self.IncidentRecordMap[SWORD_DETECTIONTIME].getValue()

    def loadedDate(self, value):
        self.IncidentRecordMap[SWORD_LOADEDDATE].set(value)
        return self

    def getLoadedDate(self):
        return self.IncidentRecordMap[SWORD_LOADEDDATE].getValue()

    def loadedTime(self, value):
        self.IncidentRecordMap[SWORD_LOADEDTIME].set(value)
        return self

    def getLoadedTime(self):
        return self.IncidentRecordMap[SWORD_LOADEDTIME].getValue()

    def SELECT_OWNER_GROUP_Prd(self, value):
        self.IncidentRecordMap[SWORD_SELECT_OWNER_GROUP_PRD].set(value)
        return self

    def getSELECT_OWNER_GROUP_Prd(self):
        return self.IncidentRecordMap[SWORD_SELECT_OWNER_GROUP_PRD].getValue()

    def SELECT_OWNER_GROUP_Tst(self, value):
        self.IncidentRecordMap[SWORD_SELECT_OWNER_GROUP_TST].set(value)
        return self

    def getSELECT_OWNER_GROUP_Tst(self):
        return self.IncidentRecordMap[SWORD_SELECT_OWNER_GROUP_TST].getValue()

    def plannedLoadDate(self, value):
        self.IncidentRecordMap[SWORD_PLANNEDLOADDATE].set(value)
        return self

    def getPlannedLoadDate(self):
        return self.IncidentRecordMap[SWORD_PLANNEDLOADDATE].getValue()

    def plannedLoadTime(self, value):
        self.IncidentRecordMap[SWORD_PLANNEDLOADTIME].set(value)
        return self

    def getPlannedLoadTime(self):
        return self.IncidentRecordMap[SWORD_PLANNEDLOADTIME].getValue()

    def accountId(self, value):
        self.IncidentRecordMap[SWORD_ACCOUNTID].set(value)
        return self

    def getAccountId(self):
        return self.IncidentRecordMap[SWORD_ACCOUNTID].getValue()

    def loggerGroup(self, value):
        self.IncidentRecordMap[SWORD_LOGGERGROUP].set(value)
        return self

    def getLoggerGroup(self):
        return self.IncidentRecordMap[SWORD_LOGGERGROUP].getValue()

    def loggerName(self, value):
        self.IncidentRecordMap[SWORD_LOGGERNAME].set(value)
        return self

    def getLoggerName(self):
        return self.IncidentRecordMap[SWORD_LOGGERNAME].getValue()

    def loggerPhone(self, value):
        self.IncidentRecordMap[SWORD_LOGGERPHONE].set(value)
        return self

    def getLoggerPhone(self):
        return self.IncidentRecordMap[SWORD_LOGGERPHONE].getValue()

    def location(self, value):
        self.IncidentRecordMap[SWORD_LOCATION].set(value)
        return self

    def getLocation(self):
        return self.IncidentRecordMap[SWORD_LOCATION].getValue()

    def contactID(self, value):
        self.IncidentRecordMap[SWORD_CONTACTID].set(value)
        return self

    def getContactID(self):
        return self.IncidentRecordMap[SWORD_CONTACTID].getValue()

    def reporterGroup(self, value):
        self.IncidentRecordMap[SWORD_REPORTERGROUP].set(value)
        return self

    def getReporterGroup(self):
        return self.IncidentRecordMap[SWORD_REPORTERGROUP].getValue()

    def reporterName(self, value):
        self.IncidentRecordMap[SWORD_REPORTERNAME].set(value)
        return self

    def getReporterName(self):
        return self.IncidentRecordMap[SWORD_REPORTERNAME].getValue()

    def reporterPhone(self, value):
        self.IncidentRecordMap[SWORD_REPORTERPHONE].set(value)
        return self

    def getReporterPhone(self):
        return self.IncidentRecordMap[SWORD_REPORTERPHONE].getValue()

    def masterID(self, value):
        self.IncidentRecordMap[SWORD_MASTERID].set(value)
        return self

    def getMasterID(self):
        return self.IncidentRecordMap[SWORD_MASTERID].getValue()

    def ptrRefNo1(self, value):
        self.IncidentRecordMap[SWORD_PTRREFNO1].set(value)
        return self

    def getPtrRefNo1(self):
        return self.IncidentRecordMap[SWORD_PTRREFNO1].getValue()

    def bypassDate(self, value):
        self.IncidentRecordMap[SWORD_BYPASSDATE].set(value)
        return self

    def getBypassDate(self):
        return self.IncidentRecordMap[SWORD_BYPASSDATE].getValue()

    def recoveryTime(self, value):
        self.IncidentRecordMap[SWORD_RECOVERYTIME].set(value)
        return self

    def getRecoveryTime(self):
        return self.IncidentRecordMap[SWORD_RECOVERYTIME].getValue()

    def lastModifyDate(self, value):
        self.IncidentRecordMap[SWORD_LASTMODIFYDATE].set(value)
        return self

    def getLastModifyDate(self):
        return self.IncidentRecordMap[SWORD_LASTMODIFYDATE].getValue()

    def lastModifyTime(self, value):
        self.IncidentRecordMap[SWORD_LASTMODIFYTIME].set(value)
        return self

    def getLastModifyTime(self):
        return self.IncidentRecordMap[SWORD_LASTMODIFYTIME].getValue()

    def lastModifyUser(self, value):
        self.IncidentRecordMap[SWORD_LASTMODIFYUSER].set(value)
        return self

    def getLastModifyUser(self):
        return self.IncidentRecordMap[SWORD_LASTMODIFYUSER].getValue()

    def closedDate(self, value):
        self.IncidentRecordMap[SWORD_CLOSEDDATE].set(value)
        return self

    def getClosedDate(self):
        return self.IncidentRecordMap[SWORD_CLOSEDDATE].getValue()

    def closedTime(self, value):
        self.IncidentRecordMap[SWORD_CLOSEDTIME].set(value)
        return self

    def getClosedTime(self):
        return self.IncidentRecordMap[SWORD_CLOSEDTIME].getValue()

    def hiddenRecord(self, value):
        self.IncidentRecordMap[SWORD_HIDDENRECORD].set(value)
        return self

    def getHiddenRecord(self):
        return self.IncidentRecordMap[SWORD_HIDDENRECORD].getValue()

    def occurrenceDate(self, value):
        self.IncidentRecordMap[SWORD_OCCURRENCEDATE].set(value)
        return self

    def getOccurrenceDate(self):
        return self.IncidentRecordMap[SWORD_OCCURRENCEDATE].getValue()

    def occurrenceTime(self, value):
        self.IncidentRecordMap[SWORD_OCCURRENCETIME].set(value)
        return self

    def getOccurrenceTime(self):
        return self.IncidentRecordMap[SWORD_OCCURRENCETIME].getValue()

    def svAffRequired(self, value):
        self.IncidentRecordMap[SWORD_SVAFFREQUIRED].set(value)
        return self

    def getSvAffRequired(self):
        return self.IncidentRecordMap[SWORD_SVAFFREQUIRED].getValue()

    def reviewDate(self, value):
        self.IncidentRecordMap[SWORD_REVIEWDATE].set(value)
        return self

    def getReviewDate(self):
        return self.IncidentRecordMap[SWORD_REVIEWDATE].getValue()

    def reviewTime(self, value):
        self.IncidentRecordMap[SWORD_REVIEWTIME].set(value)
        return self

    def getReviewTime(self):
        return self.IncidentRecordMap[SWORD_REVIEWTIME].getValue()

    def ackDate(self, value):
        self.IncidentRecordMap[SWORD_ACKDATE].set(value)
        return self

    def getAckDate(self):
        return self.IncidentRecordMap[SWORD_ACKDATE].getValue()

    def ackTime(self, value):
        self.IncidentRecordMap[SWORD_ACKTIME].set(value)
        return self

    def getAckTime(self):
        return self.IncidentRecordMap[SWORD_ACKTIME].getValue()

    def replicatedToBA(self, value):
        self.IncidentRecordMap[SWORD_REPLICATEDTOBA].set(value)
        return self

    def getReplicatedToBA(self):
        return self.IncidentRecordMap[SWORD_REPLICATEDTOBA].getValue()

    def repllicatedToQF(self, value):
        self.IncidentRecordMap[SWORD_REPLLICATEDTOQF].set(value)
        return self

    def getRepllicatedToQF(self):
        return self.IncidentRecordMap[SWORD_REPLLICATEDTOQF].getValue()

    def causeCI(self, value):
        self.IncidentRecordMap[SWORD_CAUSECI].set(value)
        return self

    def getCauseCI(self):
        return self.IncidentRecordMap[SWORD_CAUSECI].getValue()

    def rejectReason(self, value):
        self.IncidentRecordMap[SWORD_REJECTREASON].set(value)
        return self

    def getRejectReason(self):
        return self.IncidentRecordMap[SWORD_REJECTREASON].getValue()

    def cOMMSSoftware(self, value):
        self.IncidentRecordMap[SWORD_COMMSSOFTWARE].set(value)
        return self

    def getCOMMSSoftware(self):
        return self.IncidentRecordMap[SWORD_COMMSSOFTWARE].getValue()

    def notesLink(self, value):
        self.IncidentRecordMap[SWORD_NOTESLINK].set(value)
        return self

    def getNotesLink(self):
        return self.IncidentRecordMap[SWORD_NOTESLINK].getValue()

    def knowledgeBase(self, value):
        self.IncidentRecordMap[SWORD_KNOWLEDGEBASE].set(value)
        return self

    def getKnowledgeBase(self):
        return self.IncidentRecordMap[SWORD_KNOWLEDGEBASE].getValue()

    def globalOpsCat1(self, value):
        self.IncidentRecordMap[SWORD_GLOBALOPSCAT1].set(value)
        return self

    def getGlobalOpsCat1(self):
        return self.IncidentRecordMap[SWORD_GLOBALOPSCAT1].getValue()

    def globalOpsCat2(self, value):
        self.IncidentRecordMap[SWORD_GLOBALOPSCAT2].set(value)
        return self

    def getGlobalOpsCat2(self):
        return self.IncidentRecordMap[SWORD_GLOBALOPSCAT2].getValue()

    def globalOpsCat3(self, value):
        self.IncidentRecordMap[SWORD_GLOBALOPSCAT3].set(value)
        return self

    def getGlobalOpsCat3(self):
        return self.IncidentRecordMap[SWORD_GLOBALOPSCAT3].getValue()

    def sLAID(self, value):
        self.IncidentRecordMap[SWORD_SLAID].set(value)
        return self

    def getSLAID(self):
        return self.IncidentRecordMap[SWORD_SLAID].getValue()

    def sLAAcceptDate(self, value):
        self.IncidentRecordMap[SWORD_SLAACCEPTDATE].set(value)
        return self

    def getSLAAcceptDate(self):
        return self.IncidentRecordMap[SWORD_SLAACCEPTDATE].getValue()

    def sLAAcceptTime(self, value):
        self.IncidentRecordMap[SWORD_SLAACCEPTTIME].set(value)
        return self

    def getSLAAcceptTime(self):
        return self.IncidentRecordMap[SWORD_SLAACCEPTTIME].getValue()

    def sLARecoveryDate(self, value):
        self.IncidentRecordMap[SWORD_SLARECOVERYDATE].set(value)
        return self

    def getSLARecoveryDate(self):
        return self.IncidentRecordMap[SWORD_SLARECOVERYDATE].getValue()

    def sLARecoveryTime(self, value):
        self.IncidentRecordMap[SWORD_SLARECOVERYTIME].set(value)
        return self

    def getSLARecoveryTime(self):
        return self.IncidentRecordMap[SWORD_SLARECOVERYTIME].getValue()

    def slaPenalty(self, value):
        self.IncidentRecordMap[SWORD_SLAPENALTY].set(value)
        return self

    def getSlaPenalty(self):
        return self.IncidentRecordMap[SWORD_SLAPENALTY].getValue()

    def lastOKDate(self, value):
        self.IncidentRecordMap[SWORD_LASTOKDATE].set(value)
        return self

    def getLastOKDate(self):
        return self.IncidentRecordMap[SWORD_LASTOKDATE].getValue()

    def lastOKTime(self, value):
        self.IncidentRecordMap[SWORD_LASTOKTIME].set(value)
        return self

    def getLastOKTime(self):
        return self.IncidentRecordMap[SWORD_LASTOKTIME].getValue()

    def irChildIncidentExists(self, value):
        self.IncidentRecordMap[SWORD_IRCHILDINCIDENTEXISTS].set(value)
        return self

    def getIrChildIncidentExists(self):
        return self.IncidentRecordMap[SWORD_IRCHILDINCIDENTEXISTS].getValue()

    def cIReferenceEn(self, value):
        self.IncidentRecordMap[SWORD_CIREFERENCEEN].set(value)
        return self

    def getCIReferenceEn(self):
        return self.IncidentRecordMap[SWORD_CIREFERENCEEN].getValue()

    def lockDuration(self, value):
        self.IncidentRecordMap[SWORD_LOCKDURATION].set(value)
        return self

    def getLockDuration(self):
        return self.IncidentRecordMap[SWORD_LOCKDURATION].getValue()

    def clockDuration(self, value):
        self.IncidentRecordMap[SWORD_CLOCKDURATION].set(value)
        return self

    def getClockDuration(self):
        return self.IncidentRecordMap[SWORD_CLOCKDURATION].getValue()

    def symptom(self, value):
        self.IncidentRecordMap[SWORD_SYMPTOM].set(value)
        return self

    def getSymptom(self):
        return self.IncidentRecordMap[SWORD_SYMPTOM].getValue()

    def loadInfo(self, value):
        self.IncidentRecordListMap[SWORD_LOADINFO].add(value)
        return self

    def getLoadInfos(self):
        return self.IncidentRecordListMap[SWORD_LOADINFO].getValues()

    def getLoadInfoAt(self, index):
        return self.IncidentRecordListMap[SWORD_LOADINFO].getValue(index)

    def fullExecSummary(self, value):
        self.IncidentRecordListMap[SWORD_FULLEXECSUMMARY].add(value)
        return self

    def getFullExecSummarys(self):
        return self.IncidentRecordListMap[SWORD_FULLEXECSUMMARY].getValues()

    def getFullExecSummaryAt(self, index):
        return self.IncidentRecordListMap[SWORD_FULLEXECSUMMARY].getValue(index)

    def link1PartnerId(self, value):
        self.IncidentRecordMap[SWORD_LINK1PARTNERID].set(value)
        return self

    def getLink1PartnerId(self):
        return self.IncidentRecordMap[SWORD_LINK1PARTNERID].getValue()

    def link1ExternalId(self, value):
        self.IncidentRecordMap[SWORD_LINK1EXTERNALID].set(value)
        return self

    def getLink1ExternalId(self):
        return self.IncidentRecordMap[SWORD_LINK1EXTERNALID].getValue()

    def link1ExternalRef(self, value):
        self.IncidentRecordMap[SWORD_LINK1EXTERNALREF].set(value)
        return self

    def getLink1ExternalRef(self):
        return self.IncidentRecordMap[SWORD_LINK1EXTERNALREF].getValue()

    def link2PartnerId(self, value):
        self.IncidentRecordMap[SWORD_LINK2PARTNERID].set(value)
        return self

    def getLink2PartnerId(self):
        return self.IncidentRecordMap[SWORD_LINK2PARTNERID].getValue()

    def link2ExternalId(self, value):
        self.IncidentRecordMap[SWORD_LINK2EXTERNALID].set(value)
        return self

    def getLink2ExternalId(self):
        return self.IncidentRecordMap[SWORD_LINK2EXTERNALID].getValue()

    def link2ExternalRef(self, value):
        self.IncidentRecordMap[SWORD_LINK2EXTERNALREF].set(value)
        return self

    def getLink2ExternalRef(self):
        return self.IncidentRecordMap[SWORD_LINK2EXTERNALREF].getValue()

    def link1ExternalNumber(self, value):
        self.IncidentRecordMap[SWORD_LINK1EXTERNALNUMBER].set(value)
        return self

    def getLink1ExternalNumber(self):
        return self.IncidentRecordMap[SWORD_LINK1EXTERNALNUMBER].getValue()

    def link2ExternalNumber(self, value):
        self.IncidentRecordMap[SWORD_LINK2EXTERNALNUMBER].set(value)
        return self

    def getLink2ExternalNumber(self):
        return self.IncidentRecordMap[SWORD_LINK2EXTERNALNUMBER].getValue()

    def hotelCode(self, value):
        self.IncidentRecordMap[SWORD_HOTELCODE].set(value)
        return self

    def getHotelCode(self):
        return self.IncidentRecordMap[SWORD_HOTELCODE].getValue()

    def vendorCategory(self, value):
        self.IncidentRecordMap[SWORD_VENDORCATEGORY].set(value)
        return self

    def getVendorCategory(self):
        return self.IncidentRecordMap[SWORD_VENDORCATEGORY].getValue()

    def vendor(self, value):
        self.IncidentRecordMap[SWORD_VENDOR].set(value)
        return self

    def getVendor(self):
        return self.IncidentRecordMap[SWORD_VENDOR].getValue()

    def vendorName(self, value):
        self.IncidentRecordMap[SWORD_VENDORNAME].set(value)
        return self

    def getVendorName(self):
        return self.IncidentRecordMap[SWORD_VENDORNAME].getValue()

    def vendorPhone(self, value):
        self.IncidentRecordMap[SWORD_VENDORPHONE].set(value)
        return self

    def getVendorPhone(self):
        return self.IncidentRecordMap[SWORD_VENDORPHONE].getValue()

    def vendorReference(self, value):
        self.IncidentRecordMap[SWORD_VENDORREFERENCE].set(value)
        return self

    def getVendorReference(self):
        return self.IncidentRecordMap[SWORD_VENDORREFERENCE].getValue()

    def airwCompliance(self, value):
        self.IncidentRecordMap[SWORD_AIRWCOMPLIANCE].set(value)
        return self

    def getAirwCompliance(self):
        return self.IncidentRecordMap[SWORD_AIRWCOMPLIANCE].getValue()

    def hierEscalation(self, value):
        self.IncidentRecordMap[SWORD_HIERESCALATION].set(value)
        return self

    def getHierEscalation(self):
        return self.IncidentRecordMap[SWORD_HIERESCALATION].getValue()

    def topXErrorCode(self, value):
        self.IncidentRecordMap[SWORD_TOPXERRORCODE].set(value)
        return self

    def getTopXErrorCode(self):
        return self.IncidentRecordMap[SWORD_TOPXERRORCODE].getValue()

    def technicalIssue(self, value):
        self.IncidentRecordMap[SWORD_TECHNICALISSUE].set(value)
        return self

    def getTechnicalIssue(self):
        return self.IncidentRecordMap[SWORD_TECHNICALISSUE].getValue()

    def executiveSummary(self, value):
        self.IncidentRecordListMap[SWORD_EXECUTIVESUMMARY].add(value)
        return self

    def getExecutiveSummarys(self):
        return self.IncidentRecordListMap[SWORD_EXECUTIVESUMMARY].getValues()

    def getExecutiveSummaryAt(self, index):
        return self.IncidentRecordListMap[SWORD_EXECUTIVESUMMARY].getValue(index)

    def originatorGroupid(self, value):
        self.IncidentRecordMap[SWORD_ORIGINATORGROUPID].set(value)
        return self

    def getOriginatorGroupid(self):
        return self.IncidentRecordMap[SWORD_ORIGINATORGROUPID].getValue()

    def originatorUserid(self, value):
        self.IncidentRecordMap[SWORD_ORIGINATORUSERID].set(value)
        return self

    def getOriginatorUserid(self):
        return self.IncidentRecordMap[SWORD_ORIGINATORUSERID].getValue()

    def originatorTelephone(self, value):
        self.IncidentRecordMap[SWORD_ORIGINATORTELEPHONE].set(value)
        return self

    def getOriginatorTelephone(self):
        return self.IncidentRecordMap[SWORD_ORIGINATORTELEPHONE].getValue()

    def impactsFlightSafety(self, value):
        self.IncidentRecordMap[SWORD_IMPACTSFLIGHTSAFETY].set(value)
        return self

    def getImpactsFlightSafety(self):
        return self.IncidentRecordMap[SWORD_IMPACTSFLIGHTSAFETY].getValue()

    def confCallNumber(self, value):
        self.IncidentRecordMap[SWORD_CONFCALLNUMBER].set(value)
        return self

    def getConfCallNumber(self):
        return self.IncidentRecordMap[SWORD_CONFCALLNUMBER].getValue()

    def resolutionCause(self, value):
        self.IncidentRecordMap[SWORD_RESOLUTIONCAUSE].set(value)
        return self

    def getResolutionCause(self):
        return self.IncidentRecordMap[SWORD_RESOLUTIONCAUSE].getValue()

    def solvedTime(self, value):
        self.IncidentRecordMap[SWORD_SOLVEDTIME].set(value)
        return self

    def getSolvedTime(self):
        return self.IncidentRecordMap[SWORD_SOLVEDTIME].getValue()

    def solvedDate(self, value):
        self.IncidentRecordMap[SWORD_SOLVEDDATE].set(value)
        return self

    def getSolvedDate(self):
        return self.IncidentRecordMap[SWORD_SOLVEDDATE].getValue()

    def area(self, value):
        self.IncidentRecordMap[SWORD_AREA].set(value)
        return self

    def getArea(self):
        return self.IncidentRecordMap[SWORD_AREA].getValue()

    def baPmxRnid(self, value):
        self.IncidentRecordMap[SWORD_BAPMXRNID].set(value)
        return self

    def getBaPmxRnid(self):
        return self.IncidentRecordMap[SWORD_BAPMXRNID].getValue()

    def bACountry(self, value):
        self.IncidentRecordMap[SWORD_BACOUNTRY].set(value)
        return self

    def getBACountry(self):
        return self.IncidentRecordMap[SWORD_BACOUNTRY].getValue()

    def bALocation(self, value):
        self.IncidentRecordMap[SWORD_BALOCATION].set(value)
        return self

    def getBALocation(self):
        return self.IncidentRecordMap[SWORD_BALOCATION].getValue()

    def bALocationDesc1(self, value):
        self.IncidentRecordMap[SWORD_BALOCATIONDESC1].set(value)
        return self

    def getBALocationDesc1(self):
        return self.IncidentRecordMap[SWORD_BALOCATIONDESC1].getValue()

    def bALocationDesc2(self, value):
        self.IncidentRecordMap[SWORD_BALOCATIONDESC2].set(value)
        return self

    def getBALocationDesc2(self):
        return self.IncidentRecordMap[SWORD_BALOCATIONDESC2].getValue()

    def bALocationDesc3(self, value):
        self.IncidentRecordMap[SWORD_BALOCATIONDESC3].set(value)
        return self

    def getBALocationDesc3(self):
        return self.IncidentRecordMap[SWORD_BALOCATIONDESC3].getValue()

    def bATicketType(self, value):
        self.IncidentRecordMap[SWORD_BATICKETTYPE].set(value)
        return self

    def getBATicketType(self):
        return self.IncidentRecordMap[SWORD_BATICKETTYPE].getValue()

    def bAExternalID(self, value):
        self.IncidentRecordMap[SWORD_BAEXTERNALID].set(value)
        return self

    def getBAExternalID(self):
        return self.IncidentRecordMap[SWORD_BAEXTERNALID].getValue()

    def qFSeverity(self, value):
        self.IncidentRecordMap[SWORD_QFSEVERITY].set(value)
        return self

    def getQFSeverity(self):
        return self.IncidentRecordMap[SWORD_QFSEVERITY].getValue()

    def qFCoverageDate(self, value):
        self.IncidentRecordMap[SWORD_QFCOVERAGEDATE].set(value)
        return self

    def getQFCoverageDate(self):
        return self.IncidentRecordMap[SWORD_QFCOVERAGEDATE].getValue()

    def qFCoverageTime(self, value):
        self.IncidentRecordMap[SWORD_QFCOVERAGETIME].set(value)
        return self

    def getQFCoverageTime(self):
        return self.IncidentRecordMap[SWORD_QFCOVERAGETIME].getValue()

    def qFRefNo1(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO1].set(value)
        return self

    def getQFRefNo1(self):
        return self.IncidentRecordMap[SWORD_QFREFNO1].getValue()

    def qFRefNo2(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO2].set(value)
        return self

    def getQFRefNo2(self):
        return self.IncidentRecordMap[SWORD_QFREFNO2].getValue()

    def qFRefNo3(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO3].set(value)
        return self

    def getQFRefNo3(self):
        return self.IncidentRecordMap[SWORD_QFREFNO3].getValue()

    def qFRefNo4(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO4].set(value)
        return self

    def getQFRefNo4(self):
        return self.IncidentRecordMap[SWORD_QFREFNO4].getValue()

    def qFRefNo5(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO5].set(value)
        return self

    def getQFRefNo5(self):
        return self.IncidentRecordMap[SWORD_QFREFNO5].getValue()

    def qFRefNo6(self, value):
        self.IncidentRecordMap[SWORD_QFREFNO6].set(value)
        return self

    def getQFRefNo6(self):
        return self.IncidentRecordMap[SWORD_QFREFNO6].getValue()

    def flightDelay(self, value):
        self.IncidentRecordListMap[SWORD_FLIGHTDELAY].add(value)
        return self

    def getFlightDelays(self):
        return self.IncidentRecordListMap[SWORD_FLIGHTDELAY].getValues()

    def getFlightDelayAt(self, index):
        return self.IncidentRecordListMap[SWORD_FLIGHTDELAY].getValue(index)

    def qFExternalID(self, value):
        self.IncidentRecordMap[SWORD_QFEXTERNALID].set(value)
        return self

    def getQFExternalID(self):
        return self.IncidentRecordMap[SWORD_QFEXTERNALID].getValue()

    def qFFlightDelay(self, value):
        self.IncidentRecordMap[SWORD_QFFLIGHTDELAY].set(value)
        return self

    def getQFFlightDelay(self):
        return self.IncidentRecordMap[SWORD_QFFLIGHTDELAY].getValue()

    def ownedByQF(self, value):
        self.IncidentRecordMap[SWORD_OWNEDBYQF].set(value)
        return self

    def getOwnedByQF(self):
        return self.IncidentRecordMap[SWORD_OWNEDBYQF].getValue()

    def qfMaximoRnid(self, value):
        self.IncidentRecordMap[SWORD_QFMAXIMORNID].set(value)
        return self

    def getQfMaximoRnid(self):
        return self.IncidentRecordMap[SWORD_QFMAXIMORNID].getValue()

    def siebelRowID(self, value):
        self.IncidentRecordMap[SWORD_SIEBELROWID].set(value)
        return self

    def getSiebelRowID(self):
        return self.IncidentRecordMap[SWORD_SIEBELROWID].getValue()

    def siebelID(self, value):
        self.IncidentRecordMap[SWORD_SIEBELID].set(value)
        return self

    def getSiebelID(self):
        return self.IncidentRecordMap[SWORD_SIEBELID].getValue()

    def gSSEscalationRanking(self, value):
        self.IncidentRecordMap[SWORD_GSSESCALATIONRANKING].set(value)
        return self

    def getGSSEscalationRanking(self):
        return self.IncidentRecordMap[SWORD_GSSESCALATIONRANKING].getValue()

    def siebelCatA(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCATA].set(value)
        return self

    def getSiebelCatA(self):
        return self.IncidentRecordMap[SWORD_SIEBELCATA].getValue()

    def siebelCatB(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCATB].set(value)
        return self

    def getSiebelCatB(self):
        return self.IncidentRecordMap[SWORD_SIEBELCATB].getValue()

    def siebelCatC(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCATC].set(value)
        return self

    def getSiebelCatC(self):
        return self.IncidentRecordMap[SWORD_SIEBELCATC].getValue()

    def siebelCatD(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCATD].set(value)
        return self

    def getSiebelCatD(self):
        return self.IncidentRecordMap[SWORD_SIEBELCATD].getValue()

    def siebelCatE(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCATE].set(value)
        return self

    def getSiebelCatE(self):
        return self.IncidentRecordMap[SWORD_SIEBELCATE].getValue()

    def countryCode(self, value):
        self.IncidentRecordMap[SWORD_COUNTRYCODE].set(value)
        return self

    def getCountryCode(self):
        return self.IncidentRecordMap[SWORD_COUNTRYCODE].getValue()

    def officeID(self, value):
        self.IncidentRecordMap[SWORD_OFFICEID].set(value)
        return self

    def getOfficeID(self):
        return self.IncidentRecordMap[SWORD_OFFICEID].getValue()

    def prodPlanCategory(self, value):
        self.IncidentRecordMap[SWORD_PRODPLANCATEGORY].set(value)
        return self

    def getProdPlanCategory(self):
        return self.IncidentRecordMap[SWORD_PRODPLANCATEGORY].getValue()

    def amaProVersion2(self, value):
        self.IncidentRecordMap[SWORD_AMAPROVERSION2].set(value)
        return self

    def getAmaProVersion2(self):
        return self.IncidentRecordMap[SWORD_AMAPROVERSION2].getValue()

    def terminalAddress(self, value):
        self.IncidentRecordMap[SWORD_TERMINALADDRESS].set(value)
        return self

    def getTerminalAddress(self):
        return self.IncidentRecordMap[SWORD_TERMINALADDRESS].getValue()

    def operSystemName(self, value):
        self.IncidentRecordMap[SWORD_OPERSYSTEMNAME].set(value)
        return self

    def getOperSystemName(self):
        return self.IncidentRecordMap[SWORD_OPERSYSTEMNAME].getValue()

    def operSystemVersion(self, value):
        self.IncidentRecordMap[SWORD_OPERSYSTEMVERSION].set(value)
        return self

    def getOperSystemVersion(self):
        return self.IncidentRecordMap[SWORD_OPERSYSTEMVERSION].getValue()

    def atID(self, value):
        self.IncidentRecordMap[SWORD_ATID].set(value)
        return self

    def getAtID(self):
        return self.IncidentRecordMap[SWORD_ATID].getValue()

    def fixedInRelease(self, value):
        self.IncidentRecordMap[SWORD_FIXEDINRELEASE].set(value)
        return self

    def getFixedInRelease(self):
        return self.IncidentRecordMap[SWORD_FIXEDINRELEASE].getValue()

    def focus(self, value):
        self.IncidentRecordMap[SWORD_FOCUS].set(value)
        return self

    def getFocus(self):
        return self.IncidentRecordMap[SWORD_FOCUS].getValue()

    def cause(self, value):
        self.IncidentRecordMap[SWORD_CAUSE].set(value)
        return self

    def getCause(self):
        return self.IncidentRecordMap[SWORD_CAUSE].getValue()

    def userRemarks(self, value):
        self.IncidentRecordMap[SWORD_USERREMARKS].set(value)
        return self

    def getUserRemarks(self):
        return self.IncidentRecordMap[SWORD_USERREMARKS].getValue()

    def urlAlf(self, value):
        self.IncidentRecordMap[SWORD_URLALF].set(value)
        return self

    def getUrlAlf(self):
        return self.IncidentRecordMap[SWORD_URLALF].getValue()

    def urlSentinel(self, value):
        self.IncidentRecordMap[SWORD_URLSENTINEL].set(value)
        return self

    def getUrlSentinel(self):
        return self.IncidentRecordMap[SWORD_URLSENTINEL].getValue()

    def irlOneLink(self, value):
        self.IncidentRecordMap[SWORD_IRLONELINK].set(value)
        return self

    def getIrlOneLink(self):
        return self.IncidentRecordMap[SWORD_IRLONELINK].getValue()

    def trackerGroup5(self, value):
        self.IncidentRecordMap[SWORD_TRACKERGROUP5].set(value)
        return self

    def getTrackerGroup5(self):
        return self.IncidentRecordMap[SWORD_TRACKERGROUP5].getValue()

    def lHPscID(self, value):
        self.IncidentRecordMap[SWORD_LHPSCID].set(value)
        return self

    def getLHPscID(self):
        return self.IncidentRecordMap[SWORD_LHPSCID].getValue()

    def project(self, value):
        self.IncidentRecordMap[SWORD_PROJECT].set(value)
        return self

    def getproject(self):
        return self.IncidentRecordMap[SWORD_PROJECT].getValue()

    def explorerLanguage(self, value):
        self.IncidentRecordMap[SWORD_EXPLORERLANGUAGE].set(value)
        return self

    def getExplorerLanguage(self):
        return self.IncidentRecordMap[SWORD_EXPLORERLANGUAGE].getValue()

    def explorerServPack(self, value):
        self.IncidentRecordMap[SWORD_EXPLORERSERVPACK].set(value)
        return self

    def getExplorerServPack(self):
        return self.IncidentRecordMap[SWORD_EXPLORERSERVPACK].getValue()

    def oSSErvicePack(self, value):
        self.IncidentRecordMap[SWORD_OSSERVICEPACK].set(value)
        return self

    def getOSSErvicePack(self):
        return self.IncidentRecordMap[SWORD_OSSERVICEPACK].getValue()

    def lufthansaID(self, value):
        self.IncidentRecordMap[SWORD_LUFTHANSAID].set(value)
        return self

    def getLufthansaID(self):
        return self.IncidentRecordMap[SWORD_LUFTHANSAID].getValue()

    def ratingByCustomer(self, value):
        self.IncidentRecordMap[SWORD_RATINGBYCUSTOMER].set(value)
        return self

    def getRatingByCustomer(self):
        return self.IncidentRecordMap[SWORD_RATINGBYCUSTOMER].getValue()

    def severityOneAck(self, value):
        self.IncidentRecordMap[SWORD_SEVERITYONEACK].set(value)
        return self

    def getSeverityOneAck(self):
        return self.IncidentRecordMap[SWORD_SEVERITYONEACK].getValue()

    def siebelCompRowID(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCOMPROWID].set(value)
        return self

    def getSiebelCompRowID(self):
        return self.IncidentRecordMap[SWORD_SIEBELCOMPROWID].getValue()

    def siebelContRowID(self, value):
        self.IncidentRecordMap[SWORD_SIEBELCONTROWID].set(value)
        return self

    def getSiebelContRowID(self):
        return self.IncidentRecordMap[SWORD_SIEBELCONTROWID].getValue()

    def errorMessage(self, value):
        self.IncidentRecordMap[SWORD_ERRORMESSAGE].set(value)
        return self

    def getErrorMessage(self):
        return self.IncidentRecordMap[SWORD_ERRORMESSAGE].getValue()

    def knowledgeBaseUrl(self, value):
        self.IncidentRecordMap[SWORD_KNOWLEDGEBASEURL].set(value)
        return self

    def getKnowledgeBaseUrl(self):
        return self.IncidentRecordMap[SWORD_KNOWLEDGEBASEURL].getValue()

    def lastEverbridgeSentDate(self, value):
        self.IncidentRecordMap[SWORD_LASTEVERBRIDGESENTDATE].set(value)
        return self

    def getLastEverbridgeSentDate(self):
        return self.IncidentRecordMap[SWORD_LASTEVERBRIDGESENTDATE].getValue()

    def lastEverbridgeSentTime(self, value):
        self.IncidentRecordMap[SWORD_LASTEVERBRIDGESENTTIME].set(value)
        return self

    def getLastEverbridgeSentTime(self):
        return self.IncidentRecordMap[SWORD_LASTEVERBRIDGESENTTIME].getValue()

    def affServiceFlightDelC(self, value):
        self.IncidentRecordMap[SWORD_AFFSERVICEFLIGHTDELC].set(value)
        return self

    def getAffServiceFlightDelC(self):
        return self.IncidentRecordMap[SWORD_AFFSERVICEFLIGHTDELC].getValue()

    def affServiceFlightDelA(self, value):
        self.IncidentRecordMap[SWORD_AFFSERVICEFLIGHTDELA].set(value)
        return self

    def getAffServiceFlightDelA(self):
        return self.IncidentRecordMap[SWORD_AFFSERVICEFLIGHTDELA].getValue()

    def affServiceLastDate(self, value):
        self.IncidentRecordMap[SWORD_AFFSERVICELASTDATE].set(value)
        return self

    def getAffServiceLastDate(self):
        return self.IncidentRecordMap[SWORD_AFFSERVICELASTDATE].getValue()

    def affServiceLastTime(self, value):
        self.IncidentRecordMap[SWORD_AFFSERVICELASTTIME].set(value)
        return self

    def getAffServiceLastTime(self):
        return self.IncidentRecordMap[SWORD_AFFSERVICELASTTIME].getValue()

    def affServiceLastUser(self, value):
        self.IncidentRecordMap[SWORD_AFFSERVICELASTUSER].set(value)
        return self

    def getAffServiceLastUser(self):
        return self.IncidentRecordMap[SWORD_AFFSERVICELASTUSER].getValue()

    def updatedInBA(self, value):
        self.IncidentRecordMap[SWORD_UPDATEDINBA].set(value)
        return self

    def getUpdatedInBA(self):
        return self.IncidentRecordMap[SWORD_UPDATEDINBA].getValue()

    def updatedInQF(self, value):
        self.IncidentRecordMap[SWORD_UPDATEDINQF].set(value)
        return self

    def getUpdatedInQF(self):
        return self.IncidentRecordMap[SWORD_UPDATEDINQF].getValue()

    def closedBy(self, value):
        self.IncidentRecordMap[SWORD_CLOSEDBY].set(value)
        return self

    def getClosedBy(self):
        return self.IncidentRecordMap[SWORD_CLOSEDBY].getValue()

    def sevAtFirstAckid(self, value):
        self.IncidentRecordMap[SWORD_SEVATFIRSTACKID].set(value)
        return self

    def getSevAtFirstAckid(self):
        return self.IncidentRecordMap[SWORD_SEVATFIRSTACKID].getValue()

    def accessedDate(self, value):
        self.IncidentRecordMap[SWORD_ACCESSEDDATE].set(value)
        return self

    def getAccessedDate(self):
        return self.IncidentRecordMap[SWORD_ACCESSEDDATE].getValue()

    def accessedTime(self, value):
        self.IncidentRecordMap[SWORD_ACCESSEDTIME].set(value)
        return self

    def getAccessedTime(self):
        return self.IncidentRecordMap[SWORD_ACCESSEDTIME].getValue()

    def ackDate(self, value):
        self.IncidentRecordMap[SWORD_ACKDATE].set(value)
        return self

    def getAckDate(self):
        return self.IncidentRecordMap[SWORD_ACKDATE].getValue()

    def ackTime(self, value):
        self.IncidentRecordMap[SWORD_ACKTIME].set(value)
        return self

    def getAckTime(self):
        return self.IncidentRecordMap[SWORD_ACKTIME].getValue()

    def ackDateExt(self, value):
        self.IncidentRecordMap[SWORD_ACKDATEEXT].set(value)
        return self

    def getAckDateExt(self):
        return self.IncidentRecordMap[SWORD_ACKDATEEXT].getValue()

    def ackTimeExt(self, value):
        self.IncidentRecordMap[SWORD_ACKTIMEEXT].set(value)
        return self

    def getAckTimeExt(self):
        return self.IncidentRecordMap[SWORD_ACKTIMEEXT].getValue()

    def iwaveErrorBA(self, value):
        self.IncidentRecordMap[SWORD_IWAVEERRORBA].set(value)
        return self

    def getIwaveErrorBA(self):
        return self.IncidentRecordMap[SWORD_IWAVEERRORBA].getValue()

    def iwaveErrorQF(self, value):
        self.IncidentRecordMap[SWORD_IWAVEERRORQF].set(value)
        return self

    def getIwaveErrorQF(self):
        return self.IncidentRecordMap[SWORD_IWAVEERRORQF].getValue()

    def airFranceId(self, value):
        self.IncidentRecordMap[SWORD_AIRFRANCEID].set(value)
        return self

    def getAirFranceId(self):
        return self.IncidentRecordMap[SWORD_AIRFRANCEID].getValue()

    def lHIMViewID(self, value):
        self.IncidentRecordMap[SWORD_LHIMVIEWID].set(value)
        return self

    def getLHIMViewID(self):
        return self.IncidentRecordMap[SWORD_LHIMVIEWID].getValue()

    def maxSeverity(self, value):
        self.IncidentRecordMap[SWORD_MAXSEVERITY].set(value)
        return self

    def getMaxSeverity(self):
        return self.IncidentRecordMap[SWORD_MAXSEVERITY].getValue()

    def communityAccess(self, value):
        self.IncidentRecordMap[SWORD_COMMUNITYACCESS].set(value)
        return self

    def getCommunityAccess(self):
        return self.IncidentRecordMap[SWORD_COMMUNITYACCESS].getValue()

    def communityOwner(self, value):
        self.IncidentRecordMap[SWORD_COMMUNITYOWNER].set(value)
        return self

    def getCommunityOwner(self):
        return self.IncidentRecordMap[SWORD_COMMUNITYOWNER].getValue()

    def iMLastUpdate(self, value):
        self.IncidentRecordMap[SWORD_IMLASTUPDATE].set(value)
        return self

    def getIMLastUpdate(self):
        return self.IncidentRecordMap[SWORD_IMLASTUPDATE].getValue()

    def iMService(self, value):
        self.IncidentRecordMap[SWORD_IMSERVICE].set(value)
        return self

    def getIMService(self):
        return self.IncidentRecordMap[SWORD_IMSERVICE].getValue()

    def iMMarkets(self, value):
        self.IncidentRecordMap[SWORD_IMMARKETS].set(value)
        return self

    def getIMMarkets(self):
        return self.IncidentRecordMap[SWORD_IMMARKETS].getValue()

    def iMSince(self, value):
        self.IncidentRecordMap[SWORD_IMSINCE].set(value)
        return self

    def getIMSince(self):
        return self.IncidentRecordMap[SWORD_IMSINCE].getValue()

    def iMCause(self, value):
        self.IncidentRecordMap[SWORD_IMCAUSE].set(value)
        return self

    def getIMCause(self):
        return self.IncidentRecordMap[SWORD_IMCAUSE].getValue()

    def iMStatus(self, value):
        self.IncidentRecordListMap[SWORD_IM_STATUS].add(value)
        return self

    def getIMStatuss(self):
        return self.IncidentRecordListMap[SWORD_IM_STATUS].getValues()

    def getIMStatusAt(self, index):
        return self.IncidentRecordListMap[SWORD_IM_STATUS].getValue(index)

    def iMRecovery(self, value):
        self.IncidentRecordMap[SWORD_IMRECOVERY].set(value)
        return self

    def getIMRecovery(self):
        return self.IncidentRecordMap[SWORD_IMRECOVERY].getValue()

    def iMEmail(self, value):
        self.IncidentRecordMap[SWORD_IMEMAIL].set(value)
        return self

    def getIMEmail(self):
        return self.IncidentRecordMap[SWORD_IMEMAIL].getValue()

    def iMExternalStatus(self, value):
        self.IncidentRecordMap[SWORD_IMEXTERNALSTATUS].set(value)
        return self

    def getIMExternalStatus(self):
        return self.IncidentRecordMap[SWORD_IMEXTERNALSTATUS].getValue()

    def iMUpgradeTime(self, value):
        self.IncidentRecordMap[SWORD_IMUPGRADETIME].set(value)
        return self

    def getIMUpgradeTime(self):
        return self.IncidentRecordMap[SWORD_IMUPGRADETIME].getValue()

    def customerInfo(self, value):
        self.IncidentRecordListMap[SWORD_CUSTOMERINFO].add(value)
        return self

    def getCustomerInfos(self):
        return self.IncidentRecordListMap[SWORD_CUSTOMERINFO].getValues()

    def getCustomerInfoAt(self, index):
        return self.IncidentRecordListMap[SWORD_CUSTOMERINFO].getValue(index)

    def customerNote(self, value):
        self.IncidentRecordMap[SWORD_CUSTOMERNOTE].set(value)
        return self

    def getCustomerNote(self):
        return self.IncidentRecordMap[SWORD_CUSTOMERNOTE].getValue()

    def prevStatusMail(self, value):
        self.IncidentRecordListMap[SWORD_PREVSTATUSMAIL].add(value)
        return self

    def getPrevStatusMails(self):
        return self.IncidentRecordListMap[SWORD_PREVSTATUSMAIL].getValues()

    def getPrevStatusMailAt(self, index):
        return self.IncidentRecordListMap[SWORD_PREVSTATUSMAIL].getValue(index)

    def reportRequested(self, value):
        self.IncidentRecordMap[SWORD_REPORTREQUESTED].set(value)
        return self

    def getReportRequested(self):
        return self.IncidentRecordMap[SWORD_REPORTREQUESTED].getValue()

    def reportForAirlines(self, value):
        self.IncidentRecordMap[SWORD_REPORTFORAIRLINES].set(value)
        return self

    def getReportForAirlines(self):
        return self.IncidentRecordMap[SWORD_REPORTFORAIRLINES].getValue()

    def cIReferenceEn(self, value):
        self.IncidentRecordMap[SWORD_CIREFERENCEEN].set(value)
        return self

    def getCIReferenceEn(self):
        return self.IncidentRecordMap[SWORD_CIREFERENCEEN].getValue()

    def solverGroup2(self, value):
        self.IncidentRecordMap[SWORD_SOLVERGROUP2].set(value)
        return self

    def getSolverGroup2(self):
        return self.IncidentRecordMap[SWORD_SOLVERGROUP2].getValue()

    def recoveryAction(self, value):
        self.IncidentRecordMap[SWORD_RECOVERYACTION].set(value)
        return self

    def getRecoveryAction(self):
        return self.IncidentRecordMap[SWORD_RECOVERYACTION].getValue()

    def tRReference(self, value):
        self.IncidentRecordMap[SWORD_TRREFERENCE].set(value)
        return self

    def getTRReference(self):
        return self.IncidentRecordMap[SWORD_TRREFERENCE].getValue()

    def crCpRefNo1(self, value):
        self.IncidentRecordMap[SWORD_CRCPREFNO1].set(value)
        return self

    def getCrCpRefNo1(self):
        return self.IncidentRecordMap[SWORD_CRCPREFNO1].getValue()

    def crCpRefNo2(self, value):
        self.IncidentRecordMap[SWORD_CRCPREFNO2].set(value)
        return self

    def getCrCpRefNo2(self):
        return self.IncidentRecordMap[SWORD_CRCPREFNO2].getValue()

    def resolution(self, value):
        self.IncidentRecordListMap[SWORD_RESOLUTION].add(value)
        return self

    def getResolutions(self):
        return self.IncidentRecordListMap[SWORD_RESOLUTION].getValues()

    def getResolutionAt(self, index):
        return self.IncidentRecordListMap[SWORD_RESOLUTION].getValue(index)

    def causedCR(self, value):
        self.IncidentRecordMap[SWORD_CAUSEDCR].set(value)
        return self

    def getCausedCR(self):
        return self.IncidentRecordMap[SWORD_CAUSEDCR].getValue()

    def causedWO(self, value):
        self.IncidentRecordMap[SWORD_CAUSEDWO].set(value)
        return self

    def getCausedWO(self):
        return self.IncidentRecordMap[SWORD_CAUSEDWO].getValue()

    def lRReference(self, value):
        self.IncidentRecordMap[SWORD_LRREFERENCE].set(value)
        return self

    def getLRReference(self):
        return self.IncidentRecordMap[SWORD_LRREFERENCE].getValue()

    def oSLanguage(self, value):
        self.IncidentRecordMap[SWORD_OSLANGUAGE].set(value)
        return self

    def getOSLanguage(self):
        return self.IncidentRecordMap[SWORD_OSLANGUAGE].getValue()

    def solutionXRef(self, value):
        self.IncidentRecordMap[SWORD_SOLUTIONXREF].set(value)
        return self

    def getSolutionXRef(self):
        return self.IncidentRecordMap[SWORD_SOLUTIONXREF].getValue()

    def ptrRefNo2(self, value):
        self.IncidentRecordMap[SWORD_PTRREFNO2].set(value)
        return self

    def getPtrRefNo2(self):
        return self.IncidentRecordMap[SWORD_PTRREFNO2].getValue()

    def ptrRefNo3(self, value):
        self.IncidentRecordMap[SWORD_PTRREFNO3].set(value)
        return self

    def getPtrRefNo3(self):
        return self.IncidentRecordMap[SWORD_PTRREFNO3].getValue()

    def workAroundAvail(self, value):
        self.IncidentRecordMap[SWORD_WORKAROUNDAVAIL].set(value)
        return self

    def getWorkAroundAvail(self):
        return self.IncidentRecordMap[SWORD_WORKAROUNDAVAIL].getValue()

    def reOccurance(self, value):
        self.IncidentRecordMap[SWORD_REOCCURANCE].set(value)
        return self

    def getReOccurance(self):
        return self.IncidentRecordMap[SWORD_REOCCURANCE].getValue()

    def ptrRefNo4(self, value):
        self.IncidentRecordMap[SWORD_PTRREFNO4].set(value)
        return self

    def getPtrRefNo4(self):
        return self.IncidentRecordMap[SWORD_PTRREFNO4].getValue()

    def ciNotFound(self, value):
        self.IncidentRecordMap[SWORD_CINOTFOUND].set(value)
        return self

    def getCiNotFound(self):
        return self.IncidentRecordMap[SWORD_CINOTFOUND].getValue()

    def ciNotFoundReason(self, value):
        self.IncidentRecordMap[SWORD_CINOTFOUNDREASON].set(value)
        return self

    def getCiNotFoundReason(self):
        return self.IncidentRecordMap[SWORD_CINOTFOUNDREASON].getValue()

    def ciNotFoundList(self, value):
        self.IncidentRecordMap[SWORD_CINOTFOUNDLIST].set(value)
        return self

    def getCiNotFoundList(self):
        return self.IncidentRecordMap[SWORD_CINOTFOUNDLIST].getValue()

    def crImplementation(self, value):
        self.IncidentRecordMap[SWORD_CRIMPLEMENTATION].set(value)
        return self

    def getCrImplementation(self):
        return self.IncidentRecordMap[SWORD_CRIMPLEMENTATION].getValue()

    def ptrRefNo0(self, value):
        self.IncidentRecordMap[SWORD_PTRREFNO0].set(value)
        return self

    def getPtrRefNo0(self):
        return self.IncidentRecordMap[SWORD_PTRREFNO0].getValue()

    def localMaster(self, value):
        self.IncidentRecordMap[SWORD_LOCALMASTER].set(value)
        return self

    def getLocalMaster(self):
        return self.IncidentRecordMap[SWORD_LOCALMASTER].getValue()

    def markedAsMIRDate(self, value):
        self.IncidentRecordMap[SWORD_MARKEDASMIRDATE].set(value)
        return self

    def getMarkedAsMIRDate(self):
        return self.IncidentRecordMap[SWORD_MARKEDASMIRDATE].getValue()

    def markedAsMIRTime(self, value):
        self.IncidentRecordMap[SWORD_MARKEDASMIRTIME].set(value)
        return self

    def getMarkedAsMIRTime(self):
        return self.IncidentRecordMap[SWORD_MARKEDASMIRTIME].getValue()

    def diagnosedDate(self, value):
        self.IncidentRecordMap[SWORD_DIAGNOSEDDATE].set(value)
        return self

    def getDiagnosedDate(self):
        return self.IncidentRecordMap[SWORD_DIAGNOSEDDATE].getValue()

    def diagnosedTime(self, value):
        self.IncidentRecordMap[SWORD_DIAGNOSEDTIME].set(value)
        return self

    def getDiagnosedTime(self):
        return self.IncidentRecordMap[SWORD_DIAGNOSEDTIME].getValue()

    def enteredDate(self, value):
        self.IncidentRecordMap[SWORD_ENTEREDDATE].set(value)
        return self

    def getEnteredDate(self):
        return self.IncidentRecordMap[SWORD_ENTEREDDATE].getValue()

    def enteredTime(self, value):
        self.IncidentRecordMap[SWORD_ENTEREDTIME].set(value)
        return self

    def getEnteredTime(self):
        return self.IncidentRecordMap[SWORD_ENTEREDTIME].getValue()

    def templateID(self, value):
        self.IncidentRecordMap[SWORD_TEMPLATEID].set(value)
        return self

    def getTemplateID(self):
        return self.IncidentRecordMap[SWORD_TEMPLATEID].getValue()

    def qFLastGroup(self, value):
        self.IncidentRecordMap[SWORD_QFLASTGROUP].set(value)
        return self

    def getQFLastGroup(self):
        return self.IncidentRecordMap[SWORD_QFLASTGROUP].getValue()

    def qFLastUser(self, value):
        self.IncidentRecordMap[SWORD_QFLASTUSER].set(value)
        return self

    def getQFLastUser(self):
        return self.IncidentRecordMap[SWORD_QFLASTUSER].getValue()

    def qFLastTel(self, value):
        self.IncidentRecordMap[SWORD_QFLASTTEL].set(value)
        return self

    def getQFLastTel(self):
        return self.IncidentRecordMap[SWORD_QFLASTTEL].getValue()

    def amaAckSev(self, value):
        self.IncidentRecordMap[SWORD_AMAACKSEV].set(value)
        return self

    def getAmaAckSev(self):
        return self.IncidentRecordMap[SWORD_AMAACKSEV].getValue()

    def iWaveBAMode(self, value):
        self.IncidentRecordMap[SWORD_IWAVEBAMODE].set(value)
        return self

    def getIWaveBAMode(self):
        return self.IncidentRecordMap[SWORD_IWAVEBAMODE].getValue()

    def bACategory(self, value):
        self.IncidentRecordMap[SWORD_BACATEGORY].set(value)
        return self

    def getBACategory(self):
        return self.IncidentRecordMap[SWORD_BACATEGORY].getValue()

    def bASubCategory(self, value):
        self.IncidentRecordMap[SWORD_BASUBCATEGORY].set(value)
        return self

    def getBASubCategory(self):
        return self.IncidentRecordMap[SWORD_BASUBCATEGORY].getValue()

    def bAProduct(self, value):
        self.IncidentRecordMap[SWORD_BAPRODUCT].set(value)
        return self

    def getBAProduct(self):
        return self.IncidentRecordMap[SWORD_BAPRODUCT].getValue()

    def bAProblemType(self, value):
        self.IncidentRecordMap[SWORD_BAPROBLEMTYPE].set(value)
        return self

    def getBAProblemType(self):
        return self.IncidentRecordMap[SWORD_BAPROBLEMTYPE].getValue()

    def qFMSStatus(self, value):
        self.IncidentRecordMap[SWORD_QFMSSTATUS].set(value)
        return self

    def getQFMSStatus(self):
        return self.IncidentRecordMap[SWORD_QFMSSTATUS].getValue()

    def crisisActivation(self, value):
        self.IncidentRecordMap[SWORD_CRISISACTIVATION].set(value)
        return self

    def getCrisisActivation(self):
        return self.IncidentRecordMap[SWORD_CRISISACTIVATION].getValue()

    def crisisActivation(self, value):
        self.IncidentRecordMap[SWORD_CRISISACTIVATION].set(value)
        return self

    def getCrisisActivation(self):
        return self.IncidentRecordMap[SWORD_CRISISACTIVATION].getValue()

    def imStart(self, value):
        self.IncidentRecordMap[SWORD_IMSTART].set(value)
        return self

    def getImStart(self):
        return self.IncidentRecordMap[SWORD_IMSTART].getValue()

    def imStart(self, value):
        self.IncidentRecordMap[SWORD_IMSTART].set(value)
        return self

    def getImStart(self):
        return self.IncidentRecordMap[SWORD_IMSTART].getValue()

    def rejectDate(self, value):
        self.IncidentRecordMap[SWORD_REJECTDATE].set(value)
        return self

    def getRejectDate(self):
        return self.IncidentRecordMap[SWORD_REJECTDATE].getValue()

    def rejectDate2(self, value):
        self.IncidentRecordMap[SWORD_REJECTDATE_2].set(value)
        return self

    def getRejectDate2(self):
        return self.IncidentRecordMap[SWORD_REJECTDATE_2].getValue()

    def diagnosedGroupid(self, value):
        self.IncidentRecordMap[SWORD_DIAGNOSEDGROUPID].set(value)
        return self

    def getDiagnosedGroupid(self):
        return self.IncidentRecordMap[SWORD_DIAGNOSEDGROUPID].getValue()

    def loggedTool(self, value):
        self.IncidentRecordMap[SWORD_LOGGEDTOOL].set(value)
        return self

    def getLoggedTool(self):
        return self.IncidentRecordMap[SWORD_LOGGEDTOOL].getValue()

    def recTypeId(self, value):
        self.IncidentRecordMap[SWORD_RECTYPEID].set(value)
        return self

    def getRecTypeId(self):
        return self.IncidentRecordMap[SWORD_RECTYPEID].getValue()

    def servManInvolvedDate(self, value):
        self.IncidentRecordMap[SWORD_SERVMANINVOLVEDDATE].set(value)
        return self

    def getServManInvolvedDate(self):
        return self.IncidentRecordMap[SWORD_SERVMANINVOLVEDDATE].getValue()

    def servManInvolvedTime(self, value):
        self.IncidentRecordMap[SWORD_SERVMANINVOLVEDTIME].set(value)
        return self

    def getServManInvolvedTime(self):
        return self.IncidentRecordMap[SWORD_SERVMANINVOLVEDTIME].getValue()

    def createdByTool(self, value):
        self.IncidentRecordMap[SWORD_CREATEDBYTOOL].set(value)
        return self

    def getCreatedByTool(self):
        return self.IncidentRecordMap[SWORD_CREATEDBYTOOL].getValue()

    def loggerUserid(self, value):
        self.IncidentRecordMap[SWORD_LOGGERUSERID].set(value)
        return self

    def getLoggerUserid(self):
        return self.IncidentRecordMap[SWORD_LOGGERUSERID].getValue()

    def ackSMCGroup(self, value):
        self.IncidentRecordMap[SWORD_ACKSMCGROUP].set(value)
        return self

    def getAckSMCGroup(self):
        return self.IncidentRecordMap[SWORD_ACKSMCGROUP].getValue()

    def ackSMCUser(self, value):
        self.IncidentRecordMap[SWORD_ACKSMCUSER].set(value)
        return self

    def getAckSMCUser(self):
        return self.IncidentRecordMap[SWORD_ACKSMCUSER].getValue()

    def maxSevSetDate(self, value):
        self.IncidentRecordMap[SWORD_MAXSEVSETDATE].set(value)
        return self

    def getMaxSevSetDate(self):
        return self.IncidentRecordMap[SWORD_MAXSEVSETDATE].getValue()

    def maxSevSetTime(self, value):
        self.IncidentRecordMap[SWORD_MAXSEVSETTIME].set(value)
        return self

    def getMaxSevSetTime(self):
        return self.IncidentRecordMap[SWORD_MAXSEVSETTIME].getValue()

    def serviceImpactIndex(self, value):
        self.IncidentRecordMap[SWORD_SERVICEIMPACTINDEX].set(value)
        return self

    def getServiceImpactIndex(self):
        return self.IncidentRecordMap[SWORD_SERVICEIMPACTINDEX].getValue()

    def sev1SetDate(self, value):
        self.IncidentRecordMap[SWORD_SEV1SETDATE].set(value)
        return self

    def getSev1SetDate(self):
        return self.IncidentRecordMap[SWORD_SEV1SETDATE].getValue()

    def sev2SetDate(self, value):
        self.IncidentRecordMap[SWORD_SEV2SETDATE].set(value)
        return self

    def getSev2SetDate(self):
        return self.IncidentRecordMap[SWORD_SEV2SETDATE].getValue()

    def sev3SetDate(self, value):
        self.IncidentRecordMap[SWORD_SEV3SETDATE].set(value)
        return self

    def getSev3SetDate(self):
        return self.IncidentRecordMap[SWORD_SEV3SETDATE].getValue()

    def sev4SetDate(self, value):
        self.IncidentRecordMap[SWORD_SEV4SETDATE].set(value)
        return self

    def getSev4SetDate(self):
        return self.IncidentRecordMap[SWORD_SEV4SETDATE].getValue()

    def sOAInvolvedDate(self, value):
        self.IncidentRecordMap[SWORD_SOAINVOLVEDDATE].set(value)
        return self

    def getSOAInvolvedDate(self):
        return self.IncidentRecordMap[SWORD_SOAINVOLVEDDATE].getValue()

    def sOAInvolvedTime(self, value):
        self.IncidentRecordMap[SWORD_SOAINVOLVEDTIME].set(value)
        return self

    def getSOAInvolvedTime(self):
        return self.IncidentRecordMap[SWORD_SOAINVOLVEDTIME].getValue()

    def pTRIRReference(self, value):
        self.IncidentRecordMap[SWORD_PTRIRREFERENCE].set(value)
        return self

    def getPTRIRReference(self):
        return self.IncidentRecordMap[SWORD_PTRIRREFERENCE].getValue()

    def chaseUpText(self, value):
        self.IncidentRecordListMap[SWORD_CHASEUPTEXT].add(value)
        return self

    def getChaseUpTexts(self):
        return self.IncidentRecordListMap[SWORD_CHASEUPTEXT].getValues()

    def getChaseUpTextAt(self, index):
        return self.IncidentRecordListMap[SWORD_CHASEUPTEXT].getValue(index)

    def chaseUpGroups(self, value):
        self.IncidentRecordMap[SWORD_CHASEUPGROUPS].set(value)
        return self

    def getChaseUpGroups(self):
        return self.IncidentRecordMap[SWORD_CHASEUPGROUPS].getValue()

    def claimProviderCode(self, value):
        self.IncidentRecordMap[SWORD_CLAIMPROVIDERCODE].set(value)
        return self

    def getClaimProviderCode(self):
        return self.IncidentRecordMap[SWORD_CLAIMPROVIDERCODE].getValue()

    def claimAmountReq(self, value):
        self.IncidentRecordMap[SWORD_CLAIMAMOUNTREQ].set(value)
        return self

    def getClaimAmountReq(self):
        return self.IncidentRecordMap[SWORD_CLAIMAMOUNTREQ].getValue()

    def claimAmountRefund(self, value):
        self.IncidentRecordMap[SWORD_CLAIMAMOUNTREFUND].set(value)
        return self

    def getClaimAmountRefund(self):
        return self.IncidentRecordMap[SWORD_CLAIMAMOUNTREFUND].getValue()

    def claimResponsible(self, value):
        self.IncidentRecordMap[SWORD_CLAIMRESPONSIBLE].set(value)
        return self

    def getClaimResponsible(self):
        return self.IncidentRecordMap[SWORD_CLAIMRESPONSIBLE].getValue()

    def claimReason(self, value):
        self.IncidentRecordMap[SWORD_CLAIMREASON].set(value)
        return self

    def getClaimReason(self):
        return self.IncidentRecordMap[SWORD_CLAIMREASON].getValue()

    def iWaveBAClosureFlag(self, value):
        self.IncidentRecordMap[SWORD_IWAVEBACLOSUREFLAG].set(value)
        return self

    def getIWaveBAClosureFlag(self):
        return self.IncidentRecordMap[SWORD_IWAVEBACLOSUREFLAG].getValue()

    def admSource(self, value):
        self.IncidentRecordMap[SWORD_ADMSOURCE].set(value)
        return self

    def getAdmSource(self):
        return self.IncidentRecordMap[SWORD_ADMSOURCE].getValue()

    def paymentApproved(self, value):
        self.IncidentRecordMap[SWORD_PAYMENTAPPROVED].set(value)
        return self

    def getPaymentApproved(self):
        return self.IncidentRecordMap[SWORD_PAYMENTAPPROVED].getValue()

    def causedCR(self, value):
        self.IncidentRecordMap[SWORD_CAUSEDCR].set(value)
        return self

    def getCausedCR(self):
        return self.IncidentRecordMap[SWORD_CAUSEDCR].getValue()

    def hierEscalation(self, value):
        self.IncidentRecordMap[SWORD_HIERESCALATION].set(value)
        return self

    def getHierEscalation(self):
        return self.IncidentRecordMap[SWORD_HIERESCALATION].getValue()

    def mIRDetectedBy(self, value):
        self.IncidentRecordMap[SWORD_MIRDETECTEDBY].set(value)
        return self

    def getMIRDetectedBy(self):
        return self.IncidentRecordMap[SWORD_MIRDETECTEDBY].getValue()

    def parallelInvestOpen(self, value):
        self.IncidentRecordMap[SWORD_PARALLELINVESTOPEN].set(value)
        return self

    def getParallelInvestOpen(self):
        return self.IncidentRecordMap[SWORD_PARALLELINVESTOPEN].getValue()

    def firstCIRAutomationDate(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRAUTOMATIONDATE].set(value)
        return self

    def getFirstCIRAutomationDate(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRAUTOMATIONDATE].getValue()

    def firstCIRAutomationTime(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRAUTOMATIONTIME].set(value)
        return self

    def getFirstCIRAutomationTime(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRAUTOMATIONTIME].getValue()

    def firstCIRCustomerDate(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRCUSTOMERDATE].set(value)
        return self

    def getFirstCIRCustomerDate(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRCUSTOMERDATE].getValue()

    def firstCIRCustomerTime(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRCUSTOMERTIME].set(value)
        return self

    def getFirstCIRCustomerTime(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRCUSTOMERTIME].getValue()

    def firstCIRAmadeusDate(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRAMADEUSDATE].set(value)
        return self

    def getFirstCIRAmadeusDate(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRAMADEUSDATE].getValue()

    def firstCIRAmadeusTime(self, value):
        self.IncidentRecordMap[SWORD_FIRSTCIRAMADEUSTIME].set(value)
        return self

    def getFirstCIRAmadeusTime(self):
        return self.IncidentRecordMap[SWORD_FIRSTCIRAMADEUSTIME].getValue()

    def orangeCrisisTriggered(self, value):
        self.IncidentRecordMap[SWORD_ORANGECRISISTRIGGERED].set(value)
        return self

    def getOrangeCrisisTriggered(self):
        return self.IncidentRecordMap[SWORD_ORANGECRISISTRIGGERED].getValue()

    def iRPriority(self, value):
        self.IncidentRecordMap[SWORD_IRPRIORITY].set(value)
        return self

    def getIRPriority(self):
        return self.IncidentRecordMap[SWORD_IRPRIORITY].getValue()

    def iRPriorityAcceptDate(self, value):
        self.IncidentRecordMap[SWORD_IRPRIORITYACCEPTDATE].set(value)
        return self

    def getIRPriorityAcceptDate(self):
        return self.IncidentRecordMap[SWORD_IRPRIORITYACCEPTDATE].getValue()

    def iRPriorityAcceptTime(self, value):
        self.IncidentRecordMap[SWORD_IRPRIORITYACCEPTTIME].set(value)
        return self

    def getIRPriorityAcceptTime(self):
        return self.IncidentRecordMap[SWORD_IRPRIORITYACCEPTTIME].getValue()

    def targetDate(self, value):
        self.IncidentRecordMap[SWORD_TARGETDATE].set(value)
        return self

    def getTargetDate(self):
        return self.IncidentRecordMap[SWORD_TARGETDATE].getValue()

    def targetTime(self, value):
        self.IncidentRecordMap[SWORD_TARGETTIME].set(value)
        return self

    def getTargetTime(self):
        return self.IncidentRecordMap[SWORD_TARGETTIME].getValue()

    def usage(self, value):
        self.IncidentRecordMap[SWORD_USAGE].set(value)
        return self

    def getUsage(self):
        return self.IncidentRecordMap[SWORD_USAGE].getValue()

    def prioSev1(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV1].set(value)
        return self

    def getPrioSev1(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV1].getValue()

    def prioSev2U(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV2U].set(value)
        return self

    def getPrioSev2U(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV2U].getValue()

    def prioSev2(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV2].set(value)
        return self

    def getPrioSev2(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV2].getValue()

    def prioSev3U(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV3U].set(value)
        return self

    def getPrioSev3U(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV3U].getValue()

    def prioSev3(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV3].set(value)
        return self

    def getPrioSev3(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV3].getValue()

    def prioSev4U(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV4U].set(value)
        return self

    def getPrioSev4U(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV4U].getValue()

    def prioSev4(self, value):
        self.IncidentRecordMap[SWORD_PRIOSEV4].set(value)
        return self

    def getPrioSev4(self):
        return self.IncidentRecordMap[SWORD_PRIOSEV4].getValue()

    def recovDateInt(self, value):
        self.IncidentRecordMap[SWORD_RECOVDATEINT].set(value)
        return self

    def getRecovDateInt(self):
        return self.IncidentRecordMap[SWORD_RECOVDATEINT].getValue()

    def recovDateInt(self, value):
        self.IncidentRecordMap[SWORD_RECOVDATEINT].set(value)
        return self

    def getRecovDateInt(self):
        return self.IncidentRecordMap[SWORD_RECOVDATEINT].getValue()

    def nrCommonCis(self, value):
        self.IncidentRecordMap[SWORD_NRCOMMONCIS].set(value)
        return self

    def getNrCommonCis(self):
        return self.IncidentRecordMap[SWORD_NRCOMMONCIS].getValue()

    def tagCI1(self, value):
        self.IncidentRecordMap[SWORD_TAGCI1].set(value)
        return self

    def getTagCI1(self):
        return self.IncidentRecordMap[SWORD_TAGCI1].getValue()

    def tagCI2(self, value):
        self.IncidentRecordMap[SWORD_TAGCI2].set(value)
        return self

    def getTagCI2(self):
        return self.IncidentRecordMap[SWORD_TAGCI2].getValue()

    def tagCI3(self, value):
        self.IncidentRecordMap[SWORD_TAGCI3].set(value)
        return self

    def getTagCI3(self):
        return self.IncidentRecordMap[SWORD_TAGCI3].getValue()

    def tagCI4(self, value):
        self.IncidentRecordMap[SWORD_TAGCI4].set(value)
        return self

    def getTagCI4(self):
        return self.IncidentRecordMap[SWORD_TAGCI4].getValue()

    def tagMoreCommonCIs(self, value):
        self.IncidentRecordMap[SWORD_TAGMORECOMMON_CIS].set(value)
        return self

    def getTagMoreCommonCIs(self):
        return self.IncidentRecordMap[SWORD_TAGMORECOMMON_CIS].getValue()

    def tagAllCIs(self, value):
        self.IncidentRecordMap[SWORD_TAGALLCIS].set(value)
        return self

    def getTagAllCIs(self):
        return self.IncidentRecordMap[SWORD_TAGALLCIS].getValue()

    def foundCIs(self, value):
        self.IncidentRecordMap[SWORD_FOUNDCIS].set(value)
        return self

    def getFoundCIs(self):
        return self.IncidentRecordMap[SWORD_FOUNDCIS].getValue()

    def relatedbyTag(self, value):
        self.IncidentRecordMap[SWORD_RELATEDBYTAG].set(value)
        return self

    def getRelatedbyTag(self):
        return self.IncidentRecordMap[SWORD_RELATEDBYTAG].getValue()

    def tagLimit(self, value):
        self.IncidentRecordMap[SWORD_TAGLIMIT].set(value)
        return self

    def getTagLimit(self):
        return self.IncidentRecordMap[SWORD_TAGLIMIT].getValue()

    def tagOffset(self, value):
        self.IncidentRecordMap[SWORD_TAGOFFSET].set(value)
        return self

    def getTagOffset(self):
        return self.IncidentRecordMap[SWORD_TAGOFFSET].getValue()

    def tagRecordTypes(self, value):
        self.IncidentRecordMap[SWORD_TAGRECORDTYPES].set(value)
        return self

    def getTagRecordTypes(self):
        return self.IncidentRecordMap[SWORD_TAGRECORDTYPES].getValue()

    def tagStartTime(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTTIME].set(value)
        return self

    def getTagStartTime(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTTIME].getValue()

    def tagStartTimeUnit(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTTIMEUNIT].set(value)
        return self

    def getTagStartTimeUnit(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTTIMEUNIT].getValue()

    def tagEndTime(self, value):
        self.IncidentRecordMap[SWORD_TAGENDTIME].set(value)
        return self

    def getTagEndTime(self):
        return self.IncidentRecordMap[SWORD_TAGENDTIME].getValue()

    def tagEndTimeUnit(self, value):
        self.IncidentRecordMap[SWORD_TAGENDTIMEUNIT].set(value)
        return self

    def getTagEndTimeUnit(self):
        return self.IncidentRecordMap[SWORD_TAGENDTIMEUNIT].getValue()

    def tagStartDateAbs(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTDATEABS].set(value)
        return self

    def getTagStartDateAbs(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTDATEABS].getValue()

    def tagStartTimeAbs(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTTIMEABS].set(value)
        return self

    def getTagStartTimeAbs(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTTIMEABS].getValue()

    def tagEndDateAbs(self, value):
        self.IncidentRecordMap[SWORD_TAGENDDATEABS].set(value)
        return self

    def getTagEndDateAbs(self):
        return self.IncidentRecordMap[SWORD_TAGENDDATEABS].getValue()

    def tagEndTimeAbs(self, value):
        self.IncidentRecordMap[SWORD_TAGENDTIMEABS].set(value)
        return self

    def getTagEndTimeAbs(self):
        return self.IncidentRecordMap[SWORD_TAGENDTIMEABS].getValue()

    def tagTimeMode(self, value):
        self.IncidentRecordMap[SWORD_TAGTIMEMODE].set(value)
        return self

    def getTagTimeMode(self):
        return self.IncidentRecordMap[SWORD_TAGTIMEMODE].getValue()

    def tagStartTimeRel(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTTIMEREL].set(value)
        return self

    def getTagStartTimeRel(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTTIMEREL].getValue()

    def tagStartTimeUnitRel(self, value):
        self.IncidentRecordMap[SWORD_TAGSTARTTIMEUNITREL].set(value)
        return self

    def getTagStartTimeUnitRel(self):
        return self.IncidentRecordMap[SWORD_TAGSTARTTIMEUNITREL].getValue()

    def tagEndTimeRel(self, value):
        self.IncidentRecordMap[SWORD_TAGENDTIMEREL].set(value)
        return self

    def getTagEndTimeRel(self):
        return self.IncidentRecordMap[SWORD_TAGENDTIMEREL].getValue()

    def tagEndTimeUnitRel(self, value):
        self.IncidentRecordMap[SWORD_TAGENDTIMEUNITREL].set(value)
        return self

    def getTagEndTimeUnitRel(self):
        return self.IncidentRecordMap[SWORD_TAGENDTIMEUNITREL].getValue()

    def dispatchGroupCode(self, value):
        self.IncidentRecordMap[SWORD_DISPATCHGROUPCODE].set(value)
        return self

    def getDispatchGroupCode(self):
        return self.IncidentRecordMap[SWORD_DISPATCHGROUPCODE].getValue()

    def dispatchGroupName(self, value):
        self.IncidentRecordMap[SWORD_DISPATCHGROUPNAME].set(value)
        return self

    def getDispatchGroupName(self):
        return self.IncidentRecordMap[SWORD_DISPATCHGROUPNAME].getValue()

    def dispatchRelevance(self, value):
        self.IncidentRecordMap[SWORD_DISPATCHRELEVANCE].set(value)
        return self

    def getDispatchRelevance(self):
        return self.IncidentRecordMap[SWORD_DISPATCHRELEVANCE].getValue()

    def pMRSeachFor(self, value):
        self.IncidentRecordMap[SWORD_PMRSEACHFOR].set(value)
        return self

    def getPMRSeachFor(self):
        return self.IncidentRecordMap[SWORD_PMRSEACHFOR].getValue()

    def pMRId(self, value):
        self.IncidentRecordMap[SWORD_PMRID].set(value)
        return self

    def getPMRId(self):
        return self.IncidentRecordMap[SWORD_PMRID].getValue()

    def pMRSeachIn(self, value):
        self.IncidentRecordMap[SWORD_PMRSEACHIN].set(value)
        return self

    def getPMRSeachIn(self):
        return self.IncidentRecordMap[SWORD_PMRSEACHIN].getValue()

    def relatedPMRs(self, value):
        self.IncidentRecordMap[SWORD_RELATEDPMRS].set(value)
        return self

    def getRelatedPMRs(self):
        return self.IncidentRecordMap[SWORD_RELATEDPMRS].getValue()

    def tRExist(self, value):
        self.IncidentRecordMap[SWORD_TREXIST].set(value)
        return self

    def getTRExist(self):
        return self.IncidentRecordMap[SWORD_TREXIST].getValue()

    def notEngineURL(self, value):
        self.IncidentRecordMap[SWORD_NOTENGINE_URL].set(value)
        return self

    def getNotEngineURL(self):
        return self.IncidentRecordMap[SWORD_NOTENGINE_URL].getValue()

    def notificationSent(self, value):
        self.IncidentRecordMap[SWORD_NOTIFICATION_SENT].set(value)
        return self

    def getNotificationSent(self):
        return self.IncidentRecordMap[SWORD_NOTIFICATION_SENT].getValue()

    def cIR1stgService(self, value):
        self.IncidentRecordMap[SWORD_CIR_1STG_SERVICE].set(value)
        return self

    def getCIR1stgService(self):
        return self.IncidentRecordMap[SWORD_CIR_1STG_SERVICE].getValue()
