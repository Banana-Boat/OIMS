from math import degrees,atan,fabs


def compute_sva(c7side, sacrum, resolution):
    #不知道你们坐标按啥形式读的，我按每组传入的是xmin ymin xmax ymax这种写了，要是不对你们改改下标
    """计算sva，单位：cm
    sva的计算方法：
        c7side为侧面颈部c7检测框的坐标，取该框的***中心点***的x坐标
        sacrum为侧面骶1检测框的坐标，取该框的***左上端点***的x坐标
        sva为这两点x坐标距离
    """
    #c7中点的x坐标
    middleP_c7side=(c7side[0]+c7side[2])/2

    #sacrum左上端点的x坐标
    leftUpperP_sacrum=sacrum[0]

    #计算这两个x坐标的距离，然后除以分辨率，再从英尺还是什么换算成厘米
    distance = fabs(middleP_c7side - leftUpperP_sacrum)
    distance /= resolution
    distance *= 2.54

    return distance


def compute_cva(c7front, sacrumfront, resolution):
    """计算cva，单位：cm
    cva的计算方法：
        c7front为正面颈部c7检测框的坐标，取该框的***中心点***的x坐标
        sacrumfront为正面骶1检测框的坐标，取该框的***中心点***的x坐标
        cva为这两点x坐标距离
    """
    # c7中点的x坐标
    middleP_c7side = (c7front[0] + c7front[2]) / 2

    # sacrum左上端点的x坐标
    middleP_sacrum = (sacrumfront[0]+sacrumfront[2])/2

    # 计算这两个x坐标的距离，然后除以分辨率，再从英尺还是什么换算成厘米
    distance = fabs(middleP_c7side - middleP_sacrum)
    distance /= resolution
    distance *= 2.54

    return distance


def compute_cobb(upper, lower):
    """计算cobb角，单位：°
    cobb的计算方法：
        upper为/这么倾斜角度最大的椎体的***上边缘线***
        lower为\这么倾斜角度最大的椎体的***下边缘线***
        cobb为这两条线延长线的夹角

        由于我们用目标检测方法检测这些椎体，都是把这些斜线作为对角线框住，所以/
            此处的计算函数内不区分上下边缘线，只要有对角线的坐标就可以
        该函数计算方式为分别计算这两条线与水平方向夹角，然后相加
    """
    #                            ymax   -   ymin     /   xmax    - xmin
    upper_angle = degrees(atan(upper[3] - upper[1]) / (upper[2] - upper[1]))
    #                            ymax   -   ymin     /   xmax    - xmin
    lower_angle = degrees(atan(lower[3] - lower[1]) / (lower[2] - lower[1]))
    cobb_angle=upper_angle+lower_angle

    return cobb_angle


def compute_LL(T12, sacrum):
    """计算LL，单位：°
    LL的计算方法：
        T12为T12的***上边缘线***
        sacrum为骶1的***上边缘线***
        LL为这两条线延长线的夹角

        该函数计算方式为分别计算这两条线与水平方向夹角，然后相加
    """
    #                            ymax   -   ymin     /   xmax    - xmin
    upper_angle = degrees(atan(T12[3] - T12[1]) / (T12[2] - T12[1]))
    #                            ymax   -   ymin     /   xmax    - xmin
    lower_angle = degrees(atan(sacrum[3] - sacrum[1]) / (sacrum[2] - sacrum[1]))
    LL=upper_angle+lower_angle

    return LL