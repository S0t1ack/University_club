import time
import argparse
import numpy as np
#import navio.mpu9250
import mpu92_forTest


import functions as fcn

def get_angle():
    #IMU = navio.mpu9250.MPU9250()

    #IMU.initialize(1,0x06)#lowpass->20Hz

    mpu92_forTest.MPU9265_init()

    time.sleep(1)

    m6a0=np.zeros((3,))
    m6g0=np.zeros((3,))

    for i in range(1,1000):
        #ma0, mg0 = IMU.getMotion6()
        ma0=mpu92_forTest.get_accel()
        mg0=mpu92_forTest.get_gyro()

        m6a0=m6a0+np.array(ma0)
        m6g0=m6g0+np.array(mg0)

    m6g0=m6g0/1000
    m6a0=m6a0/1000
    m6a0[0],m6a0[1]=m6a0[1],m6a0[0]
    m6g0[0],m6g0[1]=m6g0[1],m6g0[0]

    x0=np.zeros((2,))
    for i in range(1,1000):
        #m6a, m6g = IMU.getMotion6()
        m6a=mpu92_forTest.get_accel()
        m6g=mpu92_forTest.get_gyro()

        m6a[0],m6a[1]=-m6a[1],-m6a[0]
        m6a=np.array(m6a)
        x0=x0+fcn.get_angle_acc(m6a)
    x0=x0/1000

    x=x0
    P=np.zeros((2,2))
    Ts=1.0/40.0
    Yaw=0
    Tri=np.zeros((2,3))

    c=np.array([[1,0],[0,1]])
    q=np.array([[1.74E-3*Ts*Ts,0],[0,1.74E-3*Ts*Ts]])
    b=np.array([[1,0],[0,1]])
    r=np.array([[1*Ts*Ts,0],[0,1*Ts*Ts]])
    Cgy=np.eye(3,3)*1.74E-3*Ts*Ts

    count=0
    m6g_before=[0,0,0]

    while(True):
     t_estimate_Attitude0=time.time()
     #m6a, m6g = IMU.getMotion6()
     m6a=mpu92_forTest.get_accel()
     m6g=mpu92_forTest.get_gyro()

     m6a[0],m6a[1]=-m6a[1],-m6a[0]
     m6g[0],m6g[1]=m6g[1],m6g[0]

     m6a=np.array(m6a)
     m6g=np.array(m6g)-m6g0
     m6g[2]=-m6g[2]
     for i in range(len(m6g)):
         if abs(m6g[i])<0.005:
             m6g[i]=0

     Tri=fcn.get_Trigonometrxic(x)
     J=fcn.Jacobian_forprocessvariance2(Tri)
     Jt=J.transpose()
     x,P=fcn.Kalman_filer2(x,fcn.get_angle_acc(m6a),m6g,c,b,q,r,P,Ts,Tri)
     Yaw=Yaw+(Tri[1,1]*(m6g[1]+m6g_before[1])+Tri[1,0]*(m6g[2]+m6g_before[2]))*Ts/(2*Tri[0,0])

     m6g_before=m6g

     phi=np.array([Yaw,x[0]-x0[0],x[1]-x0[1]])*360/2.85


     print(phi)
     print(t_estimate_Attitude0-time.time())
     if Ts-time.time()+t_estimate_Attitude0<0.002:
         continue
     else:
         time.sleep(Ts-time.time()+t_estimate_Attitude0)
     #print(t_estimate_Attitude0-time.time())
     #print(count)
