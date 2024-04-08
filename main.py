from fastapi import FastAPI
from pydantic import BaseModel
from fastapi import FastAPI,Body
from helper import checkIfMineExist, read_map,map_to_mine_models,Mine
from helper import delete_a_mine,create_mine,update_mine
from helper import read_rovers_from_file,find_rover,create_rover,delete_rover,give_commands,start_rover,RoverReq


class Input(BaseModel):
    text: str

# Define the app
app = FastAPI(
    title="MyApp",
    description="Hello API developer!",
    version="0.1.0"
)

# Define a GET operation
@app.get("/")
async def main():
    return {"message": "Hello World"}

# Define a POST operation
@app.post("/submit")
async def submit(input: Input):
    return {"message": f"Data submitted is: {input.text}"}

# Map Requests -----------------------------------------------------------------
@app.get("/map")
async def get_map():
    # To retrieve the 2D array of the field.

    map = read_map("map.txt")
    
    print(map)
    
    return map

@app.put("/map")
async def put_map(h:int,w:int):
    # To update the height and width of the field
    array = read_map("map.txt")
    old_height = len(array)
    old_width = len(array[0]) if old_height > 0 else 0

    # Initialize new array with None
    new_array = [["0" for _ in range(w)] for _ in range(h)]

    # Copy old data into new array
    for i in range(min(old_height, h)):
        for j in range(min(old_width, w)):
            new_array[i][j] = array[i][j]
    
    # Write new_array to a new file
    with open("new_map_with_updated_values.txt", "w") as f:
        for row in new_array:
            f.write(" ".join(row) + "\n")
    
    return new_array
   
    


# Mines Requests -----------------------------------------------------------------
@app.get("/mines")
def get_map():
    
    serial_map = read_map("mines.txt")
    
    print("Printing the serial numbers from the serial map")
    print(serial_map)
    
    print("Printing the JSON of format of the serial and coordinates")
    mineAndCoordinateModel = map_to_mine_models(serial_map)
    print(mineAndCoordinateModel)
    
    return mineAndCoordinateModel

@app.get("/mines/{id}")
def modify_map(id:str):

    return checkIfMineExist(read_map("mines.txt"),id)

@app.delete("/mines/{id}")
def modify_map(id:str):
    #To delete a mine with the “:id”
    return delete_a_mine(read_map("mines.txt"),id)

@app.post("/mines")
def get_map(mine:Mine= Body(...)):
    print(mine)

    return create_mine(mine.serial,mine.x,mine.y)

@app.put("/mines/{id}")
def modify_map(id:str,serial:str=None,x:int=None,y:int=None):
    return update_mine(id,serial,x,y)

# Rover Requests -----------------------------------------------------------------


@app.get("/rovers")
def get_rovers():
    
    return read_rovers_from_file("rovers.json")


# Endpoint to retrieve details of a specific rover
@app.get("/rovers/{rover_id}")
def get_rover(rover_id: str):
    # Logic to retrieve details of a specific rover
    return find_rover(rover_id)

# Endpoint to create a new rover
@app.post("/rovers")
def create_rvr(rover:RoverReq= Body(...)):
    # Logic to create a new rover with commands
    #print(rover)
    return create_rover(rover.commands)

# Endpoint to delete a rover
@app.delete("/rovers/{rover_id}")
def delete_rvr(rover_id: str):
    # Logic to delete a specific rover
    return delete_rover(rover_id)

# Endpoint to send a list of commands to a rover
@app.put("/rovers/{rover_id}")
def send_commands(rover_id: str, commands: str):
    # Logic to send commands to a specific rover
    return give_commands(rover_id,commands)

@app.post("/rovers/{rover_id}/dispatch")
def dispatch_rover(rover_id: str):

    return start_rover(rover_id=rover_id)
