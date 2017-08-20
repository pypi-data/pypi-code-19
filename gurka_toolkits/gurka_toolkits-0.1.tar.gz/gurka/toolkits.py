DEFAULT_PREFIX = 'P'
DEFAULT_OVERFLOW = 4


def autonumber(prefix=None, overflow=None, data=None):
	if not prefix:
		prefix = DEFAULT_PREFIX

	if not overflow:
		overflow = DEFAULT_OVERFLOW

	zero = "0"
	digit = 1
	result = "{prefix}{zero}{digit}"
	if data:
		digit = int(data.split(prefix)[-1]) + 1
		zero = zero * (overflow - len(str(digit)))
		result = result.format(prefix=prefix, zero=zero, digit=digit)
	else:
		zero = zero * (overflow - digit)
		result = result.format(prefix=prefix, zero=zero, digit=digit)

	return result


def to_rupiah(number):
	number_str = str(number)
	length = len(number_str)
	result = '{:' + '{length}'.format(length=length) + ',.2f}'
	return "Rp. {currency}".format(
			currency=result.format(number)
		)


