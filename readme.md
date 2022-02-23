# Labtools
A selection of various 3D printed tools for optics labs designed using [SolidPython](https://github.com/SolidCode/SolidPython) in jupyter notebooks.

STL and openscad files are provided, but if you want to tweek anything I would recommend you set up a jupyter environment, install [SolidPython](https://github.com/SolidCode/SolidPython) and ([ViewSCAD](https://github.com/nickc92/ViewSCAD)):

```
pip install solidpython
pip install viewscad
```

# Usage

Start jupyter notebooks

```
jupyter notebook
```

Use the browser interface to navigate to the design folder and open the .ipynb file. Execute the cells one by one and view the results.

Shared utilities are saved in the "mycad" module from the "mycad" directory. The Notebooks expect to find the this module exactly two directories above the notebook, so it is important to preserve the directory structure as-is. 

Design parameters use ALL_CAPS names. Parameters which are derived from other parameters, but introduce their own constant parameters, are also written ALL_CAPS. ViewSCAD can provide us with nice previews, but sometimes this is deactivated on complex models if performance is an issue. 

Once the model is finished, it is first rendered to an OpenSCAD file, and the openscad process is then called to render an STL file. This process is repeated if there are multiple models to export.

Intermediate ViewSCAD renderings are done in default quality, which will have rendering artefacts but should be adequate for visualization. The final rendering is performed in a high quality with an OpenSCAD $fn parameter of 128.

Some models may require support for printing.

# OpenSCAD command
The script attempts to call the OpenSCAD executable on the system. If it fails, you may need to manually specify the command or add the location of the executable to the system PATH.

