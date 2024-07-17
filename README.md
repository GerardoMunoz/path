# Paths Visualization Application
This Tkinter application visualizes path connections. The application allows you to load data from CSV files, visualize it on a canvas, manipulate it, and save it back to CSV or export it as SVG/HTML.

## Requirements
* Python 3.x
* Tkinter
* CSV files with curriculum data and prerequisites

## Instructions
### Files Needed
#### `curriculum.csv`: 
This file contains the curriculum data, including subject positions and additional information. The file should be a CSV with columns like Código, Nombre, Área, Semestre, Créditos, Horas, Posición

Example:
* Código,Nombre,Área,Semestre,Créditos,Horas,Posición
* MAT101,Cálculo I,Matemáticas,1,5,80,1
* FIS101,Física I,Física,1,4,60,2

#### `prerequisitos.csv`: 

This file contains the prerequisite connections between subjects. The file should be a CSV with columns Código, Código_Prerrequisito, and Camino.

Example:
* Código,Código_Prerrequisito,Camino
* MAT101,FIS101,"[(100,100), (200,200), (300,300)]"


### Usage
Place your curriculum.csv and prerequisitos.csv files in the same directory as your Python script.

Run the Python script to launch the Tkinter application:

Use the application to visualize, manipulate, and save the curriculum data.

Features
* Zooming: Use the mouse wheel with Alt for vertical scrolling, Shift+Alt for horizontal scrolling, and Ctrl+Alt for zooming.
* Dragging: Drag rectangles representing subjects on the canvas.
* Saving: Save the updated positions and prerequisite paths back to a CSV file.
* Exporting: Export the canvas to SVG or HTML format.


For now, only changes in the paths can be saved.
* If you want to delete a path, you can do it in the prerequisites.csv file, writing a 0 in the `Camino` column.
* The deleted paths appear as white lines when you press the Reload button.
* These paths can be created if AutoPath is enabled when pressing Reload.
* Using the small squares, you can reposition the path.
* To save the changes, you need to press the Save button.
