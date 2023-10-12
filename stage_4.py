import tkinter as tk
from tkinter import ttk
import threading
from time import time


# 转换装置设定
ip = [2, 6, 3, 1, 4, 8, 5, 7]
ip_inv = [4, 1, 3, 5, 7, 2, 8, 6]
ep = [4, 1, 2, 3, 2, 3, 4, 1]
p10 = [3, 5, 2, 7, 4, 10, 1, 9, 8, 6]
p8 = [6, 3, 7, 4, 8, 5, 10, 9]
p4 = [2, 4, 3, 1]
shifts_map = {
        1: [2, 3, 4, 5, 1],
        2: [3, 4, 5, 1, 2]
    }
s0 = [
    [1, 0, 3, 2],
    [3, 2, 1, 0],
    [0, 2, 1, 3],
    [3, 1, 0, 2]
]
s1 = [
    [0, 1, 2, 3],
    [2, 3, 1, 0],
    [3, 0, 1, 2],
    [2, 1, 0, 3]
]


# S-DES加密解密算法实现
def permute(perm, key):
    """执行给定的置换"""
    result = ''.join(key[i - 1] for i in perm)
    return result


def shift_left(key, shifts):
    """根据给定的定义执行左移"""
    return ''.join(key[i - 1] for i in shifts_map[shifts])


def switch(text):
    """执行SW操作，交换数据的左右两半"""
    left, right = text[:4], text[4:]
    return right + left


def get_sub_key(key):
    """根据10位密钥生成两个子密钥"""
    # 密钥扩展置换定义
    key = permute(p10, key)
    left_key, right_key = key[:5], key[5:]
    left_key = shift_left(left_key, 1)
    right_key = shift_left(right_key, 1)
    k1 = permute(p8, left_key + right_key)
    left_key = shift_left(left_key, 2)
    right_key = shift_left(right_key, 2)
    k2 = permute(p8, left_key + right_key)

    return k1, k2


def f_k(text, sub_key):
    """轮函数"""
    # 将文本分为左右两部分
    left_text, right_text = text[:4], text[4:]
    # 对文本的右半部分进行扩展置换
    right_expanded = permute(ep, right_text)
    # 使用扩展的右半部分和密钥进行异或运算
    expansion_xor = bin(int(right_expanded, 2) ^ int(sub_key, 2))[2:].zfill(8)
    # 将异或结果分为左右两部分
    xor_left, xor_right = expansion_xor[:4], expansion_xor[4:]
    # 对异或结果的左半部分的前后两位构建行和列索引，然后通过S0盒进行代替
    row, col = int(xor_left[0] + xor_left[3], 2), int(xor_left[1:3], 2)
    xor_left_replaced = bin(s0[row][col])[2:].zfill(2)
    # 对异或结果的前后两位构建行和列索引，然后通过S1盒进行代替
    row, col = int(xor_right[0] + xor_right[3], 2), int(xor_right[1:3], 2)
    xor_right_replaced = bin(s1[row][col])[2:].zfill(2)
    # 对替换后的异或结果的左右两部分进行置换
    xor_replaced = permute(p4, xor_left_replaced + xor_right_replaced)
    # 将置换结果与文本的左半部分进行异或运算
    left_text = bin(int(xor_replaced, 2) ^ int(left_text, 2))[2:].zfill(4)
    # 逆初始置换
    return left_text + right_text


def ascii_to_bin(text):
    """将ASCII字符串转换为二进制"""
    return ''.join(format(ord(ch), '08b') for ch in text)


def bin_to_ascii(binary):
    """将二进制转换为ASCII字符串"""
    return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))


def encrypt(plaintext, key):
    """加密函数"""
    binary_text = ascii_to_bin(plaintext)
    k1, k2 = get_sub_key(key)
    ciphertext = ""
    for i in range(0, len(binary_text), 8):
        block = binary_text[i:i+8]
        # 初始置换
        temp_text = permute(ip, block)
        # 第一轮变换
        temp_text = switch(f_k(temp_text, k1))
        # 第二轮变换
        temp_text = f_k((temp_text), k2)
        encrypted_block = permute(ip_inv, temp_text)
        ciphertext += chr(int(encrypted_block, 2))
    return ciphertext


def decrypt(ciphertext, key):
    """解密函数"""
    binary_text = ascii_to_bin(ciphertext)
    k1, k2 = get_sub_key(key)
    decrypted_text = ""
    for i in range(0, len(binary_text), 8):
        block = binary_text[i:i+8]
        # 初始置换
        temp_text = permute(ip, block)
        # 第一轮变换
        temp_text = switch(f_k(temp_text, k2))
        # 第二轮变换
        temp_text = f_k((temp_text), k1)
        decrypted_block = permute(ip_inv, temp_text)
        decrypted_text += chr(int(decrypted_block, 2))
    return decrypted_text


# 线程函数：暴力破解密钥
def brute_force_thread(start_key, end_key, plaintext, ciphertext, result_container):
    for key in range(start_key, end_key):  # 遍历密钥空间
        key_str = format(key, '010b')  # 将密钥转为10位的二进制字符串
        # 如果加密后的明文与给定的密文相等
        if encrypt(plaintext, key_str) == ciphertext:
            result_container.append(key_str)  # 将匹配的密钥添加到结果容器中
            break  # 找到密钥后，跳出循环


# 主函数：暴力破解密钥
def brute_force(plaintext, ciphertext, num_threads=4):
    keyspace_per_thread = 2 ** 10 // num_threads  # 计算每个线程需要搜索的密钥空间
    threads = []  # 用于存储线程的列表
    results = []  # 用于存储找到的密钥的结果容器

    # 创建并启动线程
    for i in range(num_threads):
        start_key = i * keyspace_per_thread  # 计算起始密钥
        # 计算结束密钥
        end_key = (i + 1) * keyspace_per_thread if i != num_threads - 1 else 2 ** 10
        # 创建线程
        thread = threading.Thread(target=brute_force_thread, args=(start_key, end_key, plaintext, ciphertext, results))
        threads.append(thread)  # 将线程添加到线程列表中
        thread.start()  # 启动线程

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 返回找到的密钥，如果没找到则返回"Not found"
    return results[0] if results else "Not found"


# GUI界面

# 创建主窗口
root = tk.Tk()
root.title("S-DES 加密 & 解密")  # 设置窗口标题

# 定义StringVar，用于存储和读取文本框的内容
plaintext_var = tk.StringVar()  # 明文
key_var = tk.StringVar()        # 密钥
ciphertext_var = tk.StringVar() # 密文
decrypted_text_var = tk.StringVar()  # 解密后的文本
cracked_key_var = tk.StringVar()     # 破解的密钥
time_taken_var = tk.StringVar()      # 密钥破解所需时间


# 加密按钮的动作函数
def encrypt_action():
    plaintext = plaintext_var.get()   # 获取明文
    key = key_var.get()               # 获取密钥
    ciphertext = encrypt(plaintext, key)  # 使用给定的密钥对明文进行加密
    ciphertext_var.set(ciphertext)    # 显示加密后的密文


# 解密按钮的动作函数
def decrypt_action():
    ciphertext = ciphertext_var.get() # 获取密文
    key = key_var.get()               # 获取密钥
    decrypted_text = decrypt(ciphertext, key)  # 使用给定的密钥对密文进行解密
    decrypted_text_var.set(decrypted_text)    # 显示解密后的明文


# 密钥破解按钮的动作函数
def crack_key_action():
    start_time = time()               # 记录开始时间
    plaintext = plaintext_var.get()   # 获取明文
    ciphertext = ciphertext_var.get() # 获取密文
    cracked_key = brute_force(plaintext, ciphertext)  # 使用暴力破解方法找到密钥
    end_time = time()                 # 记录结束时间
    cracked_key_var.set(cracked_key)  # 显示破解的密钥
    time_taken_var.set(f"Time taken: {end_time - start_time:.2f} seconds")  # 显示密钥破解所需的时间


# GUI布局和组件初始化
ttk.Label(root, text="明文：").grid(row=0, column=0, sticky="w", padx=10, pady=10)
ttk.Entry(root, textvariable=plaintext_var).grid(row=0, column=1, padx=10, pady=10)
ttk.Label(root, text="密钥 (10-bit)：").grid(row=1, column=0, sticky="w", padx=10, pady=10)
ttk.Entry(root, textvariable=key_var).grid(row=1, column=1, padx=10, pady=10)
ttk.Button(root, text="加密", command=encrypt_action).grid(row=2, column=0, padx=10, pady=10)
ttk.Button(root, text="解密", command=decrypt_action).grid(row=2, column=1, padx=10, pady=10)
ttk.Label(root, text="密文：").grid(row=3, column=0, sticky="w", padx=10, pady=10)
ttk.Entry(root, textvariable=ciphertext_var).grid(row=3, column=1, padx=10, pady=10)
ttk.Label(root, text="解密文本：").grid(row=4, column=0, sticky="w", padx=10, pady=10)
ttk.Entry(root, textvariable=decrypted_text_var).grid(row=4, column=1, padx=10, pady=10)
ttk.Button(root, text="暴力破解", command=crack_key_action).grid(row=5, column=0, padx=10, pady=10)
ttk.Label(root, text="破解密钥:").grid(row=6, column=0, sticky="w", padx=10, pady=10)
ttk.Entry(root, textvariable=cracked_key_var).grid(row=6, column=1, padx=10, pady=10)
ttk.Label(root, textvariable=time_taken_var).grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=10)

root.mainloop()