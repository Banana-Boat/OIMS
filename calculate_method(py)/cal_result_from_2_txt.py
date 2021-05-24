import numpy as np
import os
from math import atan, degrees
import cv2
"""下面两个函数从txt中获得p0-3关键点"""
"""
----------------------------------------------------------
txt1：sacrum.txt,每张图片记录一组xmin,ymin,xmax,ymax
(sacrum是计算必需的，如果某张图没有检测到sacrum，在计算过程中会被跳过)
得到p0:(xmin,ymin)                    (p0=骶1上缘线左上端点)
得到p1:(xmax,ymax)                    (p1=骶1上缘线右下端点)
得到p3:((xmin+xmax)/2,(ymin+ymax)/2)  (p2=骶1上缘线中点)

----------------------------------------------------------
txt2：femoralhead.txt,每张图片记录2组xmin,ymin,xmax,ymax
(只有1个股骨的按两坐标相同处理)
得到两个股骨中心p5=((xmin1+xmax1)/2,(ymin1+ymax1)/2)
             p6=((xmin2+xmax2)/2,(ymin2+ymax2)/2)
得到两个股骨中心连线的中心：
p2：((xmin1+xmax1+xmin2+xmax2)/4,(ymin1+ymax1+ymin2+ymax2)/4)
----------------------------------------------------------
"""

def get_sacrum(txtname):
    """返回每张图的[图片名，p0,p1,p3]"""
    txtlines = []
    with open(txtname, 'r') as f:
        txtlines = f.readlines()
        f.close()

    res = []
    for l in txtlines:
        name, v, xmin, ymin, xmax, ymax = l.split()
        res.append([
            name, (int(xmin), int(ymin)), (int(xmax), int(ymax)),
            (int((int(xmin) + int(xmax)) / 2), int(
                (int(ymin) + int(ymax)) / 2))
        ])
    #print(res)
    return res


def get_femoral(txtname):
    """返回每张图的[图片名，p2,股骨中心1，股骨中心2]"""
    txtlines = []
    with open(txtname, 'r') as f:
        txtlines = f.readlines()
        f.close()

    res = []

    i = 0
    while i < len(txtlines):
        if i == len(txtlines) - 1:
            name, v, xmin, ymin, xmax, ymax = txtlines[i].split()
            res.append([
                name,
                (int((int(xmin) + int(xmax) + int(xmin) + int(xmax)) / 4),
                 int((int(ymin) + int(ymax) + int(ymin) + int(ymax)) / 4)),
                (int((int(xmin) + int(xmax)) / 2),
                 int((int(ymin) + int(ymax)) / 2)),
                (int((int(xmin) + int(xmax)) / 2),
                 int((int(ymin) + int(ymax)) / 2))
            ])
            break

        name, v, xmin, ymin, xmax, ymax = txtlines[i].split()
        name_, v_, xmin_, ymin_, xmax_, ymax_ = txtlines[i + 1].split()

        if name == name_:  #假如检测出两个股骨
            res.append([
                name,
                (int((int(xmin) + int(xmax) + int(xmin_) + int(xmax_)) / 4),
                 int((int(ymin) + int(ymax) + int(ymin_) + int(ymax_)) / 4)),
                (int((int(xmin) + int(xmax)) / 2),
                 int((int(ymin) + int(ymax)) / 2)),
                (int((int(xmin_) + int(xmax_)) / 2),
                 int((int(ymin_) + int(ymax_)) / 2))
            ])
            i += 2
        else:  #假如检测出一个股骨
            res.append([
                name,
                (int((int(xmin) + int(xmax) + int(xmin) + int(xmax)) / 4),
                 int((int(ymin) + int(ymax) + int(ymin) + int(ymax)) / 4)),
                (int((int(xmin) + int(xmax)) / 2),
                 int((int(ymin) + int(ymax)) / 2)),
                (int((int(xmin) + int(xmax)) / 2),
                 int((int(ymin) + int(ymax)) / 2))
            ])
            i += 1
    #print(res)
    return res


"""下面三个函数计算三个骨盆参数"""
'''
对一张图片，检测结果包含如下数据：
骶骨上边缘线，用两个坐标表示：p0(x0，y0),p1(x1,y1)
股骨中心坐标：p2(x2,y2)
得到骶骨上边缘中心为((x0+x1)/2,(y0+y1)/2),记为p3(x3,y3)
--------------------------------------------------------------------
ss参数：表示骶骨上边缘线与水平方向夹角
ss=arctan((y1-y0)/(x1-x0))

pt参数：表示（骶骨上边缘中心与股骨中心连线）与（竖直方向）的夹角
pt=90-arctan((y3-y2)/(x3-x2))

pi参数：表示（骶骨上边缘中心与股骨中心连线）与(骶骨上边缘线的垂线)的夹角
=ss+pt
pi=ss+pt
'''


def compute_ss(p0, p1):
    #传入p0[x0,y0],p1[x1,y1]
    return degrees(atan((p1[1] - p0[1]) / (p1[0] - p0[0])))


def compute_pt(p0, p1, p2):
    #传入p0[x0,y0],p1[x1,y1],p2[x2,y2]
    p3 = [(p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2]
    return 90.0 - degrees(atan((p3[1] - p2[1]) / (p3[0] - p2[0])))


def compute_pi(ss, pt):
    #传入计算过的ss和pt
    return ss + pt


"""下面两个函数用来把缩小后的坐标还原到原尺寸"""
'''scale：图片缩放的比例，用于把坐标放大回去绘制在原尺寸图片上，我们项目中使用5'''


def x2orix(x, half_h):
    scale = 5
    return scale * x


def y2oriy(y, half_h):
    scale = 5
    return scale * y + half_h


def main():

    #这是原尺寸图像的路径
    picpath = r'./temp_data/img/side_contrast/'
    #这是输出绘制了参数的图像的路径
    outpath = r'./output_from_txt/'

    sac = get_sacrum('./temp_data/txt/sacrum.txt')
    fem = get_femoral('./temp_data/txt/femoralhead.txt')
    #print('sacrums:')
    #print(sac)
    #print('femorals:')
    #print(fem)
    """total:[图片名，p0,p1,p2,p3,p4,p5]"""
    total = []
    for i in sac:
        p0 = i[1]
        p1 = i[2]
        p3 = i[3]
        p2 = []
        p4 = []
        p5 = []
        for j in fem:
            if j[0] == i[0]:
                p2 = j[1]
                p4 = j[2]
                p5 = j[3]
        total.append([i[0], p0, p1, p2, p3, p4, p5])
    for i in total:
        print('-------------------------------------------')
        img = cv2.imread(os.path.join(picpath, i[0] + '.jpg'))
        h, w = img.shape[:2]
        h = int(h / 2)
        w = int(w / 2)

        #骶骨上缘两端点
        p0 = i[1]
        p1 = i[2]
        #股骨连线中心
        p2 = i[3]
        #骶骨上缘中点
        p3 = i[4]
        #两个股骨头中心
        p4 = i[5]
        p5 = i[6]
        print(i)

        #还原到原尺寸
        p0 = (x2orix(p0[0], h), y2oriy(p0[1], h))
        p1 = (x2orix(p1[0], h), y2oriy(p1[1], h))
        p2 = (x2orix(p2[0], h), y2oriy(p2[1], h))
        p3 = (x2orix(p3[0], h), y2oriy(p3[1], h))
        p4 = (x2orix(p4[0], h), y2oriy(p4[1], h))
        p5 = (x2orix(p5[0], h), y2oriy(p5[1], h))
        #print(p0,p1,p2,p3,p4,p5)

        #骶骨上缘p0p1的斜率
        k01 = (p0[1] - p1[1]) / (p0[0] - p1[0])
        #垂线的斜率
        k01d = -1 / k01
        #用来画垂线的点
        p01d = (p3[0] - 300, int(p3[1] - 300 * k01d))

        #骶骨上缘线
        cv2.line(img, p1, p0, (255, 0, 0), 4)
        #骶骨上缘中点和股骨中点连线
        cv2.line(img, p2, p3, (255, 0, 0), 4)
        #两个股骨头连线
        cv2.line(img, p4, p5, (255, 0, 0), 4)
        #股骨中点往上的竖线
        cv2.line(img, p2, (p2[0], p2[1] - 600), (255, 0, 0), 4)
        #骶骨上缘的垂线
        cv2.line(img, p3, p01d, (255, 0, 0), 4)

        #计算三个参数
        ss = round(compute_ss(p0, p1), 3)
        pt = round(compute_pt(p0, p1, p2), 3)
        pi = round(compute_pi(ss, pt), 3)
        print('ss=' + str(ss))
        print('pt=' + str(pt))
        print('pi=' + str(pi))

        #在图片上绘制文字
        cv2.putText(img, 'SS=' + str(ss), (w, h), cv2.FONT_ITALIC, 6.0,
                    (255, 255, 255), 5)
        cv2.putText(img, 'PT=' + str(pt), (w, h + 300), cv2.FONT_ITALIC, 6.0,
                    (255, 255, 255), 5)
        cv2.putText(img, 'PI=' + str(pi), (w, h + 600), cv2.FONT_ITALIC, 6.0,
                    (255, 255, 255), 5)

        #骶骨上缘两端点
        cv2.circle(img, p0, 10, (0, 0, 255), 10)
        cv2.circle(img, p1, 10, (0, 0, 255), 10)
        #骶骨上缘中点
        cv2.circle(img, p2, 10, (0, 0, 255), 10)
        #股骨连线中点
        cv2.circle(img, p3, 10, (0, 0, 255), 10)
        #两个股骨中心
        cv2.circle(img, p4, 10, (0, 0, 255), 10)
        cv2.circle(img, p5, 10, (0, 0, 255), 10)

        #输出绘制了辅助线和参数数值的图片
        cv2.imwrite(os.path.join(outpath, i[0] + '.jpg'), img)
        print(i[0] + ' written')


if __name__ == '__main__':
    main()
'''
------------------------------------
        faster-rcnn/iter=40000
------------------------------------
        For:femoralhead
        ap:0.9518002322880371
------------------------------------
        For:sacrum
        ap:0.9047619047619048
------------------------------------
        map:0.9282810685249709
------------------------------------
'''