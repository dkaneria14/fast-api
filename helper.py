from pydantic import BaseModel
import random
import string
import hashlib as h
import json

class Mine(BaseModel):
    serial: str = None
    x: int = None
    y: int = None

class Rover(BaseModel):
    rover_id: str
    commands: str
    status: str

class RoverReq(BaseModel):
    commands:str

def read_map(filename):

    # Read in the array
    with open(filename, 'r') as f:
        # Skip the first line, we don't need it
        #next(f)
        land_map = [line.split() for line in f]

    return land_map

def write_map(path_map: list[list[str]], file_name: str):
    with open(file_name, "w") as file:
        for row in path_map:
            file.write(' '.join(map(str, row)) + '\n')

def write_rovers_to_file(rovers: list[Rover], filename: str) -> None:
  # Convert the list of rovers to a JSON serializable list
    rover_data = [rover.model_dump() for rover in rovers]

    with open(filename, "w") as f:
        json.dump(rover_data, f, indent=4)  # Write with indentation for readability

def read_rovers_from_file(filename: str) -> list[Rover]:
    try:
        with open(filename, "r") as f:
            rover_data = json.load(f)
    except FileNotFoundError:
        print(f"File '{filename}' not found. Returning an empty list.")
        return []

    # Convert the list of dictionaries back to Rover objects
    rovers = [Rover(**data) for data in rover_data]  # Unpack data into Rover objects
    return rovers


def generate_serial_number():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))


def generate_pin():
    return ''.join(random.choices(string.digits + string.digits, k=10))


def hash_key(key: str):
    return h.sha256(key.encode('utf-8')).hexdigest()

def map_to_mine_models(array):
    mine_models = []

    # Iterate over each cell in the array
    for i in range(len(array)):
        for j in range(len(array[i])):

            # If the cell contains a 6 digit code, it's a mine
            if isinstance(array[i][j], str) and len(array[i][j]) == 6:

                # Create a new Mine model with the code and coordinates
                mine = Mine(serial=array[i][j], x=i, y=j)

                # Add the new Mine model to the list
                mine_models.append(mine)


    return mine_models

def checkIfMineExist(array,serial_id):
    for i in range(len(array)):
        for j in range(len(array[i])):

            if array[i][j]==serial_id:
                return Mine(serial=array[i][j], x=i, y=j)
    
    return Mine(serial="Not found", x = 0, y = 0)

                
def delete_a_mine(array,serial_id):

    land_map = read_map("map.txt")

    for i in range(len(array)):
        for j in range(len(array[i])):

            if array[i][j]==serial_id:
                # Deleting a mine
                array[i][j]=0
                land_map[i][j]=0
                # Write out to map files
                write_map(array,"mines.txt")
                write_map(land_map, "map.txt")
                # Need a response
                return "Deleted Mine"
    return "Not found"

def create_mine(serial_id,x,y):
    land_map = read_map("map.txt")
    
    land_map[x][y] = "1"
    write_map(land_map,"map.txt")
    
    serial_map = read_map("mines.txt")
    serial_map[x][y] = serial_id
    write_map(serial_map,"mines.txt")

    return serial_id

def update_mine(serial:str,new_serial:str=None,x:int=None,y:int=None):
    serial_map = read_map("mines.txt")
    land_map = read_map("map.txt")
    new_mine= Mine() 
     # Iterate through the serial_map
    for row_index, row in enumerate(serial_map):
        for col_index, map_serial in enumerate(row):
            if map_serial == serial:
                # Found a matching entry

                # Update serial if provided
                if new_serial is not None:
                    serial_map[row_index][col_index] = new_serial
                    new_mine.serial = new_serial

                # Update coordinates if provided
                if x is not None:
                # Ensure new X-coordinate is within valid bounds (avoiding IndexError)
                    if 0 <= x < len(serial_map[0]):
                        serial_map[row_index][col_index] = (new_serial if new_serial else map_serial, x)  # Update with (serial, x)
                        land_map[row_index][col_index] = 1
                        new_mine.x = x
                    else:
                        print(f"Invalid X-coordinate: {x}. Entry remains at ({row_index}, {col_index})")

                if y is not None:
                    # Ensure new Y-coordinate is within valid bounds
                    if 0 <= y < len(serial_map):
                        serial_map[row_index][col_index] = (new_serial if new_serial else map_serial, y)  # Update with (serial, y)
                        land_map[row_index][col_index] = 1
                        new_mine.y = y
                    else:
                        print(f"Invalid Y-coordinate: {y}. Entry remains at ({row_index}, {col_index})")
                
                write_map(serial_map,"mines.txt")
                write_map(land_map,"map.txt")
                return new_mine# Update successful

    # Entry not found
    print(f"Serial '{serial}' not found in the map.")
    return False
    
    
def find_rover(rover_id:str):
    rover_list = read_rovers_from_file("rovers.json")
    
    for rover in rover_list:
        if rover.rover_id == rover_id:
            return rover  # Return the rover object if ID matches

    return None  # Rover not found

def create_rover(commands:str):
    rover_list = read_rovers_from_file("rovers.json")
    
    new_id = int(rover_list[-1].rover_id)+1
    new_rover = Rover(rover_id=str(new_id),commands=commands,status="Not started")
    
    rover_list.append(new_rover)
    write_rovers_to_file(rovers=rover_list,filename="rovers.json")
    return int(new_rover.rover_id)

def delete_rover(rover_id:str):
    rover_list = read_rovers_from_file("rovers.json")
    
    for rover in rover_list:
        if rover.rover_id == rover_id:
            rover_list.remove(rover)
            write_rovers_to_file(rovers=rover_list,filename="rovers.json")
            return "Deleted Rover"
        
    return "Could not find Rover"

def give_commands(rover_id: str, commands: str):
    rover_list = read_rovers_from_file("rovers.json")

    for rover in rover_list:
        if rover.rover_id == rover_id:
            if rover.status == "Not started" or rover.status == "Finished":
                rover.commands = commands
                write_rovers_to_file(rover_list,"rovers.json")
                return "New Commands given"
    
    return "Failure to give new commands"


# Rover helper methods ---------------------------------------------------------------------------------------------------
def check_boundary(current_dir, x, y, x_border, y_border):
    # Hash map with direction and their boundary condition
    boundaries = {'S': (y + 1 < y_border), 'N': (y - 1 >= 0), 'E': (x + 1 < x_border), 'W': (x - 1 >= 0)}
    # Using the current_dir as a key I return whether the boundary passes or fails (T or F)
    return boundaries.get(current_dir, False)


def disarm_mine(serial_map: list[list[str]], y: int, x: int):
    # make the key
    key = generate_pin() + serial_map[y][x]
    # Hash the key
    hk = hash_key(key)
    while hk[:2] != '00':
        hk = hash_key(key)
        print(f"Attempting with {hk}")
        key = generate_pin() + serial_map[y][x]


def change_direction(dir_facing: str, turn: str):
    directions = ['N', 'E', 'S', 'W']
    index = directions.index(dir_facing)
    # make use of pythons negative indexing :)
    new_idx = (index + 1) % 4 if turn == 'R' else (index - 1) % 4

    return directions[new_idx]

def update_rover_list(rover:Rover):
    rover_list = read_rovers_from_file("rovers.json")
    
    for r in rover_list:
        if r.rover_id == rover.rover_id:
            r.status = rover.status
            write_rovers_to_file(rovers=rover_list,filename="rovers.json")
            return 
    
    

                
def start_rover(rover_id:str):
    
    land_map = read_map("map.txt")
    serial_map = read_map("mines.txt")
    print(f"Rover ID: {rover_id}")
    rover = find_rover(rover_id)
    
    if rover == None:
        return "Failure to find the Rover"
    
    rover.status = "Roaming Maze"
    update_rover_list(rover=rover)
     # Execute the Moves
    y, x = 0, 0
    current_dir = 'S'

    print(f"Rover: {rover.rover_id}")
    
    for m in rover.commands:
        # disarming the mine
        if land_map[y][x] == '1' and m == 'D':
            disarm_mine(serial_map, y, x)
            land_map[y][x] = "#"

        elif m == 'M' and check_boundary(current_dir, x, y, len(land_map[y]), len(land_map)):
            # check if I can actually move off the mine
            if land_map[y][x] == '1':
                land_map[y][x] = "x"
                print("You died!!")
                rover.status = "Finished"
                update_rover_list(rover=rover)
                break
            else:
                # CHANGE POSITIONS
                if land_map[y][x] != '#':
                    land_map[y][x] = "*"
    
                # Hash map has a tuple containing the directional move in terms of a 2D array
                directions = {'S': (0, 1), 'N': (0, -1), 'E': (1, 0), 'W': (-1, 0)}

                dx, dy = directions[current_dir]

                x = min(max(x + dx, 0), len(land_map[0]) - 1)
                y = min(max(y + dy, 0), len(land_map) - 1)

        # change direction
        elif m == 'R' or m == 'L':
            current_dir = change_direction(current_dir, m)
    
    rover.status = "Finished"
    update_rover_list(rover=rover)
    
    for row in land_map:
        print(f"Row: {row}")
        
    
    return land_map