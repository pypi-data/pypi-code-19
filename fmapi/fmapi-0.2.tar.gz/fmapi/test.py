"API Client Tests"

import unittest 
import fmapi

class BasicTestSuite(unittest.TestCase):
    """Basic test cases."""

    def test_gets(self): #pylint:disable=R0915
        "Test everything"
        client = fmapi.Client(url_base="http://127.0.0.1:5000/api")

        # States
        states = client.get_states()
        assert states
        state = states[0]
        print(state.__dict__)

        # Counties
        counties = client.get_counties(state.state_code)
        assert counties
        county = counties[0]
        print(county.__dict__)

        # Tracts
        tracts = client.get_tracts("12", "001")
        assert tracts
        tract = tracts[0]
        print(tract.__dict__)

        # Blocks
        blocks = client.get_blocks("12", "001", "000200")
        assert blocks
        block = blocks[0]
        print(block.__dict__)

        # Tract Demographic Profile
        dp = client.get_tract_profile("12", "001", "000200")
        assert dp
        print(dp.__dict__)

        # Basic Demographics by County
        bd = client.get_basic_county("12", "097")
        assert bd
        print(bd.__dict__)

        # Zip Code Tabulation Areas
        zctas = client.get_zctas("12")
        assert zctas
        z = zctas[0]
        print(z.__dict__)

        # Basic Demographics by Tract
        bd = client.get_basic_tract("12", "001", "000301")
        assert bd
        print(bd.__dict__)

        # Basic Demographics by Block
        bd = client.get_basic_block("12", "001", "000200", "1001")
        assert bd
        print(bd.__dict__)

        # Cities
        cities = client.get_cities("FL")
        assert cities
        print(cities[0].__dict__)

        # SF1 File 01 (Total Population)
        sf = client.get_sf101("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 File 03
        sf = client.get_sf103("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 File 04
        sf = client.get_sf104("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 File 05
        sf = client.get_sf105("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 File 06
        sf = client.get_sf106("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 File 07
        sf = client.get_sf107("12", "001", "000200", "1001")
        assert sf
        print(sf.__dict__)

        # SF1 Docs
        docs = client.get_sf1_docs("03")
        assert docs
        print(docs[0].__dict__)

        # Geocode
        latlon = client.geocode("1415 W Oak St, Kissimmee, FL 34741")
        assert latlon
        print(latlon.__dict__)

        # Reverse Geocode 
        addr = client.revgeocode("28.30139130", "-81.41856570")
        assert addr
        print(addr.__dict__)


if __name__ == '__main__':
    unittest.main()
    
