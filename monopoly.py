import os
import sys
import pygame
import pygame_gui
import numpy
import random

# class SpriteObject(pygame.sprite.Sprite):
#     def __init__(self, image_path, width, height, xpos=0, ypos=0):
#         super().__init__();
#         self.raw_img = pygame.image.load(image_path).convert_alpha();
#         self.image = pygame.transform.scale(self.raw_img, (width, height));
#         self.rect = self.image.get_rect();
#         self.rect.topleft = (xpos, ypos);

# 選擇題

class SelectingProblem:
    def __init__(self, prob_text, ans_text, ans, time_limit, manager):
        self.problem_statement = pygame_gui.elements.UITextBox(prob_text, pygame.rect.Rect(100, 50, 600, 300));
        self.answer_button = [];
        pos = [(100, 400), (420, 400), (100, 500), (420, 500)];
        for i in range(4):
            self.answer_button.append(pygame_gui.elements.UIButton(pygame.rect.Rect(pos[i][0], pos[i][1], 280, 80), ans_text[i], manager));
        self.ans = ans;
        if time_limit != "none":
            self.time_left = time_limit;

# Monopoly Theme

class Chess(pygame.sprite.Sprite):
    def __init__(self, width, height):
        super().__init__("./img/player1.png",width, height);

    def move(self, new_x, new_y):
        self.rect.topleft = (new_x, new_y);

class Board(pygame.sprite.Sprite):
    def __init__(self, width, height, xpos, ypos):
        super().__init__();
        self.raw_img = pygame.image.load("./img/map.png").convert_alpha();
        self.image = pygame.transform.scale(self.raw_img, (width, height));
        self.rect = self.image.get_rect();
        self.rect.topleft = (xpos, ypos);

# Battle Theme

class Battle_Theme:
    def __init__(self, player, manager):
        self.player = player;
        self.student = pygame_gui.elements.UIImage(pygame.rect.Rect(50,300,150,250), pygame.image.load("./img/student.png"), manager);
        self.professor = pygame_gui.elements.UIImage(pygame.rect.Rect(400,50,150,250), pygame.image.load("./img/shimingfeng.png"), manager);
        self.textbox = pygame_gui.elements.UITextBox("", pygame.rect.Rect(250, 400, 250, 150), manager);
        self.weapon = pygame_gui.elements.UIImage(pygame.rect.Rect(0,0,30,30), pygame.image.load("./img/rock.png"), manager);
        self.round = 0;
        self.student.health_capacity = 50;
        self.student.current_health = 50;
        self.student.defending = False;
        self.student.reflecting = False;
        self.student.debuffing = False;
        self.student.good_at_programming = self.player.score["計算機程式設計"] >= 80;
        self.student.has_vpy_repo = "資訊部長的vpython github repository" in self.player.items.keys();
        # self.student.has_rock_thrower = "投石器" in self.player.items.keys();
        self.professor.health_capacity = 50;
        self.professor.current_health = 50;
        self.professor.raging = 0;
        self.student_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.rect.Rect(50,550,150,30), manager, self.student);
        self.professor_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.rect.Rect(400,300,150,30), manager, self.professor);
        self.stats = [];
        self.stats_button = [];
        self.get_stat("投石器", "丟石頭");
        self.get_stat("防守", "防守");
        self.get_stat("電神的守護", "???");
        self.get_stat("星爆氣流斬", "???");

        for i in range(0,4):
            self.stats_button.append(pygame_gui.elements.UIButton(pygame.rect.Rect(600,350+i*50,150,40), self.stats[i],manager));
            self.stats_button[i].btnid = i;
            if self.stats[i] == "???":
                self.stats_button[i].disable();

    def get_stat(self, name1, name2):
        if name1 in self.player.items.keys():
            self.stats.append(name1);
        else:
            self.stats.append(name2);

    def clear(self):
        self.textbox.hide();
        for i in range(4):
            self.stats_button[i].hide();
        self.weapon.hide();

    def show_text(self, text):
        self.clear();
        self.textbox.set_text(text);
        self.textbox.show();

    def show_stats_buttons(self):
        self.clear();
        for i in range(0,4):
            self.stats_button[i].show();

    def show_weapon_animation(self, arg):
        self.clear();
        self.weapon.set_image(pygame.image.load(arg[0]));
        self.weapon.set_position((arg[1], arg[2]));
        self.weapon.set_dimensions((arg[3], arg[4]));
        self.weapon.show();

    def show_student_state(self, state_type):
        self.student.set_image(pygame.image.load(state_type));

    def show_professor_state(self, state_type):
        self.professor.set_image(pygame.image.load(state_type));

    def get_intro(self):
        queue = [];
        queue.append(["text", "石明豐出現了!"]);
        queue.append(["wait", 2]);
        queue.append(["select"]);
        queue.append(["stop"]);
        return queue;

    def get_professor_stat(self):
        if self.round == 3: #vpython
            return "vpython作業";
        elif self.round % 6 == 2: #bomb
            return "定時炸彈";
        elif self.round % 5 == 4: #rage
            return "盪鞦韆";
        else:
            return "投石器";

    def student_attack(self, damage):
        if self.professor.current_health < damage:
            self.professor.current_health = 0;
        else:
            self.professor.current_health -= damage;

    def professor_attack(self, damage):
        if self.student.current_health < damage:
            self.student.current_health = 0;
        else:
            self.student.current_health -= damage;

    def generate_student_atk_event(self, stat_name):
        queue = [];
        queue.append(["text", f"你使用了 {stat_name} !"]);
        queue.append(["wait",2]);
        if stat_name == "丟石頭":
            damage = 5;
            if self.student.debuffing:
                damage //= 5;
            queue.extend(self.generate_weapon_animation(0));
            queue.append(["student_atk", damage]);
        elif stat_name == "投石器":
            damage = 10;
            if self.student.debuffing:
                damage //= 5;
            queue.extend(self.generate_weapon_animation(0));
            queue.append(["student_atk", damage]);
        elif stat_name == "防守":
            self.student.defending = True;
            queue.append(["student_image", "./img/student_defend.png"]);
        elif stat_name == "電神的守護":
            self.student.reflecting = True;
            queue.append(["student_image", "./img/student_reflect.png"]);
        elif stat_name == "星爆氣流斬":
            queue.extend(self.generate_weapon_animation(1));

        queue.append(["clear"]);
        queue.append(["wait", 0.5]);
        return queue;

    def generate_professor_atk_event(self, stat_name):
        queue = [];
        queue.append(["text", f"石明豐使用了 {stat_name} !"]);
        queue.append(["wait",2]);
        if stat_name == "投石器":
            damage = 10;
            if self.professor.raging > 0:
                damage = 15;
            if self.student.defending:
                damage //= 2;
            queue.extend(self.generate_weapon_animation(2));
            if self.student.reflecting:
                if self.student.debuffing:
                    damage //= 5;
                queue.extend(self.generate_weapon_animation(0));
                queue.append(["student_atk", damage]);
            else:
                queue.append(["professor_atk", damage]);
        elif stat_name == "盪鞦韆":
            self.professor.raging = 3;
            queue.append(["text", "石明豐的傷害增加了!"]);
            queue.append(["wait", 2]);
            queue.append(["professor_image", "./img/shimingfeng_rage.png"]);
        elif stat_name == "vpython作業":
            if self.student.good_at_programming:
                queue.append(["text", "因為你很會寫程式，所以絲毫不受影響!"]);
                queue.append(["wait", 2]);
            elif self.student.has_vpy_repo:
                queue.append(["text", "因為你擁有「資訊部長的vpython github repository」，所以絲毫不受影響!"]);
                queue.append(["wait", 2]);
                queue.append(["student_image", "./img/student_debuff.png"]);
            else:
                self.student.debuffing = True;
                queue.append(["text", f"你的 {self.stats[0]} 傷害減少80%!"]);
                queue.append(["wait", 2]);
        elif stat_name == "定時炸彈":
            pass;

        queue.append(["clear"]);
        queue.append(["wait", 0.5]);
        return queue;        

    def generate_weapon_animation(self, weapon_type):
        queue = [];
        if weapon_type == 0: # rock
            for i in range(5):
                x = 200 + i * 30;
                y = 0.005 * (x-350)**2 + 200;
                queue.append(["weapon", "./img/rock.png", x, y, 30, 30]);
                queue.append(["wait", 0.1]);
        elif weapon_type == 1: # c8763
            for i in range(8):
                queue.append(["weapon", "./img/c8763_1.png", 400, 150, 150, 100]);
                queue.append(["student_atk", 1]);
                queue.append(["wait", 0.05]);
                queue.append(["weapon", "./img/c8763_2.png", 400, 150, 150, 100]);
                queue.append(["student_atk", 1]);
                queue.append(["wait", 0.05]);
        elif weapon_type == 2: # professor_rock
            for i in range(5):
                x = 200 + (5-i) * 30;
                y = 0.005 * (x-350)**2 + 200;
                queue.append(["weapon", "./img/rock.png", x, y, 30, 30]);
                queue.append(["wait", 0.1]);
        elif weapon_type == 3: # bomb
            pass;

        return queue;

    def check(self):
        queue = [];
        if self.student.current_health <= 0:
            queue.append(["text", "你輸了!"]);
            queue.append(["wait", 2]);
            return queue;
        if self.professor.current_health <= 0:
            queue.append(["text", "你贏了!"]);
            queue.append(["wait", 2]);
            return queue;
        self.student.defending = False;
        self.student.reflecting = False;
        self.professor.raging -= 1;
        if self.student.debuffing:
            queue.append(["student_image", "./img/student_debuff.png"]);
        else:
            queue.append(["student_image", "./img/student.png"]);
        if self.professor.raging <= 0:
            self.professor.raging = 0;
            queue.append(["professor_image", "./img/shimingfeng.png"]);
        queue.append(["select"]);
        queue.append(["stop"]);
        return queue;

    def handle_button_press(self, button):
        self.round += 1;
        student_stat = self.stats[button.btnid];
        professor_stat = self.get_professor_stat();
        queue = [];
        queue.extend(self.generate_student_atk_event(student_stat));
        queue.extend(self.generate_professor_atk_event(professor_stat));
        queue.append(["check"]);
        # queue.append(["select"]);
        # queue.append(["stop"]);
        return queue;
        

# Player Data

class Player:
    def __init__(self, i, ch):
        self.id = i;
        self.chess = ch;
        self.pos = "A0";
        self.money = 0;
        self.hp = 0;
        self.items = {};
        self.score = {"計算機程式設計":0};

    def move(self, the_map, steps):
        for i in range(steps):
            self.move_next_block(the_map);

    def move_next_block(self, the_map):
        next_block = the_map[self.pos]["next"];
        self.chess.move(the_map[next_block]["x"], the_map[next_block]["y"]);
        self.pos = next_block;

    def add_item(self, item_name, count):
        if item_name in self.items.keys():
            self.items[item_name] += count;
        else:
            self.items[item_name] = count;


def load_map_data(mypath = "./data/map.txt"):
    map_data = {};
    with open(mypath) as f:
        for i in f.readlines():
            print(i);
            name, xpos, ypos, is_split, nextname = i.strip().split(",");
            map_data[name] = {"x":int(xpos), "y":int(ypos), "is_split":int(is_split), "next":nextname};
    return map_data;

def monopoly_init():
    pass;

def battle_init(player):
    pass;

def cswap_init(player):
    pass;

def main():
    pygame.init();

    WINDOW_WIDTH = 800;
    WINDOW_HEIGHT = 600;
    WHITE = (255,255,255);
    FPS = 30;
    is_running = True;
    state = "battle";
    process_queue = [["init"]];
    # animation_queue = [];
    process = "";

    window_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT));
    pygame.display.set_caption("電機系大冒險");
    clock = pygame.time.Clock();

    manager = pygame_gui.UIManager((800,600));
    manager.set_locale("zh");
    # battle_theme = pygame_gui.UIManager((800,600));

    player1 = Player(1, None);
    player1.add_item("投石器", 1);
    player1.add_item("電神的守護", 1);
    player1.add_item("星爆氣流斬", 1);

    # myfont = pygame.font.SysFont("microsoftjhenghei", 30);
    
    # fake_dice = Button(120,80,10,450);
    # board = Board(400,400,0,0);
    # main_map = load_map_data();
    # player0 = Player(0, Chess(30,30,main_map["A0"]["x"], main_map["A0"]["y"]));
    # current_objects = (fake_dice, board, player0.chess);
    while is_running:
        time_delta = clock.tick(FPS) / 1000;

        if len(process_queue) == 0:
            print("goodbye");
            is_running = False;
            break;

        if not isinstance(process_queue[0], list):
            print(f"wrong process format: {process_queue[0]}");

        process = process_queue[0][0];
        # print(process);

        if state == "monopoly":
            pass;
        elif state == "battle":
            if process == "init":
                manager.clear_and_reset();
                battle_theme = Battle_Theme(player1, manager);
                process_queue.extend(battle_theme.get_intro());
                process_queue.pop(0);

            elif process == "clear":
                battle_theme.clear();
                process_queue.pop(0);

            elif process == "select":
                battle_theme.show_stats_buttons();
                process_queue.pop(0);

            elif process == "text":
                battle_theme.show_text(process_queue[0][1]);
                process_queue.pop(0);

            elif process == "student_atk":
                battle_theme.student_attack(process_queue[0][1]);
                process_queue.pop(0);

            elif process == "professor_atk":
                battle_theme.professor_attack(process_queue[0][1]);
                process_queue.pop(0);

            elif process == "student_image":
                battle_theme.show_student_state(process_queue[0][1]);
                process_queue.pop(0);

            elif process == "professor_image":
                battle_theme.show_professor_state(process_queue[0][1]);
                process_queue.pop(0);

            elif process == "wait":
                process_queue[0][1] -= time_delta;
                if process_queue[0][1] <= 0:
                    process_queue.pop(0);

            elif process == "weapon":
                battle_theme.show_weapon_animation(process_queue[0][1:]);
                process_queue.pop(0);

            elif process == "stop":
                pass;

            elif process == "check":
                process_queue.extend(battle_theme.check());
                process_queue.pop(0);
            
            else:
                print("case not handled: %s" % process);
                process_queue.pop(0);


        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False;
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass;
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if state == "monopoly":
                    pass;
                elif state == "battle":
                    if process == "stop":
                        process_queue.extend(battle_theme.handle_button_press(event.ui_element));
                        process_queue.pop(0);

            manager.process_events(event);
        manager.update(time_delta);
        
        window_surface.fill(WHITE);
        manager.draw_ui(window_surface);
        
        pygame.display.update();

if __name__ == "__main__":
    main();