#!/usr/bin/python3
import os
import pickle
import sys

from indic_transliteration import sanscript

from jyotisha.panchangam.spatio_temporal import City, Panchangam
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(levelname)s: %(asctime)s {%(filename)s:%(lineno)d}: %(message)s "
)



CODE_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))


def computeIcsCalendar(self):
    with open(os.path.join(CODE_ROOT, 'panchangam/data/festival_rules.json')) as festivals_data:
        festival_rules = json.load(festivals_data)

    self.ics_calendar = Calendar()
    uid_list = []

    alarm = Alarm()
    alarm.add('action', 'DISPLAY')
    alarm.add('trigger', timedelta(hours=-4))  # default alarm, with a 4 hour reminder

    BASE_URL = "http://adyatithih.wordpress.com/"

    for d in range(1, jyotisha.panchangam.temporal.MAX_SZ - 1):
        [y, m, dt, t] = swe.revjul(self.jd_start + d - 1)

        if len(self.festivals[d]) > 0:
            # Eliminate repeat festivals on the same day, and keep the list arbitrarily sorted
            self.festivals[d] = sorted(list(set(self.festivals[d])))
            summary_text = self.festivals[d]
            # this will work whether we have one or more events on the same day
            for stext in sorted(summary_text):
                desc = ''
                page_id = ''
                event = Event()
                if stext == 'kRttikA-maNDala-pArAyaNam':
                    event.add('summary', jyotisha.custom_transliteration.tr(stext.replace('-', ' '), self.script))
                    fest_num_loc = stext.find('#')
                    if fest_num_loc != -1:
                        stext = stext[:fest_num_loc - 2]  # Two more chars dropped, -\
                    event.add('dtstart', date(y, m, dt))
                    event.add('dtend', (datetime(y, m, dt) + timedelta(48)).date())

                    if stext in festival_rules:
                        desc = festival_rules[stext]['Short Description'] + '\n\n' + \
                               jyotisha.custom_transliteration.tr(festival_rules[stext]['Shloka'], self.script, False) + \
                               '\n\n'
                        if 'URL' in festival_rules[stext]:
                            page_id = festival_rules[stext]['URL']
                        else:
                            sys.stderr.write('No URL found for festival %s!\n' % stext)
                    else:
                        sys.stderr.write('No description found for festival %s!\n' % stext)
                    desc += BASE_URL + \
                            page_id.rstrip('-1234567890').rstrip('0123456789{}\\#')
                    uid = '%s-%d' % (page_id, y)

                    event.add_component(alarm)
                    event.add('description', desc.strip())
                    uid_list.append(uid)
                    event.add('uid', uid)
                    event['X-MICROSOFT-CDO-ALLDAYEVENT'] = 'TRUE'
                    event['TRANSP'] = 'TRANSPARENT'
                    event['X-MICROSOFT-CDO-BUSYSTATUS'] = 'FREE'
                    self.ics_calendar.add_component(event)
                elif stext.find('RIGHTarrow') != -1:
                    # It's a grahanam/yogam, with a start and end time
                    if stext.find('{}') != -1:
                        # Starting or ending time is empty, e.g. harivasara, so no ICS entry
                        continue
                    [stext, t1, arrow, t2] = stext.split('\\')
                    stext = stext.strip('-')
                    event.add('summary', jyotisha.custom_transliteration.tr(stext, self.script))
                    # we know that t1 is something like 'textsf{hh:mm(+1)}{'
                    # so we know the exact positions of min and hour
                    if t1[12] == '(':  # (+1), next day
                        event.add('dtstart', datetime(y, m, dt, int(t1[7:9]), int(t1[10:12]),
                                                      tzinfo=tz(self.city.timezone)) + timedelta(1))
                    else:
                        event.add('dtstart', datetime(y, m, dt, int(t1[7:9]), int(t1[10:12]),
                                                      tzinfo=tz(self.city.timezone)))
                    if t2[12] == '(':  # (+1), next day
                        event.add('dtend', datetime(y, m, dt, int(t2[7:9]), int(t2[10:12]),
                                                    tzinfo=tz(self.city.timezone)) + timedelta(1))
                    else:
                        event.add('dtend', datetime(y, m, dt, int(t2[7:9]), int(t2[10:12]),
                                                    tzinfo=tz(self.city.timezone)))

                    if stext in festival_rules:
                        desc = festival_rules[stext]['Short Description'] + '\n\n' + \
                               jyotisha.custom_transliteration.tr(festival_rules[stext]['Shloka'], self.script, False) + '\n\n'
                        if 'URL' in festival_rules[stext]:
                            page_id = festival_rules[stext]['URL']
                        else:
                            sys.stderr.write('No URL found for festival %s!\n' % stext)
                    else:
                        sys.stderr.write('No description found for festival %s!\n' % stext)

                    desc += BASE_URL + page_id
                    event.add('description', desc.strip())
                    uid = '%s-%d-%02d' % (page_id, y, m)
                    if uid not in uid_list:
                        uid_list.append(uid)
                    else:
                        uid = '%s-%d-%02d-%02d' % (page_id, y, m, dt)
                        uid_list.append(uid)
                    event.add('uid', uid)
                    event.add_component(alarm)
                    self.ics_calendar.add_component(event)
                elif stext.find('samApanam') != -1:
                    # It's an ending event
                    event.add('summary', jyotisha.custom_transliteration.tr(re.sub('.-samApanam',
                                                                                   '-samApanam', stext), self.script))
                    event.add('dtstart', date(y, m, dt))
                    event.add('dtend', (datetime(y, m, dt) + timedelta(1)).date())

                    if stext in festival_rules:
                        desc = festival_rules[stext]['Short Description'] + '\n\n' + \
                               jyotisha.custom_transliteration.tr(festival_rules[stext]['Shloka'], self.script, False) + \
                               '\n\n'
                        if 'URL' in festival_rules[stext]:
                            page_id = festival_rules[stext]['URL']
                        else:
                            sys.stderr.write('No URL found for festival %s!\n' % stext)
                    else:
                        sys.stderr.write('No description found for festival %s!\n' % stext)

                    desc += BASE_URL + page_id.rstrip('-1234567890').rstrip('0123456789{}\\#')
                    # print(event)
                    event.add_component(alarm)
                    event.add('description', desc.strip())
                    uid = '%s-%d-%02d' % (page_id, y, m)
                    if uid not in uid_list:
                        uid_list.append(uid)
                    else:
                        uid = '%s-%d-%02d-%02d' % (page_id, y, m, dt)
                        uid_list.append(uid)
                    event.add('uid', uid)
                    event['X-MICROSOFT-CDO-ALLDAYEVENT'] = 'TRUE'
                    event['TRANSP'] = 'TRANSPARENT'
                    event['X-MICROSOFT-CDO-BUSYSTATUS'] = 'FREE'
                    self.ics_calendar.add_component(event)

                    # Find start and add entire event as well
                    desc = ''
                    page_id = page_id.replace('-samapanam', '')
                    event = Event()
                    check_d = d
                    stext_start = stext.replace('samApanam', 'ArambhaH')
                    # print(stext_start)
                    while check_d > 1:
                        check_d -= 1
                        if stext_start in self.festivals[check_d]:
                            # print(self.festivals[check_d])
                            start_d = check_d
                            break

                    event.add('summary', jyotisha.custom_transliteration.tr(stext.replace(
                        'samApanam', '').replace('-', ' '), self.script))
                    event.add('dtstart', (datetime(y, m, dt) - timedelta(d - start_d)).date())
                    event.add('dtend', (datetime(y, m, dt) + timedelta(1)).date())

                    desc += BASE_URL + page_id.rstrip('-1234567890').rstrip('0123456789{}\\#')
                    # print(event)
                    event.add_component(alarm)
                    event.add('description', desc.strip())
                    uid = '%s-%d-%02d' % (page_id, y, m)
                    if uid not in uid_list:
                        uid_list.append(uid)
                    else:
                        uid = '%s-%d-%02d-%02d' % (page_id, y, m, dt)
                        uid_list.append(uid)
                    event.add('uid', uid)
                    event['X-MICROSOFT-CDO-ALLDAYEVENT'] = 'TRUE'
                    event['TRANSP'] = 'TRANSPARENT'
                    event['X-MICROSOFT-CDO-BUSYSTATUS'] = 'FREE'
                    self.ics_calendar.add_component(event)

                else:
                    event.add('summary', jyotisha.custom_transliteration.tr(re.sub('.-ArambhaH', '-ArambhaH', stext).replace('-', ' ').replace('\#', '#'), self.script))
                    fest_num_loc = stext.find('#')
                    if fest_num_loc != -1:
                        stext = stext[:fest_num_loc - 2]  # Two more chars dropped, -\
                    event.add('dtstart', date(y, m, dt))
                    event.add('dtend', (datetime(y, m, dt) + timedelta(1)).date())

                    if stext.find('EkAdazI') == -1:
                        if stext in festival_rules:
                            desc = festival_rules[stext]['Short Description'] + '\n\n' + \
                                   jyotisha.custom_transliteration.tr(festival_rules[stext]['Shloka'], self.script, False) + \
                                   '\n\n'
                            if 'URL' in festival_rules[stext]:
                                page_id = festival_rules[stext]['URL']
                            else:
                                sys.stderr.write('No URL found for festival %s!\n' % stext)
                        else:
                            sys.stderr.write('No description found for festival %s!\n' % stext)
                        desc += BASE_URL + \
                                page_id.rstrip('-1234567890').rstrip('0123456789{}\\#')
                        uid = '%s-%d-%02d' % (page_id, y, m)
                    else:
                        # Handle ekadashi descriptions differently
                        ekad = '-'.join(stext.split('-')[1:])  # get rid of sarva etc. prefix!
                        if ekad in festival_rules:
                            desc = festival_rules[ekad]['Short Description'] + '\n\n' + \
                                   jyotisha.custom_transliteration.tr(festival_rules[ekad]['Shloka'], self.script) + '\n\n'
                            if 'URL' in festival_rules[ekad]:
                                page_id = festival_rules[ekad]['URL']
                            else:
                                sys.stderr.write('No URL found for festival %s!\n' % stext)
                        else:
                            sys.stderr.write('No description found for festival %s!\n' % ekad)
                        desc += '\n' + BASE_URL + page_id
                        pref = jyotisha.custom_transliteration.romanise(sanscript.transliterate(
                            stext.split('-')[0],
                            sanscript.HK, sanscript.IAST)) + "-"
                        uid = '%s-%d-%02d' % (pref + page_id, y, m)
                    # print(page_id)
                    event.add_component(alarm)
                    event.add('description', desc.strip())
                    if uid not in uid_list:
                        uid_list.append(uid)
                    else:
                        uid = '%s-%d-%02d-%02d' % (page_id, y, m, dt)
                        uid_list.append(uid)
                    event.add('uid', uid)
                    event['X-MICROSOFT-CDO-ALLDAYEVENT'] = 'TRUE'
                    event['TRANSP'] = 'TRANSPARENT'
                    event['X-MICROSOFT-CDO-BUSYSTATUS'] = 'FREE'
                    self.ics_calendar.add_component(event)

        if m == 12 and dt == 31:
            break

def writeIcsCalendar(self, fname):
    ics_calendar_file = open(fname, 'wb')
    ics_calendar_file.write(self.ics_calendar.to_ical())
    ics_calendar_file.close()

def writeDebugLog(self):
    log_file = open('cal-%4d-%s-log.txt' % (self.year, self.city.name), 'w')
    # helper_functions.MAX_SZ = 368
    for d in range(1, jyotisha.panchangam.temporal.MAX_SZ - 1):
        jd = self.jd_start - 1 + d
        [y, m, dt, t] = swe.revjul(jd)
        longitude_sun_sunset = swe.calc_ut(
            self.jd_sunset[d], swe.SUN)[0] - \
                               swe.get_ayanamsa(self.jd_sunset[d])
        log_data = '%02d-%02d-%4d\t[%3d]\tsun_rashi=%8.3f\ttithi=%8.3f\tsolar_month\
        =%2d\tlunar_month=%4.1f\n' % (dt, m, y, d, (longitude_sun_sunset % 360) / 30.0,
                                      jyotisha.panchangam.temporal.get_angam_float(self.jd_sunrise[d],
                                                                                   jyotisha.panchangam.temporal.TITHI, ayanamsha_id=self.ayanamsha_id),
                                      self.solar_month[d], self.lunar_month[d])
        log_file.write(log_data)



def main():
    [city_name, latitude, longitude, tz] = sys.argv[1:5]
    year = int(sys.argv[5])

    if len(sys.argv) == 7:
        script = sys.argv[6]
    else:
        script = sanscript.IAST  # Default script is IAST for writing calendar

    city = City(city_name, latitude, longitude, tz)

    panchangam = Panchangam(city=city, year=year, script=script)

    fname_det = os.path.join(CODE_ROOT, 'data/precomputed/%s-%s-detailed.json' % (city_name, year))
    fname = os.path.join(CODE_ROOT, 'data/precomputed/%s-%s.json' % (city_name, year))

    if os.path.isfile(fname):
        # Load pickle, do not compute!
        with open(fname, 'rb') as f:
            panchangam = pickle.load(f)
        sys.stderr.write('Loaded pre-computed panchangam from %s.\n' % fname)
    elif os.path.isfile(fname_det):
        # Load pickle, do not compute!
        with open(fname_det, 'rb') as f:
            panchangam = pickle.load(f)
        sys.stderr.write('Loaded pre-computed panchangam from %s.\n' % fname)
    else:
        sys.stderr.write('No precomputed data available. Computing panchangam... ')
        sys.stderr.flush()
        panchangam = Panchangam(city=city, year=year, script=script)
        panchangam.computeAngams(computeLagnams=False)
        panchangam.assignLunarMonths()
        sys.stderr.write('done.\n')
        sys.stderr.write('Writing computed panchangam to %s...' % fname)
        with open(fname, 'wb') as f:
            # Pickle the 'data' dictionary using the highest protocol available.
            pickle.dump(panchangam, f, pickle.HIGHEST_PROTOCOL)

    panchangam.computeFestivals()
    panchangam.computeSolarEclipses()
    panchangam.computeLunarEclipses()

    panchangam.computeIcsCalendar()
    writeIcsCalendar(panchangam, '%s-%d-%s.ics' % (city_name, year, script))


if __name__ == '__main__':
    main()
else:
    '''Imported as a module'''
