# coding=utf-8
import base64
import os
import time
import tkFileDialog
import tkMessageBox
from Tkinter import *

import pyPdf

reload(sys)
sys.setdefaultencoding('utf8')
flag = True
win = False
SEP = os.sep


def imag2string(image_path="mark.png"):
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    return encoded_string


def string2imag(encoded_string='''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
''', image_path='mark.png'):
    imgdata = base64.b64decode(encoded_string)
    filename = image_path  # I assume you have a way of picking unique filenames
    with open(filename, 'wb') as f:
        f.write(imgdata)
        # f gets closed when you exit the with statement
        # Now save the value of filename to your database
    return image_path


def if_no_create_it(file_path):
    the_dir = os.path.dirname(file_path)
    if os.path.isdir(the_dir):
        pass
    else:
        os.makedirs(the_dir)


def nowTimeStr():
    secs = time.time()
    return time.strftime("%Y-%m-%d-%H%M", time.localtime(secs))


def pdf_link_2_txt(path_pdf='drm20150330-20170310.pdf'):
    PDFFile = open(path_pdf, 'rb')
    PDF = pyPdf.PdfFileReader(PDFFile)
    pages = PDF.getNumPages()
    key = '/Annots'
    uri = '/URI'
    ank = '/A'
    all_link = []
    for page in range(pages):
        pageSliced = PDF.getPage(page)
        pageObject = pageSliced.getObject()
        if pageObject.has_key(key):
            ann = pageObject[key]
            for a in ann:
                u = a.getObject()
                if u[ank].has_key(uri):
                    print u[ank][uri]
                    if 'maomaoChyan' not in u[ank][uri]:
                        if 'channel' not in u[ank][uri]:
                            all_link.append(u[ank][uri])
    out_path = path_pdf.replace('.pdf', '.txt')
    file_txt = open(out_path, 'w')
    all_link_set = set(all_link)
    for link in all_link_set:
        link = link.split('&')[0]
        file_txt.writelines(link)
        file_txt.writelines('\n')
    file_txt.close()
    return out_path


def download_youtube(link_txt='linkdrm20130701-20150325.txt'):
    txt_file = open(link_txt, 'r')
    links = txt_file.readlines()
    txt_file.close()
    for download_link in links:
        # print links
        command = "youtube-dl " + download_link.split('&')[0] + " -c"
        print command
        os.system(command)
    return 0


def rename_tag(rename_file_dir='toberename', tag='【咻】', digital_len=8):
    for parent, dirnames, filenames in os.walk(rename_file_dir):
        for filename in filenames:
            files_in = os.path.join(parent, filename)
            files_in_name = os.path.basename(files_in)
            numbers = [num for num in files_in_name if num.isdigit()]
            date = ''
            for digit_str in numbers:
                date += digit_str
            files_out = files_in.replace(files_in_name, date[:digital_len] + tag + files_in_name)
            os.rename(files_in, files_out)
    return 0


def downVideoGUI():
    def download_pdf_for_link():
        pdf_path = link_contend.get()
        if pdf_path == '':
            tkMessageBox.showinfo("sorry!", "请先点击选择MP4找到对应的pdf文件")
            return 0
        pdf_link_2_txt(pdf_path)
        txt_path = pdf_path.replace('.pdf', '.txt')
        download_youtube(txt_path)
        return 0

    def rename_it():
        dir_rename = link_contend.get()
        if dir_rename == '':
            tkMessageBox.showinfo("sorry!", "请先再输入框中键入文件夹地址")
            return 0
        rename_tag(dir_rename)
        return 0

    def find_font():
        breakflag = 0
        for root, dirs, names in os.walk('/'):
            for name in names:
                if '.ttf' in name:
                    font_path = os.path.join(root, name)
                    print name
                    breakflag = 1
                    break
            if breakflag == 1:
                break
        return font_path

    def download():
        youtube_link = link_contend.get()
        if youtube_link == '':
            tkMessageBox.showinfo("sorry!", "请先在输入框中键入YouTube地址")
            return 0
        youtube_dl_cmd = 'youtube-dl -f 137+139 ' + youtube_link + ' --external-downloader aria2c --external-downloader-args "-x 16  -k 1M"'
        info_entry.insert(1.0, '\nipv6下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')
        os.system(youtube_dl_cmd)
        return 0

    def downloadXXnet():
        youtube_link = link_contend.get()
        if youtube_link == '':
            tkMessageBox.showinfo("sorry!", "请先在输入框中键入YouTube地址")
            return 0
        youtube_dl_cmd = 'youtube-dl --no-check-certificate  --proxy 0.0.0.0:8087 -f 22 ' + youtube_link
        info_entry.insert(1.0, '\nXX-net下载：\n', 'a')
        info_entry.insert(1.0, youtube_dl_cmd, 'a')
        os.system(youtube_dl_cmd)
        return 0

    def generateGIF():
        timestamp = nowTimeStr()
        video_path = link_contend.get()
        if video_path == '':
            tkMessageBox.showinfo("sorry!", "请先选择MP4视频文件")
            return 0
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)
        ffmpeg_cmd = 'ffmpeg -ss 00:21:11 -t 00:00:06 -i ' + new_video_path + ' -r 1 -s 480*270 -f gif ' + timestamp + '.gif'
        info_entry.insert(1.0, '生成GIF\n：', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        if_no_create_it(video_path)
        os.rename(new_video_path, video_path)
        os.rename(timestamp + '.gif', video_path.replace(video_format, 'gif'))
        info_entry.insert(1.0, '生成GIF\n：', 'a')
        info_entry.insert(1.0, video_path.replace(video_format, 'gif'), 'a')
        return 0

    def picMark():
        string2imag()
        start = time.time()
        timestamp = nowTimeStr()
        video_path = link_contend.get()
        if video_path == '':
            tkMessageBox.showinfo("sorry!", "请先选择MP4视频文件")
            return 0
        info_entry.insert(1.0, '选择视频\n：', 'a')
        info_entry.insert(1.0, video_path, 'a')
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)
        split_first = 'ffmpeg -ss 00:00:00 -t 00:00:20 -i ' + new_video_path + ' -strict -2  -vcodec copy split1.mp4'
        os.system(split_first)
        split_second = 'ffmpeg -ss 00:00:20  -i ' + new_video_path + ' -strict -2  -vcodec copy split2.mp4'
        os.system(split_second)
        font_path = find_font()
        water_cmd = '''ffmpeg -i split1.mp4 -vf drawtext="fontfile=''' + font_path + ''': \
        text='From AcFun@daleloogn': fontcolor=white: fontsize=40: box=1: boxcolor=black@0.5: \
        boxborderw=5: x=100: y=100" -codec:a copy split.mp4'''
        os.system(water_cmd)
        water_cmd = 'ffmpeg -i split.mp4 -i mark.png -strict -2 -filter_complex "overlay=x=main_w-overlay_w-10:y=main_h-overlay_h-10" split0.mp4'
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
        os.remove('mark.png')
        end = time.time()
        info_entry.insert(1.0, 'watermarking...\n：%.0f s\n' % (end - start), 'a')
        return 0

    def split_8_video():
        timestamp = nowTimeStr()
        video_path = link_contend.get()
        if video_path == '':
            tkMessageBox.showinfo("sorry!", "请先选择MP4视频文件")
            return 0
        video_format = video_path.split('.')[-1]
        new_video_path = timestamp + '.' + video_format
        print new_video_path
        os.rename(video_path, new_video_path)
        cmd_line = "ffmpeg -ss 00:00:00 -t 00:14:55 -i " + new_video_path + "  -strict -2 -vcodec copy -acodec copy -y " + "split01.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:14:55  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:55 -y " + "split02.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:29:50  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:55 -y " + "split03.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:44:45  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:55 -y " + "split04.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 00:59:40  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:55 -y " + "split05.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 01:14:35  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -t 00:14:55 -y " + "split06.mp4"
        os.system(cmd_line)
        cmd_line = "ffmpeg -ss 01:29:30  -i " + new_video_path + " -strict -2 -vcodec copy -acodec copy -y " + "split07.mp4"
        os.system(cmd_line)
        return 0

    def choose():
        filename = tkFileDialog.askopenfilename(initialdir='/home/zhangxulong/Downloads/',
                                                filetypes=[('mp4', '*.mp4'), ('pdf', '*.pdf'), ('ALL', '*.*')])
        link_contend.set(filename)
        info_entry.insert(1.0, '选择文件：\n', 'a')
        info_entry.insert(1.0, filename, 'a')
        return 0

    def emptyIt():
        link_contend.set('')
        info_entry.insert(1.0, '清空输入框：\n', 'a')
        info_entry.insert(1.0, '', 'a')
        return 0

    def vidolM3U8ZD():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入M3U8地址")
            return 0
        ffmpeg_cmd = 'ffmpeg -ss 00:00:00 -i "' + M3U8 + '" -c copy -bsf:a aac_adtstoasc -y ' + nowTimeStr() + '.mp4'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0

    def playVidolM3U8ZD():
        M3U8 = link_contend.get()
        if M3U8 == '':
            tkMessageBox.showinfo("sorry!", "请先输入M3U8地址")
            return 0
        ffmpeg_cmd = 'ffplay  "' + M3U8 + '"'
        print ffmpeg_cmd
        info_entry.insert(1.0, '\nM3U8下载\n', 'a')
        info_entry.insert(1.0, ffmpeg_cmd, 'a')
        os.system(ffmpeg_cmd)
        return 0

    def hello():
        tkMessageBox.showinfo("说明书", "点击菜单查看各个按钮的使用说明吧！@咻")
        return 0

    def about():
        tkMessageBox.showinfo("关于", "关注微信公众号【宪综视频】！@咻")
        return 0

    def xxnet_info():
        tkMessageBox.showinfo("xx-net", "github 搜索xx-net 下载供上外网使用")
        return 0

    def input_link_or_path():
        tkMessageBox.showinfo("输入",
                              "1.点击选择MP4按钮可以查找本机文件pdf或mp4两种！2.键盘输入m3u8地址,或者需要批量重命名的文件夹地址,Vidol 下载需输入m3u8地址,谷歌浏览器开发模式可过滤出来!")
        return 0

    root = Tk()
    root.title('AcFun上传daleloogn下载编辑小工具@咻')
    root.minsize(323, 180)
    root.maxsize(323, 180)
    menubar = Menu(root)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="说明书", command=hello)
    filemenu.add_command(label="输入", command=input_link_or_path)
    filemenu.add_separator()
    filemenu.add_command(label="XX-net", command=xxnet_info)
    filemenu.add_command(label="关于", command=about)
    menubar.add_cascade(label="提示", menu=filemenu)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="选择MP4", command=choose)
    filemenu.add_command(label="选择PDF", command=choose)
    menubar.add_cascade(label="文件地址", menu=filemenu)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="v站下载", command=vidolM3U8ZD)
    filemenu.add_command(label="v站播放", command=playVidolM3U8ZD)
    menubar.add_cascade(label="Vidol", menu=filemenu)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="油管下载", command=download)
    filemenu.add_command(label="XX下载", command=downloadXXnet)
    filemenu.add_command(label="pdf下载", command=download_pdf_for_link)
    menubar.add_cascade(label="下载", menu=filemenu)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="图片水印", command=picMark)
    filemenu.add_command(label="提取GIF图片", command=generateGIF)
    filemenu.add_command(label="分割8视频", command=split_8_video)
    menubar.add_cascade(label="视频处理", menu=filemenu)
    # create a pulldown menu, and add it to the menu bar
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="清空输入", command=emptyIt)
    filemenu.add_command(label="重命名子文件", command=rename_it)
    menubar.add_cascade(label="重置", menu=filemenu)

    # display the menu
    root.config(menu=menubar)

    entry_link = Entry(root, width=40)
    entry_link.grid(row=0, column=0, columnspan=3)
    link_contend = StringVar()
    entry_link.config(textvariable=link_contend)
    link_contend.set('')

    string2imag('''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
    ''', 'wechat.gif')
    wechat_image = PhotoImage(file='wechat.gif', height=150, width=154)
    wechat_label = Label(root, image=wechat_image)
    wechat_label.grid(row=1, column=0, columnspan=2, rowspan=5)

    info_entry = Text(root, width=21, height=4, )
    info_entry.grid(row=1, column=2, rowspan=5)
    info_entry.tag_config('a', foreground='blue')
    info_entry.config(font='helvetica 18')
    info_entry.insert(1.0,
                      '\n微信公众号\n【宪综视频】\n',
                      'a')
    mainloop()
    return 0


if __name__ == '__main__':
    downVideoGUI()
    if os.path.isfile('mark.png'):
        os.remove('mark.png')
    if os.path.isfile('wechat.gif'):
        os.remove('wechat.gif')
