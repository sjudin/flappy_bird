import cx_Freeze, os

os.environ['TCL_LIBRARY'] = r'C:\Users\Jakob\AppData\Local\Programs\Python\Python35\tcl\tcl8.6'
os.environ['TK_LIBRARY'] = r'C:\Users\Jakob\AppData\Local\Programs\Python\Python35\tcl\tk8.6'

executables =  [cx_Freeze.Executable("Game.py")]

cx_Freeze.setup(
    name="Flappy Bird",
    options= {"build_exe": 
                {"packages": ["pygame", "sys", "random", "time"],
                "include_files": ["assets/background.png" , "E:\python_projects\\flappy_bird\\assets\ARCADE.TTF", "assets/bird.png", "assets/death.wav", "assets/game_over.png", "assets/jump.wav", "assets/pipe_long.png", "assets/pipe_top.png", "assets/pipe.png", "assets/score.wav"]}},
    executables = executables
)