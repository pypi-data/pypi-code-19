import re


class PushRadarUtils:
    """ Contains helpful methods that are used throughout the library. """

    # ------------------------------
    # Web utilities
    # ------------------------------

    @staticmethod
    def is_valid_ip(ip_address):
        """ Checks whether the given string is a valid IPv4 or IPv6 address. """
        return PushRadarUtils.is_valid_ipv4(ip_address) or PushRadarUtils.is_valid_ipv6(ip_address)

    @staticmethod
    def is_valid_ipv4(ip_address):
        """ Checks whether the given string is a valid IPv4 address. """
        pattern = re.compile(r"""
            ^
            (?:
              # Dotted variants:
              (?:
                # Decimal 1-255 (no leading 0's)
                [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
              |
                0x0*[0-9a-f]{1,2}  # Hexadecimal 0x0 - 0xFF (possible leading 0's)
              |
                0+[1-3]?[0-7]{0,2} # Octal 0 - 0377 (possible leading 0's)
              )
              (?:                  # Repeat 0-3 times, separated by a dot
                \.
                (?:
                  [3-9]\d?|2(?:5[0-5]|[0-4]?\d)?|1\d{0,2}
                |
                  0x0*[0-9a-f]{1,2}
                |
                  0+[1-3]?[0-7]{0,2}
                )
              ){0,3}
            |
              0x0*[0-9a-f]{1,8}    # Hexadecimal notation, 0x0 - 0xffffffff
            |
              0+[0-3]?[0-7]{0,10}  # Octal notation, 0 - 037777777777
            |
              # Decimal notation, 1-4294967295:
              429496729[0-5]|42949672[0-8]\d|4294967[01]\d\d|429496[0-6]\d{3}|
              42949[0-5]\d{4}|4294[0-8]\d{5}|429[0-3]\d{6}|42[0-8]\d{7}|
              4[01]\d{8}|[1-3]\d{0,9}|[4-9]\d{0,8}
            )
            $
        """, re.VERBOSE | re.IGNORECASE)
        return pattern.match(ip_address) is not None

    @staticmethod
    def is_valid_ipv6(ip_address):
        """ Checks whether the given string is a valid IPv6 address. """
        pattern = re.compile(r"""
            ^
            \s*                         # Leading whitespace
            (?!.*::.*::)                # Only a single whildcard allowed
            (?:(?!:)|:(?=:))            # Colon iff it would be part of a wildcard
            (?:                         # Repeat 6 times:
                [0-9a-f]{0,4}           #   A group of at most four hexadecimal digits
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
            ){6}                        #
            (?:                         # Either
                [0-9a-f]{0,4}           #   Another group
                (?:(?<=::)|(?<!::):)    #   Colon unless preceeded by wildcard
                [0-9a-f]{0,4}           #   Last group
                (?: (?<=::)             #   Colon iff preceeded by exacly one colon
                 |  (?<!:)              #
                 |  (?<=:) (?<!::) :    #
                 )                      # OR
             |                          #   A v4 address with NO leading zeros 
                (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                (?: \.
                    (?:25[0-4]|2[0-4]\d|1\d\d|[1-9]?\d)
                ){3}
            )
            \s*                         # Trailing whitespace
            $
        """, re.VERBOSE | re.IGNORECASE | re.DOTALL)
        return pattern.match(ip_address) is not None

    # ------------------------------
    # Collection utilities
    # ------------------------------

    @staticmethod
    def keys_where_value(dictionary, value):
        """ Searches the given dictionary for values matching the value provided, and returns the keys of those
        elements. """
        # Select the keys
        keys = []
        for x in dictionary:
            if dictionary[x].strip() == value.strip():
                keys.append(x)
        # Return the keys
        return keys

    # ------------------------------
    # Location utilities
    # ------------------------------

    @staticmethod
    def get_countries():
        """ Gets a dictionary that associates ISO 3166-1 alpha-2 country codes with country names. """
        # Return the dictionary
        return {"AD": "Andorra",
                "AE": "United Arab Emirates",
                "AF": "Afghanistan",
                "AG": "Antigua and Barbuda",
                "AI": "Anguilla",
                "AL": "Albania",
                "AM": "Armenia",
                "AO": "Angola",
                "AQ": "Antarctica",
                "AR": "Argentina",
                "AS": "American Samoa",
                "AT": "Austria",
                "AU": "Australia",
                "AW": "Aruba",
                "AX": "Åland Islands",
                "AZ": "Azerbaijan",
                "BA": "Bosnia and Herzegovina",
                "BB": "Barbados",
                "BD": "Bangladesh",
                "BE": "Belgium",
                "BF": "Burkina Faso",
                "BG": "Bulgaria",
                "BH": "Bahrain",
                "BI": "Burundi",
                "BJ": "Benin",
                "BL": "Saint Barthélemy",
                "BM": "Bermuda",
                "BN": "Brunei Darussalam",
                "BO": "Bolivia, Plurinational State of",
                "BQ": "Bonaire, Sint Eustatius and Saba",
                "BR": "Brazil",
                "BS": "Bahamas",
                "BT": "Bhutan",
                "BV": "Bouvet Island",
                "BW": "Botswana",
                "BY": "Belarus",
                "BZ": "Belize",
                "CA": "Canada",
                "CC": "Cocos (Keeling) Islands",
                "CD": "Congo, the Democratic Republic of the",
                "CF": "Central African Republic",
                "CG": "Congo",
                "CH": "Switzerland",
                "CI": "Côte d'Ivoire",
                "CK": "Cook Islands",
                "CL": "Chile",
                "CM": "Cameroon",
                "CN": "China",
                "CO": "Colombia",
                "CR": "Costa Rica",
                "CU": "Cuba",
                "CV": "Cabo Verde",
                "CW": "Curaçao",
                "CX": "Christmas Island",
                "CY": "Cyprus",
                "CZ": "Czechia",
                "DE": "Germany",
                "DJ": "Djibouti",
                "DK": "Denmark",
                "DM": "Dominica",
                "DO": "Dominican Republic",
                "DZ": "Algeria",
                "EC": "Ecuador",
                "EE": "Estonia",
                "EG": "Egypt",
                "EH": "Western Sahara",
                "ER": "Eritrea",
                "ES": "Spain",
                "ET": "Ethiopia",
                "FI": "Finland",
                "FJ": "Fiji",
                "FK": "Falkland Islands (Malvinas)",
                "FM": "Micronesia, Federated States of",
                "FO": "Faroe Islands",
                "FR": "France",
                "GA": "Gabon",
                "GB": "United Kingdom of Great Britain and Northern Ireland",
                "GD": "Grenada",
                "GE": "Georgia",
                "GF": "French Guiana",
                "GG": "Guernsey",
                "GH": "Ghana",
                "GI": "Gibraltar",
                "GL": "Greenland",
                "GM": "Gambia",
                "GN": "Guinea",
                "GP": "Guadeloupe",
                "GQ": "Equatorial Guinea",
                "GR": "Greece",
                "GS": "South Georgia and the South Sandwich Islands",
                "GT": "Guatemala",
                "GU": "Guam",
                "GW": "Guinea-Bissau",
                "GY": "Guyana",
                "HK": "Hong Kong",
                "HM": "Heard Island and McDonald Islands",
                "HN": "Honduras",
                "HR": "Croatia",
                "HT": "Haiti",
                "HU": "Hungary",
                "ID": "Indonesia",
                "IE": "Ireland",
                "IL": "Israel",
                "IM": "Isle of Man",
                "IN": "India",
                "IO": "British Indian Ocean Territory",
                "IQ": "Iraq",
                "IR": "Iran, Islamic Republic of",
                "IS": "Iceland",
                "IT": "Italy",
                "JE": "Jersey",
                "JM": "Jamaica",
                "JO": "Jordan",
                "JP": "Japan",
                "KE": "Kenya",
                "KG": "Kyrgyzstan",
                "KH": "Cambodia",
                "KI": "Kiribati",
                "KM": "Comoros",
                "KN": "Saint Kitts and Nevis",
                "KP": "Korea, Democratic People's Republic of",
                "KR": "Korea, Republic of",
                "KW": "Kuwait",
                "KY": "Cayman Islands",
                "KZ": "Kazakhstan",
                "LA": "Lao People's Democratic Republic",
                "LB": "Lebanon",
                "LC": "Saint Lucia",
                "LI": "Liechtenstein",
                "LK": "Sri Lanka",
                "LR": "Liberia",
                "LS": "Lesotho",
                "LT": "Lithuania",
                "LU": "Luxembourg",
                "LV": "Latvia",
                "LY": "Libya",
                "MA": "Morocco",
                "MC": "Monaco",
                "MD": "Moldova, Republic of",
                "ME": "Montenegro",
                "MF": "Saint Martin (French part)",
                "MG": "Madagascar",
                "MH": "Marshall Islands",
                "MK": "Macedonia, the former Yugoslav Republic of",
                "ML": "Mali",
                "MM": "Myanmar",
                "MN": "Mongolia",
                "MO": "Macao",
                "MP": "Northern Mariana Islands",
                "MQ": "Martinique",
                "MR": "Mauritania",
                "MS": "Montserrat",
                "MT": "Malta",
                "MU": "Mauritius",
                "MV": "Maldives",
                "MW": "Malawi",
                "MX": "Mexico",
                "MY": "Malaysia",
                "MZ": "Mozambique",
                "NA": "Namibia",
                "NC": "New Caledonia",
                "NE": "Niger",
                "NF": "Norfolk Island",
                "NG": "Nigeria",
                "NI": "Nicaragua",
                "NL": "Netherlands",
                "NO": "Norway",
                "NP": "Nepal",
                "NR": "Nauru",
                "NU": "Niue",
                "NZ": "New Zealand",
                "OM": "Oman",
                "PA": "Panama",
                "PE": "Peru",
                "PF": "French Polynesia",
                "PG": "Papua New Guinea",
                "PH": "Philippines",
                "PK": "Pakistan",
                "PL": "Poland",
                "PM": "Saint Pierre and Miquelon",
                "PN": "Pitcairn",
                "PR": "Puerto Rico",
                "PS": "Palestine, State of",
                "PT": "Portugal",
                "PW": "Palau",
                "PY": "Paraguay",
                "QA": "Qatar",
                "RE": "Réunion",
                "RO": "Romania",
                "RS": "Serbia",
                "RU": "Russian Federation",
                "RW": "Rwanda",
                "SA": "Saudi Arabia",
                "SB": "Solomon Islands",
                "SC": "Seychelles",
                "SD": "Sudan",
                "SE": "Sweden",
                "SG": "Singapore",
                "SH": "Saint Helena, Ascension and Tristan da Cunha",
                "SI": "Slovenia",
                "SJ": "Svalbard and Jan Mayen",
                "SK": "Slovakia",
                "SL": "Sierra Leone",
                "SM": "San Marino",
                "SN": "Senegal",
                "SO": "Somalia",
                "SR": "Suriname",
                "SS": "South Sudan",
                "ST": "Sao Tome and Principe",
                "SV": "El Salvador",
                "SX": "Sint Maarten (Dutch part)",
                "SY": "Syrian Arab Republic",
                "SZ": "Swaziland",
                "TC": "Turks and Caicos Islands",
                "TD": "Chad",
                "TF": "French Southern Territories",
                "TG": "Togo",
                "TH": "Thailand",
                "TJ": "Tajikistan",
                "TK": "Tokelau",
                "TL": "Timor-Leste",
                "TM": "Turkmenistan",
                "TN": "Tunisia",
                "TO": "Tonga",
                "TR": "Turkey",
                "TT": "Trinidad and Tobago",
                "TV": "Tuvalu",
                "TW": "Taiwan, Province of China",
                "TZ": "Tanzania, United Republic of",
                "UA": "Ukraine",
                "UG": "Uganda",
                "UM": "United States Minor Outlying Islands",
                "US": "United States of America",
                "UY": "Uruguay",
                "UZ": "Uzbekistan",
                "VA": "Holy See",
                "VC": "Saint Vincent and the Grenadines",
                "VE": "Venezuela, Bolivarian Republic of",
                "VG": "Virgin Islands, British",
                "VI": "Virgin Islands, U.S.",
                "VN": "Viet Nam",
                "VU": "Vanuatu",
                "WF": "Wallis and Futuna",
                "WS": "Samoa",
                "YE": "Yemen",
                "YT": "Mayotte",
                "ZA": "South Africa",
                "ZM": "Zambia",
                "ZW": "Zimbabwe"}

    @staticmethod
    def get_countries_continent_association():
        """ Gets a dictionary that associates ISO 3166-1 alpha-2 country codes with two-letter continent codes. """
        # Return the dictionary
        return {"AD": "EU",
                "AE": "AS",
                "AF": "AS",
                "AG": "NA",
                "AI": "NA",
                "AL": "EU",
                "AM": "AS",
                "AO": "AF",
                "AQ": "AN",
                "AR": "SA",
                "AS": "OC",
                "AT": "EU",
                "AU": "OC",
                "AW": "NA",
                "AX": "EU",
                "AZ": "AS",
                "BA": "EU",
                "BB": "NA",
                "BD": "AS",
                "BE": "EU",
                "BF": "AF",
                "BG": "EU",
                "BH": "AS",
                "BI": "AF",
                "BJ": "AF",
                "BL": "NA",
                "BM": "NA",
                "BN": "AS",
                "BO": "SA",
                "BR": "SA",
                "BS": "NA",
                "BT": "AS",
                "BV": "AN",
                "BW": "AF",
                "BY": "EU",
                "BZ": "NA",
                "CA": "NA",
                "CC": "AS",
                "CD": "AF",
                "CF": "AF",
                "CG": "AF",
                "CH": "EU",
                "CI": "AF",
                "CK": "OC",
                "CL": "SA",
                "CM": "AF",
                "CN": "AS",
                "CO": "SA",
                "CR": "NA",
                "CU": "NA",
                "CV": "AF",
                "CX": "AS",
                "CY": "AS",
                "CZ": "EU",
                "DE": "EU",
                "DJ": "AF",
                "DK": "EU",
                "DM": "NA",
                "DO": "NA",
                "DZ": "AF",
                "EC": "SA",
                "EE": "EU",
                "EG": "AF",
                "EH": "AF",
                "ER": "AF",
                "ES": "EU",
                "ET": "AF",
                "FI": "EU",
                "FJ": "OC",
                "FK": "SA",
                "FM": "OC",
                "FO": "EU",
                "FR": "EU",
                "GA": "AF",
                "GB": "EU",
                "GD": "NA",
                "GE": "AS",
                "GF": "SA",
                "GG": "EU",
                "GH": "AF",
                "GI": "EU",
                "GL": "NA",
                "GM": "AF",
                "GN": "AF",
                "GP": "NA",
                "GQ": "AF",
                "GR": "EU",
                "GS": "AN",
                "GT": "NA",
                "GU": "OC",
                "GW": "AF",
                "GY": "SA",
                "HK": "AS",
                "HM": "AN",
                "HN": "NA",
                "HR": "EU",
                "HT": "NA",
                "HU": "EU",
                "ID": "AS",
                "IE": "EU",
                "IL": "AS",
                "IM": "EU",
                "IN": "AS",
                "IO": "AS",
                "IQ": "AS",
                "IR": "AS",
                "IS": "EU",
                "IT": "EU",
                "JE": "EU",
                "JM": "NA",
                "JO": "AS",
                "JP": "AS",
                "KE": "AF",
                "KG": "AS",
                "KH": "AS",
                "KI": "OC",
                "KM": "AF",
                "KN": "NA",
                "KP": "AS",
                "KR": "AS",
                "KW": "AS",
                "KY": "NA",
                "KZ": "AS",
                "LA": "AS",
                "LB": "AS",
                "LC": "NA",
                "LI": "EU",
                "LK": "AS",
                "LR": "AF",
                "LS": "AF",
                "LT": "EU",
                "LU": "EU",
                "LV": "EU",
                "LY": "AF",
                "MA": "AF",
                "MC": "EU",
                "MD": "EU",
                "ME": "EU",
                "MF": "NA",
                "MG": "AF",
                "MH": "OC",
                "MK": "EU",
                "ML": "AF",
                "MM": "AS",
                "MN": "AS",
                "MO": "AS",
                "MP": "OC",
                "MQ": "NA",
                "MR": "AF",
                "MS": "NA",
                "MT": "EU",
                "MU": "AF",
                "MV": "AS",
                "MW": "AF",
                "MX": "NA",
                "MY": "AS",
                "MZ": "AF",
                "NA": "AF",
                "NC": "OC",
                "NE": "AF",
                "NF": "OC",
                "NG": "AF",
                "NI": "NA",
                "NL": "EU",
                "NO": "EU",
                "NP": "AS",
                "NR": "OC",
                "NU": "OC",
                "NZ": "OC",
                "OM": "AS",
                "PA": "NA",
                "PE": "SA",
                "PF": "OC",
                "PG": "OC",
                "PH": "AS",
                "PK": "AS",
                "PL": "EU",
                "PM": "NA",
                "PN": "OC",
                "PR": "NA",
                "PS": "AS",
                "PT": "EU",
                "PW": "OC",
                "PY": "SA",
                "QA": "AS",
                "RE": "AF",
                "RO": "EU",
                "RS": "EU",
                "RU": "EU",
                "RW": "AF",
                "SA": "AS",
                "SB": "OC",
                "SC": "AF",
                "SD": "AF",
                "SE": "EU",
                "SG": "AS",
                "SH": "AF",
                "SI": "EU",
                "SJ": "EU",
                "SK": "EU",
                "SL": "AF",
                "SM": "EU",
                "SN": "AF",
                "SO": "AF",
                "SR": "SA",
                "ST": "AF",
                "SV": "NA",
                "SY": "AS",
                "SZ": "AF",
                "TC": "NA",
                "TD": "AF",
                "TF": "AN",
                "TG": "AF",
                "TH": "AS",
                "TJ": "AS",
                "TK": "OC",
                "TL": "AS",
                "TM": "AS",
                "TN": "AF",
                "TO": "OC",
                "TR": "EU",
                "TT": "NA",
                "TV": "OC",
                "TW": "AS",
                "TZ": "AF",
                "UA": "EU",
                "UG": "AF",
                "UM": "OC",
                "US": "NA",
                "UY": "SA",
                "UZ": "AS",
                "VA": "EU",
                "VC": "NA",
                "VE": "SA",
                "VG": "NA",
                "VI": "NA",
                "VN": "AS",
                "VU": "OC",
                "WF": "OC",
                "WS": "OC",
                "YE": "AS",
                "YT": "AF",
                "ZA": "AF",
                "ZM": "AF",
                "ZW": "AF"}

    @staticmethod
    def get_countries_from_continent(continent_code):
        """ Gets a list of ISO 3166-1 alpha-2 country codes, corresponding to countries located within the given
        continent. """
        # Convert the continent code to uppercase
        continent_code = continent_code.strip().upper()
        # Get the country codes where the value equals the continent code
        return PushRadarUtils.keys_where_value(PushRadarUtils.get_countries_continent_association(), continent_code)
