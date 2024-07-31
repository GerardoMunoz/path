# Homeworks:
    # Create Circuit Class
    # Add a button to save and retrieve the block positions to use when blocks are moved
    # Update paths when a block is moved
    # Select a path and change its color
    # Add a button to delete the selected path
    # Insert vertices into a path
    # Save in different formats
    # Separate methods to draw paths, read prerequisites.csv, and calculate routes
    # Be able to calculate a selected route, the selected routes or all remaining routes
    # Apply AI to calculate routes

import tkinter as tk
import csv
from queue import Queue
import random
from collections import defaultdict
import json

class ZoomCanvas(tk.Canvas):
    def __init__(self, parent,zoom_entry, **kwargs):
        super().__init__(parent, **kwargs)
        self.scale_factor = 1.0
        self.bind("<MouseWheel>", self.on_mouse_wheel)
        self.bind("<Configure>", self.on_resize)
        self.bind("<ButtonPress-2>", self.start_scroll)  # Middle mouse button
        self.bind("<B2-Motion>", self.scroll)  # Mouse movement with middle button pressed
        self.scan_mark_x = 0
        self.scan_mark_y = 0
        self.rectangles = []  # List to store rectangles and their texts
        self.text_items = []  # List to store text item IDs and their original font sizes
        self.zoom_entry=zoom_entry

    def on_mouse_wheel(self, event):
        if event.state & 0x0008:  # Mod1 (Alt)
            if event.state & 0x0001:  # Shift
                self.xview_scroll(-1 * (event.delta // 120), "units")  # Horizontal scroll
            elif event.state & 0x0004:  # Control
                self.zoom(event)
            else:
                self.yview_scroll(-1 * (event.delta // 120), "units")  # Vertical scroll
        else:
            self.yview_scroll(-1 * (event.delta // 120), "units")  # Default to vertical scroll if no modifier

    def start_scroll(self, event):
        self.scan_mark_x = event.x
        self.scan_mark_y = event.y
        self.scan_mark(event.x, event.y)

    def scroll(self, event):
        self.scan_dragto(event.x, event.y, gain=1)

    def zoom(self, event):
        scale = 1.1 if event.delta > 0 else 0.9
        self.scale_factor *= scale
        self.scale("all", 0, 0, scale, scale)
        self.configure(scrollregion=self.bbox("all"))
        self.zoom_entry.configure(state='normal')  # Temporarily set to normal to allow editing
        self.zoom_entry.delete(0, tk.END)  # Clear the current text
        self.zoom_entry.insert(0, str(self.scale_factor))  # Insert the new value
        self.zoom_entry.configure(state='readonly')  # Set back to readonly
        
        
        # Adjust font size for zoom for all text items
        for text_id, original_font_size in self.text_items:
            new_font_size = int(original_font_size * self.scale_factor)
            new_font = f"TkDefaultFont {new_font_size}"
            self.itemconfig(text_id, font=new_font)

    def on_resize(self, event):
        self.configure(scrollregion=self.bbox("all"))

#     def create_zoomable_rectangle_with_text(self, x1, y1, x2, y2, **kwargs):
#         rect_id = self.create_rectangle(x1, y1, x2, y2, **kwargs)
#         center_x = (x1 + x2) / 2
#         center_y = (y1 + y2) / 2
#         text_id = self.create_zoomable_text(center_x, center_y, text="Hello", font="TkDefaultFont 10")
#         self.rectangles.append((rect_id, text_id))

    def create_zoomable_text(self, x, y, **kwargs):
        text_id = self.create_text(x, y, **kwargs)
        font_info = self.itemcget(text_id, 'font').split()
        original_font_size = int(font_info[1]) if len(font_info) > 1 else 10  # Default to 10 if not specified
        self.text_items.append((text_id, original_font_size))
        return text_id


    # Function to convert canvas shapes to SVG
    def canvas_to_svg(canvas):
        svg_elements = []
        for item in canvas.find_all():
            item_type = canvas.type(item)
            if item_type == "rectangle":
                x1, y1, x2, y2 = canvas.coords(item)
                fill = canvas.itemcget(item, "fill")
                outline = canvas.itemcget(item, "outline")
                svg_elements.append(
                    f'<rect x="{x1}" y="{y1}" width="{x2-x1}" height="{y2-y1}" fill="{fill}" stroke="{outline}" />'
                )
            elif item_type == "line":
                coords = canvas.coords(item)
                fill = canvas.itemcget(item, "fill")
                width = canvas.itemcget(item, "width")
                svg_elements.append(
                    f'<line x1="{coords[0]}" y1="{coords[1]}" x2="{coords[2]}" y2="{coords[3]}" stroke="{fill}" stroke-width="{width}" />'
                )
            elif item_type == "text":
                x, y = canvas.coords(item)
                text_content = canvas.itemcget(item, "text")
                font = canvas.itemcget(item, "font")
                fill = canvas.itemcget(item, "fill")
                font_size = 10#int(font.split()[-1] if isinstance(font, str) else font[1])
                lines = text_content.split('\n')

                # Calculate the total height of the text block
                total_text_height = len(lines) * font_size * 1.2

                # Calculate the starting y position to center the text vertically
                start_y = y - total_text_height / 2 + font_size / 2

                for i, line in enumerate(lines):
                    dy = start_y + i * font_size * 1.2
                    svg_elements.append(
                        f'<text x="{x}" y="{dy}" font-family="{font.split()[0]}" font-size="{font_size}" fill="{fill}" text-anchor="middle">{line}</text>'
                    )

        return svg_elements


    def save_to_svg_file(self, filename):
        svg_elements=self.canvas_to_svg()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()

        svg_content = f"""
            <svg width="{canvas_width}" height="{canvas_height}"  xmlns="http://www.w3.org/2000/svg" style="background-color: {canvas['bg']}">
                {' '.join(svg_elements)}
            </svg>
        """
        
        with open(filename, 'w',encoding='UTF-8') as file:
            file.write(svg_content)

    def save_to_html_file(self, filename):
        canvas=self
        svg_elements=self.canvas_to_svg()
        canvas_width = canvas.winfo_width()
        canvas_height = canvas.winfo_height()
        html_content = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Canvas to SVG</title>
        </head>
        <body>
            <svg width="{canvas_width}" height="{canvas_height}"  xmlns="http://www.w3.org/2000/svg" style="background-color: {canvas['bg']}">
                {' '.join(svg_elements)}
            </svg>
        </body>
        </html>
        """
        
        with open(filename, 'w',encoding='UTF-8') as file:
            file.write(html_content)




########################################################
class Path:
    def __init__(self, canvas, path, color_path='#fff', color_vertex='#000', reduce=True,x_grid=10,y_grid=10,**kwargs):
        self.canvas = canvas
        #self.path = path
        self.color_path = color_path
        self.color_vertex = color_vertex
        self.index_sq = {}
        self.sq_index=[]
        self.index_ln = []
        self.moving_square = None
        self.scan_mark_x = 0
        self.scan_mark_y = 0
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.kwargs=kwargs
        
        if reduce:
            self.path=self.reduce_path(path)
        else:
            self.path=path
        self.draw_path()
            

        for i, vertice in enumerate(self.path):
            sq=self.create_movable_square(*vertice)
            self.sq_index.append(sq)
            self.index_sq[sq] = i
            #print(sq)

        
    def reduce_path(self,path):
        if not path:
            return []

        reduced_path = [path[0]]  # Start with the first point

        for i in range(1, len(path) - 1):
            prev_x, prev_y = path[i - 1]
            curr_x, curr_y = path[i]
            next_x, next_y = path[i + 1]

            # Check if the current point is a turning point
            if (prev_x != curr_x or curr_x != next_x) and (prev_y != curr_y or curr_y != next_y):
                reduced_path.append(path[i])

        reduced_path.append(path[-1])  # End with the last point

        return reduced_path


    

    def draw_path(self):
        for i in range(len(self.path) - 1):
            start_x = self.path[i][0]
            start_y = self.path[i][1]
            end_x = self.path[i + 1][0]
            end_y = self.path[i + 1][1]
            line_id = self.canvas.create_line(self.canvas.scale_factor*start_x, self.canvas.scale_factor*start_y, self.canvas.scale_factor*end_x, self.canvas.scale_factor*end_y, fill=self.color_path, width=2)#, dash=(4, 2))
            self.index_ln.append(line_id)

    def update_lines(self):
        self.path=[]
        for i in range(len(self.index_ln)):
            start_square = self.sq_index[i]
            end_square = self.sq_index[i+1]

            start_coords = self.canvas.coords(start_square)
            end_coords = self.canvas.coords(end_square)

            start_x = (start_coords[0] + start_coords[2]) / 2
            start_y = (start_coords[1] + start_coords[3]) / 2
            end_x = (end_coords[0] + end_coords[2]) / 2
            end_y = (end_coords[1] + end_coords[3]) / 2

            self.canvas.coords(self.index_ln[i], start_x, start_y, end_x, end_y)
            self.path.append([start_x, start_y])
        self.path.append([end_x, end_y])
        #print('update',self.path,self)

    def create_movable_square(self, x, y, size=6, **kwargs):
        half_size = size // 2
        square_id = self.canvas.create_rectangle(self.canvas.scale_factor*(x - half_size), self.canvas.scale_factor*(y - half_size), self.canvas.scale_factor*(x + half_size), self.canvas.scale_factor*(y + half_size), fill=self.color_vertex, **kwargs)
        self.canvas.tag_bind(square_id, "<ButtonPress-1>", self.start_move_square)
        self.canvas.tag_bind(square_id, "<B1-Motion>", self.move_square)
        self.canvas.tag_bind(square_id, "<ButtonRelease-1>", self.release_square)
        return square_id

    def start_move_square(self, event):
        self.scan_mark_x = event.x//self.canvas.scale_factor
        self.scan_mark_y = event.y//self.canvas.scale_factor
        self.moving_square = self.canvas.find_withtag("current")[0]

    def move_square(self, event):
        dx = event.x//self.canvas.scale_factor - self.scan_mark_x
        dy = event.y//self.canvas.scale_factor - self.scan_mark_y
        self.canvas.move(self.moving_square, dx, dy)
        self.scan_mark_x = event.x//self.canvas.scale_factor
        self.scan_mark_y = event.y//self.canvas.scale_factor
        self.update_lines()

    def release_square(self, event):
        # Snap to grid
        x1, y1, x2, y2 = self.canvas.coords(self.moving_square)
        center_x = (x1 + x2) / 2/self.canvas.scale_factor
        center_y = (y1 + y2) / 2/self.canvas.scale_factor
        new_x = round(center_x / self.x_grid) * self.x_grid
        new_y = round(center_y / self.y_grid) * self.y_grid
        self.canvas.coords(self.moving_square, self.canvas.scale_factor*(new_x - 3), self.canvas.scale_factor*(new_y - 3), self.canvas.scale_factor*(new_x + 3), self.canvas.scale_factor*(new_y + 3))
        #print('release',self.path,self.moving_square,self.index_sq[self.moving_square],(new_x,new_y))

        self.update_lines()
        self.moving_square = None
        
        
    def dicti(self,path_name,*args):
        result={path_name:self.path}
        #print('dicti',self.path,self)
        for arg in args:
            result[arg]=self.kwargs[arg]
        return result
  
    def delete(self):
        for sq in self.index_sq:
            self.canvas.delete(sq)

    # Maze Routing Algorithm (Maze Route Algorithm)
    @staticmethod
    def maze_route(grid, start, end,cols,rows):
        start=aprox_xy(start)
        end=aprox_xy(end)
        #print(start,end)
        directions = [(-x_grid, 0), (x_grid, 0), (0, -y_grid), (0, y_grid)]
        queue = Queue()
        queue.put((start, [start]))
        visited = set([start])
        
        while not queue.empty():
            #print(queue)
            (current, path) = queue.get()            
            for direction in directions:
                next_pos = (current[0] + direction[0], current[1] + direction[1])
                if next_pos == end:
                    return  path + [next_pos]
                if 0 <= next_pos[0] < cols and 0 <= next_pos[1] < rows and grid[(next_pos[0],next_pos[1])] == 0 and next_pos not in visited:
                    #print(next_pos,end=' - ')
                    queue.put((next_pos, path + [next_pos]))
                    visited.add(next_pos)
        print('Path not found',start,end)
        return None

######################################################
area_colors = {
        "Economía": "#400",
        "Humanidades": "#500",
        #"Segunda Lengua": "#080",
        "Electivas Extrínsecas": "#440",
        "Matemáticas": "#040",
        "Física": "#342",
        "Programación": "#046",
        "Potencia Y Circuitos": "#024",
        "Electrónica": "#044",
        "Digitales": "#446",
        "DSP": "#000",
        "Automática": "#266",
        "Telecomunicaciones": "#466",
        "Telemática": "#565",
        "Bioingeniería": "#668",
        "Proyectos": "#420",
        "Idiomas": "#640",
        "Electiva": "#440" ,
        "": "#460" ,
    }


rect_width = 220
rect_height = 80
x_margin = 50
y_margin = 50
x_grid = 10
y_grid = 10
top_margin = 80
x_spacing = rect_width + x_margin
y_spacing = rect_height + y_margin
canvas_width = 12 * x_spacing
canvas_height =  12 * y_spacing + top_margin
color_path="#ccc"#Path 122,196,113
color_bg="#000"#PCB 18,92,61
color_pad="#888"
color_block=None
# color_path="#7C7"#Path 122,196,113
# color_bg="#164"#PCB 18,92,61
# color_pad="#ccc"

# Function to read the CSV file and return a list of dictionaries
def read_csv(file_path):
    data = []
    with open(file_path, newline='', encoding='UTF-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            data.append(row)
    return data

# Function to save the updated CSV data to a new file
def save_csv(file_path, data):
    print(data)
    with open(file_path, 'w', newline='', encoding='UTF-8') as csvfile:
        fieldnames = data[0].keys()
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def aprox_xy(xy,x_step=x_grid,y_step=y_grid):
    x=round(xy[0]/x_step)*x_step
    y=round(xy[1]/y_step)*y_step
    return x,y

def in_rect(p,nw,se):
    return nw[0]<=p[0]<=sw[0] and nw[1]<=p[1]<=sw[1] 



# Function to save the prerequisite paths to a new CSV file
def save_prerequisite_paths(file_path, paths_data):
    print(paths_data)
    with open(file_path, 'w', newline='', encoding='UTF-8') as csvfile:
        fieldnames = ['Código', 'Código_Prerrequisito', 'Camino']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for path in paths_data:
            writer.writerow(path.dicti('Camino','Código', 'Código_Prerrequisito'))
paths=[]
def load_prerequisite_paths(prereq_file_path,subject_positions,canvas,autopath_var,grid):
    global paths
    prereq_data = read_csv(prereq_file_path)
    
    for item in canvas.find_all():
        if canvas.type(item) == 'line':
                canvas.delete(item)
    for path in paths:
        path.delete()
    paths=[]
    
    
    # Draw prerequisite connections using the Maze route algorithm
    for prereq in prereq_data:
        code = prereq['Código']
        prereq_code = prereq['Código_Prerrequisito']
        path=prereq['Camino']

        
        path = path.replace("(", "[").replace(")", "]")
        
        # Convertir la cadena JSON a una lista
        path = json.loads(path)
        
        pads_code[code]+=1
        pads_prereq[prereq_code]+=1
        if code in subject_positions and prereq_code in subject_positions:
            start = (subject_positions[code][0] , subject_positions[code][1] + pads_code[code]*y_grid)  #x,y (row, col)
            end = (subject_positions[prereq_code][0] + rect_width, subject_positions[prereq_code][1]+pads_prereq[prereq_code]*y_grid)  #x,y (row, col)
            if  not isinstance(path,list) and autopath_var.get()==True:
                #print(start[0], start[1], end[0], end[1])
                
                path = Path.maze_route(grid, start, end, canvas_width, canvas_height )
                print('maze',path)
            if path:
                paths.append(Path(canvas,path,color_path=color_path,color_vertex=color_pad,Código=code, Código_Prerrequisito=prereq_code))
                #draw_path(path,color)
            else:
                canvas.create_line(start, end, fill='#fff', width=1)
    return paths

# Function to create the Tkinter canvas and draw the rectangles
def draw_rectangles(csv_file_path, prereq_file_path):
    global paths
    data = read_csv(csv_file_path)






    # Function to handle saving data
    def save_data():
        file_name = file_name_entry.get()
        if not file_name.endswith("_paths.csv"):
            file_name += "_paths.csv"
        # Implement saving logic here
        print(f"Saving data to {file_name}...")
        save_prerequisite_paths(file_name, paths)

    # Function to handle reloading data
    def reload_data():
        file_name = file_name_entry.get()
        if not file_name.endswith("_paths.csv"):
            file_name += "_paths.csv"
        # Implement reloading logic here
        print(f"Reloading data from {file_name}...")
        paths = load_prerequisite_paths(file_name, subject_positions, canvas,autopath_var,grid)


    def convert_canvas_to_html():
        #latex_code = extract_shapes_to_latex(canvas)
        file_name = file_name_entry.get() + ".html"
        canvas.save_to_html_file( file_name)

    def convert_canvas_to_svg():
        #latex_code = extract_shapes_to_latex(canvas)
        file_name = file_name_entry.get() + ".svg"
        canvas.save_to_svg_file( file_name)

    def black_theme():
        global color_path,color_bg,color_pad
        color_path="#ccc"#Path 122,196,113
        color_bg="#000"#PCB 18,92,61
        color_pad="#888"
        color_block=None
        canvas.configure(bg=color_bg)
        
    def green_theme():
        global color_path,color_bg,color_pad
        color_path="#7C7"#Path 122,196,113
        color_bg="#164"#PCB 18,92,61
        color_pad="#ccc"
        color_block="#444"
        canvas.configure(bg=color_bg)

    # Initialize the main window
    root = tk.Tk()
    root.title("Curriculum")

    # Frame to hold buttons and text boxes
    control_frame = tk.Frame(root)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

    # Save button
    save_button = tk.Button(control_frame, text="Save", command=save_data)
    save_button.pack(side=tk.LEFT, padx=10, pady=10)

    # File name entry
    file_name_entry = tk.Entry(control_frame)
    file_name_entry.pack(side=tk.LEFT, padx=10, pady=10)
    file_name_entry.insert(0, "curriculum")  # Default file name without extension

    # Reload button
    reload_button = tk.Button(control_frame, text="Reload", command=reload_data)
    reload_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Zoom level entry
    zoom_label = tk.Label(control_frame, text="Zoom:")
    zoom_label.pack(side=tk.LEFT, padx=5, pady=10)

    zoom_entry = tk.Entry(control_frame, width=5, state='readonly')
    zoom_entry.pack(side=tk.LEFT, padx=5, pady=10)
#    zoom_entry.insert(0, "1.0")  # Default zoom level
#     zoom_entry.configure(state='normal')  # Temporarily set to normal to allow editing
#     zoom_entry.delete(0, tk.END)  # Clear the current text
#     zoom_entry.insert(0, str(1.0))  # Insert the new value
#     zoom_entry.configure(state='readonly')  # Set back to readonly
    #zoom_entry.bind("<Return>", change_zoom)  # Change zoom on Enter key press

    autopath_var = tk.BooleanVar()
    autopath_checkbox = tk.Checkbutton(control_frame, text="AutoPath", variable=autopath_var)
    autopath_checkbox.pack(side=tk.LEFT, padx=10, pady=10)

    # Convert to HTML button
    convert_button = tk.Button(control_frame, text="To HTML", command=convert_canvas_to_html)
    convert_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Convert to SVG button
    convert_button = tk.Button(control_frame, text="To SVG", command=convert_canvas_to_svg)
    convert_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Black Theme
    convert_button = tk.Button(control_frame, text="Black Theme", command=black_theme)
    convert_button.pack(side=tk.LEFT, padx=10, pady=10)

    # Green Theme
    convert_button = tk.Button(control_frame, text="Green Theme", command=green_theme)
    convert_button.pack(side=tk.LEFT, padx=10, pady=10)


    # Canvas for drawing
    canvas = ZoomCanvas(root,zoom_entry, width=canvas_width, height=canvas_height, bg=color_bg)
    canvas.pack()

 
    # Dictionary to hold the total credits per semester
    credits_per_semester = {}

    # Dictionary to hold subject positions
    subject_positions = {}
    
    

    def on_start_move(event):
        widget = event.widget
        widget.startX = event.x
        widget.startY = event.y
        widget.moving_item_tag = canvas.gettags(canvas.find_withtag("current"))[0]

    def on_move(event):
        widget = event.widget
        dx = event.x - widget.startX
        dy = event.y - widget.startY
        canvas.move(widget.moving_item_tag, dx, dy)
        widget.startX = event.x
        widget.startY = event.y

    def update_credits():
        # Clear previous credits text
        canvas.delete("credit_text")
        for semester, credits in credits_per_semester.items():
            x = x_margin + (semester - 1) * x_spacing
            y = 40  # Place the text above the first row of the semester
            credits_text = f"Créditos: {credits}"
            canvas.create_text(x + rect_width / 2, y + 20, text=credits_text, fill='#fff', font=('Arial', 10, 'bold'), tags="credit_text")

    def on_release(event):
        widget = event.widget
        item_coords = canvas.coords(widget.moving_item_tag)
        x = item_coords[0]
        y = item_coords[1]

        # Calculate nearest grid position
        nearest_x = round((x - x_margin) / x_spacing) * x_spacing + x_margin
        nearest_y = round((y - top_margin) / y_spacing) * y_spacing + top_margin

        # Move item to nearest grid position
        dx = nearest_x - x
        dy = nearest_y - y
        canvas.move(widget.moving_item_tag, dx, dy)

        # Update the CSV data with the new position
        tag_parts = widget.moving_item_tag.split("_")
        nearest_semester = (nearest_x - x_margin) // x_spacing + 1
        nearest_row = (nearest_y - top_margin) // y_spacing + 1
        for subject in data:
            if subject['Código'] == tag_parts[1]:
                # Update credits for the old and new semester
                old_semester = int(subject['Semestre'])
                credits_per_semester[old_semester] -= int(subject['Créditos'])
                if nearest_semester not in credits_per_semester:
                    credits_per_semester[nearest_semester] = 0
                credits_per_semester[nearest_semester] += int(subject['Créditos'])

                subject['Semestre'] = str(nearest_semester)
                subject['Posición'] = str(nearest_row)
                break

        update_credits()

    for subject in data:
        semester = int(subject['Semestre'])
        row = int(subject['Renglón Malla'])
        name = (subject['Nombre'].replace('\\n','\n')
                #+'\n - '
                #+subject['Temas'].replace('\\n','\n - ').replace('"','').strip()
                +'\n - \n - \n - '
                +'\n Código: '+subject['Código']
                +', Créditos: '+subject['Créditos'])
        code = subject['Código']
        credits = int(subject['Créditos'])
        area = subject['Área']
        if color_block==None and area in area_colors:
            area_color = area_colors[area]
        else:
            area_color = color_block
        

        # Update total credits for the semester
        if semester not in credits_per_semester:
            credits_per_semester[semester] = 0
        credits_per_semester[semester] += credits

        x = x_margin + (semester - 1) * x_spacing
        y = top_margin + (row - 1) * y_spacing

        # Create a unique tag for each subject using 'Código'
        tag = f"subject_{code}"

        # Store subject positions
        subject_positions[code] = (x, y, semester, row)

        # Draw rectangle
        rect = canvas.create_rectangle(x, y, x + rect_width, y + rect_height, fill=area_color, tags=tag)
        # Add text
        text = canvas.create_zoomable_text(x + rect_width / 2, y + rect_height / 2, text=name, fill='#fff', tags=tag)

        # Bind mouse events for dragging
        canvas.tag_bind(tag, "<ButtonPress-1>", on_start_move)
        canvas.tag_bind(tag, "<B1-Motion>", on_move)
        canvas.tag_bind(tag, "<ButtonRelease-1>", on_release)

    # Add semester numbers and total credits to the canvas
    for semester in credits_per_semester:
        x = x_margin + (semester - 1) * x_spacing
        y = 40  # Place the text above the first row of the semester
        semester_text = f"Semestre: {semester}"
        credits_text = f"Créditos: {credits_per_semester[semester]}"
        canvas.create_text(x + rect_width / 2, y, text=semester_text, fill='#fff', font=('Arial', 10, 'bold'))
        canvas.create_text(x + rect_width / 2, y + 20, text=credits_text, fill='#fff', font=('Arial', 10, 'bold'), tags="credit_text")

    # Create a grid representation for the Maze route algorithm
    rows = (canvas_height // y_grid) + 1
    cols = (canvas_width // x_grid) + 1
    grid = {(i,j):0 for i in range(0,canvas_width,x_grid) for j in range(0,canvas_height,y_grid)}#[[0 for _ in range(cols)] for _ in range(rows)]

    # Mark grid cells occupied by rectangles
    for x, y, _, _ in subject_positions.values():
        x,y=aprox_xy((x,y))
        for i in range(x,x+rect_width+1,x_grid):
            for j in range(y,y+rect_height+1,y_grid):
                #print('grid',rows,cols,i,j)
                grid[(i,j)] = 1

    paths=load_prerequisite_paths(prereq_file_path,subject_positions,canvas,autopath_var,grid)
    
    root.mainloop()
    #save_prerequisite_paths('prerequisitos.csv', paths)

# File paths
csv_file_path = 'curriculum_nodes.csv'
prereq_file_path = 'curriculum_paths.csv'
pads_code=defaultdict(int)
pads_prereq=defaultdict(int)
pereq_path=[]

# Read CSV data
#csv_data = read_csv(csv_file_path)
#prereq_data = read_csv(prereq_file_path)

# Draw rectangles with prerequisites
#draw_rectangles(csv_data, prereq_data)
draw_rectangles(csv_file_path, prereq_file_path)
