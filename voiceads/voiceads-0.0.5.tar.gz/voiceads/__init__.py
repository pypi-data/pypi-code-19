import sys

if (sys.version_info > (3, 0)):
    from voiceads.voiceads import VoiceAdsAI
else:
    from voiceads import VoiceAdsAI
