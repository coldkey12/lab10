import pygame
import random
import time
import psycopg2

DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': '12070107Don',
    'host': 'localhost',
    'port': '5432'
}

blue = (50, 153, 213)
black = (0, 0, 0)
red = (213, 50, 80)
green = (0, 255, 0)
white = (255, 255, 255)

dis_width = 600
dis_height = 400
snake_block = 10

pygame.init()
display = pygame.display.set_mode((dis_width, dis_height))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 25)


def message(msg, color, x, y):
    screen_text = font.render(msg, True, color)
    display.blit(screen_text, [x, y])


def print_snake(snake_block, snake_list):
    seen = set()
    collision = False

    for segment in snake_list:
        segment_tuple = tuple(segment)
        if segment_tuple in seen:
            collision = True
            break
        seen.add(segment_tuple)

    if collision:
        return True

    for x in snake_list:
        pygame.draw.rect(display, black, [x[0], x[1], snake_block, snake_block])

    return False


def show_paused_screen():
    display.fill(blue)
    message("PAUSED", white, dis_width / 2 - 30, dis_height / 2 - 20)
    message("Press P to continue", white, dis_width / 2 - 60, dis_height / 2 + 10)
    pygame.display.update()


def get_player_name():
    name = ""
    input_active = True
    while input_active:
        display.fill(blue)
        message("Enter your name: " + name, white, dis_width / 4, dis_height / 2)
        message("Press ENTER to confirm", white, dis_width / 4, dis_height / 2 + 30)
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                else:
                    name += event.unicode
    return name


def save_score(player_name, score, duration):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO players (player_name) 
            VALUES (%s) 
            ON CONFLICT (player_name) DO NOTHING
            RETURNING player_id
            """,
            [player_name]
        )

        player_id = cursor.fetchone()
        if not player_id:
            cursor.execute(
                "SELECT player_id FROM players WHERE player_name = %s",
                [player_name]
            )
            player_id = cursor.fetchone()[0]
        else:
            player_id = player_id[0]

        cursor.execute(
            "INSERT INTO player_scores (player_id, score, game_duration) VALUES (%s, %s, %s)",
            [player_id, score, duration]
        )

        conn.commit()
        return True

    except Exception as e:
        print(f"Database error: {e}")
        return False
    finally:
        if 'conn' in locals():
            cursor.close()
            conn.close()


def show_high_scores():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cursor = conn.cursor()

        cursor.execute("""
            SELECT p.player_name, ps.score, ps.game_duration 
            FROM player_scores ps
            JOIN players p ON ps.player_id = p.player_id
            ORDER BY ps.score DESC
            LIMIT 5
        """)

        scores = cursor.fetchall()
        cursor.close()
        conn.close()

        display_scores(scores)

    except Exception as e:
        print(f"Database error: {e}")


def display_scores(scores):
    display.fill(blue)
    message("HIGH SCORES", white, dis_width / 2 - 50, 30)

    y_offset = 70
    for i, (name, score, duration) in enumerate(scores, 1):
        message(f"{i}. {name}: {score} points ({duration}s)", white, dis_width / 4, y_offset)
        y_offset += 30

    message("Good job", white, dis_width / 4, y_offset + 40)
    pygame.display.update()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.KEYDOWN:
                waiting = False


def main():
    player_name = get_player_name()
    if not player_name:
        return

    paused = False
    game_over = False
    x1 = dis_width / 2
    y1 = dis_height / 2
    x1_change = 0
    y1_change = 0

    snake_list = []
    snake_length = 1

    food_x = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    food_y = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
    food_timer = time.time()

    coin_x = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
    coin_y = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
    coin_value = random.choice([1, 2, 5])
    start_time = time.time()

    while not game_over:
        display.fill(blue)
        elapsed_time = int(time.time() - start_time)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_p:
                    paused = not paused
                if not paused:
                    if event.key == pygame.K_LEFT:
                        if x1_change != snake_block:
                            x1_change = -snake_block
                            y1_change = 0
                    elif event.key == pygame.K_RIGHT:
                        if x1_change != -snake_block:
                            x1_change = snake_block
                            y1_change = 0
                    elif event.key == pygame.K_UP:
                        if y1_change != snake_block:
                            y1_change = -snake_block
                            x1_change = 0
                    elif event.key == pygame.K_DOWN:
                        if y1_change != -snake_block:
                            y1_change = snake_block
                            x1_change = 0

        if paused:
            show_paused_screen()
            pygame.display.update()
            continue

        x1 += x1_change
        y1 += y1_change

        if x1 < 0 or x1 >= dis_width or y1 < 0 or y1 >= dis_height:
            game_over = True
            break

        # snake_head = [x1, y1]
        # snake_list.append(snake_head)
        # if len(snake_list) > snake_length:
        #     del snake_list[0]

        snake_head = [x1, y1]

        snake_list.append(snake_head)
        if len(snake_list) > snake_length:
            del snake_list[0]

        if time.time() - food_timer > 5:
            food_x = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            food_y = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            food_timer = time.time()

        pygame.draw.rect(display, red, [food_x, food_y, snake_block, snake_block])
        pygame.draw.rect(display, green, [coin_x, coin_y, snake_block, snake_block])

        if x1 == food_x and y1 == food_y:
            snake_length += coin_value
            food_x = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            food_y = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            food_timer = time.time()

        if x1 == coin_x and y1 == coin_y:
            snake_length += 1
            coin_x = round(random.randrange(0, dis_width - snake_block) / 10.0) * 10.0
            coin_y = round(random.randrange(0, dis_height - snake_block) / 10.0) * 10.0
            coin_value = random.choice([1, 2, 5])

        if print_snake(snake_block, snake_list):
            game_over = True
        message(f"Player: {player_name}", white, 10, 10)
        message(f"Score: {snake_length}", white, 10, 30)
        message(f"Time: {elapsed_time} sec", white, 10, 50)
        pygame.display.update()
        clock.tick(15)

    final_score = snake_length
    final_time = int(time.time() - start_time)
    save_score(player_name, final_score, final_time)
    show_high_scores()

    pygame.quit()


if __name__ == "__main__":
    main()
