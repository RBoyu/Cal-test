import numpy as np
import math
from math import sqrt
import time
import shutil

def print_centred(text, width=None):
    if width is None:
        width = shutil.get_terminal_size().columns
    # 计算需要添加的空格数
    padding = (width - len(text)) // 2
    # 打印居中的文本
    print(f"{padding * ' '}{text}")

#part文件存储粒子速度信息 
def read_data(filename):
    v_x = []
    v_y = []
    v_z = []
    l_x = []
    l_y = []
    valid_line_found = False  # 添加一个标志，用于跟踪是否找到有效的行
    try:
        with open(filename, 'r') as file:
            for line_number, line in enumerate(file, 1):
                columns = line.split()
                if len(columns) >= 7:  # 至少需要7列数据
                    valid_line_found = True  # 找到至少一个有效行
                    vx = float(columns[2])
                    vy = float(columns[4])
                    vz = float(columns[6])
                    lx = float(columns[1])
                    ly = float(columns[3])
                    v_x.append(vx)
                    v_y.append(vy)
                    v_z.append(vz)
                    l_x.append(lx)
                    l_y.append(ly)
    except FileNotFoundError:
        print_centred(f"错误：文件 '{filename}' 未找到。")
        time.sleep(5)  # 如果文件未找到，直接退出前等待5秒
        return None, None, None, None, None, None

    if not valid_line_found:
        print_centred("错误：文件中没有找到任何符合要求的数据行。")
        time.sleep(5)  # 如果没有有效行，退出前等待5秒
        return None, None, None, None, None, None

    count = len(v_x)
    return np.array(v_x), np.array(v_y), np.array(v_z), count, l_x, l_y

#计算横向速度与纵向速度的比值
def speed_fraction(v_x, v_y, v_z):
	x_p = v_x / v_z
	y_p = v_y / v_z
	return x_p, y_p

#计算RMS发散角
def RMS_theta(x_p, y_p, count):
	RMS_x = sqrt(sum(x**2 for x in x_p) / count)
	RMS_y = sqrt(sum(x**2 for x in y_p) / count)
	RMS_total = sqrt((sum(x**2 for x in x_p)+sum(x**2 for x in y_p)) / (count + count))
	RMS_x_degrees = math.degrees(RMS_x)
	RMS_y_degrees = math.degrees(RMS_y)
	RMS_total_degrees = math.degrees(RMS_total)

	return RMS_x, RMS_y, RMS_total, RMS_x_degrees, RMS_y_degrees, RMS_total_degrees

#计算束偏角
def Beam_declination(x_p, y_p, count):
	Beam_dec = sqrt((sum(x_p)/count)**2+((sum(y_p)/count)**2))
	Beam_dec_degrees = math.degrees(Beam_dec)

	return Beam_dec, Beam_dec_degrees

#计算束offset
def Beam_offset(l_x, l_y, count):
	Offset = sqrt((sum(l_x)/count)**2+((sum(l_y)/count)**2))
	return Offset

#按Ref{Beam optics of RF ion sources in view of ITER’s NBI systems}计算1/e发散角
def e1_theta(v_x, v_y, v_z, count):
	mean_vx = np.mean(v_x)
	mean_vy = np.mean(v_y)
	mean_xy = (sum(v_x) + sum(v_y)) / (2 * count)
	refe1_theta = sqrt(2*np.mean(np.arctan((v_x-mean_vx)/v_z)**2))
	refe1_theta_degrees = math.degrees(refe1_theta)
	return refe1_theta, refe1_theta_degrees

#按GPT的方差方法计算
def e1_theta2(v_x, v_y, v_z, count):
	mean_vx = np.mean(v_x)
	mean_vy = np.mean(v_y)
	mean_vz = np.mean(v_z)
	mean_xy = (sum(v_x) + sum(v_y)) / (2 * count)
	variance_vx = np.mean((v_x - mean_vx)**2)
	variance_vy = np.mean((v_y - mean_vy)**2)
	GPTe1_theta = np.arctan(sqrt(2*variance_vx)/mean_vz)
	GPTe1_theta_degrees = math.degrees(GPTe1_theta)
	return GPTe1_theta, GPTe1_theta_degrees




#主函数
def main():

	print()
	print()
	print_centred(f"IBSIMU跑完计算会生成part.txt文件，存储粒子信息。")
	print_centred(f"本程序通过信息文件计算相关参数。")
	print_centred(f"By:Enn Inscyn")
	print()
	print()
	filename = 'part.txt'
	v_x, v_y, v_z, count, l_x, l_y = read_data(filename)
	#if count is None:
	#	print_centred(f"文件未找到或数据为空")  # 如果文件未找到或数据为空，不执行后续计算
	#	time.sleep(5)  # 程序将等待60秒后自动退出
	#	return
	x_p, y_p = speed_fraction(v_x, v_y, v_z)
	RMS_x, RMS_y, RMS_total, RMS_x_degrees, RMS_y_degrees, RMS_total_degrees = RMS_theta(x_p, y_p, count)
	Beam_dec, Beam_dec_degrees = Beam_declination(x_p, y_p, count)
	Offset = Beam_offset(l_x, l_y, count)
	refe1_theta, refe1_theta_degrees = e1_theta(v_x, v_y, v_z, count)
	GPTe1_theta, GPTe1_theta_degrees = e1_theta2(v_x, v_y, v_z, count)

	print()
	print()
	print_centred(f"采集到的粒子数：{count} 个")
	print_centred(f"RMS_x:{RMS_x*1000:.2f} mrad, {RMS_x_degrees:.2f} deg")
	print_centred(f"RMS_y: {RMS_y*1000:.2f} mrad, {RMS_y_degrees:.2f} deg")
	print_centred(f"RMS_total: {RMS_total*1000:.2f} mrad, {RMS_total_degrees:.2f} deg")
	print_centred(f"束偏角Beam_declination为:{Beam_dec*1000:.2f} mrad, {Beam_dec_degrees:.2f} deg")
	print_centred(f"束Offset为：{Offset*1000:.2f} mm")
	print()
	print()
	print_centred(f"Ref:1/e divergence(X方向) = {refe1_theta*1000:.6f} mrad, {refe1_theta_degrees:.6f} deg")
	print_centred(f"GPT:1/e divergence(X方向) = {GPTe1_theta*1000:.6f} mrad, {GPTe1_theta_degrees:.6f} deg")

	time.sleep(60)  # 程序将等待60秒后自动退出



if __name__ == "__main__":
    main()