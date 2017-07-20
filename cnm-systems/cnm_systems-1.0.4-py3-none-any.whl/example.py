from .services.email import EmailService


def sendmail(request):
    try:
        data = EmailService('Andrew', 'mrhieutrieu@gmail.com', 'Hieu Trieu', 'hieu@cinnamon.is') \
            .get_content_by_name('template_1') \
            .render_content(name="My Name",
                            candidate_name="Candidate Name",
                            candidate_phone="Candidate Phone",
                            candidate_email="Candidate Email",
                            admin_name="Admin Name",
                            admin_email="admin@gmail.com",
                            ) \
            .send()
    except Exception as Ex:
        print(Ex)
