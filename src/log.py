import matplotlib.pyplot as plt
import os

LOG_PATH = "/home/pi/Desktop/logs/"

log = []
x_axis = []



GOAL = 3
TOLERANCE = 0.05
Y_LOW = 2.5
Y_HIGH = 3.5

def reset():
    global log, x_axis
    log = []
    x_axis = []
    print("Log has been reset")

def log_diameter(dia, inc):
    # Diameter is in mm
    log.append(dia)
    x_axis.append(len(x_axis) * inc)

def draw_line(fig, val, col, thickness=1):
    line = fig.add_subplot(111)
    line_data = []
    for i in range(len(x_axis)):
        line_data.append(val)
    line.plot(x_axis, line_data, linewidth=thickness, color=col)

def plot_pdf(date, batch, percent):
    fig = plt.figure(num=2, figsize=(15, 7))
    fig.clf()
    ax = fig.add_subplot(111)
    
    # Log Permutations
    for i in range(len(log)):
        if log[i] < Y_LOW:
            log[i] = Y_LOW
        if log[i] > Y_HIGH:
            log[i] = Y_HIGH
    
    
    draw_line(fig, GOAL-TOLERANCE, "orange")
    draw_line(fig, GOAL+TOLERANCE, "orange")
    draw_line(fig, GOAL + 0.2, "red")
    draw_line(fig, GOAL - 0.2, "red")
    ax.plot(x_axis, log, linewidth=2, color="black")
    draw_line(fig, Y_LOW, "white", 4)
    draw_line(fig, Y_HIGH, "white", 4)
    
    title = "[" + date + "]" + " batch " + batch + ": " + percent + "%";
    fig.suptitle(title)
    ax.set_xlabel('Seconds')
    ax.set_ylabel('Diameter (mm)')
    
    date_path = LOG_PATH + date + "/batch-" + batch
    
    if not os.path.exists(date_path):
        os.makedirs(date_path)
        
    # Record to text file
    
    text_file_name = date_path + "/log.txt"
    f = open(text_file_name, 'w')
    
    contents = ''
    for entry in log:
        contents += str(entry) + '\n'
    f.write(contents)
    f.close()
        
    fname = "plot"
    fig_path = date_path + "/" + fname + ".pdf"
    if os.path.exists(fig_path):
        os.remove(fig_path)
    fig.savefig(fig_path)
    
    
    
    """
    log = []
    x_axis = []
    tolerance_low = []
    tolerance_high = []
    y_low = []
    y_high = []
    """
    
    
    
    

    