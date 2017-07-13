# coding=utf-8
from __future__ import unicode_literals
from faker.generator import random
from faker.providers import BaseProvider


class MobileAgent(BaseProvider):
    user_agents = ('android', 'ios', 'windows')

    ios_hardware = ('iPhone', 'iPad', 'iPod touch')

    android_hardware = ('LG-L160L Build/IML74K',
                        'HTC Sensation Build/IML74K',
                        'HTC Desire HD A9191 Build/GRJ90',
                        'ViewPad7 Build/FRF91',
                        'Nexus 7 Build/JRO03D',
                        'Nexus One Build/FRF91',
                        'Nexus S Build/GRJ22',
                        'HTC_One_X Build/IMM76D',
                        'Sprint APA9292KT Build/FRF91',
                        'LG-D852 Build/LRX21Y',
                        'DROID2 Build/VZW',
                        'KFTHWI Build/JDQ39',
                        'Prime Build/JZO54K',
                        'POV_TV-HDMI-200BT Build/JRO03H')

    win_hardware = ('ARM; Touch; HTC; Windows Phone 8X by HTC',
                    'NOKIA; Lumia 820',
                    'ARM; Touch; NOKIA; Lumia 925',
                    'HTC; Radar; Orange',
                    'Touch; HTC; HTC6990LVW',
                    'Touch; NOKIA; Lumia 920',
                    'ARM; Touch; NOKIA; Lumia 520; Vodafone',
                    'HTC; Radar C110e; 1.08.164.02',
                    'HTC; 7 Trophy T8686',
                    'ARM; Touch; HUAWEI; W1-U00')

    def android(self, hw=None):
        # Mozilla/5.0 (Linux; U; Android 4.0.3; ko-kr; LG-L160L Build/IML74K) AppleWebkit/534.30 (KHTML, like Gecko)
        #  Version/4.0 Mobile Safari/534.30
        saf = str(str(random.randint(531, 536)) + str(random.randint(0, 2)))
        tmplt = 'Mozilla/5.0 (Linux; U; Android {0}.{1}.{2};{3};{4}) AppleWebKit/{5} (KHTML, like Gecko)' \
                ' Version/4.0 Mobile Safari/{6}'

        if hw is None:
            hw = self.android_hardware_token()

        return tmplt.format(random.choice((2, 4)),
                            random.randint(0, 4),
                            random.randint(0, 5),
                            hw,
                            'en-us',
                            saf,
                            saf)

    def ios(self, hw=None):
        # Mozilla/5.0 (iPhone; CPU iPhone OS 7_0_3 like Mac OS X) AppleWebKit/537.51.1 (KHTML, like Gecko)
        # CriOS/30.0.1599.16
        # Mobile/11B511 Safari/8536.25 (D7A6DB13-4271-4C41-86CC-42FCDBC2BF90)
        saf = str(random.choice(('', '6.', '8.', '9.')) + str(random.randint(531, 536)) + '.' +
                  str(random.randint(0, 25)))

        tmplt = 'Mozilla/5.0 ({0}; CPU OS {1}_{2}_{3} like Mac OS X) AppleWebKit/{4} (KHTML, like Gecko) ' \
                'CriOS/30.0.1599.16 Mobile/11B511 Safari/{5}'

        if hw is None:
            hw = self.ios_hardware_token()

        return tmplt.format(hw,
                            random.randint(4, 9),
                            random.randint(0, 3),
                            random.randint(1, 4),
                            saf,
                            saf)

    def windows(self, hw=None):
        # Mozilla/5.0 (compatible; MSIE 10.0; Windows Phone 8.0; Trident/6.0; IEMobile/10.0; ARM; Touch; HTC;
        # Windows Phone 8X by HTC)
        tmplt = 'Mozilla/5.0 (compatible; MSIE {0}; Windows Phone {1}; Trident/{2}; IEMobile/{0}; {3}'

        if hw is None:
            hw = self.win_hardware_token()

        return tmplt.format(random.randint(9, 10),
                            random.randint(7, 8),
                            random.randint(5, 6),
                            hw)

    def android_hardware_token(self):
        return self.random_element(self.android_hardware)

    def ios_hardware_token(self):
        return self.random_element(self.ios_hardware)

    def win_hardware_token(self):
        return self.random_element(self.win_hardware)

    def mobile_agent(self):
        name = self.random_element(self.user_agents)
        return getattr(self, name)()
