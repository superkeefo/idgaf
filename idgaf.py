import os
from os.path import join
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
        stats_mode = ['full','diff']              # 0,1
        diff_mode = ['rectangle','none']          # 0,1
        colours = [32,64,128,256]                 # 0,1,2,3
        dither_method = ['bayer:bayer_scale=1',   #0 high quality bayer
                         'bayer:bayer_scale=2',   #1
                         'bayer:bayer_scale=3',   #2
                         'bayer:bayer_scale=4',   #3
                         'bayer:bayer_scale=5',   #4 low quality bayer
                         'sierra2',               #5
                         'floyd_steinberg',       #6
                         'sierra2_4a',            #7 Highest size
                         'none']                  #8 ugly
        

        ### GIF SETTINGS ###
        self.fps = 8
        self.scalediv = 2
        self.max_colours = colours[1]
        self.dither_method = dither_method[8]
        self.stats_mode = stats_mode[1]
        self.diff_mode = diff_mode[0]
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
        self.geometry("260x250")
        self.title("I don't gif a f***")
        # self.iconbitmap(os.path.join('icons','punch.ico'))
        self.resizable(False, False)
        self.find_btn = self.btn(200, 50, "find file", 30, 30, 
                                 self.control.find_file_location)
        self.save_btn = self.btn(200, 50, "Set save Location", 30, 100, 
                                 self.control.set_save_location)
        self.gen_btn = self.btn(200, 50, "Generate gif", 30, 170, 
                                self.control.generate_gif)
        

    def btn(self, set_width, set_height, set_text, set_x, set_y,set_command,):
        button = ui.CTkButton(self, 
                              width=set_width, 
                              height= set_height, 
                              text=set_text, 
                              text_color='#000000',
                              command=set_command)
        button.place(x=set_x, y=set_y)
        return button
        
model = Model()
control = Control(None, model) 
view = View(control)             
control.view = view              

view.mainloop()