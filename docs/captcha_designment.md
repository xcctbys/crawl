# Statement of Goals

方便开发人员使用，破解工商信用网站的验证码

# Functional Description

## 识别图像文字

- 输入: 图像内容
- 输出: 识别码
- 逻辑流程
- 性能
    
    90%的响应时间控制在3s以下
    内存占用不超过1G
    
- 失败后，直接抛出异常
- 支持python2.7，模型从远程下载，不再入代码库


# User Interface


## 图像识别的编程接口

- 调用方式: 使用sdk的方式调用
- 输入
    
    province: string
    image: Image
    
- 输出: string of captcha, unicode type
- 例子

    from captcha_recoginition import CaptchaRecognition
    
    recoginition = CaptchaRecognition("beijing", im)
    result = recoginition.predict()
    

## 配置模型行为

配置存放目录，修改 clawer/settings.py 文件，加入

    CAPTCHA_MODEL_DIR = "/data/clawer/model/"
    
配置下载模型的url地址，远程文件是经过gzip压缩过的。修改 clawer/settings.py 文件，加入

    CAPTCHA_MODEL_URL = "http://x.com/model.tgz"
    


# Internel 内部实现

## Directory 代码目录结构

     |-- captcha
     |---- captcha_recoginition.py  #实现 CaptchaRecognition

