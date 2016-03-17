# -*- coding:UTF-8 -*-
from PIL import Image
from PIL import ImageEnhance
from PIL import ImageFilter
import pandas as pd
import os
import re
import numpy as np
from AntiNoise import AntiNoise
from sklearn.svm import SVC
from sklearn.neural_network import BernoulliRBM
from sklearn.pipeline import Pipeline
from sklearn.externals import joblib
import datetime


class CaptchaRecognition(object):
    '''

      Should you find any problems or any models with extremely low accuracy in predict results,
      please feel free to contact me.

      Author: Yutong Zhou
      Email: yutongz@princetechs.com


    '''

    image_start = 30  # start postion of first number
    image_width = 30  # width of each number
    image_height = 47  # end postion from top
    image_top = 3  # start postion of top
    image_gap = 0
    width = 0
    height = 0
    image_label_count = 4
    masker = 255
    to_denoise = True
    pixel_index = 1
    to_calculate = False
    customized_postisions = False
    double_denoise = False
    customized_width = None
    position_left = None
    position_right = None
    to_binarized = False
    anti_noise = False
    to_summarized = False
    is_dynamic = False
    style_checker = None

    def __init__(self, captcha_type="beijing"):
        '''

        :param captcha_type:

            captcha_type points out the province captcha you want to use.
            There are few provinces in the same models, but the difference can be ignored.
            You are allowed to use the specific province name as the model name.

            For example:
              beijing is for the model of Beijing City.
              fujian is for Fujian Province, although Yunan has the same model with Fujian.

            Attention:
               zongju stands for the national gov.
               shanxi stands for Shanxi Province, where Taiyuan is the Captial city.
               shaanxi is for Shaanxi Province, whose Captial is Xi'an.
               Neimenggu is for Inner Mengolia.

        :return: predict results
        '''

        captcha_type = captcha_type.lower()
        if captcha_type not in ["jiangsu", "beijing", "zongju", "liaoning", "guangdong", "hubei", "tianjin",
                                "qinghai", "shanxi", "henan", "guangxi", "xizang", "heilongjiang", "anhui", "shaanxi",
                                "ningxia", "chongqing", "sichuan", "hunan", "gansu", "xinjiang", "guizhou", "shandong",
                                "neimenggu", "zhejiang", "heibei", "jilin", "yunnan", "fujian", "hebei", "shanghai"]:
            raise Exception("unknown province %s" % catpcha_type)
        elif captcha_type in ["jiangsu", "beijing", "liaoning"]:
            self.label_list = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
                               "q", "w", "e", "r", "t", "y", "u", "i", "o", "p",
                               "a", "s", "d", "f", "g", "h", "j", "k", "l", "z",
                               "x", "c", "v", "b", "n", "m",
                               "Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P",
                               "A", "S", "D", "F", "G", "H", "J", "K", "L",
                               "Z", "X", "C", "V", "B", "N", "M"]
            self.to_denoise = True
            self.masker = 255
        elif captcha_type in ["guangdong", "hubei", "shanghai", "zongju", "tianjin", "qinghai", "shanxi", "henan",
                              "guangxi", "xizang",
                              "heilongjiang", "anhui", "shaanxi", "ningxia", "chongqing", "sichuan", "hunan", "gansu",
                              "xinjiang", "guizhou", "shandong", "hebei", "neimenggu", "zhejiang", "jilin", "yunnan",
                              "fujian", "hebei"]:
            self.to_denoise = True
            self.masker = 255
            self.to_calculate = True
            self.label_list = [u"零", u"壹", u"贰", u"叁", u"肆", u"伍", u"陆", u"柒", u"捌", u"玖", u"拾", u"加", u"减", u"乘", u"除",
                               u"等", u"于", u"以", u"上", u"去", u"?", u"0", u"1", u"2", u"3", u"4", u"5", u"6", u"7", u"8",
                               u"9", u"的", u"一", u"二", u"三", u"四", u"五", u"六", u"七", u"八", u"九", u"十", u"〇", u"是",
                               u"=", u"*", u"+"]
        if captcha_type == "jiangsu":
            self.image_label_count = 6
            self.image_start = 0
            self.image_width = 20
            self.image_height = 47
            self.image_top = 3
            self.image_gap = 5
        elif captcha_type == "tianjin":
            self.image_label_count = 6
            self.customized_postisions = True
            self.position_left = [13, 40, 73, 104, 136, 162]
            self.position_right = [23, 60, 83, 119, 151, 172]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.customized_width = 20
            self.to_binarized = True
            self.masker = 150
        elif captcha_type in ["yunnan", "fujian", "zongju", "shanghai"]:
            self.image_label_count = 3
            self.margin = 8
            self.customized_postisions = True
            self.position_left = [0, 40, 74]
            self.position_right = [40, 80, 110]
            self.image_top = 5
            self.image_height = 38
            self.image_width = 160
            self.to_denoise = False
            self.customized_width = 25
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 540
            self.to_summarized = True
            self.anti_noise = True
            captcha_type = "yunnan"
        elif captcha_type == "neimenggu":
            self.margin = 8
            self.image_label_count = 3
            self.masker = 450
            self.customized_postisions = True
            self.image_top = 0
            self.image_height = 40
            self.image_width = 180
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 30
            self.anti_noise = True
        elif captcha_type == "chongqing":
            self.image_label_count = 3
            self.margin = 3
            self.customized_postisions = True
            self.position_left = [0, 23, 40]
            self.position_right = [15, 45, 60]
            self.image_top = 8
            self.image_height = 40
            self.image_width = 120
            self.to_denoise = False
            self.customized_width = 25
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 250
            self.to_summarized = True
        elif captcha_type in ["sichuan", "xinjiang"]:
            self.image_label_count = 5
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [3, 18, 35, 49, 65]
            self.position_right = [14, 35, 45, 65, 80]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 20
            self.double_denoise = False
            captcha_type = "sichuan"
        elif captcha_type in ["hunan", "hebei"]:
            self.margin = 8
            self.image_label_count = 3
            self.masker = 450
            self.customized_postisions = True
            self.position_left = [0, 28, 68, 96, 128]
            self.position_right = [30, 68, 108, 131, 160]
            self.image_top = 5
            self.image_height = 35
            self.image_width = 160
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = True
            self.customized_width = 25
            self.anti_noise = True
            captcha_type = "hunan"
        elif captcha_type in ["guizhou"]:
            self.image_label_count = 4
            self.customized_postisions = True
            self.position_left = [31, 51, 90, 115]
            self.position_right = [60, 88, 115, 146]
            self.image_top = 10
            self.image_height = 40
            self.image_width = 260
            self.to_denoise = False
            self.customized_width = 40
            self.to_calculate = True
            self.to_binarized = True
            self.masker = 180
            captcha_type = "guizhou"
        elif captcha_type == "gansu":
            self.image_label_count = 3
            self.customized_postisions = True
            self.position_left = [5, 19, 37]
            self.position_right = [19, 37, 55]
            self.image_top = 25
            self.image_height = 45
            self.to_denoise = False
            self.customized_width = 20
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 580
            self.to_summarized = True
        elif captcha_type == "hubei":
            self.image_label_count = 5
            # self.masker = 110
            self.customized_postisions = True
            self.position_left = [3, 27, 56, 79, 95]
            self.position_right = [28, 57, 82, 97, 124]
            self.image_top = 0
            self.image_height = 40
            self.to_denoise = False
            self.customized_width = 32
            self.double_denoise = False
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 445
            self.to_summarized = True
        elif captcha_type == "shandong":
            self.image_label_count = 4
            self.customized_postisions = True
            self.position_left = [10, 29, 54, 74]
            self.position_right = [29, 54, 74, 93]
            self.image_top = 12
            self.image_height = 32
            self.to_denoise = False
            self.customized_width = 30
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 370
            self.to_summarized = True
        elif captcha_type == "jilin":
            self.image_label_count = 4
            self.customized_postisions = True
            self.position_left = [13, 34, 53, 73]
            self.position_right = [34, 53, 73, 94]
            self.image_top = 12
            self.image_height = 32
            self.to_denoise = False
            self.customized_width = 30
            self.to_calculate = True
            self.to_binarized = False
            self.masker = 410
            self.to_summarized = True
        elif captcha_type == "ningxia":
            self.image_label_count = 5
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [20, 45, 70, 95, 120]
            self.position_right = [35, 60, 85, 110, 135]
            self.image_top = 7
            self.image_height = 27
            self.to_denoise = False
            self.to_calculate = False
            self.to_binarized = True
            self.customized_width = 40
            self.double_denoise = False
        elif captcha_type == "shaanxi":
            self.image_label_count = 5
            self.masker = 110
            self.customized_postisions = True
            self.position_left = [0, 16, 35, 49, 65]
            self.position_right = [15, 35, 44, 65, 80]
            self.image_top = 0
            self.image_height = 30
            self.to_denoise = False
            self.to_binarized = True
            self.customized_width = 30
            self.double_denoise = False
            self.to_calculate = True
        elif captcha_type in ["qinghai", "shanxi", "henan", "guangxi", "xizang", "heilongjiang", "anhui"]:
            self.image_label_count = 5
            self.masker = 420
            self.customized_postisions = True
            self.position_left = [6, 30, 59, 82, 95, 125, 150]
            self.position_right = [28, 57, 81, 100, 135, 155, 175]
            self.image_top = 15
            self.image_height = 50
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = False
            self.customized_width = 40
            self.double_denoise = False
            self.to_summarized = True
            captcha_type = "qinghai"
        elif captcha_type == "liaoning":
            self.image_label_count = 4
            self.image_start = 11
            self.image_width = 9
            self.image_height = 31
            self.image_top = 0
            self.image_gap = 11
            self.to_denoise = False
            self.masker = 254
            self.width = 86
            self.height = 31
            self.style_checker = "model/liaoning_style_checker/model.m"
        # elif captcha_type == "zongju":
        #     self.image_label_count = 4
        #     self.image_width = 180
        #     self.image_height = 50
        #     self.image_top = 5
        #     self.margin = 10.0
        #     self.masker = 550
        #     self.customized_postisions = True
        #     self.to_denoise = False
        #     self.to_calculate = False
        #     self.to_binarized = True
        #     self.customized_width = 25
        #     self.anti_noise = True
        elif captcha_type in ["guangdong"]:
            self.image_label_count = 5
            self.image_start = 26
            self.image_width = 25
            self.image_height = 40
            self.image_top = 0
            self.image_gap = 0
        elif captcha_type == "zhejiang":
            self.image_label_count = 3
            self.masker = 500
            self.is_dynamic = True
            self.dynamic_masker = [110, 175, 175]
            self.customized_postisions = True
            self.position_left = [35, 65, 135]
            self.position_right = [70, 100, 165]
            self.to_denoise = False
            self.to_calculate = True
            self.to_binarized = False
            self.customized_width = 35
            self.to_summarized = False
            self.image_top = 0
            self.image_height = 50
            self.width = 250
            self.height = 50
            self.style_checker = "model/zhejiang_style_checker/model.m"

        self.model_path = "model/" + captcha_type
        self.model_file = self.model_path + "/model.m"

    def __get_pixel_list__(self, captcha_image):

        (width, height) = captcha_image.size
        _pixel_data = []
        for i in range(width):
            for j in range(height):
                if self.to_denoise:
                    pixel = captcha_image.getpixel((i, j))
                    if pixel == self.masker:
                        _pixel_data.append(0.0)
                    else:
                        _pixel_data.append(1.0)
                elif self.is_dynamic:
                    _pixel_data.append(sum(captcha_image.getpixel((i, j))))
                elif self.to_binarized:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j)) < self.masker else 0.0)
                elif self.to_summarized:
                    _pixel_data.append(0.0 if sum(captcha_image.getpixel((i, j))) > self.masker else 1.0)
                else:
                    _pixel_data.append(1.0 if captcha_image.getpixel((i, j))[self.pixel_index] > self.masker else 0.0)
        if self.customized_width is not None:
            difference = self.customized_width - width
            half = difference / 2
            _pixel_data = [0.0] * half * height + _pixel_data + [0.0] * height * (difference - half)
        return _pixel_data

    def __convertPoint__(self, image_path):
        _data = []
        if not self.anti_noise:
            try:
                im = Image.open(image_path)
                (width, height) = im.size
                if self.to_denoise:
                    if self.double_denoise:
                        im = im.convert('L')
                    im = im.filter(ImageFilter.MedianFilter())
                    enhancer = ImageEnhance.Contrast(im)
                    im = enhancer.enhance(10)
                    im = im.convert('L')
                elif self.to_binarized:
                    im = im.convert("L")
                for k in range(self.image_label_count):
                    if not self.customized_postisions:
                        left = max(0, self.image_start + self.image_width * k + self.image_gap * k)
                        right = min(self.image_start + self.image_width * (k + 1) + self.image_gap * k, width)
                    else:
                        left = self.position_left[k]
                        right = self.position_right[k]
                    sub_image = im.crop((left, self.image_top, right, self.image_height))
                    pixel_list = self.__get_pixel_list__(sub_image)
                    if k == 0:
                        _data = np.array([pixel_list])
                    else:
                        try:
                            _data = np.append(_data, [pixel_list], axis=0)
                        except:
                            print image_path, len(pixel_list), len(_data[0])
                            exit(1)
                return _data
            except IOError:
                pass
        else:
            an = AntiNoise(image_path, self.masker)
            pixels = an.pixels
            self.__update_positions__(pixels)
            if len(self.position_left) != self.image_label_count:
                return None
            for i in range(self.image_label_count):
                left = self.position_left[i]
                right = self.position_right[i]
                pixel_list = []
                height = self.image_height - self.image_top
                for x in range(left, right):
                    for y in range(self.image_top, self.image_height):
                        pixel_list.append(pixels[y][x])
                if self.customized_width is not None:
                    difference = self.customized_width - (right - left)
                    half = difference / 2
                    pixel_list = [0.0] * half * height + pixel_list + [0.0] * height * (difference - half)
                if i == 0:
                    _data = np.array([pixel_list])
                else:
                    _data = np.append(_data, [pixel_list], axis=0)

            return _data

    def update_model(self, image_path, label_file, train_size):
        if not os.path.isdir(self.model_path):
            os.mkdir(self.model_path)
        if not os.path.isdir(image_path):
            exit(1)

        image_label_pair = pd.read_csv(label_file, encoding="utf-8")
        image_label_pair = image_label_pair[:train_size]
        index = 0
        x = []
        y = []
        y_count = 0
        start = datetime.datetime.now()
        start_time = datetime.datetime.now()
        for i in range(len(image_label_pair)):
            image = image_path + "/" + str(image_label_pair.iloc[i]["name"])
            labels = image_label_pair.iloc[i]["value"]
            if type(labels) == int:
                labels = str(labels)
            for l in range(self.image_label_count):
                y.append(self.label_list.index(labels[l]))
                y_count += 1
            if index == 0:
                x = self.__convertPoint__(image)
            else:
                x = np.append(x, self.__convertPoint__(image), axis=0)
            # print len(y), len(x)
            index += 1
            end_time = datetime.datetime.now()
            if i in range(0, len(image_label_pair), len(image_label_pair) / 20):
                print u"数据集已完成:", round(float(i) / len(image_label_pair), 4) * 100, "%", u"所用时间:", end_time - start_time
                start_time = datetime.datetime.now()
        print u"数据集已生成 共用时", datetime.datetime.now() - start, u"开始建模"
        rbm = BernoulliRBM(random_state=0, verbose=True, learning_rate=0.02, n_iter=400, n_components=650,
                           batch_size=12)
        svm = SVC(kernel="linear", tol=5e-14, class_weight="balanced")
        classifier = Pipeline(steps=[("rbm", rbm), ("svm", svm)])
        model = classifier.fit(x, y)
        joblib.dump(model, self.model_file)
        return True

    def __convert_to_number__(self, number):
        digits = {u"零": 0, u"〇": 0, u"壹": 1, u"贰": 2, u"叁": 3, u"肆": 4, u"伍": 5, u"陆": 6, u"柒": 7, u"捌": 8, u"玖": 9,
                  u"拾": 10}
        number_in_digit = ""
        for n in number:
            number_in_digit += n if n not in digits else str(digits[n])
        return int(number_in_digit)

    def __calculate__(self, results):

        number_pattern = u"[0-9壹贰叁肆伍陆柒捌玖拾零]+"
        numbers = re.findall(number_pattern, results)
        if len(numbers) < 1:
            return 2
        elif len(numbers) == 1:
            first_num = self.__convert_to_number__(numbers[0])
            if results.__contains__(u"乘") or results.__contains__(u"*"):
                if first_num == 0:
                    return 0
                else:
                    return first_num * 2
            else:
                return first_num

        first_num = self.__convert_to_number__(numbers[0])
        second_num = self.__convert_to_number__(numbers[1])

        if results.__contains__(u"加") or results.__contains__(u"+"):
            return first_num + second_num
        elif results.__contains__(u"减") or results.__contains__(u"-"):
            return first_num - second_num
        elif results.__contains__(u"乘") or results.__contains__(u"*"):
            return first_num * second_num
        elif results.__contains__(u"除") or results.__contains__(u"/"):
            if second_num == 0:
                return 0
            return first_num / second_num

        elif first_num == 0 or second_num == 0:
            return 0
        else:
            return first_num + second_num

    def __update_positions__(self, pixels):
        pixels_sum = sum(pixels)
        # print pixels_sum
        start = 0
        for i in range(10):
            count = pixels_sum[i]
            if count > self.margin:
                start = i
                break
            else:
                start = i

        position_left = range(start, self.image_width, self.customized_width)[:self.image_label_count]
        index = 0
        # print position_left
        for i in range(1, self.image_label_count):
            index = position_left[i]
            l = pixels_sum[index]
            while l <= self.margin:
                index += 1
                if index > self.image_width - 1:
                    break
                l = pixels_sum[index]
            left = range(index, self.image_width, self.customized_width)[:(self.image_label_count - i)]
            position_left = position_left[:i] + left

        if len(position_left) != self.image_label_count:
            self.position_left = []
        else:
            position_right = [0] * self.image_label_count
            for i in range(self.image_label_count):
                position_right[i] = min(self.image_width - 1, position_left[i] + self.customized_width)

            self.position_left = position_left
            self.position_right = position_right

    def __check_style__(self, im):
        if self.style_checker is not None:
            im_checker = im.convert("L")
            width, height = im_checker.size
            if width != self.width and height != self.height:
                return 0

            checker = joblib.load(self.style_checker)
            pixel = []
            for w in range(width):
                for h in range(height):
                    pixel.append(im_checker.getpixel((w, h)))
            pixel = np.array([pixel])
            predict = checker.predict(pixel)
            return predict
        else:
            return 1

    def predict_result(self, image_path):
        '''
        This function will return two results.
        The first one is the predict value,
        and the second one is used to pass the Captcha.

        If the captcha is in the type of calculation, the second value is a number;
        and if the captcha is the type of letters and/or numbers, the second value is the content.
        '''
        if os.path.isfile(self.model_file):
            self.clf = joblib.load(self.model_file)
        else:
            raise IOError
        try:
            im = Image.open(image_path)
        except:
            return "", ""

        if self.__check_style__(im) == 0:
            return "", ""

        pixel_matrix = self.__convertPoint__(image_path)
        if pixel_matrix is None:
            return "", ""
        pixel_matrix = self.__convertPoint__(image_path)
        if pixel_matrix is None:
            return "", ""
        predict_result = u""
        for feature in pixel_matrix:
            _f = np.array([feature], dtype=np.float)
            predict = self.clf.predict(_f)[0]
            if int(predict) >= len(self.label_list) or int(predict) < 0:
                return "", ""
            predict_result += unicode(self.label_list[int(predict)])

        if self.to_calculate:
            return predict_result, self.__calculate__((predict_result))
        else:
            return predict_result, predict_result
