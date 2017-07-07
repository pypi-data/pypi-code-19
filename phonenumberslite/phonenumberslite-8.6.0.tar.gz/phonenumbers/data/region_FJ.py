"""Auto-generated file, do not edit by hand. FJ metadata"""
from ..phonemetadata import NumberFormat, PhoneNumberDesc, PhoneMetadata

PHONE_METADATA_FJ = PhoneMetadata(id='FJ', country_code=679, international_prefix='0(?:0|52)',
    general_desc=PhoneNumberDesc(national_number_pattern='[35-9]\\d{6}|0\\d{10}', possible_length=(7, 11)),
    fixed_line=PhoneNumberDesc(national_number_pattern='(?:3[0-5]|6[25-7]|8[58])\\d{5}', example_number='3212345', possible_length=(7,)),
    mobile=PhoneNumberDesc(national_number_pattern='(?:5[018]|[79]\\d|8[034679])\\d{5}', example_number='7012345', possible_length=(7,)),
    toll_free=PhoneNumberDesc(national_number_pattern='0800\\d{7}', example_number='08001234567', possible_length=(11,)),
    preferred_international_prefix='00',
    number_format=[NumberFormat(pattern='(\\d{3})(\\d{4})', format='\\1 \\2', leading_digits_pattern=['[35-9]']),
        NumberFormat(pattern='(\\d{4})(\\d{3})(\\d{4})', format='\\1 \\2 \\3', leading_digits_pattern=['0'])])
