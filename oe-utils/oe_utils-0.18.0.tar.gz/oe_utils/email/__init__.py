# -*- coding: utf-8 -*-


def get_oe_email_footer_html():
    return """
    <div style="float:left; width:100%;">
        Onroerend Erfgoed<br/>
        Phoenixgebouw  |  Koning Albert II-laan 19 bus 5  |  1210 Brussel <br/>
        <div style="width:100%">
            <div style="float:left; width:100%">
                <a href='https://www.onroerenderfgoed.be'>www.onroerenderfgoed.be</a>
            </div>
            <div style="float:left; width:100%">
                <img src="https://www.onroerenderfgoed.be/assets/img/logo-vlaanderen.png" height="100">
            </div>
        </div>
    </div>
    """


def get_oe_email_footer_plain():
    return """
    \n
    Onroerend Erfgoed\n
    Phoenixgebouw  |  Koning Albert II-laan 19 bus 5  |  1210 Brussel\n
    www.onroerenderfgoed.be\n
    \n
    """