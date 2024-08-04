# raytracing
The raytracing program

<H2>Purpose</H2>
<p>Thej raytracing program aims to do simple raytracing. The program can read the Thorlabs ZEMAX files. It uses publicly available material libraries, which are included with the source. Custom lenses can be inserted as well.</p>

<h2>Installation</h2>
The program runs on PyQt5. The extras you need is pyqtgraph and numpy.

<H2>Usage</H2>

<p>python raytrace_main.py</p>

<p> We start with a (light) source, which is a point radiating a number of rays with a certain wavelength. Any number of sources can be added. </p>

<p>Custom lenses can be added in sequence. There is not a lot of error checking going on in terms of ordering the lenses along the optical axis. So until that is sorted, do your own ordering of surfaces.</p>

<p>Thorlabs ZEMAX files describing further lenses can be added.</p>

<p>Once you have designed your optical system, press "Write" and "Run"</p>

<p>There is an "Optimise" button that can help you optimise positions of the lenses to obtain either a collimated beam or a focus. The optimisation settings can be accessed through "Settings"</p>
