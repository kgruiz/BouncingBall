import math

import pygame

WINDOW_WIDTH = 600
WINDOW_HEIGHT = 600
FPS = 60

SQUARE_SIZE = 300
BALL_RADIUS = 20
BALL_SPEED = 4
ROTATION_SPEED = 1  # degrees per frame

YELLOW = (255, 255, 0)
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)


def RotateVector(x, y, angleDegrees):
    # Rotates the vector (x,y) around (0,0) by angleDegrees (counter-clockwise).
    # Returns the (rotatedX, rotatedY).
    radians = math.radians(angleDegrees)
    cosA = math.cos(radians)
    sinA = math.sin(radians)
    rotatedX = x * cosA - y * sinA
    rotatedY = x * sinA + y * cosA
    return rotatedX, rotatedY


def GlobalToLocal(px, py, centerX, centerY, angleDegrees):
    # Translate (px, py) so (centerX, centerY) is origin, then rotate by -angle.
    translatedX = px - centerX
    translatedY = py - centerY
    # We rotate by negative angle because we're going from global to local.
    localX, localY = RotateVector(translatedX, translatedY, -angleDegrees)
    return localX, localY


def LocalToGlobal(lx, ly, centerX, centerY, angleDegrees):
    # Rotate by +angle, then translate back to global coords.
    rotatedX, rotatedY = RotateVector(lx, ly, angleDegrees)
    globalX = rotatedX + centerX
    globalY = rotatedY + centerY
    return globalX, globalY


def GetSquareCorners(centerX, centerY, size, angleDegrees):
    # Return the four corners of a square of side 'size' centered at (centerX, centerY),
    # rotated by angleDegrees around its center.
    half = size / 2
    corners = [
        (centerX - half, centerY - half),
        (centerX + half, centerY - half),
        (centerX + half, centerY + half),
        (centerX - half, centerY + half),
    ]
    rotated = []
    for x, y in corners:
        # Rotate each corner around the center
        lx, ly = GlobalToLocal(x, y, centerX, centerY, -angleDegrees)  # local
        gx, gy = LocalToGlobal(lx, ly, centerX, centerY, angleDegrees)  # back to global
        rotated.append((gx, gy))
    return rotated


def RunGame():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    centerX = WINDOW_WIDTH // 2
    centerY = WINDOW_HEIGHT // 2

    # Ball setup in global space
    ballX = centerX
    ballY = centerY
    velX = BALL_SPEED
    velY = BALL_SPEED

    rotationAngle = 0

    # For collision in local space, the bounding region for the ball’s center is:
    # [-halfS + BALL_RADIUS, halfS - BALL_RADIUS] in both X and Y,
    # where halfS = SQUARE_SIZE / 2
    halfS = SQUARE_SIZE / 2
    minCoord = -halfS + BALL_RADIUS
    maxCoord = halfS - BALL_RADIUS

    while running:
        dt = clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update global ball position
        ballX += velX
        ballY += velY

        # Transform ball position and velocity to local (unrotated) space of the square
        localX, localY = GlobalToLocal(ballX, ballY, centerX, centerY, rotationAngle)
        localVelX, localVelY = RotateVector(velX, velY, -rotationAngle)

        # Check collisions in local space (axis-aligned)
        # X-axis checks
        if localX < minCoord:
            localX = minCoord
            localVelX = -localVelX
        elif localX > maxCoord:
            localX = maxCoord
            localVelX = -localVelX

        # Y-axis checks
        if localY < minCoord:
            localY = minCoord
            localVelY = -localVelY
        elif localY > maxCoord:
            localY = maxCoord
            localVelY = -localVelY

        # Transform ball position & velocity back to global
        ballX, ballY = LocalToGlobal(localX, localY, centerX, centerY, rotationAngle)
        velX, velY = RotateVector(localVelX, localVelY, rotationAngle)

        # Rotate the square a bit each frame
        rotationAngle += ROTATION_SPEED
        rotationAngle %= 360

        # Drawing
        screen.fill(BLACK)

        # Draw rotated square (just for display)
        corners = GetSquareCorners(centerX, centerY, SQUARE_SIZE, rotationAngle)
        pygame.draw.polygon(screen, GRAY, corners, 2)

        # Draw ball
        pygame.draw.circle(screen, YELLOW, (int(ballX), int(ballY)), BALL_RADIUS)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    RunGame()
