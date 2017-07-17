# coding: utf-8
from rest_framework.reverse import reverse

from .choices import (
    QUESTION_TYPE_RADIO,
    QUESTION_TYPE_SELECT,
    QUESTION_TYPE_CHECKBOXES,
    QUESTION_TYPE_GRID
)


def answer_question(survey,
                    content_type_id,
                    object_id,
                    question_name,
                    value):
    """
    Answer a question for a single survey taken.

    this method should take care of it all.
    """
    from .models import (
        Answer,
        OtherAnswer,
        SurveyedObject,
    )
    try:
        new_survey = False
        surveyed = SurveyedObject.objects.get(
            content_type_id=content_type_id,
            object_id=object_id,
            survey_id=survey.pk
        )
    except SurveyedObject.DoesNotExist:
        new_survey = True
        surveyed = SurveyedObject(
            content_type_id=content_type_id,
            object_id=object_id,
            survey_id=survey.pk
        )

    question = get_question_by_name(question_name)
    if not question:
        raise ValueError('question does not exist')

    if question.survey_id != survey.pk:
        raise ValueError('question does not belong to this questionary')

    # possibilities
    # new survey and new question
    # old survey and new question
    # old survey and old question
    # this determines what is the case and updates/creates the answer value
    if not new_survey:
        # old survey
        try:
            # old question
            answer = Answer.objects.get(
                surveyed_id=surveyed.pk,
                question_id=question.pk
            )
        except Answer.DoesNotExist:
            # new question
            answer = Answer(
                surveyed=surveyed,
                question=question
            )
    else:
        # new survey and new question
        surveyed.save()
        answer = Answer(
            surveyed=surveyed,
            question=question
        )

    answer.value = value

    if question.other_token:
        if isinstance(value, basestring) and value not in question.options:
            answer.value = question.other_token
            create_other_answer(question, value)

        if isinstance(value, list):
            other_value = set(value).difference(set(question.options)).pop()
            value.remove(other_value)
            answer.value = value
            create_other_answer(question, other_value)
    
    answer.save()

    return answer


def create_other_answer(question, value):
    from .models import OtherAnswer
    try:
        OtherAnswer.objects.get(value=value.upper())
    except OtherAnswer.DoesNotExist:
        OtherAnswer.objects.create(
            question=question,
            value=value.upper()
        )


def reverse_list(request, view_name, field, obj):

    """
    reverses a list name
    """
    return reverse(view_name, request=request) + '?{0}={1}'.format(field, obj)


def build_survey_data(survey):
    """
    From a survey, build survey
    data.

    survey_data is a dict with all
    the options, ready for rendering
    """
    return {
        'schema': build_schema(survey),
        'fieldsets': build_fieldsets(survey)
    }


def build_answer(answer):

    return {build_question_name(answer.question): answer.value}


def build_answers(surveyed):

    answer_data = {}
    for a in surveyed.answers:
        answer_data.update(build_answer(a))
    return answer_data


def get_question_by_name(question_name):

    from .models import Question
    if question_name.startswith('q'):
        return Question.objects.get(id=int(question_name[1:]))

    return None


def build_question_name(question):

    return 'q' + str(question.id)


def build_fieldset_name(section):
    return 'f' + str(section.id)


def build_question(question):
    question_data = {}
    question_name = build_question_name(question)
    question_data[question_name] = {
        'name': question_name,
        'title': question.text,
        'help': question.help,
        'type': question.type,
        'options': question.options
    }
    if question.type in (QUESTION_TYPE_RADIO,
                         QUESTION_TYPE_SELECT,
                         QUESTION_TYPE_CHECKBOXES):

        question_data[question_name]['options'] = question.options['values']
        if question.other_token:
            question_data[question_name]['options'].append(question.other_token)
            question_data[question_name]['otherToken'] = question.other_token

    if question.type == QUESTION_TYPE_GRID:
        question_data[question_name]['columns'] = question.options.get('columns')
        question_data[question_name]['rows'] = question.options.get('rows')

    if question.validators:
        question_data[question_name]['validators'] = question.validators

    if question.parent:
        question_data[question_name]['parent'] = build_question_name(question.parent)
        question_data[question_name]['parent_value'] = question.parent_value

    return question_data


def build_schema(survey):
    schema = {}
    questions = survey.questions.all()
    for q in questions:
        schema.update(build_question(q))
    return schema


def build_fieldsets(survey):
    fieldsets = []
    sections = survey.sections.all()
    for section in sections:
        fieldsets.append(
            {
                'legend': section.title,
                'fields': [build_question_name(q) for q in section.questions.all()],
                'name': build_fieldset_name(section)
            }
        )
    return fieldsets
