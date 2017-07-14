"""Classes that are used to interact with the ORCID public API"""
from requests import Session
from ORCSchlange.config import Config
import pybtex.database
from ORCSchlange.bib import Date, WorkSummary


class OrcID:
    """The class that represent one orcid i.e. one member of the group."""
    
    def __init__(self, orcid, start, stop):
        """Save the id and the time in which the paper are fetched.
        
        :param orcid: The id of the member.
        :param start: The start of the time in which the paper are fetched.
        :param stop:  The end of the time in which the paper are fetched.
        """
        self.id = orcid.replace("-", "")
        self.start = Date(*start.split("-"))
        self.stop = Date(*stop.split("-")) if stop else Date(None, None, None)
    
    def get_id(self):
        """Return the id in a ORCID way: "XXXX-XXXX-XXXX-XXXX" """
        return "-".join([self.id[4 * i: 4 * (i + 1)] for i in range(4)])
    
    def __str__(self):
        """Nice string representation that contains all information"""
        return self.get_id() + ": " + str(self.start) + (" - " + str(self.stop) if self.stop else "")
    
    def __lt__(self, other):
        """Check these OrcID is smaller then an other OrcID. In respect of the id.

        :param other: The other OrcID.
        :return: True if these OrcID is smaller.
        """
        return self.id < other.id
    
    def __eq__(self, other):
        """Check if these OrcID is equal to an other OrcID. In respect of the id.

        :param other: The other OrcID.
        :return: True if the OrcIDs are equal
        """
        return self.id == other.id
    
    def __hash__(self):
        """Use the hash from self.id to hash this class"""
        return hash(self.id)


def get_date(d):
    """Function that turn a dict that contains the date in the ORCID way into a Date object.
    
    :param d: The date as dict in the ORCID way.
    :return: The date as Date object.
    """
    return Date(d["year"]["value"], d["month"]["value"] if d["month"] else None,
                d["day"]["value"] if d["day"] else None)


def create_citation(cit):
    """Create from an citation dictionary an pybtex database.
    
    :param cit: The citation dictionary
    :return: The pybtex database if a valid citation is found, None otherwise.
    """
    if cit is not None:
        if cit['citation-type'] == "BIBTEX":
            return pybtex.database.parse_string(cit['citation-value'], "bibtex")
    return None


class API:
    """The class that interact with the ORCID public api."""
    
    def __init__(self):
        """Initialize the connection to the api.
        
        Creates a connection session that takes the connection life.
        Also a read access token is requested and save in the header.
        """
        self.authurl = Config().auth
        self.baseurl = Config().api
        self.s = Session()
        self.s.headers = {'Accept': 'application/json'}
        data = {"grant_type": "client_credentials", "scope": "/read-public", "client_id": Config().client_id,
                "client_secret": Config().client_secret}
        r = self.s.request(method="post", url=self.authurl, data=data)
        self.s.headers = {'Accept': 'application/json', "Access token": r.json()["access_token"]}
    
    def get_worksums(self, orcid):
        """Get all work summaries of a specific ORCID.
        
        :param orcid: The ORCID as OrcId class.
        :return: An iteration over all work summaries of these orcid.
        """
        r = self.s.request(method="get", url="{0}/{1}/works".format(self.baseurl, orcid.get_id()))
        for work in (w["work-summary"][0] for w in r.json()["group"]):
            if work["publication-date"] is not None:
                d = get_date(work["publication-date"])
                if orcid.start <= d <= orcid.stop:
                    yield WorkSummary(orcid, work["put-code"], work["title"]["title"]["value"], d)
    
    def get_work(self, summary):
        """Get the full work data for a work summary.
        
        :param summary: The work summary.
        :return: The full data as a pybtex bibliography.
        """
        r = self.s.request(method="get", url=self.baseurl + summary.path)
        json = r.json()
        return create_citation(json['citation'])
    
    def get_works(self, orcid, works):
        """Get all the full data of a list of works that belong to a specific orcid.
        
        These function use the option to fetch upto 50 works of one orcid at the same time.
        So it is more effective then use the get_work function for every work individual.
        
        :param orcid: The orcid to which the works belong.
        :param works: The works as list of ids.
        :return: An iterator over the full works as pybtex bibliography.
        """
        step = 49
        for i in range(0, len(works), step):
            subworks = works[i:min(i + step, len(works))]
            path = "/{orc}/works/{ids}".format(orc=orcid.get_id(), ids=",".join(subworks))
            r = self.s.request(method="get", url=self.baseurl + path)
            # json = r.json()
            for cit in (work["work"]["citation"] for work in r.json()["bulk"]):
                w = create_citation(cit)
                if w is not None:
                    yield w
