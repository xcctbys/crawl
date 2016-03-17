import numpy as np
from PIL import Image


class AntiNoise(object):
    offset = 3
    threshold = 20
    masker = 545

    def __init__(self, image_path, makser):
        self.masker = makser
        im = Image.open(image_path)
        self.width, self.height = im.size
        self.pixels = self.__generate_pixels__(im)
        self.__noise_detection__()

    def __generate_pixels__(self, im):

        pixels = np.zeros((self.height, self.width))

        for h in range(self.height):
            for w in range(self.width):
                if sum(im.getpixel((w, h))) <= self.masker:
                    pixels[h][w] = 1

        return pixels

    def __print_pixels__(self):
        # print 0, "\t".join([str(x) for x in range(0, 180)])
        for i in range(10, 50):
            line = self.pixels[i]
            print i, "\t".join(["x" if x == 1 else "" for x in line])

    def __remove_noise__(self):
        for h in range(len(self.pixels)):
            for w in range(len(self.pixels[h])):
                self.pixels[h][w] = 1 if self.pixels[h][w] == 1 else 0

    def __noise_detection__(self):

        ys = []
        xs = []
        for h in range(self.height):
            for w in range(self.width):
                ys0, xs0 = self.__noise_detection_helper(w, h, 0)
                ys1, xs1 = self.__noise_detection_helper(w, h, 1)
                ys += ys0 + ys1
                xs += xs0 + xs1

        if len(ys) >= self.offset:
            for i in range(len(ys)):
                self.pixels[ys[i]][xs[i]] = 2
        self.__remove_noise__()
        # for w in range(self.width):
        #     for h in range(self.height):
        #         self.__noise_detection_helper(w, h, 0)
        #         self.__noise_detection_helper(w, h, 1)
        # self.__remove_noise__()
        # print "Noise Detection is finished. Please have a check."
        # self.__print_pixels__()

    def __noise_detection_helper(self, x=0, y=0, direction=0, last_empty=False):
        '''

        direction: a binary parameter, 0 for up, 1 for down.
            All directions are towards to right.

        x and y locate the currect position.

        x = 0 means the leftest of the image, and x = width - 1 means the rightest of the image.
        y = 0 means the top of the image, and y = height - 1 means the bottom of the image.

        This function starts default at (0, 0) point.

        last_empty stands for the case that the last position is empty or not.
            If both the last position and the current one are empty , it will be considered to stop;
            otherwise, it is going to detect next position.
        '''
        # print x, y
        if y == 0 and direction == 0:
            return [], []
        elif y == self.height - 1 and direction == 1:
            return [], []
        elif x == self.width - 1:
            return [], []

        checker = []

        if x == 0:
            if y == 0:
                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y][x + 1])
                checker.append(self.pixels[y + 1][x + 1])
            elif y == self.height - 1:
                checker.append(self.pixels[y - 1][x])

                checker.append(self.pixels[y - 1][x + 1])
                checker.append(self.pixels[y][x + 1])
            else:
                checker.append(self.pixels[y - 1][x])
                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y - 1][x + 1])
                checker.append(self.pixels[y][x + 1])
                checker.append(self.pixels[y + 1][x + 1])
        elif x == self.width - 1:

            if y == 0:
                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y][x - 1])
                checker.append(self.pixels[y + 1][x - 1])
            elif y == self.height - 1:
                checker.append(self.pixels[y - 1][x])

                checker.append(self.pixels[y - 1][x - 1])
                checker.append(self.pixels[y][x - 1])
            else:
                checker.append(self.pixels[y - 1][x])
                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y - 1][x - 1])
                checker.append(self.pixels[y][x + 1])
                checker.append(self.pixels[y + 1][x - 1])
        else:

            if y == 0:
                checker.append(self.pixels[y][x - 1])
                checker.append(self.pixels[y + 1][x - 1])

                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y][x + 1])
                checker.append(self.pixels[y + 1][x + 1])
            elif y == self.height - 1:
                checker.append(self.pixels[y - 1][x - 1])
                checker.append(self.pixels[y][x - 1])

                checker.append(self.pixels[y - 1][x])

                checker.append(self.pixels[y - 1][x + 1])
                checker.append(self.pixels[y][x + 1])
            else:
                checker.append(self.pixels[y - 1][x - 1])
                checker.append(self.pixels[y][x - 1])
                checker.append(self.pixels[y + 1][x - 1])

                checker.append(self.pixels[y - 1][x])
                checker.append(self.pixels[y + 1][x])

                checker.append(self.pixels[y - 1][x + 1])
                checker.append(self.pixels[y][x + 1])
                checker.append(self.pixels[y + 1][x + 1])

        if sum(checker) >= 3:
            return [], []
        elif sum(checker) == 0:
            return [y], [x]

        y_list = []
        x_list = []
        new_y_list = []
        new_x_list = []
        new_y = y - 1 if direction == 0 else y + 1
        new_x = x + 1
        if self.pixels[new_y][new_x] > 1:
            y_list.append(y)
            x_list.append(x)
            new_y_list, new_x_list = self.__noise_detection_helper(new_x, new_y, direction, last_empty)
        elif self.pixels[y][new_x] > 1:
            y_list.append(y)
            x_list.append(x)
            new_y_list, new_x_list = self.__noise_detection_helper(new_x, y, direction, last_empty)
        else:
            if last_empty:
                return [], []
            checker1_y, _ = self.__noise_detection_helper(new_x, y, direction, last_empty=True)
            if len(checker1_y) == 0:
                y_list.append(y)
                x_list.append(x)
            checker2_y, _ = self.__noise_detection_helper(new_x, new_y, direction, last_empty=True)
            if len(checker2_y) == 0:
                y_list.append(y)
                x_list.append(x)
        y_list += new_y_list
        x_list += new_x_list
        return y_list, x_list


# #
if __name__ == '__main__':
    image_path = "raw/images/zongju/zongju1_481.png"
    an = AntiNoise(image_path, 550)
