import math

def Localization(v0, v1, v2, global_inches):

    _global_red_xyz_pts =   {'x': None, 'y': None, 'z': None, 'isCalculated': False}
    _global_green_xyz_pts = {'x': None, 'y': None, 'z': None, 'isCalculated': False}
    _global_blue_xyz_pts =  {'x': None, 'y': None, 'z': None, 'isCalculated': False}
    _global_yellow_xyz_pts ={'x': None, 'y': None, 'z': None, 'isCalculated': False}

    X_REF_POINT  = 200
    Y_REF_POINT = 150
    PIXEL_TRACKING = 5
    BALL_RADIUS = 5
    FRAME_CENTER = (X_REF_POINT,Y_REF_POINT)
    V0_ANGLE = 0
    V1_ANGLE =  90*(math.pi/180)
    V2_ANGLE = 0
    MIN_NUM_POINTS = 10

    KNOWN_DISTANCE = 24.0
    KNOWN_WIDTH = 2.65
    marker = 30

    focalLength =(marker * KNOWN_DISTANCE) / KNOWN_WIDTH


    def calculate_global_x_y(v0_color, v1_color, v2_color):
        try:
            _global_xyz_pts = {'x': None, 'y': None, 'z': None, 'isCalculated': False}
            length0 = 0
            length1 = 0
            length2 = 0
            if ((len(v0_color['x']) > MIN_NUM_POINTS) and (len(v1_color['x']) > MIN_NUM_POINTS)):
                # and (len(v2_color['pts']) > MIN_NUM_POINTS)):
                length0 = round((v0_color['x'][-1] - X_REF_POINT) * math.cos(V0_ANGLE) +
                                (v0_color['y'][-1] - Y_REF_POINT) * math.sin(V0_ANGLE))
                length1 = round((v1_color['x'][-1] - X_REF_POINT) * math.cos(V1_ANGLE) +
                                (v1_color['y'][-1] - Y_REF_POINT) * math.sin(V1_ANGLE))

            else:
                _global_xyz_pts['isCalculated'] = False
                return
            determinant = (1 / ((math.cos(V0_ANGLE)) * (math.sin(V1_ANGLE)) - (math.sin(V0_ANGLE)) * (math.cos(V1_ANGLE))))
            inverseMatrix = [determinant * round(math.sin(V1_ANGLE)), determinant * round(math.sin(V0_ANGLE))], \
                            [determinant * round(math.cos(V1_ANGLE)), determinant * round(math.cos(V0_ANGLE))]
            GLOBAL_REF_ADD = [inverseMatrix[0][0] * length0 + inverseMatrix[0][1] * length1,
                              inverseMatrix[1][0] * length0 + inverseMatrix[1][1] * length1]

            _global_xyz_pts['x'] = round(X_REF_POINT + GLOBAL_REF_ADD[0])
            _global_xyz_pts['y'] = round(Y_REF_POINT + GLOBAL_REF_ADD[1])
            _global_xyz_pts['z'] = 0
            _global_xyz_pts['isCalculated'] = True
            _global_xyz_pts['x'] = (dis_to_camera_x(focalLength, 67.31, 400, 5.14, _global_xyz_pts['x']) * .039) / 100
            _global_xyz_pts['y'] = (dis_to_camera_y(focalLength, 67.31, 300, 3.5, _global_xyz_pts['y']) * .039) / 100
            _global_xyz_pts['z'] = global_inches

            return _global_xyz_pts

        except Exception as e:
            print(e)

    def distance_to_camera(knownWidth, focalLength, perWidth):
        # compute and return the distance from the image to camera
        return (knownWidth * focalLength) / perWidth

    def dis_to_camera_x(focalLength, REAL_WIDTH, IMAGE_WIDTH, SENSOR_WIDTH, OBJECT_WIDTH):

        return ((focalLength * REAL_WIDTH * IMAGE_WIDTH) / (OBJECT_WIDTH * SENSOR_WIDTH))

    def dis_to_camera_y(focalLength, REAL_HEIGHT, IMAGE_HEIGHT, SENSOR_HEIGHT, OBJECT_HEIGHT):

        return ((focalLength * REAL_HEIGHT * IMAGE_HEIGHT) / (OBJECT_HEIGHT * SENSOR_HEIGHT))



    if(v0.isDetected['red'] is True and v1.isDetected['red'] is True):# or v2_isDetected['red']):
        _global_red_xyz_pts = calculate_global_x_y(v0.red, v1.red, v2.red)
    if (v0.isDetected['green'] is True  and v1.isDetected['green'] is True):# or v2_isDetected['green']):

        _global_green_xyz_pts = calculate_global_x_y(v0.green, v1.green, v2.green)

    if (v0.isDetected['blue'] is True and v1.isDetected['blue'] is True):# or v2_isDetected['blue']):
        _global_blue_xyz_pts = calculate_global_x_y(v0.blue, v1.blue, v2.blue)


    if (v0.isDetected['yellow'] is True and v1.isDetected['yellow'] is True):# v2_isDetected['yellow']):
        _global_yellow_xyz_pts = calculate_global_x_y(v0.yellow, v1.yellow, v2.yellow)



    return _global_red_xyz_pts, _global_green_xyz_pts, _global_blue_xyz_pts,_global_yellow_xyz_pts