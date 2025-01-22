import math

import pygame

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
FPS = 60

# Each coordinate of the tesseract ranges from -1 to +1,
# so the total side length is 2. If you want a larger
# or smaller tesseract, adjust the projection scale below.
BALL_RADIUS_4D = 0.2
BALL_SPEED_4D = 0.01

# We'll rotate in two 2D-planes within 4D: (X,Y) and (Z,W).
# Adjust these speeds to change rotation rates.
ROTATION_SPEED_XY = 0.5  # degrees per frame
ROTATION_SPEED_ZW = 0.8  # degrees per frame

# Colors
WHITE = (255, 255, 255)
GRAY = (150, 150, 150)
YELLOW = (255, 255, 0)
BLACK = (0, 0, 0)


# To visualize the 4D points in 2D, we apply an orthographic projection:
# We'll treat (x, y) as the primary axes on the screen,
# and we use z and w as "offset" adjustments to the final 2D coordinates.
# Then we scale and center them on the window.
def Project4DTo2D(x, y, z, w):
    # Simple linear transformation; tweak factors for a different look
    # finalX = x + 0.5*z
    # finalY = y + 0.5*w
    # You can experiment with other forms of projection.
    finalX = x + 0.5 * z
    finalY = y + 0.5 * w
    return finalX, finalY


# Rotate a single point (x, y, z, w) in two planes: XY and ZW.
# angleXY rotates around XY-plane, angleZW around ZW-plane.
# Angles are in degrees. The function returns the rotated coordinates.
def Rotate4D(x, y, z, w, angleXY, angleZW):
    # Convert degrees to radians
    rXY = math.radians(angleXY)
    rZW = math.radians(angleZW)

    cosXY = math.cos(rXY)
    sinXY = math.sin(rXY)
    cosZW = math.cos(rZW)
    sinZW = math.sin(rZW)

    # Rotate in XY-plane
    # (x, y) -> (x*cos - y*sin, x*sin + y*cos)
    rx = x * cosXY - y * sinXY
    ry = x * sinXY + y * cosXY
    rz = z
    rw = w

    # Rotate in ZW-plane
    # (z, w) -> (z*cos - w*sin, z*sin + w*cos)
    rzx = rx
    rzy = ry
    rzz = rz * cosZW - rw * sinZW
    rzw = rz * sinZW + rw * cosZW

    return rzx, rzy, rzz, rzw


# We’ll define the 16 corners of the tesseract, i.e. all sign combinations (±1, ±1, ±1, ±1).
# Then define edges as pairs of those corners that differ in exactly one coordinate.
def GenerateTesseractCornersAndEdges():
    corners = []
    for sx in [-1, 1]:
        for sy in [-1, 1]:
            for sz in [-1, 1]:
                for sw in [-1, 1]:
                    corners.append((sx, sy, sz, sw))

    edges = []
    # Edges connect corners that differ in exactly one coordinate.
    for i in range(len(corners)):
        for j in range(i + 1, len(corners)):
            diffCount = 0
            for c1, c2 in zip(corners[i], corners[j]):
                if c1 != c2:
                    diffCount += 1
            if diffCount == 1:  # differ in exactly one dimension
                edges.append((i, j))

    return corners, edges


def RunGame():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    # Pre-generate the 16 corners and the edges that connect them.
    tesseractCorners, tesseractEdges = GenerateTesseractCornersAndEdges()

    # The ball’s position in 4D.
    ballX = 0.0
    ballY = 0.0
    ballZ = 0.0
    ballW = 0.0

    # The ball’s velocity in 4D (tweak as desired).
    ballVelX = BALL_SPEED_4D
    ballVelY = BALL_SPEED_4D
    ballVelZ = BALL_SPEED_4D
    ballVelW = BALL_SPEED_4D

    # Angles for rotating the tesseract in the XY-plane and ZW-plane.
    angleXY = 0.0
    angleZW = 0.0

    running = True
    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update ball’s 4D position
        ballX += ballVelX
        ballY += ballVelY
        ballZ += ballVelZ
        ballW += ballVelW

        # Collision in each 4D dimension: the tesseract extends from -1 to +1 in all coords.
        # The ball’s “radius” means if center < -1 + r or center > 1 - r, reflect.
        if ballX < -1 + BALL_RADIUS_4D:
            ballX = -1 + BALL_RADIUS_4D
            ballVelX = -ballVelX
        elif ballX > 1 - BALL_RADIUS_4D:
            ballX = 1 - BALL_RADIUS_4D
            ballVelX = -ballVelX

        if ballY < -1 + BALL_RADIUS_4D:
            ballY = -1 + BALL_RADIUS_4D
            ballVelY = -ballVelY
        elif ballY > 1 - BALL_RADIUS_4D:
            ballY = 1 - BALL_RADIUS_4D
            ballVelY = -ballVelY

        if ballZ < -1 + BALL_RADIUS_4D:
            ballZ = -1 + BALL_RADIUS_4D
            ballVelZ = -ballVelZ
        elif ballZ > 1 - BALL_RADIUS_4D:
            ballZ = 1 - BALL_RADIUS_4D
            ballVelZ = -ballVelZ

        if ballW < -1 + BALL_RADIUS_4D:
            ballW = -1 + BALL_RADIUS_4D
            ballVelW = -ballVelW
        elif ballW > 1 - BALL_RADIUS_4D:
            ballW = 1 - BALL_RADIUS_4D
            ballVelW = -ballVelW

        # Rotate the tesseract a bit each frame
        angleXY += ROTATION_SPEED_XY
        angleZW += ROTATION_SPEED_ZW

        # Clear screen
        screen.fill(BLACK)

        # Rotate and project each corner, draw edges
        projectedPoints = []
        for corner in tesseractCorners:
            rx, ry, rz, rw = Rotate4D(
                corner[0], corner[1], corner[2], corner[3], angleXY, angleZW
            )
            px, py = Project4DTo2D(rx, ry, rz, rw)
            # Scale and shift to screen center
            screenX = int(px * 100 + WINDOW_WIDTH / 2)
            screenY = int(py * 100 + WINDOW_HEIGHT / 2)
            projectedPoints.append((screenX, screenY))

        # Draw the edges of the tesseract
        for e in tesseractEdges:
            c1 = projectedPoints[e[0]]
            c2 = projectedPoints[e[1]]
            pygame.draw.line(screen, GRAY, c1, c2, 1)

        # Rotate and project the ball’s 4D position
        bx, by, bz, bw = Rotate4D(ballX, ballY, ballZ, ballW, angleXY, angleZW)
        projBallX, projBallY = Project4DTo2D(bx, by, bz, bw)
        finalBallX = int(projBallX * 100 + WINDOW_WIDTH / 2)
        finalBallY = int(projBallY * 100 + WINDOW_HEIGHT / 2)

        # Draw the ball as a circle. Since it’s 4D, we just pick a 2D radius for display.
        # This is purely aesthetic, ignoring the 4D radius. Let’s pick something like 10 pixels.
        pygame.draw.circle(screen, YELLOW, (finalBallX, finalBallY), 10)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    RunGame()
