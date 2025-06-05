import os
import sys
import subprocess
import customtkinter as ui

class Model:
    def __init__(self):
        self.setstamp = True
        self.input_dir = None
        self.input_dir_files = None
        self.input_file = None
        self.output_dir = None
        self.ff_cmdstr = None
        self.dithername = None
        self.prefix = "noname"

        ### GIF SETTING OPTIONS ###
        self.loop_list = ['Yes','No']
        self.optimize_list = ['Animation','Video']
        self.scale_list = ['100%','75%','50%','25%']
        self.stats_mode_list = ['full','diff']              # 0,1
        self.diff_mode_list = ['rectangle','none']          # 0,1
        self.colours_list = [256, 192, 128, 96, 64, 48,32]  # 0,1,2,3
        self.dither_method_list = ['bayer:bayer_scale=1',   # 0 high quality bayer
                                   'bayer:bayer_scale=2',   # 1
                                   'bayer:bayer_scale=3',   # 2
                                   'bayer:bayer_scale=4',   # 3
                                   'bayer:bayer_scale=5',   # 4 low quality bayer
                                   'sierra2',               # 5
                                   'floyd_steinberg',       # 6
                                   'sierra2_4a',            # 7 Highest size
                                   'none']                  # 8 ugly


    def convert_menu_scale(self, menu_scale):
        value = float(menu_scale.strip('%'))
        return 100.0 / value
    
    def convert_menu_dither(self, menu_dither):
        if menu_dither == 'Bayer 1':
            self.dither_method = self.dither_method_list[0]
        elif menu_dither == 'Bayer 2':
            self.dither_method = self.dither_method_list[1]
        elif menu_dither == 'Bayer 3':
            self.dither_method = self.dither_method_list[2]
        elif menu_dither == 'Bayer 4':
            self.dither_method = self.dither_method_list[3]
        elif menu_dither == 'Bayer 5':
            self.dither_method = self.dither_method_list[4]
        elif menu_dither == 'Sierra2':
            self.dither_method = self.dither_method_list[5]
        elif menu_dither == 'Floyd_steinberg':
            self.dither_method = self.dither_method_list[6]
        elif menu_dither == 'Sierra2_4a':
            self.dither_method = self.dither_method_list[7]
        elif menu_dither == 'None':
            self.dither_method = self.dither_method_list[8]            

    def optimize_from_menu(self, optimize):
        if optimize == 'Animation':
            self.stats_mode = self.stats_mode_list[1]
            self.diff_mode = self.diff_mode_list[0]
        elif optimize == 'Video':
            self.stats_mode = self.stats_mode_list[0]
            self.diff_mode = self.diff_mode_list[1]

    def convert_menu_loops(self, loops):
        if loops == 'Yes':
            self.loops = 0
        elif loops == 'No':
            self.loops = 1    

    def settings_from_menu(self, fps, scale, colours, dither, optimize, loops, output):
        self.fps = fps 
        self.scalediv = self.convert_menu_scale(scale)
        self.max_colours = colours
        self.convert_menu_dither(dither)
        self.optimize_from_menu(optimize)
        self.convert_menu_loops(loops)
        self.output_dir = output

    def set_prefix_from_path(self, full_path):
        base = os.path.basename(full_path)           
        name, _ = os.path.splitext(base)             
        self.prefix = name

    def set_input_file(self):
        input_file = ui.filedialog.askopenfilename()
        self.input_file = input_file
        self.input_dir = None
        self.input_dir_files = None

    def set_input_dir(self):
        input_dir = ui.filedialog.askdirectory()
        self.input_dir = input_dir
        self.input_dir_files = self.list_input_files()
        self.input_file = None

    def list_input_files(self):
        if not self.input_dir:
            return []
        return [os.path.join(self.input_dir, f)
                for f in os.listdir(self.input_dir)
                if f.lower().endswith(('.mov', '.mp4'))]

    def set_output_dir(self):
        output_dir = ui.filedialog.askdirectory()
        self.output_dir = output_dir

    def set_output_filename(self, prefix):
        if self.setstamp:
            self.dithername_output()
            self.output_filename = (f'{prefix}_{self.fps}f'
                                    f'{self.max_colours}c{self.dithername}.gif')
        else:
            self.output_filename = self.prefix

    def concatenate_cmdstr(self, file):
        self.set_output_filename(self.prefix)
        self.ff_cmdstr = (f'ffmpeg -i {file} ' 
                          f'-vf "fps={self.fps},scale=iw/{self.scalediv}:ih/{self.scalediv}:flags=lanczos,'
                          f'split[s0][s1];'
                          f'[s0]palettegen=max_colors={self.max_colours}:stats_mode={self.stats_mode}[p];'
                          f'[s1][p]paletteuse=dither={self.dither_method}:diff_mode={self.diff_mode}" '
                          f'-loop {self.loops} '
                          f'{self.output_dir}/{self.output_filename} -y')
        print(f'string = {self.ff_cmdstr}')

    def run_ffmpeg_cmdstr(self, file):
        self.set_prefix_from_path(file)
        self.concatenate_cmdstr(file)
        os.system(self.ff_cmdstr)
        print(f'generating gif')

    def dithername_output(self):
        if self.dither_method.startswith('bayer:bayer_scale='):
            scale = self.dither_method.split('=')[1]
            self.dithername = (f'Bayer{scale}')
        else:
            self.dithername = self.dither_method

    def rename_ditherlist(self):
        renamed = []
        for method in self.dither_method_list:
            if method.startswith('bayer:bayer_scale='):
                scale = method.split('=')[1]
                renamed.append(f'Bayer {scale}')
            else:
                renamed.append(method.capitalize())
        return renamed
    
    def open_output_folder(self):
        path = self.output_dir
        if not path or not os.path.exists(path):
            return
        if sys.platform.startswith('win'):
            os.startfile(path)
        elif sys.platform.startswith('darwin'):
            subprocess.Popen(['open', path])
        else:
            subprocess.Popen(['xdg-open', path])


class Control: 
    def __init__(self, view, model):
        self.view = view
        self.model = model

    def find_file_location(self):
        self.model.set_input_file()
        self.view.single_file_btn.configure(fg_color='#DBDBDB',text_color='grey3')
        self.view.folder_btn.configure(fg_color='grey3',text_color='grey70')

    def find_folder_location(self):
        self.model.set_input_dir()
        self.view.folder_btn.configure(fg_color='#DBDBDB',text_color='grey3')
        self.view.single_file_btn.configure(fg_color='grey3',text_color='grey70')

    def set_save_location(self):
        self.model.set_output_dir()
        self.view.output_input.delete(0,'end')
        self.view.output_input.insert(0, self.model.output_dir)
        self.view.output_input.xview('end')

    def generate_gif(self):
        model.settings_from_menu(fps=self.view.fps_input.get(),
                                 scale=self.view.scale_dd.get(),
                                 colours=self.view.max_dd.get(),
                                 dither=self.view.dith_dd.get(),
                                 optimize=self.view.opt_dd.get(),
                                 loops=self.view.loop_dd.get(),
                                 output=self.view.output_input.get())
        
        if not self.model.output_dir or not os.path.exists(self.model.output_dir):
            self.view.flash_red()
            return
        if self.model.input_file:
            if not os.path.exists(self.model.input_file):
                self.view.flash_red()
                return
            self.model.run_ffmpeg_cmdstr(self.model.input_file)
        elif self.model.input_dir_files:
            if len(self.model.input_dir_files) == 0:
                self.view.flash_red()
                return
            for file in self.model.input_dir_files:
                if not os.path.exists(file):
                    continue
                self.model.run_ffmpeg_cmdstr(file)
        else:
            self.view.flash_red()
            return
        
        self.model.open_output_folder()
        self.view.flash_green()




class View(ui.CTk): 
    def __init__(self, control):
        super().__init__()
        self.control = control
        ui.set_appearance_mode("dark")
        ui.set_default_color_theme("green")
        self.geometry("300x675")
        self.title("I don't gif a f***")
        # self.iconbitmap(os.path.join('icons','punch.ico'))
        self.resizable(False, False)

        # fps
        self.fps_area = self.area(300,50,0,10,self)
        self.fps_text  = self.menu_text("FPS:",20,12,self.fps_area)
        self.fps_input = self.input(125,35,155,7.5,self.fps_area)
        self.fps_input.insert(0,'30') # will need to change this if I end up saving settings
        self.fps_area.bind('<Enter>', self.fps_help)
        self.fps_text.bind('<Enter>', self.fps_help)
        self.fps_input.bind('<Enter>', self.fps_help)
        self.fps_area.bind('<Leave>', self.overview_help)

        # scale
        self.scale_area = self.area(300,50,0,60,self)
        self.scale_text  = self.menu_text("Scale:",20,12,self.scale_area)
        self.scale_dd = self.drop_down(125,35,155,7.5, self.control.model.scale_list, self.scale_area)
        self.scale_area.bind('<Enter>', self.scale_help)
        self.scale_text.bind('<Enter>', self.scale_help)
        self.scale_dd.bind('<Enter>', self.scale_help)
        self.scale_area.bind('<Leave>', self.overview_help)

        # max colours
        self.max_area = self.area(300,50,0,110,self)
        self.max_text  = self.menu_text("Max colours:",20,12,self.max_area)
        self.max_dd = self.drop_down(125,35,155,7.5, self.control.model.colours_list, self.max_area)
        self.max_area.bind('<Enter>', self.max_help)
        self.max_text.bind('<Enter>', self.max_help)
        self.max_dd.bind('<Enter>', self.max_help)
        self.max_area.bind('<Leave>', self.overview_help)

        # dither method
        self.dith_area = self.area(300,50,0,160,self)
        self.dith_text  = self.menu_text("Dither method:",20,12,self.dith_area)
        self.dith_dd = self.drop_down(125,35,155,7.5, self.control.model.rename_ditherlist(), self.dith_area)
        self.dith_area.bind('<Enter>', self.dith_help)
        self.dith_text.bind('<Enter>', self.dith_help)
        self.dith_dd.bind('<Enter>', self.dith_help)
        self.dith_area.bind('<Leave>', self.overview_help)

        # optimize preference
        self.opt_area = self.area(300,50,0,210,self)
        self.opt_text  = self.menu_text("Optimize for:",20,12,self.opt_area)
        self.opt_dd = self.drop_down(125,35,155,7.5, self.control.model.optimize_list, self.opt_area)
        self.opt_area.bind('<Enter>', self.opt_help)
        self.opt_text.bind('<Enter>', self.opt_help)
        self.opt_dd.bind('<Enter>', self.opt_help)
        self.opt_area.bind('<Leave>', self.overview_help)

        # loop preference
        self.loop_area = self.area(300,50,0,260,self)
        self.loop_text  = self.menu_text("Loop:",20,12,self.loop_area)
        self.loop_dd = self.drop_down(125,35,155,7.5, self.control.model.loop_list, self.loop_area)
        self.loop_area.bind('<Enter>', self.loop_help)
        self.loop_text.bind('<Enter>', self.loop_help)
        self.loop_dd.bind('<Enter>', self.loop_help)
        self.loop_area.bind('<Leave>', self.overview_help)

        # file input
        self.input_text = self.menu_text("Select input:",20,320,self)
        self.input_text.configure(font = ('Roboto Bold', 16))
        self.input_area = self.area(300, 60, 0, 350, self)
        self.single_file_btn = self.btn(125,40,"Single File",20,10, self.control.find_file_location ,self.input_area)
        self.single_file_btn.bind('<Enter>', self.single_help)
        self.single_file_btn.bind('<Leave>', self.overview_help)
        self.folder_btn = self.btn(125,40,"Folder",155,10, self.control.find_folder_location ,self.input_area)
        self.folder_btn.bind('<Enter>', self.folder_help)
        self.folder_btn.bind('<Leave>', self.overview_help)

        # Set output
        self.output_text = self.menu_text("Select save location:",20,415,self)
        self.output_text.configure(font = ('Roboto Bold', 16))
        self.output_area = self.area(600, 150, 0, 440, self)
        self.output_input = self.input(260, 35, 20, 10, self.output_area)
        self.output_input.configure(justify='left')
        self.output_btn = self.btn(260, 40, "Set Output Folder", 20, 55, self.control.set_save_location, self.output_area)
        self.makegif_btn = self.btn(260, 80, "Generate Gif(s)!", 20, 555, self.control.generate_gif, self)
        self.makegif_btn.configure(fg_color="#DBDBDB", text_color='black', hover_color="#FFFFFF")
        self.output_area.bind('<Enter>', self.output_help)
        self.output_text.bind('<Enter>', self.output_help)
        self.output_input.bind('<Enter>', self.output_help)
        self.output_btn.bind('<Enter>', self.output_help)
        self.output_area.bind('<Leave>', self.overview_help)

        # Overview 
        self.overviewlabel = self.menu_text("Show Overview ◨", 170, 642, self)
        self.overviewlabel.configure(font=('Roboto', 14), text_color="#7D7D7D", cursor="hand2")
        self.overviewlabel.bind("<Button-1>", self.overview_toggle)

        # Set overview panel
        self.overview_area = self.area(280,618,300,18,self)
        self.overview_area.configure(fg_color='grey9', corner_radius=7)
        self.overview_helptext = self.overview_text('Placeholder', self.overview_area)
        self.overview_help(None)
        
    def btn(self, set_width, set_height, set_text, set_x, set_y,set_command,set_root):
        button = ui.CTkButton(set_root, 
                              width=set_width, 
                              height= set_height, 
                              text=set_text, 
                              text_color='grey70',
                              font=("Roboto Bold", 16),
                              fg_color='grey3',
                              hover_color='grey20',
                              command=set_command)
        button.place(x=set_x, y=set_y)
        return button
    
    def area(self, set_width, set_height, set_x, set_y, set_root):
        label = ui.CTkLabel(set_root,
                            width=set_width,
                            height=set_height,
                            text=None,
                            bg_color='transparent')
        label.place(x=set_x,y=set_y)
        return label
    
    def input(self, set_width, set_height, set_x, set_y,set_root):
        input = ui.CTkEntry(set_root, 
                             width=set_width, 
                             height= set_height,
                             font=("Roboto Bold", 16),
                             justify="center",
                             border_width=0)
        input.place(x=set_x, y=set_y)
        return input
    
    def menu_text(self, menu_text, set_x, set_y, set_root):
        label = ui.CTkLabel(set_root,
                            text=menu_text,
                            font=("Roboto", 16),
                            text_color='grey60')
        label.place(x=set_x,y=set_y)
        return label
    
    def overview_text(self, help_text, set_root):
        label = ui.CTkLabel(set_root,
                            text=help_text,
                            font=("Roboto", 18),
                            text_color='grey50',
                            wraplength=230)
        label.place(relx=0.5, rely=0.5, anchor="center")
        return label
    
    def drop_down(self, set_width, set_height, set_x, set_y, opt_list, set_root):
        menu = ui.CTkOptionMenu(set_root, 
                                 width = set_width, 
                                 height = set_height,
                                 values = [str(item) for item in opt_list],
                                 font=("Roboto", 16),
                                 text_color="grey70",
                                 fg_color='grey7',
                                 button_color='grey3',
                                 button_hover_color='grey20',
                                 dynamic_resizing=False)
        menu.place(x=set_x, y=set_y)
        return menu
    
    def flash_green(self):
        original_color = self.makegif_btn.cget("fg_color")
        self.makegif_btn.configure(fg_color="#72e572")
        self.after(1000, lambda: self.makegif_btn.configure(fg_color=original_color))

    def flash_red(self):
        original_color = self.makegif_btn.cget("fg_color")
        self.makegif_btn.configure(fg_color="#d30000")
        self.after(1000, lambda: self.makegif_btn.configure(fg_color=original_color))
    
    def overview_toggle(self, event):
        current = self.geometry().split("+")[0]
        if current == "300x675":
            self.geometry("600x675")
            self.overviewlabel.configure(text='Hide Overview ◧')
            self.overviewlabel.place(x=475, y=642)
        else:
            self.geometry("300x675")
            self.overviewlabel.configure(text='Show Overview ◨')
            self.overviewlabel.place(x=170, y=642)
    
    def overview_help(self, event):
        self.overview_helptext.configure(text=
        'Overview:\n\nThe options on the left are arranged from top ' \
        'to bottom based on their typical impact on reducing file size.\n\n ' \
        'Hover over any option to see more details here.')

    def fps_help(self, event):
        self.overview_helptext.configure(text=
        'FPS:\n\nReducing FPS is one of the most effective ways to reduce file size,' \
        '\n\nJust keep in mind that lowering it too much can ' \
        'make motion appear choppy.')

    def scale_help(self, event):
        self.overview_helptext.configure(text=
        'Scale:\n\nLowering the scale can often reduce file size even more than adjusting FPS. ' \
        'However, we’re often aiming for specific dimensions. \n\nThe Scale option is useful ' \
        'for scaling down from a larger video output size when needed.')

    def max_help(self, event):
        self.overview_helptext.configure(text=
        'Max Colours:\n\nReducing colours can significantly shrink file size by ' \
        'simplifying the image. \n\nHowever, cutting too many colours may cause ' \
        'noticeable banding or loss of detail.')
    
    def dith_help(self, event):
        self.overview_helptext.configure(text=
        'Dither method:\n\nDithering blends pixels of different colours to ' \
        'simulate more colour depth, Important when you have limited colours ' \
        'available such as gifs. \n\nBayer 1-5 are your go to for animations, ' \
        '1 being the highest file size and smoothest, 5 being almost unusable!' \
        '\n\nThe "Sierra" and "Flyod Steinberg" methods are worth using for ' \
        'footage quality, and "None" is useful for very simple animations ' \
        'with very low colour detail needed.')

    def opt_help(self, event):
        self.overview_helptext.configure(text=
        'Optimize for:\n\n Optimize for settings refer to multiple options ' \
        'which dont have a significant impact beyond minimal optimization ' \
        'for either animations or video footage.')
    
    def loop_help(self, event):
        self.overview_helptext.configure(text=
        'Loop:\n\n Set whether the gif loops or not, this shouldnt effect ' \
        'file size much if at all')

    def single_help(self, event):
        self.overview_helptext.configure(text=
        'Single File:\n\n This button is for when you want to convert ' \
        'a single ".mp4" or ".mov" file.')
    
    def folder_help(self, event):
        self.overview_helptext.configure(text=
        'Folder:\n\n This button is for when you want to convert multiple ' \
        'files, it will convert any file with the extensions ".mp4" or ".mov" in the folder.')
    
    def output_help(self, event):
        self.overview_helptext.configure(text=
        'Output:\n\n You can enter the output location manually throught the ' \
        'input or click the "Set Output Folder" button.')


        
model = Model()
control = Control(None, model) 
view = View(control)             
control.view = view              

view.mainloop()