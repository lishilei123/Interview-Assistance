import Microphone as Mic
import nls
import time
import json
import tkinter as tk

class Get_Microphone:
     
    def __init__(self,APPKEY,TOKEN,textbox):
        self.source = Mic.Microphone(sample_rate=16000)
        self.APPKEY=APPKEY
        self.TOKEN=TOKEN  
        self.textbox=textbox 
        self.b=0

    def Recording(self):
        with self.source as s:
            print("麦克风实时转写已经启动")   
            sr = nls.NlsSpeechTranscriber(
                            url="wss://nls-gateway.aliyuncs.com/ws/v1",
                            token=self.TOKEN,
                            appkey=self.APPKEY,
                            #最后识别结果
                            on_sentence_end=self.get_on_sentence_end,
                            #中间结果
                            on_result_changed=self.get_on_result_chg,
                            #通知用户任务完成，并附带所有结果
                            on_completed=self.get_on_completed,
                            on_error=self.get_on_error,
                            #用于指定当语音识别会话关闭时，NlsSpeechTranscriber 对象调用的回调函数。这意味着每当语音识别任务结束、连接关闭时，get_on_close 函数将会被触发，以处理会话关闭的情况。
                            #on_close=self.get_on_close,

                        )
            #开始发送标识
            sr.start(aformat="pcm",                              # 设置音频格式为 PCM（脉冲编码调制）
		    	    enable_intermediate_result=True,            # 启用中间结果返回
		    	    enable_punctuation_prediction=True,         # 启用标点符号预测
		    	    enable_inverse_text_normalization=True)     # 启用反向文本标准化
            self.flag=True
            while  self.flag:         
                   buffer = s.stream.read(512)   #XF:2048要压缩  ali:512压缩   XF:1024不压缩  ali:256不压缩  
                   if len(buffer) == 0: 
                        break
                   else:
                        sr.send_audio(buffer)            
            time.sleep(0.3)
            #终止线程
            sr.stop() 
            print("麦克风实时转写已经关闭") 

    def stop(self):
        self.flag=False
    

    #获取一句话消息 
    def get_on_sentence_end(self, message, *args):
        message = json.loads(message)
        result = message["payload"]["result"]
        if self.b==0:
            self.textbox.insert("end-1c", result)
        else: 
            self.textbox.delete("end-2l linestart", "end-1c")
            self.textbox.insert("end-2l lineend", result)
        self.b=0
        self.textbox.see(tk.END)
        print("完整的句子:{}".format(result))
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
        #print("中间句子:{}".format(result))
        self.textbox.see(tk.END)
    #通知用户任务完成，并附带所有结果
    def get_on_completed(self, message, *args):
        print("on_completed:args=>{} message=>{}".format(args, message))