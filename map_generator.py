import random 

def create_solid_map(rows, cols):
    grid = [] 
    for r in range(rows):
        row = [] 
        for c in range(cols):
            row.append("1")
        grid.append(row) 
    return grid 

def carve_room(grid, roomTop_x, roomTop_y, room_width, room_height):
    rows = len(grid)
    cols = len(grid[0])

    for r in range(roomTop_y, roomTop_y + room_height):
        for c in range(roomTop_x, roomTop_x + room_width):
            if 0 < r < rows - 1 and 0 < c < cols - 1: # prevents carving outside the map
                grid[r][c] = "0"

def carve_horizontal_tunnel(grid, x1, x2, y):
    for x in range(min(x1, x2), max(x1,x2) + 1):
        if 0 < y < len(grid) - 1 and 0 < x < len(grid[0]) - 1:
            grid[y][x] = "0" 

def carve_vertical_tunnel(grid, y1, y2, x):
    for y in range(min(y1, y2), max(y1, y2) + 1):
        if 0 < y < len(grid) - 1 and 0 < x < len(grid[0]) - 1:
            grid[y][x] = "0"

def room_center(room):
    x, y, w, h = room 
    return (x + w // 2, y + h // 2)

def rooms_overlap(room1, room2, padding=1):
    x1, y1, w1, h1 = room1 
    x2, y2, w2, h2 = room2 

    room1_left = x1 
    room1_right = x1 + w1 
    
    room2_left = x2 
    room2_right = x2 + w2 

    room1_top = y1 
    room1_bottom = y1 + h1 

    room2_top = y2 
    room2_bottom = y2 + h2 

    if room1_left < room2_right + padding and room1_right + padding > room2_left:
        if room1_top < room2_bottom + padding and room1_bottom + padding > room2_top:
            return True 

    return False 


def generate_cave_map(rows=30, cols=40, room_attempts=150, min_size=2, max_size=4):
    # make filled grid 
    grid = create_solid_map(rows, cols)

    # initialize list to store successful rooms created 
    rooms = []

    # attempt to make rooms as many times as specified in room_attempts
    for _ in range(room_attempts):
        room_width = random.randint(min_size, max_size)
        room_height = random.randint(min_size, max_size)
        roomTop_x = random.randint(1, cols - room_width - 2)
        roomTop_y = random.randint(1, rows - room_height - 2)

        # make the new_room tuple 
        new_room = (roomTop_x, roomTop_y, room_width, room_height)

        overlap_found = False 

        for other in rooms: 
            if rooms_overlap(new_room, other, padding=2):
                overlap_found = True
                break 
                
        if overlap_found:
            continue 

        # carve the room 
        carve_room(grid, roomTop_x, roomTop_y, room_width, room_height)
        
        if len(rooms) > 0: 
            prev_cx, prev_cy = room_center(rooms[-1])
            new_cx, new_cy = room_center(new_room)
            
            if random.choice([True, False]):
                carve_horizontal_tunnel(grid, prev_cx, new_cx, prev_cy)
                carve_vertical_tunnel(grid, prev_cy, new_cy, new_cx)
            else:
                carve_vertical_tunnel(grid, prev_cy, new_cy, prev_cx)
                carve_horizontal_tunnel(grid, prev_cx, new_cx, new_cy)

        # add new_room to rooms list 
        rooms.append(new_room)

    # create level_map as multiple strings instead of a 2D list 
    level_map = ["".join(row) for row in grid]
    return level_map, rooms

