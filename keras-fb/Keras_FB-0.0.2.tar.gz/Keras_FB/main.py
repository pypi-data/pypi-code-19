# -*- coding: utf-8 -*-
#Original Author: QuantumLiu
#https://github.com/QuantumLiu/wechat_callback/blob/master/wechat_utils.py
#Modified by Kotobuki
from keras import __version__ as kv
kv=int(kv[0])
import platform
pv=int(platform.python_version()[0])
import numpy as np
import scipy.io as sio
from keras.callbacks import Callback
import time
import matplotlib  
matplotlib.use('Agg') # 
import matplotlib.pyplot as plt
from math import ceil

if pv>2:
    import _thread as th
else:
    import thread as th
import os
from os import system
import re
import traceback
import platform
from requests.exceptions import ConnectionError
from fbchat import Client
from fbchat.models import *




def send_text(text):
    try:
        client.sendMessage(text, thread_id=client.uid, thread_type=ThreadType.USER)
        return
    except (ConnectionError,NotImplementedError,KeyError):
        traceback.print_exc()
        print('\nConection error,failed to send the message!\n')
        return
    else:
        return
def send_img(filename):
    try:
        client.sendLocalImage(filename, thread_id=client.uid, thread_type=ThreadType.USER)
        return
    except (ConnectionError,NotImplementedError,KeyError):
        traceback.print_exc()
        print('\nConection error,failed to send the figure!\n')
        return
    else:
        return
#==============================================================================
#     
#==============================================================================
class sendmessage(Callback):

    def __init__(self,savelog=True,fexten='',username="",password=""):
        self.username=username
        self.password=password
        self.fexten=(fexten if fexten else '')#the name of log and figure files 
        self.savelog=bool(savelog)#save log or not
        global client
        client = Client(username, password)
    def t_send(self,msg):
        try:
            send_text(msg)
            return
        except (ConnectionError,NotImplementedError,KeyError):
            traceback.print_exc()
            print('\nConection error,failed to send the message!\n')
            return
        else:
            return
    def t_send_img(self,filename):
        try:
            send_img(filename)
            return
        except (ConnectionError,NotImplementedError,KeyError):
            traceback.print_exc()
            print('\nConection error,failed to send the figure!\n')
            return
        else:
            return
       
            
    def shutdown(self,sec,save=True,filepath='temp.h5'):
        if save:
            self.model.save(filepath, overwrite=True)
            self.t_send('Command accepted,the model has already been saved,shutting down the computer....')
        else:
            self.t_send('Command accepted,shutting down the computer....')
        if 'Windows' in platform.system():
            th.start_new_thread(system, ('shutdown -s -t %d' %sec,))
        else:
            m=(int(sec/60) if int(sec/60) else 1)
            th.start_new_thread(system, ('shutdown -h -t %d' %m,))
            
#==============================================================================
#         
#==============================================================================
    def cancel(self):
        #Cancel function to cancel shutting down the computer
        self.t_send('Command accepted,cancel shutting down the computer....')
        if 'Windows' in platform.system():
            th.start_new_thread(system, ('shutdown -a',))
        else:
            th.start_new_thread(system, ('shutdown -c',))
#==============================================================================
#         
#==============================================================================
    def GetMiddleStr(self,content,startStr,endStr):
        #get the string between two specified strings
        #从指定的字符串之间截取字符串
        try:
          startIndex = content.index(startStr)
          if startIndex>=0:
            startIndex += len(startStr)
          endIndex = content.index(endStr)
          return content[startIndex:endIndex]
        except:
            return ''
#==============================================================================
# 
#==============================================================================
    def validateTitle(self,title):
        #transform a string to a validate filename
        #将字符串转化为合法文件名
        rstr = r"[\/\\\:\*\?\"\<\>\|]"  # '/\:*?"<>|'
        new_title = re.sub(rstr, "", title).replace(' ','')
        return new_title
#==============================================================================
#         
#==============================================================================
    def prog(self):#Show progress
        nb_batches_total=(self.params['nb_epoch'] if not kv-1 else self.params['epochs'])*self.params['nb_sample']/self.params['batch_size']
        nb_batches_epoch=self.params['nb_sample']/self.params['batch_size']
        prog_total=(self.t_batches/nb_batches_total if nb_batches_total else 0)+0.01
        prog_epoch=(self.c_batches/nb_batches_epoch if nb_batches_epoch else 0)+0.01
        if self.t_epochs:
            now=time.time()
            t_mean=float(sum(self.t_epochs)) / len(self.t_epochs)
            eta_t=(now-self.train_start)*((1/prog_total)-1)
            eta_e=t_mean*(1-prog_epoch)
            t_end=time.asctime(time.localtime(now+eta_t))
            e_end=time.asctime(time.localtime(now+eta_e))
            m='\nTotal:\nProg:'+str(prog_total*100.)[:5]+'%\nEpoch:'+str(self.epoch[-1])+'/'+str(self.stopped_epoch)+'\nETA:'+str(eta_t)[:8]+'sec\nTrain will be finished at '+t_end+'\nCurrent epoch:\nPROG:'+str(prog_epoch*100.)[:5]+'%\nETA:'+str(eta_e)[:8]+'sec\nCurrent epoch will be finished at '+e_end
            self.t_send(m)
            print(m)
        else:
            now=time.time()
            eta_t=(now-self.train_start)*((1/prog_total)-1)
            eta_e=(now-self.train_start)*((1/prog_epoch)-1)
            t_end=time.asctime(time.localtime(now+eta_t))
            e_end=time.asctime(time.localtime(now+eta_e))
            m='\nTotal:\nProg:'+str(prog_total*100.)[:5]+'%\nEpoch:'+str(len(self.epoch))+'/'+str(self.stopped_epoch)+'\nETA:'+str(eta_t)[:8]+'sec\nTrain will be finished at '+t_end+'\nCurrent epoch:\nPROG:'+str(prog_epoch*100.)[:5]+'%\nETA:'+str(eta_e)[:8]+'sec\nCurrent epoch will be finished at '+e_end
            self.t_send(m)
            print(m)
            
#==============================================================================
# 
#==============================================================================
    def get_fig(self,level='all',metrics=['all']):
        color_list='rgbyck'*10
        def batches(color_list='rgbyck'*10,metrics=['all']):
            if 'all' in metrics:
                m_available=list(self.logs_batches.keys())
            else:
                m_available=([val for val in list(self.logs_batches.keys()) if val in metrics]if[val for val in list(self.logs_batches.keys()) if val in metrics]else list(self.logs_batches.keys()))
            nb_rows_batches=int(ceil(len(m_available)*1.0/2))
            fig_batches=plt.figure('all_subs_batches')
            for i,k in enumerate(m_available):
                p=plt.subplot(nb_rows_batches,2,i+1)
                data=self.logs_batches[k]
                p.plot(range(len(data)),data,color_list[i]+'-',label=k)
                p.set_title(k+' in batches',fontsize=14)
                p.set_xlabel('batch',fontsize=10)
                p.set_ylabel(k,fontsize=10)
                #p.legend()
            filename=(self.fexten if self.fexten else self.validateTitle(self.localtime))+'_batches.jpg'
            plt.tight_layout()
            plt.savefig(filename)
            plt.close('all')
#==============================================================================

#==============================================================================
            self.t_send_img(filename)
            time.sleep(.5)
            self.t_send('Batches figure')
            return
#==============================================================================
#             
#==============================================================================
        def epochs(color_list='rgbyck'*10,metrics=['all']):
            if 'all' in metrics:
                m_available=list(self.logs_epochs.keys())
            else:
                m_available=([val for val in list(self.logs_epochs.keys()) if val in metrics]if[val for val in list(self.logs_epochs.keys()) if val in metrics]else list(self.logs_epochs.keys()))
            nb_rows_epochs=int(ceil(len(m_available)*1.0/2))
            fig_epochs=plt.figure('all_subs_epochs')
            for i,k in enumerate(m_available):
                p=plt.subplot(nb_rows_epochs,2,i+1)
                data=self.logs_epochs[k]
                p.plot(range(len(data)),data,color_list[i]+'-',label=k)
                p.set_title(k+' in epochs',fontsize=14)
                p.set_xlabel('epoch',fontsize=10)
                p.set_ylabel(k,fontsize=10)
            filename=(self.fexten if self.fexten else self.validateTitle(self.localtime))+'_epochs.jpg'
            plt.tight_layout()
            plt.savefig(filename)
            plt.close('all')
#==============================================================================

#==============================================================================
            self.t_send_img(filename)
            time.sleep(.5)
            self.t_send('Epochs figure')
            return
#==============================================================================
#             
#==============================================================================
        try:
            if not self.epoch and (level in ['all','epochs']):
                level='batches'
            if level=='all':
                batches(metrics=metrics)
                epochs(metrics=metrics)
                th.exit()
                return
            elif level=='epochs':
                epochs(metrics=metrics)
                th.exit()
                return
            elif level=='batches':
                batches(metrics=metrics)
                th.exit()
                return
            else:
                batches(metrics=metrics)
                epochs(metrics=metrics)
                th.exit()
                return
        except Exception:
            return
#==============================================================================
#             
#==============================================================================
    def gpu_status(self,av_type_list):
        for t in av_type_list:
            cmd='nvidia-smi -q --display='+t
            #print('\nCMD:',cmd,'\n')
            r=os.popen(cmd)
            info=r.readlines()
            r.close()
            content = " ".join(info)
            #print('\ncontent:',content,'\n')
            index=content.find('Attached GPUs')
            s=content[index:].replace(' ','').rstrip('\n')
            self.t_send(s)
            time.sleep(.5)
        #th.exit()
#==============================================================================
# 
#==============================================================================
    def on_train_begin(self, logs={}):
        self.epoch=[]
        self.t_epochs=[]
        self.t_batches=0
        self.logs_batches={}
        self.logs_epochs={}
        self.train_start=time.time()
        self.localtime = time.asctime( time.localtime(self.train_start) )
        self.mesg = 'Train started at: '+self.localtime
        self.t_send(self.mesg)
        self.stopped_epoch = (self.params['epochs'] if kv-1 else self.params['nb_epoch'])
#==============================================================================

#==============================================================================

#==============================================================================
#     
#==============================================================================
    def on_batch_end(self, batch, logs=None):
        logs = logs or {}
        for k in self.params['metrics']:
            if k in logs:
                self.logs_batches.setdefault(k, []).append(logs[k])
        self.c_batches+=1
        self.t_batches+=1
#==============================================================================
#                 
#==============================================================================
    def on_epoch_begin(self, epoch, logs=None):
        self.t_s=time.time()
        self.epoch.append(epoch)
        self.c_batches=0
        self.t_send('Epoch'+str(epoch+1)+'/'+str(self.stopped_epoch)+' started')
        self.mesg = ('Epoch:'+str(epoch+1)+' ')
#==============================================================================
#         
#==============================================================================
    def on_epoch_end(self, epoch, logs=None):
        for k in self.params['metrics']:
            if k in logs:
                self.mesg+=(k+': '+str(logs[k])[:5]+' ')
                self.logs_epochs.setdefault(k, []).append(logs[k])
#==============================================================================

#==============================================================================
        if epoch+1>=self.stopped_epoch:
            self.model.stop_training = True
        logs = logs or {}
        self.epoch.append(epoch)
        self.t_epochs.append(time.time()-self.t_s)
        if self.savelog:
            sio.savemat((self.fexten if self.fexten else self.validateTitle(self.localtime))+'_logs_batches'+'.mat',{'log':np.array(self.logs_batches)})
            sio.savemat((self.fexten if self.fexten else self.validateTitle(self.localtime))+'_logs_batches'+'.mat',{'log':np.array(self.logs_epochs)})
        th.start_new_thread(self.get_fig,())
#==============================================================================

#==============================================================================
        self.t_send(self.mesg)
        return
#==============================================================================
#         
#==============================================================================
    def on_train_end(self, logs=None):
        self.t_send('Train stopped at epoch'+str(self.epoch[-1]+1))
   
