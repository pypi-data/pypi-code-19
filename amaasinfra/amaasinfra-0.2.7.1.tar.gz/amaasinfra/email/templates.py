"""
Ideally this should be in the package as a resource.
"""
EMAIL_TEMPLATES = {
    "user_invitation": """<div style='font-family:Helvetica;color:#404040;min-width:320px;'> 
                            <div style='margin:auto;width:100%%;max-width:700px;min-width:300px'> 
                                <div style='background-color:white;border:solid 1px lightgrey;padding:40px;min-width:250px;'> 
                                    <img src='https://d245lrezs6dicg.cloudfront.net/dark-argomi-logo-on-white-bg.jpg' width=250> 
                                    <p> {admin_email} has invited you to join {company_name} in Argomi </p> 
                                    <a style='text-align:center;font-size:1.5em;' href="http://app-staging.argomi.com"> Join Now </a> 
                                    <p>Sincerely,</p> 
                                    <p>The Argomi Team</p> 
                                </div> 
                                <div style='text-align:center;font-size:0.75em;min-width:300px;'> 
                                    <p>Argomi&nbsp;&nbsp;&nbsp;&nbsp;600 North Bridge Road #15-02&nbsp;&nbsp;&nbsp;&nbsp;188778&nbsp;&nbsp;&nbsp;&nbsp;Singapore</p> 
                                </div> 
                            </div> 
                        </div>
                       """
}