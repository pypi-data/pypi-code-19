import requests


class Amara:

    def __init__(self,headers):
        self.headers = headers

    def get_subtitles(self,amara_id,language):
        url='https://amara.org/api/videos/'+amara_id+'/languages/'+language+'/subtitles/?sub_format=srt'

        r =requests.get(url, headers=self.headers)
        rjs = r.json()
        if 'subtitles' in rjs:
            return rjs['subtitles']
        else:
            return None

    def get_amara_id(self, video_url,language_code):
        url = 'https://amara.org/api/videos/'
        urldict = dict({'video_url': video_url})
        r = requests.get(url, params=urldict, headers=self.headers)
        json_ret = r.json()

        if 'objects' in json_ret and len (json_ret['objects']) > 0 :
            return json_ret['objects'][0]['id']
        else:
            return self.post_video(video_url,language_code)

    def post_video(self,video_url,language_code):
        url = 'https://amara.org/api/videos/'
        urldict = dict({'video_url':video_url, 'primary_audio_language_code':language_code})

        r = requests.post(url, data=urldict, headers=self.headers )
        json_ret =  r.json()
        if 'id' in json_ret:
            return json_ret['id']
        else:
            return None

    def get_actions(self,amara_id,language_code):
        url = 'https://amara.org/api/videos/'+amara_id+'/languages/'+language_code+'/subtitles/actions/'
        r = requests.get(url, headers=self.headers)
        return r.json()

    def post_subtitles(self,amara_id,language_code, subtitles):
        url = 'https://amara.org/api/videos/'+amara_id+'/languages/'+language_code+'/subtitles/'
        urldict = dict({'subtitles': subtitles, 'sub_format': 'srt'})
        r = requests.post(url, data=urldict, headers=self.headers)

    def convert_to_lyrics(self,lines):
        ret_value = ""
        rows_t = lines.split('\n')
        rows = [x for x in rows_t if len(x.strip()) > 0]
        for count,row in enumerate(rows):
            ret_value = ret_value + str(count+1) +'\r\n'
            ret_value = ret_value + '99:59:59,999 --> 99:59:59,999\r\n'
            ret_value = ret_value + row
            ret_value = ret_value + '\r\n\r\n'

        return ret_value


