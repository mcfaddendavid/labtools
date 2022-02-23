# Some useful utilities for OpenSCAD design with SolidPython

from solid import *
from solid.utils import *
import numpy as np
import subprocess
import warnings

def centerize(func):
    """Returns cube and square functions which accept lists as "center" parameters. 
    This can be used to center and object in x and y, but not in z, for example.

    :param func: [description]
    :type func: [type]
    """    
    def wrapper(size, center):
        if isinstance(center,list):
            return translate(-np.array(size)*np.array(center)/2)(func(np.array(size), 
                                                                    center=False))
        elif isinstance(center, bool):
            return func(size, center=center)
    return wrapper

my_cube = centerize(cube)
my_square = centerize(square)
    

def pointed_sphere(rad=0.5, dist_fac=1.2):
    """Rounding sphere with sharp bottom, good for filleting parts
       with a steep bottom for better printing.

    :param rad: Rounding radius, defaults to 0.5
    :type rad: float, optional
    :param dist_fac: Higher means a steeper bottom, defaults to 1.2
    :return: [description]
    :rtype: [type]
    """   
    FUDGE = 1e-3
    dist = rad*dist_fac
    p_sphere = up(dist)(hull()(
        [sphere(r=rad, segments=20), down(dist)(cylinder(FUDGE, h=FUDGE, center=True))]))
    p_sphere.total_height = rad+dist
    p_sphere.rad = rad
    return p_sphere
    
def bevelling_cone(rad=0.5, dist_fac=1.2):
    FUDGE = 1e-4
    dist = rad*dist_fac
    cone = hull()(up(dist)(cylinder(r=rad, h=FUDGE))+cube(FUDGE, center=True))
    cone.rad = rad
    cone.total_height = dist
    return cone


def nut_diam(wrench_size):
    """Calculate the necessary outer circumference of a hexagon
       Usefuls for constructing a nut from a given wrench size
    """
    return wrench_size*2/np.sqrt(3)
    


def sector_2D(rad, angle):
    """
    Create a circular sector.
    :param rad: [description]
    :type rad: [type]
    :param angle: [description]
    :type angle: [type]
    :return: [description]
    :rtype: [type]
    """
    # two squares to define angle
    s1 =rotate(-angle/2)(my_square([2*rad, rad], center=[1,0]))
    s2 =rotate(angle/2)(mirror([0,1])(my_square([2*rad, rad], center=[1,0])))
    if angle < 180:
        angle_cutter = s1*s2
    else:
        angle_cutter = s1+s2
    circle_cutter = circle(r=rad)
    sector = angle_cutter*circle_cutter
    return sector

def arc_2D(rad, angle, width):
    """Create a circular arc
    """    
    return sector_2D(rad+width/2, angle) - circle(r=rad-width/2)

def my_screw(m_size=None, shaft_diam = 4.7, head_diam = 8.1, shaft_length = 100, head_length = 100):
    # https://de.wikipedia.org/wiki/Durchgangsbohrung
    sizes = {
        "M4": [4.7, 8.1],
        "M6": [6.8, 11],
    }
    if m_size != None:
        sz = sizes[m_size]
        shaft_diam = sz[0]
        head_diam = sz[1]
    fudge = 1e-4
    screw = (up(fudge)(mirror([0,0,1])(cylinder(d=shaft_diam, h=shaft_length)))
             + cylinder(d=head_diam, h=head_length))
    return screw
    
def my_cyl_templ(diam_hole, diam_head):
    FUDGE = 1e-4
    length_placeholder = 10*diam_head
    return (down(length_placeholder-FUDGE)(cylinder(d = diam_hole, h=length_placeholder)) +
            cylinder(d = diam_head, h=length_placeholder/3))
        
    
def my_m4base(flat_side=True):
    # M4_base 
    BASE_HEIGHT = 4
    LAT_SPACE = 2
    FUDGE = 1e-3
    BASE_STRENGTH = 2
    HOLE_DIAM = 4.7
    HEAD_DIAM = 12

    base_width = HEAD_DIAM+2*LAT_SPACE

    M4_base = cylinder(d=base_width, h=BASE_HEIGHT)
    if flat_side:
        M4_base = (hull()([M4_base,
                   translate([base_width/2,0,BASE_HEIGHT/2])(cube([FUDGE,base_width, BASE_HEIGHT], center=True)),])
        )
    M4_base += hole()(up(BASE_STRENGTH)(my_cyl_templ(HOLE_DIAM, HEAD_DIAM)))
    if flat_side:
        M4_base = left(base_width/2)(M4_base)
    M4_base.width = base_width   
    M4_base.height = BASE_HEIGHT
    return M4_base

def my_regpoly(r=1,d=None,n=3,y0=True):
    if d != None:
        r_circum = d/2
    else:
        r_circum = r
    poly = circle(r=r_circum, segments=n)
    apothem = np.cos(np.pi/n)*r_circum
    if y0:
        poly = right(apothem)(poly)
    poly.height = apothem+r_circum
    return poly

def slot_rod(rod_diam, rod_length, with_hat=True):
    FUDGE = 1e-3
    rod_negative = cylinder(d=rod_diam, h=10*rod_length)
    if with_hat:
        hat_dist = rod_diam*0.9
        rod_negative = hull()(rod_negative + forward(hat_dist)(my_cube([FUDGE,FUDGE,10*rod_length], center=[1,1,0])))

    rod_negative = down(rod_length/2)(rod_negative)
    slot_side_length = rod_diam*np.sqrt(2)/2*1.1
    slot = down(10*rod_length+rod_length/2)(cube([slot_side_length, slot_side_length, 20*rod_length], center=True))    
    slot_n_rod = rotate([90,0,0])(rod_negative+slot)
    return slot_n_rod

def nut_bracket(CAM_WRENCH_SIZE, CAM_SCREW_DIAM, BASE_THICKNESS, COUNTERHOLE_STRENGTH,
                 base_width=None, flat_side=False, flat_side_dist=0):
    "Generate a hollow half cylinder to insert a nut. This gives a part a thread."
    if base_width is None:
        base_width = CAM_WRENCH_SIZE*2
    nut_screw_hole = (up(COUNTERHOLE_STRENGTH)(cylinder(d=nut_diam(CAM_WRENCH_SIZE), h=4, segments=6))
                    + cylinder(d=CAM_SCREW_DIAM, h=CAM_WRENCH_SIZE*10, center=True))
    bracket = cylinder(d=base_width, h=BASE_THICKNESS) 
    if flat_side:
        bracket = hull()(bracket+my_cube([base_width/2+flat_side_dist,base_width,BASE_THICKNESS], center=[0,1,0]))
    bracket -= nut_screw_hole
    bracket.base_width = base_width
    return bracket


OPENSCAD_EXEC = "openscad"
try:
    subprocess.run([OPENSCAD_EXEC, "--version"])
except FileNotFoundError:
    OPENSCAD_EXEC = "openscad-nightly"
    try:
        subprocess.run([OPENSCAD_EXEC, "--version"])
    except FileNotFoundError:
        import platform
        if "Windows" in platform.platform():
            OPENSCAD_EXEC = r"C:\Program Files\OpenSCAD\openscad.exe"
            try:
                subprocess.run([OPENSCAD_EXEC, "--version"])
            except FileNotFoundError:
                warnings.warn("Could not find OpenSCAD executable. Preview and STL renderings will fail.")

try:
    import viewscad
    r = viewscad.Renderer(openscad_exec=OPENSCAD_EXEC)
except:
    print("ViewSCAD could not be imported. Previews will fail.")
    
def my_render(shape):
    try:
        r.render(shape)
    except Exception as ee:
        print("Failed to render object, attempting to render as 2D shape.")
        r.render(linear_extrude(0.01)(shape))
