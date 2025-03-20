import tkinter as tk
'''
def chat(input,GPT_client,messages,model,textbox):
    
    """
    chat 函数支持多轮对话，每次调用 chat 函数与大模型对话时，大模型都会”看到“此前已经产生的历史对话消息，
    """   
    messages.append({
    	"role": "user",
    	"content": input,	
    })   
    stream = GPT_client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
        )
    result=''
    textbox.insert(tk.END, '\n'+'GPT:  ')
    for chunk in stream:
        delta = chunk.choices[0].delta 
        if delta.content:
            result+=delta.content
            textbox.insert(tk.END, delta.content)
            textbox.see(tk.END)
    messages.append({"role": "assistant","content": result})

'''

def chat(input, GPT_client, messages, model, textbox):
    messages.append({
        "role": "user",
        "content": input,
    })
    
    # 假设 GPT_client 支持流式输出
    stream = GPT_client.chat.completions.create(
        model=model,
        messages=messages,
        stream=True,
    )
    result = ''
    textbox.insert(tk.END, '\n')
    textbox.see(tk.END)
    
    def update_textbox():
        nonlocal result
        try:
            chunk = next(stream)
            delta = chunk.choices[0].delta
            if delta.content:
                result += delta.content
                textbox.insert(tk.END, delta.content)
                textbox.see(tk.END)
            # 使用更短的时间间隔
            textbox.after(1, update_textbox)
        except StopIteration:
            # 在流结束后将结果添加到 messages
            messages.append({"role": "assistant", "content": result})
            #print("Assistant response added to messages:", messages)
 
    update_textbox()
    










