# 信息安全导论作业——S-DES加密

## 1.背景介绍

## 2.算法流程

### 总体流程

![image-20231012210445444](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012210445444.png)

上图是加密和解密的总体流程，下面介绍具体步骤

### 具体步骤

#### 加密

##### 1.密钥生成

输入10位二进制的密钥，先与P10进行直接置换，左移一位与P8进行压缩置换得到子密钥k1；将P10置换后的密钥左移两位与P8进行压缩置换得到子密钥k2![image-20231012140948752](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012140948752.png)



##### 2.明文初始置换

输入8位二进制的明文，与IP进行**直接置换**

![image-20231012151228815](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012151228815.png)

##### 3.**S-DES 函数** fk

将上步得到的8位等**分割**成左右两部分

对右边部分进行**轮函数**F操作

![image-20231012154019116](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012154019116.png)

1.与EPBox进行**扩展置换**

![image-20231012154042646](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012154042646.png)

2.加轮密钥，与k1进行**异或**操作

![image-20231012205713038](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012205713038.png)

3.分割成左右部分，分别于替换盒SBox进行**替换**操作，得到两段2位二进制数

![image-20231012205729311](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012205729311.png)

4.拼在一起得到4位二进制数，与SP进行**直接置换**，轮函数完成

![image-20231012210151358](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012210151358.png)

得到的4位右边部分与左边部分进行**异或**操作作为左边，右边仍然用最初的右边部分

![image-20231012210205455](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012210205455.png)

这里将**左右互换**，再执行一次S-DES函数，这次的加轮密钥用k2操作。这里可以进行拓展，执行几次S-DES函数，就在密钥生成环节生成相同数量的密钥

![image-20231012210230364](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012210230364.png)

##### 4.最终置换

将左右合并，与IP^-1进行置换，注意，一串明文经过一次IP置换，马上进行IP^-1置换能够得到它自己

![image-20231012210406953](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012210406953.png)

IP^-1置换得到的就是密文

#### 解密

解密步骤与加密相同，将明文替换为密文，以及将两次轮函数所用的子密钥的**顺序颠倒**即可

### 数据

密钥扩展置换：P10与P8置换

![image-20231012211022530](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211022530.png)

初始置换盒：

![image-20231012211114439](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211114439.png)

最终置换盒：

![image-20231012211129780](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211129780.png)

轮函数F：

​	EP扩展置换

![image-20231012211149885](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211149885.png)

​	SBox替换盒

![image-20231012211233063](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211233063.png)

SP直接置换：

![image-20231012211255890](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211255890.png)

### 运行环境

Python 3.9,

NVIDIA RTX 4090 GPU,

i9-13980HX CPU

## 3.关卡测试

### 第一关：基本测试

根据S-DES算法编写和调试程序，提供GUI解密支持用户交互。输入可以是8bit的数据和10bit的密钥，输出是8bit的密文。

测试：

加密：

![image-20231012211607034](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211607034.png)

解密：

![image-20231012211618506](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211618506.png)

### 第二关：交叉测试

考虑到是**算法标准**，所有人在编写程序的时候需要使用相同算法流程和转换单元(P-Box、S-Box等)，以保证算法和程序在异构的系统或平台上都可以正常运行。

设有A和B两组位同学(选择相同的密钥K)；则A、B组同学编写的程序对明文P进行加密得到相同的密文C；或者B组同学接收到A组程序加密的密文C，使用B组程序进行解密可得到与A相同的P。

测试：

![image-20231012211708602](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012211708602.png)

![level2_encode](C:\Users\25300\Documents\Tencent Files\2530043389\FileRecv\level2_encode.gif)

### 第三关：扩展功能

考虑到向实用性扩展，加密算法的数据输入可以是ASII编码字符串(分组为1 Byte)，对应地输出也可以是ACII字符串(很可能是乱码)。

测试：

![image-20231012212055358](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012212055358.png)

### 第四关：暴力破解

假设你找到了使用相同密钥的明、密文对(一个或多个)，请尝试使用暴力破解的方法找到正确的密钥Key。在编写程序时，你也可以考虑使用多线程的方式提升破解的效率。请设定时间戳，用视频或动图展示你在多长时间内完成了暴力破解。

![image-20231012212147675](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012212147675.png)

### 第五关：封闭测试

根据第4关的结果，进一步分析，对于你随机选择的一个明密文对，是不是有不止一个密钥Key？进一步扩展，对应明文空间任意给定的明文分组$$P_{n}$$，是否会出现选择不同的密钥$$K_{i}\ne K_{j}$$ 加密得到相同密文$$C_n$$的情况？

测试：

![image-20231012213233749](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012213233749.png)

![image-20231012213239773](C:\Users\25300\AppData\Roaming\Typora\typora-user-images\image-20231012213239773.png)

问题解答：

是否有不止一个密钥可以对应同一明密文对？或者说，对应明文空间任意给定的明文分组，是否会出现选择不同的密钥加密得到相同密文的情况？这种情况是可能发生的，特别是当明文空间大于密钥空间时。在这里，我们有2^8 = 256个可能的明文和2^10 = 1024个可能的密钥，这使得密钥空间非常有限。这种现象称为"密钥冲突"，也就是说当两个不同的密钥对同一个明文加密时产生相同的密文，这意味着这两个密钥在此特定明文上是不可区分的。总的来说，对于S-DES算法，由于它的简单性和有限的密钥空间，发生密钥冲突的可能性较高。

