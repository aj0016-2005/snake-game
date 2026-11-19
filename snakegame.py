import pygame
import random


# Window and board settings
WINDOW_WIDTH = 640
WINDOW_HEIGHT = 760
CELL_SIZE = 25
COLUMNS = 24
ROWS = 20
BOARD_LEFT = 20
BOARD_TOP = 145
BOARD_WIDTH = COLUMNS * CELL_SIZE
BOARD_HEIGHT = ROWS * CELL_SIZE

# Colors
BACKGROUND = (13, 19, 32)
BOARD_COLOR = (21, 31, 48)
GRID_COLOR = (34, 47, 65)
WHITE = (238, 244, 250)
MUTED = (151, 167, 187)
GREEN = (83, 220, 143)
HEAD_GREEN = (127, 245, 174)
FOOD_RED = (255, 104, 119)
CARD_COLOR = (27, 39, 58)
ACCENT = (100, 196, 255)


def make_food(snake):
    """Choose an unoccupied board cell, or return None if the board is full."""
    occupied = set(snake)
    empty_cells = [
        (x, y)
        for x in range(COLUMNS)
        for y in range(ROWS)
        if (x, y) not in occupied
    ]
    return random.choice(empty_cells) if empty_cells else None


def draw_text(surface, text, font, color, center):
    image = font.render(text, True, color)
    surface.blit(image, image.get_rect(center=center))


def reset_game():
    snake = [
        (COLUMNS // 2, ROWS // 2),
        (COLUMNS // 2 - 1, ROWS // 2),
        (COLUMNS // 2 - 2, ROWS // 2),
    ]
    return snake, (1, 0), make_food(snake), 0


def draw_board(surface, snake, food):
    board_rect = pygame.Rect(
        BOARD_LEFT,
        BOARD_TOP,
        BOARD_WIDTH,
        BOARD_HEIGHT,
    )
    pygame.draw.rect(surface, BOARD_COLOR, board_rect, border_radius=14)

    for x in range(COLUMNS + 1):
        line_x = BOARD_LEFT + x * CELL_SIZE
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (line_x, BOARD_TOP),
            (line_x, BOARD_TOP + BOARD_HEIGHT),
        )

    for y in range(ROWS + 1):
        line_y = BOARD_TOP + y * CELL_SIZE
        pygame.draw.line(
            surface,
            GRID_COLOR,
            (BOARD_LEFT, line_y),
            (BOARD_LEFT + BOARD_WIDTH, line_y),
        )

    if food is not None:
        food_x = BOARD_LEFT + food[0] * CELL_SIZE + CELL_SIZE // 2
        food_y = BOARD_TOP + food[1] * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(surface, FOOD_RED, (food_x, food_y), CELL_SIZE // 2 - 3)
        pygame.draw.circle(surface, WHITE, (food_x - 3, food_y - 4), 2)

    for index, (x, y) in enumerate(snake):
        cell_rect = pygame.Rect(
            BOARD_LEFT + x * CELL_SIZE + 2,
            BOARD_TOP + y * CELL_SIZE + 2,
            CELL_SIZE - 4,
            CELL_SIZE - 4,
        )
        color = HEAD_GREEN if index == 0 else GREEN
        pygame.draw.rect(surface, color, cell_rect, border_radius=7)


def draw_overlay(surface, title, lines, title_font, body_font):
    overlay = pygame.Surface((BOARD_WIDTH, BOARD_HEIGHT), pygame.SRCALPHA)
    overlay.fill((8, 13, 23, 205))
    surface.blit(overlay, (BOARD_LEFT, BOARD_TOP))

    card_width = 490
    card_height = 300
    card = pygame.Rect(
        BOARD_LEFT + (BOARD_WIDTH - card_width) // 2,
        BOARD_TOP + (BOARD_HEIGHT - card_height) // 2,
        card_width,
        card_height,
    )
    pygame.draw.rect(surface, CARD_COLOR, card, border_radius=20)
    pygame.draw.rect(surface, GRID_COLOR, card, width=2, border_radius=20)

    draw_text(
        surface,
        title,
        title_font,
        WHITE,
        (card.centerx, card.top + 58),
    )

    line_y = card.top + 125
    for index, (text, color) in enumerate(lines):
        draw_text(
            surface,
            text,
            body_font,
            color,
            (card.centerx, line_y + index * 36),
        )


def main():
    pygame.init()
    pygame.display.set_caption("Snake — Arcade")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    title_font = pygame.font.Font(None, 54)
    body_font = pygame.font.Font(None, 29)
    small_font = pygame.font.Font(None, 23)
    score_font = pygame.font.Font(None, 36)

    snake, direction, food, score = reset_game()
    next_direction = direction
    best_score = 0
    speed_level = 5
    state = "menu"
    time_since_move = 0.0

    direction_keys = {
        pygame.K_UP: (0, -1),
        pygame.K_w: (0, -1),
        pygame.K_DOWN: (0, 1),
        pygame.K_s: (0, 1),
        pygame.K_LEFT: (-1, 0),
        pygame.K_a: (-1, 0),
        pygame.K_RIGHT: (1, 0),
        pygame.K_d: (1, 0),
    }

    running = True
    while running:
        elapsed = min(clock.tick(60) / 1000, 0.1)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_q:
                running = False
                continue

            if state == "menu":
                if event.key in (pygame.K_SPACE, pygame.K_RETURN):
                    snake, direction, food, score = reset_game()
                    next_direction = direction
                    time_since_move = 0.0
                    state = "playing"

            elif state == "playing":
                if event.key in (pygame.K_ESCAPE, pygame.K_p):
                    state = "paused"
                    time_since_move = 0.0
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS, pygame.K_KP_PLUS):
                    speed_level = min(10, speed_level + 1)
                elif event.key in (pygame.K_MINUS, pygame.K_KP_MINUS):
                    speed_level = max(1, speed_level - 1)
                elif event.key in direction_keys:
                    requested = direction_keys[event.key]
                    reverse = (-direction[0], -direction[1])
                    if requested != reverse:
                        next_direction = requested

            elif state == "paused":
                if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_SPACE):
                    state = "playing"
                    time_since_move = 0.0
                elif event.key == pygame.K_m:
                    state = "menu"

            elif state in ("game_over", "won"):
                if event.key in (pygame.K_r, pygame.K_SPACE, pygame.K_RETURN):
                    snake, direction, food, score = reset_game()
                    next_direction = direction
                    time_since_move = 0.0
                    state = "playing"
                elif event.key == pygame.K_m:
                    state = "menu"

        if state == "playing":
            time_since_move += elapsed
            move_interval = max(0.055, 0.22 - speed_level * 0.015 - score * 0.002)

            while time_since_move >= move_interval and state == "playing":
                time_since_move -= move_interval
                direction = next_direction

                head_x = snake[0][0] + direction[0]
                head_y = snake[0][1] + direction[1]
                new_head = (head_x, head_y)
                eating = new_head == food

                outside_board = not (
                    0 <= head_x < COLUMNS and 0 <= head_y < ROWS
                )
                body_to_check = snake if eating else snake[:-1]
                hits_snake = new_head in body_to_check

                if outside_board or hits_snake:
                    state = "game_over"
                    break

                snake.insert(0, new_head)

                if eating:
                    score += 1
                    best_score = max(best_score, score)
                    food = make_food(snake)
                    if food is None:
                        state = "won"
                else:
                    snake.pop()

        screen.fill(BACKGROUND)

        draw_text(
            screen,
            "SNAKE",
            title_font,
            WHITE,
            (WINDOW_WIDTH // 2, 39),
        )

        score_card = pygame.Rect(BOARD_LEFT, 75, 190, 52)
        best_card = pygame.Rect(BOARD_LEFT + 205, 75, 190, 52)
        speed_card = pygame.Rect(BOARD_LEFT + 410, 75, 190, 52)
        pygame.draw.rect(screen, CARD_COLOR, score_card, border_radius=12)
        pygame.draw.rect(screen, CARD_COLOR, best_card, border_radius=12)
        pygame.draw.rect(screen, CARD_COLOR, speed_card, border_radius=12)

        score_label = score_font.render(f"SCORE {score}", True, WHITE)
        best_label = score_font.render(f"BEST {best_score}", True, ACCENT)
        speed_label = score_font.render(f"SPEED {speed_level}/10", True, GREEN)
        screen.blit(score_label, score_label.get_rect(center=score_card.center))
        screen.blit(best_label, best_label.get_rect(center=best_card.center))
        screen.blit(speed_label, speed_label.get_rect(center=speed_card.center))

        draw_board(screen, snake, food)

        if state == "menu":
            draw_overlay(
                screen,
                "SNAKE",
                [
                    ("Eat the food. Don't hit the walls!", MUTED),
                    ("Move with arrow keys or WASD", WHITE),
                    ("Use + / - to adjust snake speed", ACCENT),
                    ("Press SPACE or ENTER to start", GREEN),
                    ("P / ESC pauses  •  Q quits", MUTED),
                ],
                title_font,
                body_font,
            )
        elif state == "paused":
            draw_overlay(
                screen,
                "PAUSED",
                [
                    ("Take a breather.", MUTED),
                    ("Press P, ESC, or SPACE to continue", GREEN),
                    ("Q quits the game", MUTED),
                ],
                title_font,
                body_font,
            )
        elif state == "game_over":
            draw_overlay(
                screen,
                "GAME OVER",
                [
                    (f"You scored {score}!", MUTED),
                    ("Press R or SPACE to play again", GREEN),
                    ("Press M for the start screen", WHITE),
                    ("Q quits the game", MUTED),
                ],
                title_font,
                body_font,
            )
        elif state == "won":
            draw_overlay(
                screen,
                "YOU WIN!",
                [
                    ("You filled the whole board!", MUTED),
                    (f"Final score: {score}", ACCENT),
                    ("Press R or SPACE to play again", GREEN),
                    ("Press M for the start screen", WHITE),
                ],
                title_font,
                body_font,
            )

        draw_text(
            screen,
            "Arrows / WASD: move    +/-: speed    P / ESC: pause    Q: quit",
            small_font,
            MUTED,
            (WINDOW_WIDTH // 2, 690),
        )
        draw_text(
            screen,
            "Collect the red food to grow and earn points",
            small_font,
            MUTED,
            (WINDOW_WIDTH // 2, 719),
        )

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()