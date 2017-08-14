"""
Copyright (c) 2017 James Patrick Dill

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from enum import Enum


class language(Enum):
    AF = "af"
    SQ = "sq"
    AM = "am"
    AR = "ar"
    HY = "hy"
    AZ = "az"
    EU = "eu"
    BE = "be"
    BN = "bn"
    BS = "bs"
    BG = "bg"
    CA = "ca"
    CO = "co"
    HR = "hr"
    CS = "cs"
    DA = "da"
    NL = "nl"
    EN = "en"
    EO = "eo"
    ET = "et"
    FI = "fi"
    FR = "fr"
    FY = "fy"
    GL = "gl"
    KA = "ka"
    DE = "de"
    EL = "el"
    GU = "gu"
    HT = "ht"
    HA = "ha"
    IW = "iw"
    HI = "hi"
    HU = "hu"
    IS = "is"
    IG = "ig"
    ID = "id"
    GA = "ga"
    IT = "it"
    JA = "ja"
    JW = "jw"
    KN = "kn"
    KK = "kk"
    KM = "km"
    KO = "ko"
    KU = "ku"
    KY = "ky"
    LO = "lo"
    LA = "la"
    LV = "lv"
    LT = "lt"
    LB = "lb"
    MK = "mk"
    MG = "mg"
    MS = "ms"
    ML = "ml"
    MI = "mi"
    MR = "mr"
    MN = "mn"
    MY = "my"
    NE = "ne"
    NO = "no"
    NY = "ny"
    PS = "ps"
    FA = "fa"
    PL = "pl"
    PT = "pt"
    PA = "pa"
    RO = "ro"
    RU = "ru"
    SM = "sm"
    GD = "gd"
    SR = "sr"
    ST = "st"
    SN = "sn"
    SD = "sd"
    SI = "si"
    SK = "sk"
    SL = "sl"
    SO = "so"
    ES = "es"
    SU = "su"
    SW = "sw"
    SV = "sv"
    TL = "tl"
    TG = "tg"
    TA = "ta"
    TE = "te"
    TH = "th"
    TR = "tr"
    UK = "uk"
    UR = "ur"
    UZ = "uz"
    VI = "vi"
    CY = "cy"
    XH = "xh"
    YI = "yi"
    YO = "yo"
    ZU = "zu"
    ZH_CN = "zh-cn"
    ZH_TW = "zh-tw"
    CEB = "ceb"
    HAW = "haw"
    HMN = "hmn"
    MT = "mt"
    AUTO = "auto"



_LANGUAGES = {
    "auto": language.AUTO,
    "afrikaans": language.AF,
    "albanian": language.SQ,
    "amharic": language.AM,
    "arabic": language.AR,
    "armenian": language.HY,
    "azerbaijani": language.AZ,
    "basque": language.EU,
    "belarusian": language.BE,
    "bengali": language.BN,
    "bosnian": language.BS,
    "bulgarian": language.BG,
    "catalan": language.CA,
    "cebuano": language.CEB,
    "chichewa": language.NY,
    "chinese": language.ZH_CN,
    "chinese (simplified)": language.ZH_CN,
    "chinese (traditional)": language.ZH_TW,
    "corsican": language.CO,
    "croatian": language.HR,
    "czech": language.CS,
    "danish": language.DA,
    "dutch": language.NL,
    "english": language.EN,
    "esperanto": language.EO,
    "estonian": language.ET,
    "filipino": language.TL,
    "finnish": language.FI,
    "french": language.FR,
    "frisian": language.FY,
    "galician": language.GL,
    "georgian": language.KA,
    "german": language.DE,
    "greek": language.EL,
    "gujarati": language.GU,
    "haitian creole": language.HT,
    "hausa": language.HA,
    "hawaiian": language.HAW,
    "hebrew": language.IW,
    "hindi": language.HI,
    "hmong": language.HMN,
    "hungarian": language.HU,
    "icelandic": language.IS,
    "igbo": language.IG,
    "indonesian": language.ID,
    "irish": language.GA,
    "italian": language.IT,
    "japanese": language.JA,
    "javanese": language.JW,
    "kannada": language.KN,
    "kazakh": language.KK,
    "khmer": language.KM,
    "korean": language.KO,
    "kurdish (kurmanji)": language.KU,
    "kyrgyz": language.KY,
    "lao": language.LO,
    "latin": language.LA,
    "latvian": language.LV,
    "lithuanian": language.LT,
    "luxembourgish": language.LB,
    "macedonian": language.MK,
    "malagasy": language.MG,
    "malay": language.MS,
    "malayalam": language.ML,
    "maltese": language.MT,
    "maori": language.MI,
    "marathi": language.MR,
    "mongolian": language.MN,
    "myanmar (burmese)": language.MY,
    "nepali": language.NE,
    "norwegian": language.NO,
    "pashto": language.PS,
    "persian": language.FA,
    "polish": language.PL,
    "portuguese": language.PT,
    "punjabi": language.PA,
    "romanian": language.RO,
    "russian": language.RU,
    "samoan": language.SM,
    "scots gaelic": language.GD,
    "serbian": language.SR,
    "sesotho": language.ST,
    "shona": language.SN,
    "sindhi": language.SD,
    "sinhala": language.SI,
    "slovak": language.SK,
    "slovenian": language.SL,
    "somali": language.SO,
    "spanish": language.ES,
    "sundanese": language.SU,
    "swahili": language.SW,
    "swedish": language.SV,
    "tajik": language.TG,
    "tamil": language.TA,
    "telugu": language.TE,
    "thai": language.TH,
    "turkish": language.TR,
    "ukrainian": language.UK,
    "urdu": language.UR,
    "uzbek": language.UZ,
    "vietnamese": language.VI,
    "welsh": language.CY,
    "xhosa": language.XH,
    "yiddish": language.YI,
    "yoruba": language.YO,
    'zu': language.ZU,
}


def get_language(name):
    if name.lower() not in _LANGUAGES:
        raise ValueError("No language found with name {!r}".format(name))

    return _LANGUAGES[name.lower()]
