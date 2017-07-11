# coding=utf-8
import os
import time
import tkFileDialog
from Tkinter import *

reload(sys)
sys.setdefaultencoding('utf8')
flag = True
win = False


def if_no_create_it(file_path):
    the_dir = os.path.dirname(file_path)
    if os.path.isdir(the_dir):
        pass
    else:
        os.makedirs(the_dir)


def nowTimeStr():
    secs = time.time()
    return time.strftime("%Y-%m-%d-%H%M", time.localtime(secs))


def downVideoGUI():
    def get_m3u8():
        return M3U8_link_contend_gif.get()

    def download():
        youtube_link = link_contend.get()
        youtube_dl_cmd = 'youtube-dl -f 137+139 ' + youtube_link + ' --external-downloader aria2c --external-downloader-args "-x 16  -k 1M"'
        info_entry.insert(1.0, '\nipv6下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')

        os.system(youtube_dl_cmd)
        return 0

    def downloadXXnet():
        youtube_link = link_contend.get()
        youtube_dl_cmd = 'youtube-dl --no-check-certificate  --proxy 0.0.0.0:8087 -f 22 ' + youtube_link
        info_entry.insert(1.0, '\nXX-net下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')
        os.system(youtube_dl_cmd)
        return 0

    def generateGIF():
        timestamp = nowTimeStr()
        video_path = link_contend_gif.get()
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)
        ffmpeg_cmd = 'ffmpeg -ss 00:11:11 -t 00:00:06 -i ' + new_video_path + ' -r 1 -s 480*270 -f gif ' + timestamp + '.gif'

        info_entry.insert(1.0, '生成GIF\n：', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        if_no_create_it(video_path)
        os.rename(new_video_path, video_path)
        os.rename(timestamp + '.gif', video_path.replace(video_format, 'gif'))
        info_entry.insert(1.0, '生成GIF\n：', 'a')
        info_entry.insert(1.0, video_path.replace(video_format, 'gif'), 'a')
        return 0

    def textMark():
        start = time.time()
        timestamp = nowTimeStr()
        video_path = watermark_link_contend_gif.get()
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)

        split_first = 'ffmpeg -ss 00:00:00 -t 00:00:10 -i ' + new_video_path + ' -strict -2  -vcodec copy split1.mp4'
        os.system(split_first)

        split_second = 'ffmpeg -ss 00:00:10  -i ' + new_video_path + ' -strict -2  -vcodec copy split2.mp4'
        os.system(split_second)

        water_cmd = '''ffmpeg -i split1.mp4 -vf drawtext="fontfile=/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf: \
text='JackyWuQQgroup@161133400 By AcFun@daleloogn': fontcolor=white: fontsize=60: box=1: boxcolor=black@0.5: \
boxborderw=5: x=100: y=100" -codec:a copy split0.mp4'''
        os.system(water_cmd)
        cmd_line = "ffmpeg -i split0.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb c_1.ts"
        os.system(cmd_line)
        cmd_line = "ffmpeg -i split2.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb c_2.ts"
        os.system(cmd_line)
        cmd_line = "ffmpeg -i \"concat:c_1.ts|c_2.ts\"  -vcodec copy -acodec copy -absf aac_adtstoasc combine.mp4"
        print(cmd_line)
        os.system(cmd_line)
        os.remove("c_2.ts")
        os.remove("c_1.ts")
        os.rename('combine.mp4', video_path.replace('.mp4', '_text_water.mp4'))
        if_no_create_it(video_path)
        os.rename(new_video_path, video_path)
        os.remove('split1.mp4')
        os.remove('split0.mp4')
        os.remove('split2.mp4')
        end = time.time()
        info_entry.insert(1.0, 'watermarking...\n：%.0f s\n' % (end - start), 'a')
        return 0

    def picMark():
        start = time.time()
        timestamp = nowTimeStr()
        video_path = pic_watermark_link_contend_gif.get()
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)

        split_first = 'ffmpeg -ss 00:00:00 -t 00:00:10 -i ' + new_video_path + ' -strict -2  -vcodec copy split1.mp4'
        os.system(split_first)

        split_second = 'ffmpeg -ss 00:00:10  -i ' + new_video_path + ' -strict -2  -vcodec copy split2.mp4'
        os.system(split_second)

        water_cmd = '''ffmpeg -i split1.mp4 -vf drawtext="fontfile=/usr/share/fonts/truetype/ubuntu-font-family/Ubuntu-B.ttf: \
        text='JackyWuQQgroup@161133400 By AcFun@daleloogn': fontcolor=white: fontsize=60: box=1: boxcolor=black@0.5: \
        boxborderw=5: x=100: y=100" -codec:a copy split.mp4'''
        os.system(water_cmd)

        water_cmd = 'ffmpeg -i split.mp4 -i mark.png -strict -2 -filter_complex "overlay=x=10:y=main_h-overlay_h-10" split0.mp4'
        print water_cmd
        os.system(water_cmd)
        cmd_line = "ffmpeg -i split0.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb c_1.ts"
        os.system(cmd_line)
        cmd_line = "ffmpeg -i split2.mp4 -vcodec copy -acodec copy -vbsf h264_mp4toannexb c_2.ts"
        os.system(cmd_line)
        cmd_line = "ffmpeg -i \"concat:c_1.ts|c_2.ts\"  -vcodec copy -acodec copy -absf aac_adtstoasc combine.mp4"
        print(cmd_line)
        os.system(cmd_line)
        os.remove("c_2.ts")
        os.remove("c_1.ts")
        os.rename('combine.mp4', video_path.replace('.mp4', '_pic_water.mp4'))
        if_no_create_it(video_path)
        os.rename(new_video_path, video_path)
        os.remove('split1.mp4')
        os.remove('split0.mp4')
        os.remove('split2.mp4')
        os.remove('split.mp4')
        end = time.time()
        info_entry.insert(1.0, 'watermarking...\n：%.0f s\n' % (end - start), 'a')
        return 0

    def split_video():
        start = time.time()
        timestamp = nowTimeStr()
        video_path = splitSegments_link_contend_gif.get()
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)
        cmd_line = "ffmpeg -ss 00:00:00 -t 00:12:00 -i " + new_video_path + "  -strict -2 -vcodec copy -acodec copy -y " + "split01.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:12:00 -t 00:24:00 -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -y " + "split02.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:24:00 -t 00:36:00 -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -y " + "split03.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:36:00 -t 00:48:00 -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -y " + "split04.mp4"
        os.system(cmd_line)
        return 0

    def choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/video', filetypes=[('mp4', '*.mp4')])
        link_contend_gif.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def water_choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/video', filetypes=[('mp4', '*.mp4')])
        watermark_link_contend_gif.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def pic_water_choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/video', filetypes=[('mp4', '*.mp4')])
        pic_watermark_link_contend_gif.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def split_seg_water_choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/video', filetypes=[('mp4', '*.mp4')])
        splitSegments_link_contend_gif.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def vidolM3U8ZD():
        M3U8 = get_m3u8()
        ffmpeg_cmd = 'ffmpeg -ss 00:01:00 -i "' + M3U8 + '" -c copy -bsf:a aac_adtstoasc -y ' + nowTimeStr() + '.mp4'

        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0

    root = Tk()
    root.title('AcFun上传daleloogn下载小工具')
    labe_txt = Label(root, text='YouTube链接：')
    labe_txt.grid(row=0, column=0)
    entry_link = Entry(root, width=40)
    entry_link.grid(row=0, column=1, columnspan=2)
    link_contend = StringVar()
    entry_link.config(textvariable=link_contend)
    link_contend.set('')
    start_button = Button(root, text='下载', command=download, width=15)
    start_button.grid(row=0, column=3)
    start_button = Button(root, text='XX-net下载', command=downloadXXnet, width=15)
    start_button.grid(row=0, column=4)

    labe_txt_gif = Label(root, text='选择视频文件：')
    labe_txt_gif.grid(row=1, column=0)
    entry_link_gif = Entry(root, width=40)
    entry_link_gif.grid(row=1, column=1, columnspan=2)
    link_contend_gif = StringVar()
    entry_link_gif.config(textvariable=link_contend_gif)
    link_contend_gif.set('')
    choose_button = Button(root, text='选择', command=choose, width=15)
    choose_button.grid(row=1, column=3)
    gif_button = Button(root, text='提取GIF图片', command=generateGIF, width=15)
    gif_button.grid(row=1, column=4)

    M3U8_labe_txt_gif = Label(root, text='V站下载：')
    M3U8_labe_txt_gif.grid(row=2, column=0)
    M3U8_entry_link_gif = Entry(root, width=21)
    M3U8_entry_link_gif.grid(row=2, column=1)
    M3U8_link_contend_gif = StringVar()
    M3U8_entry_link_gif.config(textvariable=M3U8_link_contend_gif)
    M3U8_link_contend_gif.set('')
    M3U8_choose_button = Button(root, text='<<<左侧输入m3u8地址,谷歌浏览器开发模式可过滤出来.点击并等待下载吧!', command=vidolM3U8ZD, width=52)
    M3U8_choose_button.grid(row=2, column=2, columnspan=3)

    watermark_labe_txt_gif = Label(root, text='选择视频文件：')
    watermark_labe_txt_gif.grid(row=3, column=0)
    watermark_entry_link_gif = Entry(root, width=40)
    watermark_entry_link_gif.grid(row=3, column=1, columnspan=2)
    watermark_link_contend_gif = StringVar()
    watermark_entry_link_gif.config(textvariable=watermark_link_contend_gif)
    watermark_link_contend_gif.set('')
    watermark_choose_button = Button(root, text='选择视频', command=water_choose, width=15)
    watermark_choose_button.grid(row=3, column=3)
    watermark_gif_button = Button(root, text='文字水印', command=textMark, width=15)
    watermark_gif_button.grid(row=3, column=4)

    pic_watermark_labe_txt_gif = Label(root, text='选择视频文件：')
    pic_watermark_labe_txt_gif.grid(row=4, column=0)
    pic_watermark_entry_link_gif = Entry(root, width=40)
    pic_watermark_entry_link_gif.grid(row=4, column=1, columnspan=2)
    pic_watermark_link_contend_gif = StringVar()
    pic_watermark_entry_link_gif.config(textvariable=pic_watermark_link_contend_gif)
    pic_watermark_link_contend_gif.set('')
    pic_watermark_choose_button = Button(root, text='选择视频', command=pic_water_choose, width=15)
    pic_watermark_choose_button.grid(row=4, column=3)
    pic_watermark_gif_button = Button(root, text='图片水印', command=picMark, width=15)
    pic_watermark_gif_button.grid(row=4, column=4)

    splitSegments_labe_txt_gif = Label(root, text='选择视频文件：')
    splitSegments_labe_txt_gif.grid(row=5, column=0)
    splitSegments_entry_link_gif = Entry(root, width=40)
    splitSegments_entry_link_gif.grid(row=5, column=1, columnspan=2)
    splitSegments_link_contend_gif = StringVar()
    splitSegments_entry_link_gif.config(textvariable=splitSegments_link_contend_gif)
    splitSegments_link_contend_gif.set('')
    splitSegments_choose_button = Button(root, text='选择视频', command=split_seg_water_choose, width=15)
    splitSegments_choose_button.grid(row=5, column=3)
    splitSegments_gif_button = Button(root, text='分割视频', command=split_video, width=15)
    splitSegments_gif_button.grid(row=5, column=4)

    info_entry = Text(root, width=50, height=4, )
    info_entry.grid(row=6, column=0, columnspan=5, rowspan=2)
    info_entry.tag_config('a', foreground='green')
    info_entry.config(font='helvetica 18')
    info_entry.insert(1.0,
                      '视频源：【1】youtube【2】vidol\n欢迎加入QQ群：》》》》532671563《《《《【咻是群主】\n【主要上传吴宗宪节目哦】\nVidol 下载需输入m3u8地址',
                      'a')

    mainloop()
    return 0


if __name__ == '__main__':
    downVideoGUI()
