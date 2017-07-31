from restclients_core import models


class GradingStatus(models.Model):
    section_id = models.CharField(max_length=256)
    grading_period_open = models.NullBooleanField(default=False)
    no_grades_submitted = models.NullBooleanField(default=True)
    grading_status = models.CharField(max_length=64)
    display_name = models.CharField(max_length=64)
    section_url = models.CharField(max_length=256)
    status_url = models.CharField(max_length=256)
    submitted_count = models.PositiveSmallIntegerField(null=True)
    unsubmitted_count = models.PositiveSmallIntegerField(null=True)
    submitted_by = models.CharField(max_length=128, null=True)
    submitted_date = models.DateTimeField(blank=True, null=True)
    accepted_date = models.DateTimeField(blank=True, null=True)

    def json_data(self):
        return {
            'section_id': self.section_id,
            'grading_period_open': self.grading_period_open,
            'no_grades_submitted': self.no_grades_submitted,
            'grading_status': self.grading_status,
            'display_name': self.display_name,
            'section_url': self.section_url,
            'status_url': self.status_url,
            'submitted_count': self.submitted_count,
            'unsubmitted_count': self.unsubmitted_count,
            'submitted_by': self.submitted_by,
            'submitted_date': (str(self.submitted_date)
                               if self.submitted_date else None),
            'accepted_date': (str(self.accepted_date)
                              if self.accepted_date else None),
        }
