import numpy as np
from scipy.optimize import fsolve
import matplotlib.pyplot as plt
import time
#import shared
#from matplotlib.lines import plt.plot

class segment:
    def __init__(self, startz, starty, stopz, stopy):
        self.start=np.array([startz, starty])
        self.stop=np.array([stopz, stopy])

class ray:
    def __init__(self):
        self.segments=np.array([])

    def addSegment(self, segment):
        self.segments=np.append(self.segments, segment)

class source:
    def __init__(self):
        self.rays=np.array([])
        self.intersections=np.array([])
        self.wavelength=532

    def addRay(self, ray):
        self.rays=np.append(self.rays, ray)

    def getVariance(self, index):
        print("GETTING VARIANCE")
        self.intersections=np.array([])
        ex=-1
        for i in range(0, len(self.rays)):
            for j in range(i+1, len(self.rays)):
                #i is first ray, j is second
                #index refers to relevant segment
                if index < len(self.rays[i].segments) and index < len(self.rays[j].segments):
                    #get equation of first line
                    #print self.rays[i].segments[index].start
                    #print self.rays[i].segments[index].stop
                    #print self.rays[j].segments[index].start
                    #print self.rays[j].segments[index].stop
                    z1=self.rays[i].segments[index].start[0]
                    z2=self.rays[i].segments[index].stop[0]
                    y1=self.rays[i].segments[index].start[1]
                    y2=self.rays[i].segments[index].stop[1]
                    m1=(y1-y2)/(z1-z2)
                    c1=y1-m1*z1
                    #print "y=",m1,"x+",c1
                    #and equation is y=m1*z+c1

                    #get equation of second line
                    z3=self.rays[j].segments[index].start[0]
                    z4=self.rays[j].segments[index].stop[0]
                    y3=self.rays[j].segments[index].start[1]
                    y4=self.rays[j].segments[index].stop[1]
                    m2=(y3-y4)/(z3-z4)
                    c2=y3-m2*z3
                    #print "y=",m2,"x+",c2
                    #and equation is y=m2*z+c2

                    #intersection
                    z=-(c2-c1)/(m2-m1)
                    y=m1*z + c1

                    #print z, y
                    #print m2*z + c2


                    if len(self.intersections)==0:
                        self.intersections=np.array([float(z),float(y)])
                        ex=1
                    else:
                        self.intersections=np.vstack((self.intersections,np.array([float(z),float(y)])))
                        ex=0


        #find mean of intersections
        mz=0
        my=0

        #print(self.intersections)

        if ex==1:
            print("only one intersection")
            return 0

        for i in range(0, len(self.intersections)):
            mz=mz+self.intersections[i][0]
            my=my+self.intersections[i][1]

        if len(self.intersections) > 0:
            mz=mz/len(self.intersections)
            my=my/len(self.intersections)


            #print mz, my

            #caclualate variance
            var=0
            for i in range(0, len(self.intersections)):
                var=var+(mz-self.intersections[i][0])**2 + (my-self.intersections[i][1])**2

            var=var/len(self.intersections)
            print(var)
            return var
        else:
            print("no intersections")
            return 1e9

    def getCollimate(self, index):
        print("GETTING VARIANCE OF SLOPES")
        self.slopes=np.array([])
        ex=-1
        for i in range(0, len(self.rays)):
            if index < len(self.rays[i].segments):
                slope=(self.rays[i].segments[index].start[1]-self.rays[i].segments[index].stop[1])/(self.rays[i].segments[index].start[0]-self.rays[i].segments[index].stop[0])
                self.slopes=np.append(self.slopes, slope)

        #get mean of slopes
        mslope=0
        for i in range(0, len(self.slopes)):
            mslope=mslope+self.slopes[i]

        if len(self.slopes)>0:
            mslope=mslope/len(self.slopes)

            #calculate variance
            var=0
            for i in range(0, len(self.slopes)):
                var=var+(mslope-self.slopes[i])**2

            var=var/len(self.slopes)
            return var
        else:
            print("no segments of given index")
            return 1e9


def asphere(y,R,k,A):
    if (R==0.0):
        return 0*y;
    else:
        z=y**2/R/(1+np.sqrt(1.0-(1.0+k)*y**2/R**2));
        A[0]=0; A[1]=0; A[2]=0; A[3]=0.0
        B=A[::-1];
        #B=[B 0];
        z=z+np.polyval(B,y)
        return z

def findline(a,b,sz,sy,f,refrind,ray):
    #This function is the basic element of the raytracing program since any
    #lens consists of two refracting surfaces. Finding the intersection and
    #refraction of a single ray is repeated 2N times for N lines in one lens.
    #line intersection: solving equation a*z+b = y where z =
    #f(y) and plotting the newfound line from (sz,sy) to the intersection point
    #then calculate the refracted ray
    pi=np.pi
    #print("initial",a,b,sz,sy)

    if sz==shared.endPoint:
        return a, b, sz, sy

    try:
        ey = fsolve(lambda y: a*f(y)+b-y , 0.0)
    except RuntimeWarning:
        try:
            ey = fsolve(lambda y: a*f(y)+b-y , -50)
        except:
            ey=np.nan
    ey=float(ey)
    ez = f(ey);
    #print("ez,ey",ez,ey)
    plt.plot(ez,ey,'o')
#    na = (ey-sy)/(ez-sz) # new version of a, should be the same as a
#    nb = ey-na*ez; # new version of b, should be the same as b
    #print(sz,ez,sy,ey)
    plt.plot([sz,ez],[sy,ey]);
    shared.startzarray=np.append(shared.startzarray, sz)
    shared.stopzarray=np.append(shared.stopzarray, ez)
    shared.startyarray=np.append(shared.startyarray, sy)
    shared.stopyarray=np.append(shared.stopyarray, ey)
    ray.addSegment(segment(sz,sy,ez,ey))
    #plt.show()
    #find the gradient using the midpoint rule
    ty=np.arange(-10.0,10.0)
    tz=f(ty)
    #print(ty)
    #print(tz)
    plt.plot(tz,ty,'x')
    dy = 0.01;
    y1 = ey+dy;
    ym1 = ey-dy;
    z1 = f(y1);
    zm1 = f(ym1);
    if (z1!=zm1):
        dydz = (2*dy)/(z1-zm1)
    else:
        dydz=1e9
    #find the angle and use Snell's law
    sangle = np.arctan(dydz); #angle of surface measured to horizontal
    #print("angle in degrees",sangle/pi*180.0)
    normf =  np.sign(dydz); #select the proper normal
    #print("sangle,normf",sangle,normf)
    aoi = normf*np.pi/2+sangle - np.arctan(a) + np.pi; #angle of incidence measured to normal
    t1=1/refrind*np.sin(aoi)
    try:
        aor = np.arcsin(t1) #angle of refraction measured to normal
    except:
        aor = np.nan

    #print("angles",aoi/pi*180,t1,aor*180/pi)
    ea = np.tan(normf*np.pi/2+sangle - aor); #new tangent of first refracted line
    eb = ey-ea*ez; # new offset of first refracted line
    #print("final",ea,eb,ez,ey)
    return ea,eb,ez,ey

def addachromat(a,b,sz,sy,Z,f1,f2,f3,R,refrind1,refrind2,source):
#f1 is the first surface curvature function, f2 is the second, f3 is the
#third.
#R is the radius of the lens
#refrind1 and refrind2 are the refractive index
#Z is the position
#draw the lenses
    my = np.arange(-R,R,0.1)
    enda=a
    endb=b
    endz=sz
    endy=sy
    plt.plot(Z+f1(my),my,'black',Z+f2(my),my,'black',Z+f3(my),my,'black')
    myf1= lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: f1(y) + Z, shared.endPoint])
    myf2= lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: f2(y) + Z, shared.endPoint])
    myf3= lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: f3(y) + Z, shared.endPoint])
    #draw the lines
    for i in range(a.shape[0]):
    #findline find the intersection point with a surface and returns the
    #refracted line parameters
        ea,eb,ez,ey = findline(a[i],b[i],sz[i],sy[i],myf1,refrind1,source.rays[i]);
        ea,eb,ez,ey = findline(ea,eb,ez,ey,myf2,refrind2/refrind1, source.rays[i]);
        enda[i],endb[i],endz[i],endy[i] = findline(ea,eb,ez,ey,myf3,1/refrind2, source.rays[i]);
    return enda,endb,endz,endy

def plotachromat(Z,f1,f2,f3,R):
    my = np.arange(-R,R+0.1,0.1)
    myf1= lambda y: f1(y) + Z
    myf2= lambda y: f2(y) + Z
    myf3= lambda y: f3(y) + Z
    return my, myf1(my), myf2(my), myf3(my)


def addlens(a,b,sz,sy,Z,f1,f2,R,refrind,C,source):
    #This function finds the intersections with the first surface by using the
    #array inputs a and b. Lines will be drawn using sz, sy and the found
    #intersection points. The outgoing lines will be calculated and returned using enda
    #endb, endz and endy.
    #f1 is the first surface curvature function, f2 is the second
    #R is the radius of the lens %C is the center of the lens
    #refrind in the refractive index
    #draw the lenses
    D=2.0*R
    myf1= lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: f1(y) + Z, shared.endPoint])
    myf2= lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: f2(y) + Z, shared.endPoint])
    my = np.arange(C-D/2,C+D/2,0.1);
    mz1=myf1(my);
    mz2=myf2(my);
    plt.plot(mz1,my,'black',mz2,my,'black');
    #plt.show()
    enda=np.zeros(a.shape[0])
    endb=np.zeros(a.shape[0])
    endz=np.zeros(a.shape[0])
    endy=np.zeros(a.shape[0])
    #draw the lines

    for i in range(a.shape[0]):
        #findline find the intersection point with a surface and returns the
        #refracted line parameters
        ea,eb,ez,ey = findline(a[i],b[i],sz[i],sy[i], myf1,refrind, source.rays[i]);
        #print( "counter=",shared.mycount)
        #time.sleep(0.2)
        shared.mycount=shared.mycount+1
        enda[i],endb[i],endz[i],endy[i] = findline(ea,eb,ez,ey,myf2,1.0/refrind, source.rays[i]);
    return enda,endb,endz,endy

def plotlens(Z,f1,f2,R,C):
    D=2.0*R
    myf1 = lambda y: f1(y)+Z
    myf2 = lambda y: f2(y)+Z
    my = np.arange(C-R,C+R+0.1,0.1);
    mz1=myf1(my);
    mz2=myf2(my);
    return my,mz1,mz2

def addzemax(a,b,sz,sy,lens, source):
    #where lens is a zemaxlens object as defined in zemax.py
    wavelength=source.wavelength
    enda=a
    endb=b
    endz=sz
    endy=sy
    for r in range(a.shape[0]):
        ea, eb, ez, ey = a[r],b[r],sz[r],sy[r]
        #print("############ new ray ############")
        for i in range(0, len(lens.surfaces)):  #cycle through surfaces of zemaxlens
            R=lens.surfaces[i].radius
            #print("------- new surface --------")
            #print("i = ", i)
            #print("radius = ", R)
            #print("ROC = ", lens.surfaces[i].R)
            myf=lambda y: np.piecewise(y, [(y<=R) & (y>=-R)],[lambda y: lens.surfaces[i].z(y), shared.endPoint])

            if i==0:
                refrind1=1.0  #assumes lens is in vacuum/air
                refrind2=lens.surfaces[i].nr(wavelength)
            elif i==len(lens.surfaces)-1:
                refrind1=lens.surfaces[i-1].nr(wavelength)
                refrind2=1.0
            else:
                refrind1=lens.surfaces[i-1].nr(wavelength)
                refrind2=lens.surfaces[i].nr(wavelength)

            #print("refractive indices: before, after", refrind1, refrind2)
            ea,eb,ez,ey = findline(ea, eb, ez, ey, myf,refrind2/refrind1, source.rays[r])


        enda[r], endb[r], endz[r], endy[r]= ea, eb, ez, ey

    return enda, endb, endz, endy






def addaperture(a,b,sz,sy,Z,R,C):
    #adds an aperture to the setup with radius R, center C at position Z
    plt.plot([Z,Z],[C-R/2,C-R/2-25],'b');
    plt.plot([Z,Z],[C+R/2,C+R/2+25],'b');
    j = 0;
    enda=np.zeros(a.shape[0])
    endb=np.zeros(a.shape[0])
    endz=np.zeros(a.shape[0])
    endy=np.zeros(a.shape[0])
    for i in range(a.shape[0]):
        #find the y-coordinate at the aperture position and don't refract
        t1,t2,t3,ty = findline(a[i],b[i],sz[i],sy[i], lambda y: Z,1.0);
        if ((C-R/2<=ty) & (ty<= C+R/2)): #select only lines that are within the aperture
            enda[j] = a[i];
            endb[j] = b[i];
            endz[j] = Z;
            endy[j] = ty;
            j = j+1;
    return enda,endb,endz,endy

def startraytrace(sz,sy,N,NA, source):
    #initiates a point source with numerical aperture NA, N rays will be
    #emitted from point (sz,sy).
    for i in range(0, int(N)):
        newRay=ray()
        source.addRay(newRay)

    #print(source.rays)
    enda = np.linspace(-NA,NA,int(N));
    endb = sy-enda*sz;
    endz = sz*np.ones(enda.shape[0]);
    endy = sy*np.ones(enda.shape[0]);
    return enda,endb,endz,endy

def stopraytrace(a,b,sz,sy,ez, source):
    #ends ray tracing session by drawing the lines up to the endpoint ez
    #plt.plot([ez,ez],[-255.5*1.6e-3,255.5*1.6e-3],'b')
    histy=np.zeros(a.shape[0])
    for i in range (a.shape[0]):
      t1,t2,t3,histy[i] =  findline(a[i],b[i],sz[i],sy[i],lambda y: ez+0*y,1, source.rays[i]);
    return histy
