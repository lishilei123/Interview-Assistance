import tkinter as tk
from tkinter import ttk
import threading
import Get_Loudspeaker
from openai import OpenAI
import ChatGPT
import Get_Microphone
import yaml
import Aliyuntoken
import time
from tkinter import simpledialog, messagebox

# 定义一个函数来显示密码输入对话框
def show_password_dialog():
    password = simpledialog.askstring("Password", "Enter your password:", show='*')
    return password

def main():
    correct_password = "木鱼"
    max_attempts = 3
    attempts = 0

    while attempts < max_attempts:
        password = show_password_dialog()
        if password == correct_password:
            break
        else:
            messagebox.showerror("Error", "Incorrect password!")
            attempts += 1
    else:
        messagebox.showwarning("Warning", "Too many incorrect attempts!")
        return
    def submit_content3():
        current_bg = button3.cget("bg")  # 获取当前按钮的背景颜色
        if current_bg == "red":
            button3.config(bg="SystemButtonFace", fg="black")  # 恢复为默认样式
            Louds.stop()
        else:
            button3.config(bg="red", fg="white")  # 设置背景为红色，文本为白色
            Louds_Recording=threading.Thread(target=Louds.Recording)
            Louds_Recording.start()

    # 定义按钮点击事件,I
    def submit_content1():
        current_bg = button1.cget("bg")  # 获取当前按钮的背景颜色
        if current_bg == "red":
            button1.config(bg="SystemButtonFace", fg="black")  # 恢复为默认样式
            MIC.stop()
        else:
            button1.config(bg="red", fg="white")  # 设置背景为红色，文本为白色
            MIC_Recording=threading.Thread(target=MIC.Recording)
            MIC_Recording.start()
 
    # 定义按钮点击事件,提交
    
    def submit_content4(event=None):
        content = entry1.get("1.0", tk.END).strip() 
        if content:     
            # 在界面上立即显示用户输入的内容，并在右侧显示
            text.insert(tk.END, f"\n{content}", "left_green_large")
            text.see(tk.END)
            entry1.delete('1.0', tk.END)
            global messages  
            global Number
            global Number_of_contexts
            Number+=1
            if Number > Number_of_contexts:
                del messages[1]
                del messages[1]
                Number -=1
            print(messages)
            #threading.Thread(target=ChatGPT.chat, args=(content, GPT_client,messages, model, text)).start()
            text.after(1, ChatGPT.chat, content, GPT_client, messages, model, text)
    def submit_content5(event=None):
        entry1.delete('1.0', tk.END)
    #窗口顶置开关
    def toggle_topmost():
        global topmost
        topmost = not topmost
        root.attributes("-topmost", topmost)
        topmost_button.config(text="顶置" if topmost else "默认")
    # 初始化按钮状态变量
   
    def toggle_button():
        global  messages # 声明使用全局变量
        global Number
        Number=0
        entry1.delete('1.0', tk.END)#清空文本框1
        text.delete('1.0', tk.END)#清空文本框1
        # 初始化消息数据
        messages = prompts.copy()
        print('重置后的prompts',messages)
    def on_closing():
        global stop_threads
        stop_threads = True
        MIC.stop()
        Louds.stop()
        root.destroy()
    # 创建主窗口
    root = tk.Tk()
    root.title("ChatGPT 面试助手")
    # 设置窗口的默认大小
    root.geometry("400x600")  # 宽度为400，高度为600的窗口
    # 设置窗口最小尺寸
    root.minsize(300, 400)
    # 初始化顶置标志
    topmost = True
    root.attributes("-topmost", topmost)
    # 创建可调整大小的框架
    frame = ttk.Frame(root, padding="10 10 10 10")
    frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))
    # 配置列和行的伸缩性
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    frame.columnconfigure(0, weight=1)
    frame.columnconfigure(1, weight=0)  # 设置输入框所在列的权重为0
    frame.rowconfigure(0, weight=0)  # Topmost button row
    frame.rowconfigure(1, weight=1)  # Text area row
    frame.rowconfigure(2, weight=0)  # Original input row
    frame.rowconfigure(3, weight=0)  # Additional input row

    # 创建一个内框架来容纳两个按钮
    button_frame = ttk.Frame(frame)
    button_frame.grid(column=0, row=0, sticky=(tk.W, tk.E), pady=(0, 10))
    # 创建 "顶置按钮"
    topmost_button = ttk.Button(button_frame, text="顶置", command=toggle_topmost)
    topmost_button.grid(column=0, row=0, sticky=(tk.W, tk.E))
    # 创建 "重置对话" 按钮
    reset_button = ttk.Button(button_frame, text="重置对话", command=toggle_button)
    reset_button.grid(column=1, row=0, sticky=(tk.W, tk.E))
    # 让两个按钮平分按钮框架的宽度
    button_frame.columnconfigure(0, weight=1)
    button_frame.columnconfigure(1, weight=1)

    # 添加一个多行文本框
    text = tk.Text(   frame, 
                      wrap="word", 
                      height=4, #高度
                      font=("KaiTi", 18),# 字体字号
                      #bg="lightyellow",  # 设置背景颜色
                      #fg="black",        # 设置前景颜色（文本颜色）
                      bg="#E6FFE6", # 护眼绿
                      spacing3=3, 
    )
    text.grid(column=0, row=1, columnspan=5, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))


   
    text.tag_configure("left_green_large", justify='left', foreground="green")



    button1 = tk.Button(frame, text="I", bg="SystemButtonFace", fg="black", command=submit_content1)
    button1.grid(column=1, row=2, sticky=(tk.W, tk.E), padx=(10, 0))
    button5 = tk.Button(frame, text="清空输入框", command=submit_content5)
    button5.grid(column=0, row=2, sticky=(tk.W, tk.E), padx=(10, 0))




    # 添加第二个输入框
    entry1 = tk.Text( frame, 
                      wrap="word", 
                      height=4, #高度
                      font=("KaiTi", 15),# 字体字号
                      bg="lightyellow",  # 设置背景颜色
                      fg="black",        # 设置前景颜色（文本颜色）
                      spacing3=3,         #行间距
                        )
    entry1.grid(column=0, row=4, sticky=(tk.W, tk.E, tk.N, tk.S))



    button3 = tk.Button(frame, text="WHO", bg="SystemButtonFace", fg="black", command=submit_content3)
    button3.grid(column=1, row=4, sticky=(tk.W, tk.E), padx=(10, 0))

    button4 = tk.Button(frame, text="提交", command=submit_content4)
    button4.grid(column=1, row=5, sticky=(tk.W, tk.E), padx=(10, 0))


    ## 绑定 Enter 键到 提交WHO
    root.bind('<Return>', submit_content4)
    # 读取 config.yaml 文件
    with open('base_data.yaml', 'r', encoding='utf-8') as config_file:
        config = yaml.safe_load(config_file)
    access_key_id=config['access_key_id'] 
    access_key_secret=config['access_key_secret']
    ChatGPT_key = config['ChatGPT_key']
    ChatGPT_url = config['ChatGPT_url']
    prompts = config['prompts']
    model = config['model']
    appkey=config['APPKEY']
    token=config['TOKEN']
    Time=config['TIME']
    global Number_of_contexts
    Number_of_contexts =int(config['Number_of_contexts'])+1
    if time.time()>Time:
        token, expire_time=Aliyuntoken.AccessToken.create_token(access_key_id, access_key_secret)
        config['TIME']=expire_time
        config['TOKEN'] =token
        with open('base_data.yaml', 'w', encoding='utf-8') as config_file:
            yaml.dump(config, config_file, allow_unicode=True)
        print('更新完成')
    else:print('不更新')
    global messages
    global Number
    Number=0
    messages = prompts.copy()
    
    GPT_client = OpenAI(api_key = ChatGPT_key, 
                        base_url = ChatGPT_url ,) 
    MIC=Get_Microphone.Get_Microphone(appkey,token,entry1)
    Louds=Get_Loudspeaker.Get_Loudspeaker(appkey,token,entry1)
    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()
    print('结束')


# 调用函数
# 运行主循环
if __name__ == '__main__':
    main() 
    
    
    