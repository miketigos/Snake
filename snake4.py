"""
Module: Snake
Author: Michael Thomas

A Python implementation of Snake
"""
from tkinter import HORIZONTAL
import random
import tkinter as tk
from tkinter.font import Font
from enum import Enum
import time


class Snake:
    """ This is the controller """
    def __init__(self):
        """ Initializes the snake game """
        self.NUM_ROWS = 20
        self.NUM_COLS = 20
        self.game_loop = None
        self.timer = None
        # instantiate view
        self.the_view = SnakeView(self.NUM_ROWS, self.NUM_COLS)
        # instantiate the model
        self.the_model = SnakeModel(self.NUM_ROWS, self.NUM_COLS)
        # set button handlers
        self.the_view.set_start_btn_handler(self.start_btn_handler)
        self.the_view.set_pause_btn_handler(self.pause_btn_handler)
        self.the_view.set_reset_btn_handler(self.reset_btn_handler)
        self.the_view.set_quit_btn_handler(self.quit_btn_handler)
        # set key-press handlers
        self.the_view.set_up_arrow_handler(self.up_arrow_handler)
        self.the_view.set_right_arrow_handler(self.right_arrow_handler)
        self.the_view.set_down_arrow_handler(self.down_arrow_handler)
        self.the_view.set_left_arrow_handler(self.left_arrow_handler)
        # start main loop
        self.update_view()
        self.the_view.window.mainloop()

    def update_view(self):
        # testing

        self.the_view.make_all_open()
        if self.the_model.snake[0] == self.the_model.food_location:
            self.the_model.grow_snake()
            self.the_view.points_var.set(self.the_model.cur_points)
            self.the_model.move_food()

        self.the_view.add_food(self.the_model.food_location[0],
                                self.the_model.food_location[1])
        snakehead = self.the_model.snake[0]
        snakebody = self.the_model.snake[1:]
        self.the_view.add_snakehead(snakehead[0], snakehead[1])

        for segment in snakebody:
            self.the_view.add_snakebody(segment[0], segment[1])    

    def play_game(self):
        self.the_model.move_snake()
        game_speed = self.the_view.game_speed_slider.get()
        self.game_loop = self.the_view.start_btn.after(1000//game_speed, self.play_game)
        if self.the_model.has_collided() or self.the_model.is_out_of_bounds():
            self.the_view.gameover_var.set("GAME OVER")
            self.the_view.start_btn.after_cancel(self.game_loop)
            self.the_view.start_btn.after_cancel(self.timer)
            self.the_view.make_all_open()
        else:
            self.update_view()

    def time_handler(self):
        self.the_model.time_elapsed = time.time() - self.the_model.timer_start
        self.the_view.time_var.set(round(self.the_model.time_elapsed, 1))
        self.the_view.pps_var.set(self.the_model.cur_points // self.the_model.time_elapsed)
        self.timer = self.the_view.start_btn.after(10, self.time_handler)

    # button handlers
    def start_btn_handler(self):
        if not self.the_model.timer_running:
            self.the_model.timer_start = time.time() - self.the_model.time_elapsed
            self.the_model.timer_running = 1
            self.time_handler()
        self.play_game()

    def pause_btn_handler(self):
        self.the_view.start_btn.after_cancel(self.timer)
        self.the_model.timer_running = 0
        self.the_view.start_btn.after_cancel(self.game_loop)
       
    def reset_btn_handler(self):
        self.the_view.game_speed_slider.set(1)
        self.the_view.start_btn.after_cancel(self.game_loop)
        self.the_view.start_btn.after_cancel(self.timer)
        self.the_model.time_elapsed = 0.0
        self.the_view.make_all_open()
        self.the_view.points_var.set(0)
        self.the_view.gameover_var.set("")
        self.the_view.time_var.set(0.0)
        self.the_view.pps_var.set(0.0)
        self.the_model.reset()
        self.update_view()
        self.update_time()

    def quit_btn_handler(self):
        self.the_view.window.destroy()        

    # key-press handlers
    def up_arrow_handler(self, event):
        self.the_model.set_direction(Direction.UP)
        
    def right_arrow_handler(self, event):
        self.the_model.set_direction(Direction.RIGHT)

    def down_arrow_handler(self, event):
        self.the_model.set_direction(Direction.DOWN)

    def left_arrow_handler(self, event):
        self.the_model.set_direction(Direction.LEFT)


class SnakeView:

    def __init__(self, num_rows, num_cols):
        """ Initialize view of the game """
        self.CELL_SIZE = 20
        self.CONTROL_FRAME_HEIGHT = 100
        self.SCORE_FRAME_WIDTH = 200
        self.WIDGET_PADDING = 15

        self.num_rows = num_rows
        self.num_cols = num_cols

        self.window = tk.Tk()
        self.window.title("Greedy Snake")
        # create frames for game
        self.grid_frame = tk.Frame(self.window, 
                                   height = self.num_rows * self.CELL_SIZE, 
                                   width = self.num_cols * self.CELL_SIZE)
        self.grid_frame.grid(row=0, column=0)
        self.cells = self.add_cells(num_rows, num_cols)

        self.score_frame = tk.Frame(self.window, 
                                    height = self.num_rows * self.CELL_SIZE, 
                                    width = self.SCORE_FRAME_WIDTH)
        self.score_frame.grid(row=0, column=1)
        self.add_score()

        self.control_frame = tk.Frame(self.window, 
                                      height = self.CONTROL_FRAME_HEIGHT,
                                      width = 600)
        self.control_frame.grid(row=1, columnspan=2)
        self.add_controls()

    # helper methods to build game layout
    def add_cells(self, num_rows, num_cols):

        cells = []
        for r in range(num_rows):
            row = []
            for c in range(num_cols):
                cell = tk.Frame(self.grid_frame, width = self.CELL_SIZE, 
                                height = self.CELL_SIZE, borderwidth=1, relief="solid") 
                cell.grid(row=r, column=c)
                row.append(cell)
            cells.append(row)    
        return cells

    def add_controls(self):
        self.start_btn = tk.Button(self.control_frame, text="Start")
        self.start_btn.grid(row=0, column=0, padx=self.WIDGET_PADDING, 
                            pady=self.WIDGET_PADDING)
        self.pause_btn = tk.Button(self.control_frame, text="Pause")
        self.pause_btn.grid(row=0, column=1, padx=self.WIDGET_PADDING, 
                            pady=self.WIDGET_PADDING)
        self.game_speed_slider = tk.Scale(self.control_frame, 
                                          from_=1, to=5,
                                          tickinterval=1, 
                                          orient=HORIZONTAL)
        self.game_speed_slider.set(0)                                  
        self.game_speed_slider.grid(row=0, column=2, 
                                    padx=self.WIDGET_PADDING, 
                                    pady=self.WIDGET_PADDING)

        self.reset_btn = tk.Button(self.control_frame, text="Reset")
        self.reset_btn.grid(row=0, column=3, 
                            padx=self.WIDGET_PADDING, 
                            pady=self.WIDGET_PADDING)
        self.quit_btn = tk.Button(self.control_frame, text="Quit")
        self.quit_btn.grid(row=0, column=4, 
                           padx=self.WIDGET_PADDING, 
                           pady=self.WIDGET_PADDING)

        self.wraparound_checkbtn = tk.Checkbutton(self.control_frame, text="Wraparound")
        self.wraparound_checkbtn.grid(row=0, column=5,
                                      padx=self.WIDGET_PADDING,
                                      pady=self.WIDGET_PADDING)

        self.control_frame.grid_columnconfigure(1, weight=1)
        self.control_frame.grid_rowconfigure(1, weight=1)

    def add_score(self):

        self.score_lbl = tk.Label(self.score_frame, text="Score", font=("Courier", 16))
        self.score_lbl.grid(row=0, column=0,
                            padx=self.WIDGET_PADDING,
                            pady=self.WIDGET_PADDING)
        
        self.points_lbl = tk.Label(self.score_frame, text="Points:")
        self.points_lbl.grid(row=1, column=0,
                             padx=self.WIDGET_PADDING,
                             pady=self.WIDGET_PADDING)
        self.points_var = tk.IntVar()
        self.points = tk.Label(self.score_frame, textvariable=self.points_var)
        self.points.grid(row=1, column=1,
                         padx=self.WIDGET_PADDING,
                         pady=self.WIDGET_PADDING)

        self.time_lbl = tk.Label(self.score_frame, text="Time:")
        self.time_lbl.grid(row=2, column=0,
                           padx=self.WIDGET_PADDING,
                           pady=self.WIDGET_PADDING)
        self.time_var = tk.DoubleVar()
        self.time = tk.Label(self.score_frame, textvariable=self.time_var)
        self.time.grid(row=2, column=1,
                       padx=self.WIDGET_PADDING,
                       pady=self.WIDGET_PADDING)

        self.pps_lbl = tk.Label(self.score_frame, text="Points / sec:")
        self.pps_lbl.grid(row=3, column=0, 
                          padx=self.WIDGET_PADDING,
                          pady=self.WIDGET_PADDING)
        self.pps_var = tk.DoubleVar()
        self.pps = tk.Label(self.score_frame, textvariable=self.pps_var)
        self.pps.grid(row=3, column=1,
                      padx=self.WIDGET_PADDING,
                      pady=self.WIDGET_PADDING)

        self.gameover_var = tk.StringVar()
        self.gameover_lbl = tk.Label(self.score_frame, textvariable=self.gameover_var)  
        self.gameover_lbl.grid(row=4, column=0)            

    # helper methods for building snake
    def add_snakehead(self, row, col):
        self.cells[row][col]["bg"] = "blue"

    def add_snakebody(self, row, col):
        self.cells[row][col]["bg"] = "black"

    def add_food(self, row, col):
        self.cells[row][col]["bg"] = "red"
    
    def make_all_open(self):
        for i in range(self.num_rows):
            for j in range(self.num_rows):
                self.cells[i][j]['bg'] = 'white'
    
    # methods to bind/handle button events
    def set_start_btn_handler(self, handler):
        self.start_btn.configure(command=handler)

    def set_pause_btn_handler(self, handler):
        self.pause_btn.configure(command=handler)

    def set_reset_btn_handler(self, handler):
        self.reset_btn.configure(command=handler)

    def set_quit_btn_handler(self, handler):
        self.quit_btn.configure(command=handler)   

    # methods to bind/handle key events
    def set_up_arrow_handler(self, handler):
        self.window.bind("<Up>", handler)

    def set_right_arrow_handler(self, handler):
        self.window.bind("<Right>", handler)

    def set_down_arrow_handler(self, handler):
        self.window.bind("<Down>", handler)

    def set_left_arrow_handler(self, handler):
        self.window.bind("<Left>", handler)            


class SnakeModel:
    def __init__(self, num_rows, num_cols):
        """ initialize the model of the game """
        self.num_rows = num_rows
        self.num_cols = num_cols

        self.food_location = None
        self.cur_direction = None
        self.cur_points = 0
        self.empty_cells = None
        self.snake = None
        self.add_body_segment_location = None

        self.timer_running = 0
        self.timer_start = 0.0
        self.time_elapsed = 0.0

        self.reset()

    def reset(self):
        self.timer_running = 0
        self.timer_start = time.time()
        self.time_elapsed = 0.0
        self.cur_points = 0
        self.empty_cells = [(i,j) for i in range(self.num_rows)
                            for j in range(self.num_cols)]
        self.move_food()   
        self.empty_cells.remove(self.food_location)    
        snakehead = random.choice(self.empty_cells) # tuple coordinates (i,j)
        self.empty_cells.remove(snakehead)
        self.snake = [snakehead] # array of coordinate tuples  
        # assign direction to start, default is up
        self.cur_direction = Direction.UP 
    
    def move_food(self):
        old_food_location = self.food_location
        self.food_location = random.choice(self.empty_cells)
        self.empty_cells.append(old_food_location)

    def grow_snake(self):
        self.snake.append(self.add_body_segment_location)
        self.cur_points += 100

    def move_snake(self):
        if self.cur_direction == Direction.UP:
            self.snake.insert(0, (self.snake[0][0]-1, self.snake[0][1]))
        if self.cur_direction == Direction.RIGHT:
            self.snake.insert(0, (self.snake[0][0], self.snake[0][1]+1))
        if self.cur_direction == Direction.DOWN:
            self.snake.insert(0, (self.snake[0][0]+1, self.snake[0][1]))
        if self.cur_direction == Direction.LEFT:
            self.snake.insert(0, (self.snake[0][0], self.snake[0][1]-1))
        self.add_body_segment_location = self.snake.pop()

    def is_out_of_bounds(self):
        if self.snake[0][0] < 0 or self.snake[0][0] > self.num_rows-1 \
           or self.snake[0][1] < 0 or self.snake[0][1] > self.num_cols-1:
            return True
        return False    

    def has_collided(self):
        for segment in self.snake[1:]:
            if self.snake[0] == segment:
                return True     
        return False

    def set_direction(self, direction):
        self.cur_direction = direction  
            

class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4


if __name__ == "__main__":
   snake_game = Snake()