import pygame
import time
from queue import PriorityQueue

# Constants for screen and grid setup
WIDTH = 600  # Width of the display window
ROWS = 30  # Number of rows/columns in the grid
WIN = pygame.display.set_mode((WIDTH, WIDTH))  # Create a square display window
pygame.display.set_caption("Connect Colors Game with A* Pathfinding")  # Set the window title

# Color definitions (RGB values)
WHITE = (255, 255, 255)  # Default node color
BLACK = (0, 0, 0)  # Barrier color
GREY = (128, 128, 128)  # Grid lines color
COLORS = [
    (255, 0, 0),  # Red
    (0, 255, 0),  # Green
    (0, 0, 255),  # Blue
    (255, 165, 0),  # Orange
    (128, 0, 128),  # Purple
    (255, 255, 0),  # Yellow
]

# Node class to represent each cell in the grid
class Node:
    def __init__(self, row, col, width, total_rows):
        # Initialize node properties
        self.row = row  # Row index of the node
        self.col = col  # Column index of the node
        self.x = row * width  # Pixel x-coordinate of the node
        self.y = col * width  # Pixel y-coordinate of the node
        self.color = WHITE  # Initial color of the node
        self.width = width  # Width of the node
        self.total_rows = total_rows  # Total number of rows/columns in the grid
        self.neighbors = []  # List to store neighboring nodes

    def get_pos(self):
        # Returns the position of the node as (row, col)
        return self.row, self.col

    def is_barrier(self):
        # Checks if the node is a barrier
        return self.color == BLACK

    def is_empty(self):
        # Checks if the node is empty (white)
        return self.color == WHITE

    def reset(self):
        # Resets the node's color to white
        self.color = WHITE

    def make_barrier(self):
        # Sets the node's color to black, marking it as a barrier
        self.color = BLACK

    def make_color(self, color):
        # Sets the node's color to a specific color
        self.color = color

    def draw(self, win):
        # Draws the node as a rectangle on the display window
        pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

    def update_neighbors(self, grid):
        # Updates the list of neighbors for the node
        self.neighbors = []
        # Check and add non-barrier neighbors in the cardinal directions
        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # Down
            self.neighbors.append(grid[self.row + 1][self.col])
        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # Up
            self.neighbors.append(grid[self.row - 1][self.col])
        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # Right
            self.neighbors.append(grid[self.row][self.col + 1])
        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # Left
            self.neighbors.append(grid[self.row][self.col - 1])

# Heuristic function for A* pathfinding using Chebyshev distance
def chebyshev(p1, p2):
    # Returns the Chebyshev distance between two points
    x1, y1 = p1
    x2, y2 = p2
    return max(abs(x1 - x2), abs(y1 - y2))

# A* Pathfinding algorithm
def a_star(draw, grid, start, end, color, used_nodes):
    # Initialize the open set and scores for A*
    count = 0  # Used for tie-breaking in the priority queue
    open_set = PriorityQueue()  # Priority queue for the open set
    open_set.put((0, count, start))  # Add the starting node to the open set
    came_from = {}  # Dictionary to track the path
    g_score = {node: float("inf") for row in grid for node in row}  # Movement cost from start
    g_score[start] = 0
    f_score = {node: float("inf") for row in grid for node in row}  # Estimated total cost
    f_score[start] = chebyshev(start.get_pos(), end.get_pos())

    open_set_hash = {start}  # Set for quick lookup of nodes in the open set

    while not open_set.empty():
        # Get the node with the lowest f_score
        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            # If the end node is reached, reconstruct the path
            reconstruct_path(came_from, end, draw, color, used_nodes)
            return True

        for neighbor in current.neighbors:
            if neighbor in used_nodes and neighbor.color != color:
                # Skip nodes already used by another color's path
                continue

            temp_g_score = g_score[current] + 1  # Tentative g_score

            if temp_g_score < g_score[neighbor]:
                # Update path and scores if a better path is found
                came_from[neighbor] = current
                g_score[neighbor] = temp_g_score
                f_score[neighbor] = temp_g_score + chebyshev(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((f_score[neighbor], count, neighbor))
                    open_set_hash.add(neighbor)

        draw()  # Redraw the grid after each step

    print(f"Failed to connect: Start {start.get_pos()} -> End {end.get_pos()} for color {color}")
    return False  # Return failure if no path is found

# Reconstructs the path from the came_from dictionary
def reconstruct_path(came_from, current, draw, color, used_nodes):
    while current in came_from:
        # Move backward through the path and color nodes
        current = came_from[current]
        current.make_color(color)
        used_nodes.add(current)
        draw()
        time.sleep(0.05)  # Add delay for visualization

# Draws the grid lines on the display window
def draw_grid(win, rows, width):
    gap = width // rows  # Gap between grid lines
    for i in range(rows):
        pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))  # Horizontal lines
        pygame.draw.line(win, GREY, (i * gap, 0), (i * gap, width))  # Vertical lines

# Draws the entire grid (nodes + grid lines)
def draw(win, grid, rows, width):
    for row in grid:
        for node in row:
            node.draw(win)
    draw_grid(win, rows, width)  # Draw grid lines
    pygame.display.update()  # Update the display

# Creates a grid of Node objects
def make_grid(rows, width):
    grid = []
    gap = width // rows  # Width of each node
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            node = Node(i, j, gap, rows)
            grid[i].append(node)
    return grid

# Main function to run the program
def main(win, width):
    grid = make_grid(ROWS, width)  # Create the grid
    pairs = []  # List to store start and end nodes for each color
    used_nodes = set()  # Set to store nodes already used in paths

    run = True
    color_index = 0  # Index for selecting colors

    while run:
        draw(win, grid, ROWS, width)  # Draw the grid

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Check for quit event
                run = False

            if pygame.mouse.get_pressed()[0]:  # Check for left mouse button press
                pos = pygame.mouse.get_pos()
                row, col = pos[0] // (width // ROWS), pos[1] // (width // ROWS)
                node = grid[row][col]

                if len(pairs) < 12 and node.is_empty():  # Allow up to 6 pairs of start and end nodes
                    node.make_color(COLORS[color_index])
                    pairs.append(node)
                    if len(pairs) % 2 == 0:  # Change color after every pair
                        color_index += 1

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and len(pairs) == 12:
                    # Start pathfinding when the spacebar is pressed
                    for row in grid:
                        for node in row:
                            node.update_neighbors(grid)

                    for i in range(0, len(pairs), 2):
                        # Solve for each pair of start and end nodes
                        start, end = pairs[i], pairs[i + 1]
                        color = COLORS[i // 2]
                        if not a_star(lambda: draw(win, grid, ROWS, width), grid, start, end, color, used_nodes):
                            print(f"Failed to connect nodes of color {color}")
                            run = False

                if event.key == pygame.K_c:  # Clear the grid when 'C' is pressed
                    grid = make_grid(ROWS, width)
                    pairs = []
                    used_nodes = set()
                    color_index = 0

    pygame.quit()  # Quit the program

# Run the main function
main(WIN, WIDTH)