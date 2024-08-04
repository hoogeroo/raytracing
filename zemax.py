# -*- coding: utf-8 -*-
"""
Created on Mon Nov  7 10:58:26 2016
raytracelib.py
@author: mdh
"""

import numpy as np
import io
from scipy.optimize import fsolve
import matplotlib.pyplot as plt

#surfaces=[]
lenses=[]
rays=[]

def peek_line(f):
    pos = f.tell()
    line = f.readline()
    f.seek(pos)
    return line

class surface:
    def __init__(self, ROC,ZPOS,RAD, mc, k=0.0, Ain=np.zeros(10)):
        self.R = ROC
        self.k = k
        self.Z = ZPOS
        self.radius=RAD
        self.mc = mc
        self.n=mc[0]
        self.A = Ain

    def z(self,y):
        #print(self.R, self.k, self.Z, self.A)
        if (self.R==0.0):
            return y*0.0+self.Z;
        else:
            out=y**2/self.R/(1+np.sqrt(1.0-(1.0+self.k)*y**2/self.R**2));
            #A[0]=0; A[1]=0; A[2]=0; A[3]=0.0
            B=self.A[::-1];
            #B=[B 0];
            out=out+np.polyval(B,y)+self.Z
            return out
    def nr(self,wl):
        wl=wl/1000.0
        c=self.mc
        nsq=1+c[0]*wl**2/(wl**2-c[1])+c[2]*wl**2/(wl**2-c[3])+c[4]*wl**2/(wl**2-c[5])
        n=np.sqrt(nsq)
        #print("Hello ", n)
        return n

class point:  # The only reason for this is to define rays as a collection of points
    def __init__(self,xi,yi,zi):
        self.x=xi
        self.y=yi
        self.z=zi

class ray:
    def __init__(self,y0,a0): # A ray is just a list of points
        self.points=[]
        self.points.append(point(0.0,y0,0.0))
        self.a=a0
        self.b=y0

class agfile:
    def __init__(self,filename):
        self.catalog={} # making a dictionary
        self.name=filename
        f=open(filename)
        #print("Loading file", filename)
        t1=np.zeros(8) # refractive index coefficients
        while True:
            line=f.readline()
            if line=='':
                break
            #print(line)
            if line[0:2]=='NM': # This is the line with the material name
                parts=line.split(' ')
                matname=parts[1]
                #print(matname," added")
                foundcd=False
                while not foundcd: # Then we look for the coefficients, starting with CD
                    line=f.readline()
                    if line[0:2]=='CD':
                        #print(line)
                        foundcd=True
                        parts=line.split(' ')
                        #parts=parts[1:]
                        for i in range(1,9): #,part in enumerate(parts):
                            t1[i-1]=float(parts[i])
                self.catalog[matname]=np.copy(t1)
                #print(matname)
        f.close()

    def getindex(self,name,wl):
        wl=wl/1000.0
        c=self.catalog[name]
        nsq=1+c[0]*wl**2/(wl**2-c[1])+c[2]*wl**2/(wl**2-c[3])+c[4]*wl**2/(wl**2-c[5])
        n=np.sqrt(nsq)
        return n

class zemaxlens:
    def __init__(self,Z,filename,way):
        self.Z=Z
        catalogs=[]
        self.surfaces=[]
        CONI=0.0
        AC=np.zeros(16)
        f = io.open(filename, encoding='utf-16')
        try:
            f.readline()
            if f.readline()=='':
                f.close()
                f = open(filename,'r', encoding='latin-1')
                #print("latin-1 encoding")
            #else:
                #f = io.open(filename, encoding='utf-16')
                #print("utf-16 encoding")
        except:
            f.close()
            f = open(filename,'r', encoding='latin-1')
            #print("latin-1 encoding")
        endfile=False
        self.D1=0.0
        while not endfile:
            line=f.readline()
            if line=='':
                endfile=True
            if line[0:4]=='GCAT':
                parts=line.split()
                #print(line)
                for part in parts[1:]:
                    #print(part)
                    agfname=part+'.agf'
                    thiscat=agfile(agfname)
                    catalogs.append(thiscat)
            #print(line)
            if line[0:4]=="SURF":
                #print(line)
                parts=line.split()
                endsurf=False
                matcoef=np.zeros(8)
                DIAM=0
                while not endsurf:
                    pos=f.tell()
                    line=f.readline()
                    if line[0:4]=='SURF':
                        endsurf=True
                        f.seek(pos)
                        #print(line)
                    if line[2:6]=="CURV":
                        parts=line.split()
                        t1=float(parts[1])
                        if (t1!=0.0):
                            ROC=1.0/t1
                        else:
                            ROC=1e9
                        #print(ROC)
                    if line[2:6]=='PARM':
                        parts=line.split()
                        ind=(int(parts[1])-1)*2
                        AC[ind]=float(parts[2])
                    if line[2:6]=="GLAS":
                        parts=line.split()
                        mat=parts[1]
                        #print(mat)
                        for cat in catalogs:
                            try:
                                matcoef=cat.catalog[mat]
                                #print("material", mat, "found in catalog", cat.name)
                                break
                            except:
                                matcoef=np.zeros(8)
                                #print("material", mat, "not found in catalog", cat.name)
                        #print(mat,matcoef)
                    if line[2:6]=='CONI':
                        parts=line.split()
                        CONI=float(parts[1])
                    if line[2:6]=="DISZ":
                        parts=line.split()
                        if parts[1]=='INFINITY':
                            dist=0.0
                        else:
                            dist=float(parts[1])
                    if line[2:6]=='DIAM':
                        parts=line.split()
                        DIAM=float(parts[1])
                    if line[0:2]!='  ':
                        endsurf=True
                #endfile=True
                thissurface=surface(ROC,self.Z+self.D1,DIAM,matcoef, k=CONI, Ain=AC)
                #print(self.D1,dist)
                self.D1=self.D1+dist
                self.surfaces.append(thissurface)
        del self.surfaces[0]
        del self.surfaces[-1]

        if way==False:   #flip lens around
            #reorder surfaces
            tempSurfaces=self.surfaces[:]
            n=len(self.surfaces)
            #print("number of surfaces: ", n)
            stopZ=tempSurfaces[n-1].Z
            for i in range(0, n):
                self.surfaces[i]=tempSurfaces[n-i-1]
                self.surfaces[i].R=-self.surfaces[i].R
                self.surfaces[i].A=-self.surfaces[i].A
                self.surfaces[i].Z=self.Z+(stopZ-self.surfaces[i].Z)

                if i != n-1:
                    self.surfaces[i].mc=tempSurfaces[n-i-2].mc
                    self.surfaces[i].n=tempSurfaces[n-i-2].n
                else:
                    self.surfaces[i].mc=tempSurfaces[i].mc
                    self.surfaces[i].n=tempSurfaces[i].n

                #print("surface", i)
                #print("ROC:", self.surfaces[i].R)
        print("loaded zemax lens")
        f.close()

    def drawit(self):
        for s in self.surfaces:
            y=np.arange(-s.radius,s.radius*1.01,s.radius/100.0)
            #print(y)
            #print(s.radius,s.R,s.Z)
            z=s.z(y)
            #print(z)
            plt.plot(z,y,'b')




class pcxsinglet:
    def __init__(self,Z,R,d,n,rad,way):
        self.surfaces=[]
        if way:
            self.surfaces.append(surface(1e9,Z,n))
            self.surfaces.append(surface(-R,Z+d,1.0))
        else:
            self.surfaces.append(surface(R,Z,n))
            self.surfaces.append(surface(1e9,Z+d,1.0))
        self.radius=rad

    def drawit(self):
        y=np.arange(-self.radius,self.radius,self.radius/100.0)
        for s in self.surfaces:
            z=s.z(y)
            plt.plot(z,y,'b')

class achromat:
    def __init__(self,Z,R1,d1,n1,R2,d2,n2,R3,dia,way):
        self.surfaces=[]
        if way:
            self.Z=Z


class calculation:
    def __init__(self,NA,nr,ns,ss):
        #self.rays=[]
        #self.surfaces=[]
        #self.lenses=[]
        for i in range(ns):
            y0=-(ns//2)*ss+i*ss
            for j in range(nr):
                a0=-NA+2*NA*j/nr
                rays.append(ray(y0,a0))
    def refract(self,r,s,n):
        dy=1e-3
        y=r.points[-1].y
        z=r.points[-1].z
        n2=s.n
        n1=n
        dz=(s.z(y+dy)-s.z(y-dy))/2
        myvec=np.array([0.0,dy,dz])
        myvec=myvec/np.linalg.norm(myvec)
        normvec=np.cross(np.array([1.0,0.0,0.0]),myvec)
        normvec=normvec/np.linalg.norm(normvec)
        #print(normvec)
#        if dzdy!=0.0:
#            dydz=1.0/dzdy
#        else:
#            dydz=1e9
        avec=np.array([0.0,r.a,1.0])
        avec=avec/np.linalg.norm(avec)
        costheta=np.dot(normvec,avec)
        plt.plot([z-normvec[2],z+normvec[2]],[y-normvec[1],y+normvec[1]])
        plt.plot([z-myvec[2],z+myvec[2]],[y-myvec[1],y+myvec[1]])
        sintheta=np.sign(dz)*np.sqrt(1.0-costheta**2)
        sintheta2=sintheta*n1/n2
        #if (n2<n1):
        #    sintheta2=-sintheta2
        a=np.tan(np.sign(dz)*np.pi/2+np.arcsin(sintheta2)+np.arctan(dy/dz))#+dy/dz#+np.arctan(dy/dz))
        b=y-a*z
        return(a,b)

    def propagate(self):
        for r in rays:
            nold=1.0
            for l in lenses:
                for s in l.surfaces:
                    a=r.a
                    b=r.b
                    ey = fsolve(lambda y: a*s.z(y)+b-y , b)
                    ez = s.z(ey)
                    plt.plot(ez,ey,'o')
                    r.points.append(point(0.0,ey,ez))
                    #print((r.points))
                    ta,tb=self.refract(r,s,nold)
                    nold=s.n
                    r.a=ta
                    r.b=tb
    def endit(self,myz):
        for r in rays:
            ey=r.a*myz+r.b
            r.points.append(point(0.0,ey,myz))
            x=[]
            y=[]
            for p in r.points:
                x.append(p.z)
                y.append(p.y)
            plt.plot(x,y)

if __name__=="__main__":
    a=zemaxlens(100,'zemaxfiles/LA1134-B-Zemax(ZMX).zmx',True)
    #mycalc=calculation(0.1,11,1,0.1)
    #lenses.append(pcxsinglet(50,25,4.0,1.5,12.7,1))
    #for lens in lenses:
    #    lens.drawit()
    #mycalc.propagate()
    #mycalc.endit(200)
    plt.show()
