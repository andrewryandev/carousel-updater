import tkinter as tk
from tkinter import Button, Entry, Label, ttk, StringVar, messagebox
from tkinter import filedialog as fd
from PIL import Image, ImageTk
import os
from jinja2 import Environment, FileSystemLoader
import shutil
import paramiko
from scp import SCPClient
import configparser
import time
import glob



startInfo = 'Welcome to the BHS Carousel Updater tool!\n\nPlease only work on one section at once and only start\nthe next after you generate and send the section before'
tk.messagebox.showinfo(title="Welcome",message=startInfo)

###################Jinja2_Vars#########################
osRoot = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(osRoot, 'templates')
env = Environment( loader = FileSystemLoader(templates_dir) )

ht_template = env.get_template('ht_carousel_template.html')
exec_template = env.get_template('exec_carousel_template.html')
yr_template = env.get_template('yr_carousel_template.html')

ht_filename = os.path.join(osRoot, 'html', 'carousel_aem_ht.html')
exec_filename = os.path.join(osRoot, 'html', 'carousel_aem_exec.html')
yr_filename = os.path.join(osRoot, 'html', 'carousel_aem_ya.html')

#################scp_vars#####################

parser = configparser.ConfigParser()
config_file = osRoot + "\config\server.ini"
parser.read(config_file)
server = parser.get("scp_vars", "server")
port = parser.get("scp_vars", "port")
user = parser.get("scp_vars", "user")
password = parser.get("scp_vars", "password")



ht_array = []
exec_array = []
yr_array = []
ht_button_dict = {}
exec_button_dict = {}
yr_button_dict = {}
global htCount
global execCount
global yrCount
htCount = 5
execCount = 5
yrCount = 5

class staff():
    def __init__(self, name, title, imagePath, image):
        self.name = name
        self.title = title
        self.imagePath = imagePath
        self.image = image
        

# create the root window
root = tk.Tk()
root.title('BHS Carousel Updater')
root.resizable(False, False)
root.geometry('1670x768')

blankPath = Image.open(osRoot + '\\config\\blank.jpg')
blank = ImageTk.PhotoImage(blankPath)

class htDelButt():
    def __init__(self, l):
        self.k = None
        self.l = l
        self.id = id(self)
        self.newButt = Button(root, text="Delete", command=lambda: htDelete(self.id, self.l, self.k))

class execDelButt():
    def __init__(self, l):
        self.k = None
        self.l = l
        self.id = id(self)
        self.newButt = Button(root, text="Delete", command=lambda: execDelete(self.id, self.l, self.k))

class yrDelButt():
    def __init__(self, l):
        self.k = None
        self.l = l
        self.id = id(self)
        self.newButt = Button(root, text="Delete", command=lambda: yrDelete(self.id, self.l, self.k))

class arrayLabel():
    def __init__(self, v):
        self.values = v
        self.id = id(self)
        self.newLabel = Label(root, text=f'{self.values}')

##########################################################
eHTName = Entry(root)
eHTTitle = Entry(root)
eHTImagePath = Entry(root)
eExecName = Entry(root)
eExecTitle = Entry(root)
eExecImagePath = Entry(root)
eYrName = Entry(root)
eYrTitle = Entry(root)
eYrImagePath = Entry(root)

space1 = tk.Label(root, text='                ')
space1.grid(column=5, row=0, rowspan=20)

space2 = tk.Label(root, text='                ')
space2.grid(column=10, row=0, rowspan=20)

b1 = tk.Button(root, text='Upload Image', 
   width=20,command = lambda:browsefunc())

b1.grid(row=3,column=2)

b3 = tk.Button(root, text='Upload Image', 
   width=20,command = lambda:execBrowsefunc())

b3.grid(row=3,column=7)

b5 = tk.Button(root, text='Upload Image', 
   width=20,command = lambda:yrBrowsefunc())

b5.grid(row=3,column=12)

eHTNameText=StringVar()
eHTNameText.set("Head Teacher Name")
eHTNameLabel=Label(root, textvariable=eHTNameText, height=4)
eHTNameLabel.grid(row=1,column=3)
eHTName.grid(row=1,column=4)

eHTTitleText=StringVar()
eHTTitleText.set("Head Teacher Faculty")
eHTTitleLabel=Label(root, textvariable=eHTTitleText, height=4)
eHTTitleLabel.grid(row=2,column=3)
eHTTitle.grid(row=2,column=4)

eHTTitleText=StringVar()
eHTTitleText.set("Head Teacher Image Path")
eHTTitleLabel=Label(root, textvariable=eHTTitleText, height=4)
eHTTitleLabel.grid(row=3,column=3)
eHTImagePath.grid(row=3,column=4)
####################################################################

eExecNameText=StringVar()
eExecNameText.set("Senior Executive Name")
eExecNameLabel=Label(root, textvariable=eExecNameText, height=4)
eExecNameLabel.grid(row=1,column=8)
eExecName.grid(row=1,column=9)

eExecTitleText=StringVar()
eExecTitleText.set("Senior Executive Title")
eExecTitleLabel=Label(root, textvariable=eExecTitleText, height=4)
eExecTitleLabel.grid(row=2,column=8)
eExecTitle.grid(row=2,column=9)

eExecTitleText=StringVar()
eExecTitleText.set("Senior Executive Image Path")
eExecTitleLabel=Label(root, textvariable=eExecTitleText, height=4)
eExecTitleLabel.grid(row=3,column=8)
eExecImagePath.grid(row=3,column=9)

###################################################################

eYrNameText=StringVar()
eYrNameText.set("Year Advisor Name")
eYrNameLabel=Label(root, textvariable=eYrNameText, height=4)
eYrNameLabel.grid(row=1,column=13)
eYrName.grid(row=1,column=14)

eYrTitleText=StringVar()
eYrTitleText.set("Year Advisor Cohort")
eYrTitleLabel=Label(root, textvariable=eYrTitleText, height=4)
eYrTitleLabel.grid(row=2,column=13)
eYrTitle.grid(row=2,column=14)

eYrTitleText=StringVar()
eYrTitleText.set("Year Advisor Image Path")
eYrTitleLabel=Label(root, textvariable=eYrTitleText, height=4)
eYrTitleLabel.grid(row=3,column=13)
eYrImagePath.grid(row=3,column=14)


def htDelete(buttonID, label, button):
    x = ht_button_dict[buttonID]
    label.grid_forget()
    button.grid_forget()
    for ix, staff in enumerate(ht_array):
        if (staff.name == x):
            u = osRoot + '\\html\\staff-photos\\' + staff.image
            os.remove(u)
            del ht_array[ix]

def execDelete(buttonID, label, button):
    x = exec_button_dict[buttonID]
    label.grid_forget()
    button.grid_forget()
    for ix, staff in enumerate(exec_array):
        if (staff.name == x):
            u = osRoot + '\\html\\staff-photos\\' + staff.image
            os.remove(u)
            del exec_array[ix]

def yrDelete(buttonID, label, button):
    x = yr_button_dict[buttonID]
    label.grid_forget()
    button.grid_forget()
    for ix, staff in enumerate(yr_array):
        if (staff.name == x):
            u = osRoot + '\\html\\staff-photos\\' + staff.image
            os.remove(u)
            del yr_array[ix]

def htAppendClick2():
    if not eHTName.get() or not eHTTitle.get() or not eHTImagePath.get():
        tk.messagebox.showerror(title="Woops", message="Must have a name, faculty and image")
    else:
        global htCount
        image = os.path.basename(eHTImagePath.get())
        ht = staff(eHTName.get(), eHTTitle.get(), eHTImagePath.get(), image)
        ht_array.append(ht)
        x = ht_array.index(ht)
        v = ht.name + ", " + ht.title
        htLabel = arrayLabel(v)
        htLabel.values = v
        p = htLabel.id
        u = htLabel.newLabel
        u.grid(row=htCount,column=2)
        #####################################
        z = htDelButt(u)
        z.k = z.newButt
        z.newButt.grid(row=htCount,column=3)
        y = z.id
        ht_button_dict[y] = ht.name
        
        dst = os.path.join(osRoot, 'html\staff-photos')
        shutil.copy(eHTImagePath.get(), dst)

        htCount += 1
        eHTName.delete(0, 'end')
        eHTTitle.delete(0, 'end')
        eHTImagePath.delete(0, 'end')
        try:
            b2
        except NameError:
            return
        else:
            b2.configure(image=blank)

def execAppendClick2():
    if not eExecName.get() or not eExecTitle.get() or not eExecImagePath.get():
        tk.messagebox.showerror(title="Woops", message="Must have a name, title and image")
    else:
        global execCount
        image = os.path.basename(eExecImagePath.get())
        exec = staff(eExecName.get(), eExecTitle.get(), eExecImagePath.get(), image)
        exec_array.append(exec)
        x = exec_array.index(exec)
        v = exec.name + ", " + exec.title
        execLabel = arrayLabel(v)
        execLabel.values = v
        p = execLabel.id
        u = execLabel.newLabel
        u.grid(row=execCount,column=7)
        #####################################
        z = execDelButt(u)
        z.k = z.newButt
        z.newButt.grid(row=execCount,column=8)
        y = z.id
        exec_button_dict[y] = exec.name
        
        dst = os.path.join(osRoot, 'html\staff-photos')
        shutil.copy(eExecImagePath.get(), dst)

        execCount += 1
        eExecName.delete(0, 'end')
        eExecTitle.delete(0, 'end')
        eExecImagePath.delete(0, 'end')
        try:
            b4
        except NameError:
            return
        else:
            b4.configure(image=blank)
            
def yrAppendClick2():
    if not eYrName.get() or not eYrTitle.get() or not eYrImagePath.get():
        tk.messagebox.showerror(title="Woops", message="Must have a name, year group and image")
    else:
        global yrCount
        image = os.path.basename(eYrImagePath.get())
        yr = staff(eYrName.get(), eYrTitle.get(), eYrImagePath.get(), image)
        yr_array.append(yr)
        x = yr_array.index(yr)
        v = yr.name + ", " + yr.title
        yrLabel = arrayLabel(v)
        yrLabel.values = v
        p = yrLabel.id
        u = yrLabel.newLabel
        u.grid(row=yrCount,column=11)
        #####################################
        z = yrDelButt(u)
        z.k = z.newButt
        z.newButt.grid(row=yrCount,column=12)
        y = z.id
        yr_button_dict[y] = yr.name
        
        dst = os.path.join(osRoot, 'html\staff-photos')
        shutil.copy(eYrImagePath.get(), dst)

        yrCount += 1
        eYrName.delete(0, 'end')
        eYrTitle.delete(0, 'end')
        eYrImagePath.delete(0, 'end')
        try:
            b6
        except NameError:
            return
        else:

            b6.configure(image=blank)


def htResetEntry():
    eHTName.delete(0, 'end')
    eHTTitle.delete(0, 'end')
    eHTImagePath.delete(0, 'end')
    b2.configure(image=blank)

def execResetEntry():
    eExecName.delete(0, 'end')
    eExecTitle.delete(0, 'end')
    eExecImagePath.delete(0, 'end')
    b4.configure(image=blank)

def yrResetEntry():
    eYrName.delete(0, 'end')
    eYrTitle.delete(0, 'end')
    eYrImagePath.delete(0, 'end')
    b6.configure(image=blank)

###################SCP_Upload##############################
def createSSHClient(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(server, port, user, password)
    return client

ssh = createSSHClient(server, port, user, password)
scp = SCPClient(ssh.get_transport(), sanitize=lambda x: x)

def htJinja():
    with open(ht_filename, 'w') as fh:
        fh.write(ht_template.render(
            staff=staff,
            ht_array= ht_array,
        ))
    time.sleep(3)
    scp.put(ht_filename, remote_path='/a/valid/path')
    photos = glob.glob(osRoot + '/html/staff-photos/*')
    scp.put(photos, remote_path="/a/valid/path")
    os.remove(ht_filename)
    for f in photos:
        os.remove(f)
    htSend.config(text='Sent!', state="disabled")

def execJinja():
    with open(exec_filename, 'w') as fh:
        fh.write(exec_template.render(
            staff=staff,
            exec_array= exec_array,
        ))
    time.sleep(3)
    scp.put(exec_filename, remote_path='/a/valid/path')
    photos = glob.glob(osRoot + '/html/staff-photos/*')
    scp.put(photos, remote_path="/a/valid/path")
    os.remove(exec_filename)
    for f in photos:
        os.remove(f)
    execSend.config(text='Sent!', state="disabled")

def yrJinja():
    with open(yr_filename, 'w') as fh:
        fh.write(yr_template.render(
            staff=staff,
            yr_array= yr_array,
        ))
    time.sleep(3)
    scp.put(yr_filename, remote_path='/a/valid/path')
    photos = glob.glob(osRoot + '/html/staff-photos/*')
    scp.put(photos, remote_path="/a/valid/path")
    os.remove(yr_filename)
    for f in photos:
        os.remove(f)
    yrSend.config(text='Sent!', state="disabled")

def htCreateSend():
    MsgBox = tk.messagebox.askquestion ('Generate & Upload Files','Are you sure you want to send files to server',icon = 'warning')
    if MsgBox == 'yes':
       htJinja()
    else:
        tk.messagebox.showinfo('Turning Around','You will now return to the application screen')

def execCreateSend():
    MsgBox = tk.messagebox.askquestion ('Generate & Upload Files','Are you sure you want to send files to server',icon = 'warning')
    if MsgBox == 'yes':
       execJinja()
    else:
        tk.messagebox.showinfo('Turning Around','You will now return to the application screen')

def yrCreateSend():
    MsgBox = tk.messagebox.askquestion ('Generate & Upload Files','Are you sure you want to send files to server',icon = 'warning')
    if MsgBox == 'yes':
       yrJinja()
    else:
        tk.messagebox.showinfo('Turning Around','You will now return to the application screen')

htAppendButton = Button(root, text="Add to HT List", command=lambda:htAppendClick2())
htAppendButton.grid(row=1,column=1)
htResetButton = Button(root, text="Reset Values", command=htResetEntry)
htResetButton.grid(row=3,column=1)
htSend = Button(root, text="Create & Send", command=htCreateSend)
htSend.grid(row=4,column=1)

execAppendButton = Button(root, text="Add to Exec List", command=lambda:execAppendClick2())
execAppendButton.grid(row=1,column=6)
execResetButton = Button(root, text="Reset Values", command=execResetEntry)
execResetButton.grid(row=3,column=6)
execSend = Button(root, text="Create & Send", command=execCreateSend)
execSend.grid(row=4,column=6)

yrAppendButton = Button(root, text="Add to YA List", command=lambda:yrAppendClick2())
yrAppendButton.grid(row=1,column=11)
yrResetButton = Button(root, text="Reset Values", command=yrResetEntry)
yrResetButton.grid(row=3,column=11)
yrSend = Button(root, text="Create & Send", command=yrCreateSend)
yrSend.grid(row=4,column=11)

def browsefunc():
    global img
    global b2
    filename =fd.askopenfilename(filetypes=[("image files", ".png .jpg")])
    original_image = Image.open(filename)
    resized_img = original_image.resize((150, 200), Image.ANTIALIAS)
    #img = ImageTk.PhotoImage(file=filename)
    img = ImageTk.PhotoImage(resized_img)
    b2 = tk.Button(root, image=img, compound='center') # using Button 
    b2.grid(row=1,column=2, rowspan=2)
    b2.config(width=150, height=200)
    eHTImagePath.insert(-1, filename)

def execBrowsefunc():
    global img
    global b4
    filename =fd.askopenfilename(filetypes=[("image files", ".png .jpg")])
    original_image = Image.open(filename)
    resized_img = original_image.resize((150, 200), Image.ANTIALIAS)
    #img = ImageTk.PhotoImage(file=filename)
    img = ImageTk.PhotoImage(resized_img)
    b4 = tk.Button(root, image=img, compound='center') # using Button 
    b4.grid(row=1,column=7, rowspan=2)
    b4.config(width=150, height=200)
    eExecImagePath.insert(-1, filename)

def yrBrowsefunc():
    global img
    global b6
    filename =fd.askopenfilename(filetypes=[("image files", ".png .jpg")])
    original_image = Image.open(filename)
    resized_img = original_image.resize((150, 200), Image.ANTIALIAS)
    #img = ImageTk.PhotoImage(file=filename)
    img = ImageTk.PhotoImage(resized_img)
    b6 = tk.Button(root, image=img, compound='center') # using Button 
    b6.grid(row=1,column=12, rowspan=2)
    b6.config(width=150, height=200)
    eYrImagePath.insert(-1, filename)


# run the application

root.mainloop()
