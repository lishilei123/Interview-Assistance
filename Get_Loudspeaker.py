"""
这个脚本定义了音频录制相关的类，用于从默认扬声器捕获音频数据
"""
import Microphone as Mic
import pyaudiowpatch as pyaudio
import audioop
import numpy as np
import json
import tkinter as tk
import nls
import time
class Get_Loudspeaker():
    
    def __init__(self,APPKEY,TOKEN,textbox):
        self.flag=True
        self.APPKEY=APPKEY
        self.TOKEN=TOKEN  
        self.textbox=textbox 
        self.b=0
        with pyaudio.PyAudio() as p:
            wasapi_info = p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_speakers = p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
            
            #检测是否为回放设备
            if not default_speakers["isLoopbackDevice"]:
                for loopback in p.get_loopback_device_info_generator():
                    if default_speakers["name"] in loopback["name"]:
                        default_speakers = loopback
                        break
                else:
                    print("[ERROR]未找到回放设备")
              
        self.source = Mic.Microphone(speaker=True,
                            device_index= default_speakers["index"],
                            sample_rate=int(default_speakers["defaultSampleRate"]),         
                            chunk_size=pyaudio.get_sample_size(pyaudio.paInt16),
                            channels=default_speakers["maxInputChannels"])

    def Recording(self):
        with self.source as s:       
            print("扬声器实时转写已经启动")   
            sr = nls.NlsSpeechTranscriber(
                        url="wss://nls-gateway.aliyuncs.com/ws/v1",
                        token=self.TOKEN,
                        appkey=self.APPKEY,
                        #最后识别结果
                        on_sentence_end=self.get_on_sentence_end,
                        #中间结果
                        on_result_changed=self.get_on_result_chg,
                        #通知用户任务完成，并附带所有结果
                        #on_completed=self.get_on_completed,
                        on_error=self.get_on_error,
                        #用于指定当语音识别会话关闭时，NlsSpeechTranscriber 对象调用的回调函数。这意味着每当语音识别任务结束、连接关闭时，get_on_close 函数将会被触发，以处理会话关闭的情况。
                        on_close=self.get_on_close,
                        )
            sr.start(aformat="pcm",                              # 设置音频格式为 PCM（脉冲编码调制）
		    	    enable_intermediate_result=True,            # 启用中间结果返回
		    	    enable_punctuation_prediction=True,         # 启用标点符号预测
		    	    enable_inverse_text_normalization=True)     # 启用反向文本标准化
            self.flag=True
            while  self.flag:          
                   buffer = s.stream.read(2048)   #XF:2048要压缩  ali:512压缩   XF:1024不压缩  ali:256不压缩  
                   if len(buffer) == 0: 
                        break
                   else:
                        buffer=self.stereo_to_mono(self.get_raw_data(buffer,convert_rate=16000))
                        sr.send_audio(buffer)   
            time.sleep(0.3)
            sr.stop() 
            print("扬声器实时转写已经关闭")
 
    def stop(self):
        self.flag=False

    #转换声道由立体声到单声道
    def stereo_to_mono(self,stereo_data):
        audio_data = np.frombuffer(stereo_data, dtype=np.int16)
        audio_data = np.reshape(audio_data, (-1, 2))
        mono_data = audio_data.mean(axis=1).astype(np.int16)
        mono_data_bytes = mono_data.tobytes()
        return mono_data_bytes
    
    #压缩码率将音频采样率44.1KHz转16KHz.
    def get_raw_data(self, raw_data,convert_rate=1600):
        # 如果指定，则以所需的速率对音频进行重采样
        if convert_rate is not None and self.source.SAMPLE_RATE != convert_rate:
            raw_data, _ = audioop.ratecv(raw_data,self.source.SAMPLE_WIDTH,1,self.source.SAMPLE_RATE,convert_rate,None,)
        return raw_data

    #获取开始的消息  
    def get_on_sentence_begin(self, message, *args):
        print("get_on_sentence_begin:{}".format(message))
    #获取一句话消息 
    def get_on_sentence_end(self, message, *args):
        message = json.loads(message)
        result = message["payload"]["result"]
        if self.b==0:
            self.textbox.insert("end-1c", result)
            self.b=0
        else: 
            self.textbox.delete("end-2l linestart", "end-1c")
            self.textbox.insert("end-2l lineend", result)
            self.b=0
        self.textbox.see(tk.END)
        print("完整句子:{}".format(result))
    #连接开始
    def get_on_start(self, message, *args):
        print("get_on_start:{}".format(message))
    #错误消息
    def get_on_error(self, message, *args):
        print("on_error args=>{}".format(args))
    #关闭消息
    def get_on_close(self, *args):
        print("on_close: args=>{}".format(args))
    #获得一句话中间消息
    def get_on_result_chg(self, message, *args):
        message = json.loads(message)
        result = message["payload"]["result"]
        if self.b==0:
            self.textbox.insert(tk.END, "\n")
            self.textbox.insert(tk.END, result)
            self.textbox.insert(tk.END, "\n")
        else:
            self.textbox.delete("end-2l", tk.END)
            self.textbox.insert(tk.END, "\n")
            self.textbox.insert(tk.END,  result )
            self.textbox.insert(tk.END, "\n")
        self.b=1
        self.textbox.see(tk.END)
    def get_on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))