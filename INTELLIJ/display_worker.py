
from devicesPython import lcd_setup as dislay
from flask import jsonify

def display(data):
    print(f"Init display with data : {data}")
    lcdScreen = None
    try:
        lcdScreen = dislay.lcd_setup()
    except Exception as e:
        print(f"Error while setting up the display : {e}")
        return False

    #clear the screen :
    lcdScreen.clear()
        #test if scale is in the data :
    if 'scale' not in data or data['scale']<=0:
        scale = 24
    elif data['scale']>72:
        scale = 72
    else:
        scale = data['scale']

    #test if color is in the data :
    if 'color' not in data:
        color = (255, 255, 255)
    else:
        color = tuple(data['color'])

    if 'message' not in data:
        return jsonify({'message': 'error: message is missing'}), 400
    else:
        message = data['message']

    if 'speed' not in data:
        speed = 1
    elif data['speed'] <= 0:
        return jsonify({'message': 'error: speed must be greater than 0'}), 400
    elif isinstance(data['speed'], int) == False:
        return jsonify({'message': 'error: speed must be an Integer'}), 400
    else:
        speed = data['speed']
    #debug all the data :
    
    lcdScreen.print(message, font_size=scale, color=color, x=lcdScreen.display.width//2, y=lcdScreen.display.height//2, speed=speed)
    return True
