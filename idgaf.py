import os
import customtkinter as ui

class Model:
    def __init__(self):
        self.troubleshoot = True
        self.input_dir = None
        self.input_file = 'C:/Users/iamke/CODE/idgaf/testfiles/input/Giftest1_prores422_16bpc_srgb.mov'
        self.output_dir = 'C:/Users/iamke/CODE/idgaf/testfiles/output'
        self.ff_cmdstr = None
        self.dithername = None
        self.prefix = "Howabout"

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

        ### GIF SETTINGS ###
        self.fps = 8
        self.scalediv = 2
        self.max_colours = self.colours_list[1]
        self.dither_method = self.dither_method_list[8]
        self.stats_mode = self.stats_mode_list[1] #testing this one
        self.diff_mode = self.diff_mode_list[0]
        self.loops = 0

        ### OUTPUT NAME ###

    def set_input_file(self):
        input_file = ui.filedialog.askopenfilename()
        self.input_file = input_file

    def set_input_dir(self):
        input_dir = ui.filedialog.askdirectory()
        self.input_dir = input_dir

    def set_output_dir(self):
        output_dir = ui.filedialog.askdirectory()
        self.output_dir = output_dir

    def set_output_filename(self, prefix):
        if self.troubleshoot:
            self.dithername_output()
            self.output_filename = (f'{prefix}_{self.fps}fps_divby{self.scalediv}_'
                                    f'{self.max_colours}max_{self.dithername}_'
                                    f'{self.stats_mode}_{self.diff_mode}.gif')
        else:
            self.output_filename = self.prefix # Need to decide on output name overwrite etc

    def concatenate_singlefile(self):
        self.set_output_filename(self.prefix)
        self.ff_cmdstr = (f'ffmpeg -i {self.input_file} ' 
                          f'-vf "fps={self.fps},scale=iw/{self.scalediv}:ih/{self.scalediv}:flags=lanczos,'
                          f'split[s0][s1];'
                          f'[s0]palettegen=max_colors={self.max_colours}:stats_mode={self.stats_mode}[p];'
                          f'[s1][p]paletteuse=dither={self.dither_method}:diff_mode={self.diff_mode}" '
                          f'-loop {self.loops} '
                          f'{self.output_dir}/{self.output_filename} -y')
        print(f'string = {self.ff_cmdstr}')
        pass

    def concetenate_wholedir(self):
        pass

    def concatenate_cmdstr(self):
        # add if to choose single or directory
        self.concatenate_singlefile()
        
        pass

    def run_ffmpeg_cmdstr(self):
        self.concatenate_cmdstr()
        os.system(self.ff_cmdstr)
        print(f'generating gif')
        pass

    def dithername_output(self):
        if self.dither_method.startswith('bayer:bayer_scale='):
            scale = self.dither_method.split('=')[1]
            self.dithername = (f'bayer{scale}')
        else:
            self.dithername = self.dither_method

class Control: 
    def __init__(self, view, model):
        self.view = view
        self.model = model

    def find_file_location(self):
        model.set_input_file()
        print(f'the input file is located at {model.input_file}')
        pass

    def set_save_location(self):
        model.set_output_dir()
        print(f'the output directory is located at {model.output_dir}')
        pass

    def generate_gif(self):
        model.run_ffmpeg_cmdstr()
        pass

    

class View(ui.CTk): # display and pass to controller only
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
        self.fps_input.insert(0,'30') # will need to change this when preferences are saved/called

        # scale
        self.scale_area = self.area(300,50,0,60,self)
        self.scale_text  = self.menu_text("Scale:",20,12,self.scale_area)
        self.scale_dd = self.drop_down(125,35,155,7.5, self.control.model.scale_list, self.scale_area)

        # max colours
        self.max_area = self.area(300,50,0,110,self)
        self.max_text  = self.menu_text("Max colours:",20,12,self.max_area)
        self.max_dd = self.drop_down(125,35,155,7.5, self.control.model.colours_list, self.max_area)

        # dither method
        self.dith_area = self.area(300,50,0,160,self)
        self.dith_text  = self.menu_text("Dither method:",20,12,self.dith_area)
        self.dith_dd = self.drop_down(125,35,155,7.5, self.control.model.dither_method_list, self.dith_area)

        # optimize preference
        self.opt_area = self.area(300,50,0,210,self)
        self.opt_text  = self.menu_text("Optimize for:",20,12,self.opt_area)
        self.opt_dd = self.drop_down(125,35,155,7.5, self.control.model.optimize_list, self.opt_area)

        # loop preference
        self.loop_area = self.area(300,50,0,260,self)
        self.loop_text  = self.menu_text("Loop:",20,12,self.loop_area)
        self.loop_dd = self.drop_down(125,35,155,7.5, self.control.model.loop_list, self.loop_area)

        # file input
        self.input_text = self.menu_text("Select input:",20,320,self)
        self.input_text.configure(font = ('Roboto Bold', 16))
        self.input_area = self.area(300, 60, 0, 350, self)
        self.single_file_btn = self.btn(125,40,"Single File",20,10, self.control.find_file_location ,self.input_area)
        self.folder_btn = self.btn(125,40,"Folder",155,10,None,self.input_area)

        # Set output
        self.output_text = self.menu_text("Select save location:",20,415,self)
        self.output_text.configure(font = ('Roboto Bold', 16))
        self.output_area = self.area(600, 500, 0, 440, self)
        self.output_input = self.input(260, 35, 20, 10, self.output_area)
        self.output_btn = self.btn(260, 40, "Set Output Folder", 20, 55, self.control.set_save_location, self.output_area)
        self.makegif_btn = self.btn(260, 80, "Generate Gif(s)!", 20, 115, self.control.generate_gif, self.output_area)

        self.overviewlabel = self.menu_text("Show Overview ◨", 170, 203, self.output_area)
        self.overviewlabel.configure(font=('Roboto', 14), text_color="#7D7D7D", cursor="hand2")
        self.overviewlabel.bind("<Button-1>", self.overview_toggle)
        

    def btn(self, set_width, set_height, set_text, set_x, set_y,set_command,set_root):
        button = ui.CTkButton(set_root, 
                              width=set_width, 
                              height= set_height, 
                              text=set_text, 
                              text_color='#000000',
                              font=("Roboto Bold", 16),
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
                            # width=set_width,
                            # height=set_height,
                            text=menu_text,
                            font=("Roboto", 16))
        label.place(x=set_x,y=set_y)
        return label
    
    def drop_down(self, set_width, set_height, set_x, set_y, opt_list, set_root):
        menu = ui.CTkOptionMenu(set_root, 
                                 width = set_width, 
                                 height = set_height,
                                 values = [str(item) for item in opt_list],
                                 font=("Roboto Bold", 16),
                                 text_color="#000000",
                                 dynamic_resizing=False)
        menu.place(x=set_x, y=set_y)
        return menu
    
    def overview_toggle(self, event):
        current = self.geometry().split("+")[0]
        if current == "300x675":
            self.geometry("600x675")
            self.overviewlabel.configure(text='Hide Overview ◧')
            self.overviewlabel.place(x=475, y=203)
        else:
            self.geometry("300x675")
            self.overviewlabel.configure(text='Show Overview ◨')
            self.overviewlabel.place(x=170, y=203)

                    
model = Model()
control = Control(None, model) 
view = View(control)             
control.view = view              

view.mainloop()