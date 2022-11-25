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
    def __init__(self, player):
        self.player = player;
        self.student = pygame_gui.elements.UIImage(pygame.rect.Rect(50,300,150,250), pygame.image.load("./img/student.png"));
        self.professor = pygame_gui.elements.UIImage(pygame.rect.Rect(400,50,150,250), pygame.image.load("./img/shimingfeng.png"));
        self.textbox = pygame_gui.elements.UITextBox("", pygame.rect.Rect(250, 400, 250, 150));
        self.weapon = pygame_gui.elements.UIImage(pygame.rect.Rect(0,0,30,30), pygame.image.load("./img/rock.png"));
        self.round = 0;
        self.student.hp = 50
        self.student.health_capacity = 50;
        self.student.current_health = 50;
        self.student_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.rect.Rect(50,550,150,30), sprite_to_monitor = self.student);

        self.student.defending = False;
        self.student.reflecting = False;
        self.student.debuffing = False;
        self.student.good_at_programming = self.player.score["計算機程式設計"] >= 80;
        self.student.has_vpy_repo = "資訊部長的vpython github repository" in self.player.items.keys();
        # self.student.has_rock_thrower = "投石器" in self.player.items.keys();
        self.professor.hp = 50;
        self.professor.health_capacity = 50;
        self.professor.current_health = 50;
        self.professor_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(pygame.rect.Rect(400,300,150,30), sprite_to_monitor = self.professor);
        self.professor.raging = 0;

        self.stats = [];
        self.stats_button = [];
        self.get_stat("投石器", "丟石頭");
        self.get_stat("防守", "防守");
        self.get_stat("電神的守護", "???");
        self.get_stat("星爆氣流斬", "???");

        for i in range(0,4):
            self.stats_button.append(pygame_gui.elements.UIButton(pygame.rect.Rect(600,350+i*50,150,40), self.stats[i]));
            self.stats_button[i].btnid = i;
            if self.stats[i] == "???":
                self.stats_button[i].disable();

    def get_stat(self, name1, name2):
        if name1 in self.player.items.keys():
            self.stats.append(name1);
        else:
            self.stats.append(name2);

    def show_clear(self, args = None):
        self.textbox.hide();
        for i in range(4):
            self.stats_button[i].hide();
        self.weapon.hide();

    def show_text(self, text):
        self.show_clear();
        self.textbox.set_text(text);
        self.textbox.show();

    def show_stats_buttons(self, args = None):
        self.show_clear();
        for i in range(0,4):
            self.stats_button[i].show();

    def show_weapon(self, args):
        self.show_clear();
        self.weapon.set_image(pygame.image.load(args[0]));
        self.weapon.set_position((args[1], args[2]));
        self.weapon.set_dimensions((args[3], args[4]));
        self.weapon.show();

    def show_student_image(self, new_state):
        self.student.set_image(pygame.image.load(new_state));

    def show_professor_image(self, new_state):
        self.professor.set_image(pygame.image.load(new_state));

    def get_professor_stat(self, stat):
        seed = random.randint(1,10);
        if self.round == 1:
            return "投石器";
        elif self.round == 2:
            return "定時炸彈";
        elif self.round == 3: #vpython
            return "vpython作業";
        elif stat == "電神的守護": # 若沒rage則rage, 否則50%炸彈50%投石器
            if self.professor.raging:
                if seed <= 5:
                    return "定時炸彈";
                else:
                    return "投石器";
            else:
                return "盪鞦韆";
        else: # 20% rage(若沒rage), 20% bomb, 否則投石器
            if seed <= 2 and not self.professor.raging:
                return "盪鞦韆";
            elif seed <= 4:
                return "定時炸彈";
            else:
                return "投石器";
            
    def generate_student_atk_event(self, stat_name):
        queue = [];
        queue.append([self.show_text, f"你使用了 {stat_name} !"]);
        queue.append(["Wait",2]);
        damage = 0;

        if stat_name == "丟石頭":
            damage = 5;
            if self.student.debuffing:
                damage //= 5;
            queue.extend(self.generate_weapon_animation(0, damage));
            # if damage <= 5:
            #     queue.append([self.show_text, "效果不是很好..."]);
            #     queue.append(["wait", 2]);
        elif stat_name == "投石器":
            damage = 10;
            if self.student.debuffing:
                damage //= 5;
            queue.extend(self.generate_weapon_animation(0, damage));
            # if damage <= 5:
            #     queue.append([self.show_text, "效果不是很好..."]);
            #     queue.append(["wait", 2]);
        elif stat_name == "防守":
            self.student.defending = True;
            queue.append([self.show_clear, 0]);
            queue.append([self.show_student_image, "./img/student_defend.png"]);
            queue.append(["Wait", 1]);
            queue.append([self.show_text, "你這回合受到的傷害將減少50%!"]);
            queue.append(["Wait", 2]);

        elif stat_name == "電神的守護":
            self.student.reflecting = True;
            queue.append([self.show_clear, 0]);
            queue.append([self.show_student_image, "./img/student_reflect.png"]);
            queue.append(["Wait", 1])

        elif stat_name == "星爆氣流斬":
            damage = 16;
            queue.extend(self.generate_weapon_animation(1, damage));

        self.professor.hp -= damage;
        return queue;

    def generate_professor_atk_event(self, stat_name):
        queue = [];
        queue.append([self.show_text, f"石明豐使用了 {stat_name} !"]);
        queue.append(["wait",2]);
        damage = 0;
        reverse = False;

        if stat_name == "投石器":
            damage = 10;
            if self.professor.raging > 0:
                damage = 15;
            if self.student.defending:
                damage //= 2;
            if self.student.reflecting:
                if random.randint(1,2) == 1: # success
                    reverse = True;
                    queue.extend(self.generate_weapon_animation(2, 0));
                    queue.extend(self.generate_weapon_animation(0, damage));
                    queue.append([self.show_text, "反擊成功!"]);
                    queue.append(["wait", 2]);
                else: # fail
                    queue.extend(self.generate_weapon_animation(2, damage));
                    queue.append([self.show_text, "反擊失敗..."]);
                    queue.append(["wait", 2]);
            else:
                queue.extend(self.generate_weapon_animation(2, damage));

        elif stat_name == "盪鞦韆":
            self.professor.raging = 4;
            queue.append([self.show_clear, 0]);
            queue.append([self.show_professor_image, "./img/shimingfeng_rage.png"]);
            queue.append(["wait", 1]);
            queue.append([self.show_text, "石明豐的傷害增加了!"]);
            queue.append(["wait", 2]);
            
        elif stat_name == "vpython作業":
            if self.student.good_at_programming:
                queue.append([self.show_text, "因為你很會寫程式，所以絲毫不受影響!"]);
                queue.append(["wait", 2]);
            elif self.student.has_vpy_repo:
                queue.append([self.show_text, "因為你擁有「資訊部長的vpython github repository」，所以絲毫不受影響!"]);
                queue.append(["wait", 2]);
            else:
                self.student.debuffing = True;
                queue.append([self.show_clear, 0]);
                queue.append([self.show_student_image, "./img/student_debuff.png"]);
                queue.append(["wait", 1]);
                queue.append([self.show_text, f"你的 {self.stats[0]} 傷害減少80%!"]);
                queue.append(["wait", 2]);

        elif stat_name == "定時炸彈":
            pass;

        if reverse:
            self.professor.hp -= damage;
        else:
            self.student.hp -= damage;

        return queue;

    def generate_weapon_animation(self, weapon_type, total_damage):
        queue = [];
        if weapon_type == 0: # rock
            for i in range(10):
                x = 200 + i * 15;
                y = 0.005 * (x-350)**2 + 200;
                queue.append([self.show_weapon, ["./img/rock.png", x, y, 30, 30]]);
                queue.append(["wait", 0.05]);
            queue.append([self.damage, [1, total_damage]]);
            
        elif weapon_type == 1: # c8763
            for i in range(8):
                queue.append([self.show_weapon, ["./img/c8763_1.png", 400, 150, 150, 100]]);
                queue.append([self.damage, [1, total_damage//16]]);
                queue.append(["wait", 0.05]);
                queue.append([self.show_weapon, ["./img/c8763_2.png", 400, 150, 150, 100]]);
                queue.append([self.damage, [1, total_damage//16]]);
                queue.append(["wait", 0.05]);

        elif weapon_type == 2: # professor rock
            for i in range(10):
                x = 200 + (10-i) * 15;
                y = 0.005 * (x-350)**2 + 200;
                queue.append([self.show_weapon, ["./img/rock.png", x, y, 30, 30]]);
                queue.append(["wait", 0.05]);
            queue.append([self.damage, [0, total_damage]]);

        elif weapon_type == 3: # bomb
            pass;

        return queue;

    def damage(self, args):
        id, damage = args[0], args[1];
        if id == 0: # 學生受到傷害
            if self.student.current_health < damage:
                self.student.current_health = 0;
            else:
                self.student.current_health -= damage;
        elif id == 1: # 教授受到傷害
            if self.professor.current_health < damage:
                self.professor.current_health = 0;
            else:
                self.professor.current_health -= damage;

    def get_intro(self):
        queue = [];
        queue.append([self.show_text, "石明豐出現了!"]);
        queue.append(["Wait", 2]);
        queue.extend(self.new_round());
        return queue;

    def new_round(self):
        queue = [];
        self.round += 1;
        self.student.defending = False;
        self.student.reflecting = False;
        if self.student.debuffing:
            queue.append([self.show_student_image, "./img/student_debuff.png"]);
        else:
            queue.append([self.show_student_image, "./img/student.png"]);
        
        self.professor.raging -= 1;
        
        if self.professor.raging > 0:
            queue.append([self.show_professor_image, "./img/shimingfeng_rage.png"]);
        else:
            queue.append([self.show_professor_image, "./img/shimingfeng.png"]);
        queue.append([self.show_stats_buttons, 0]);
        queue.append(["stop", 0]);
        return queue;

    def student_win(self):
        return [[self.show_text, "你贏了!"], ["wait", 3], ["goodbye", None]];

    def professor_win(self):
        return [[self.show_text, "你輸了!"], ["wait", 3], ["goodbye", None]];

    def handle_button_press(self, button):
        student_stat = self.stats[button.btnid];
        professor_stat = self.get_professor_stat(student_stat);

        queue = [];
        queue.extend(self.generate_student_atk_event(student_stat));
        print(self.professor.current_health);

        if self.student.hp <= 0:
            queue.extend(self.professor_win());
            return queue;
        elif self.professor.hp <= 0:
            queue.extend(self.student_win());
            return queue;
        
        queue.extend(self.generate_professor_atk_event(professor_stat));
        if self.student.hp <= 0:
            queue.extend(self.professor_win());
            return queue;
        elif self.professor.hp <= 0:
            queue.extend(self.student_win());
            return queue;

        queue.extend(self.new_round());
        
        return queue;

# Start Theme

class Start_Theme:
    def __init__(self):
        # self.manager = manager;
        self.title = pygame_gui.elements.UILabel(pygame.rect.Rect(200, 100, 400, 150), "電機系大冒險");
        self.start_button = pygame_gui.elements.UIButton(pygame.rect.Rect(300, 400, 200, 150), "開始遊戲");

    def get_intro(self):
        # queue = list();
        # queue.append(("stop", ()));
        # return queue;
        return [["Stop", None]];

    def handle_button_press(self, button):
        # print(button_name);
        if button == self.start_button:
            return [["NewState", ["Battle", player0]]];

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

# debug 用
player0 = Player(1, None);
player0.add_item("投石器", 1);
player0.add_item("電神的守護", 1);
player0.add_item("星爆氣流斬", 1);

# 之後可以搬到monopoly_theme的class裡面
def load_map_data(mypath = "./data/map.txt"):
    map_data = {};
    with open(mypath) as f:
        for i in f.readlines():
            print(i);
            name, xpos, ypos, is_split, nextname = i.strip().split(",");
            map_data[name] = {"x":int(xpos), "y":int(ypos), "is_split":int(is_split), "next":nextname};
    return map_data;

# def monopoly_init():
#     pass;

# def battle_init(player):
#     pass;

# def cswap_init(player):
#     pass;

def initialize_new_stage(args, queue):
    state = args[0];
    if state == "Start":
        theme = Start_Theme();
        queue.extend(theme.get_intro());
    elif state == "Battle":
        theme = Battle_Theme(args[1]);
        queue.extend(theme.get_intro());

    # queue.extend(theme.get_intro());
    return theme;


def main():
    pygame.init();

    WINDOW_WIDTH = 800;
    WINDOW_HEIGHT = 600;
    WHITE = (255,255,255);
    FPS = 60;
    is_running = True;
    state = None; # 目標是不要用到這個state，但可做為debug用
    process_queue = list(); # 可以存入文字或類別的方法
    # animation_queue = [];

    window_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT));
    pygame.display.set_caption("電機系大冒險");
    clock = pygame.time.Clock();

    manager = pygame_gui.UIManager((800,600));
    manager.set_locale("zh");
    # battle_theme = pygame_gui.UIManager((800,600));

    # start game
    process_queue.append(["NewState", ["Start"]]);
    # state = "start";
    # current_theme = initialize_new_stage(state, process_queue);

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

        # if not isinstance(process_queue[0], list):
        #     print(f"wrong process format: {process_queue[0]}");

        process = process_queue[0][0];
        process_args = process_queue[0][1];
        # print(process, process_args);

        if process == "NewState" or process == "new_state":
            state = process_args[0];
            print("=======new state========");
            print(state);
            manager.clear_and_reset();
            current_theme = initialize_new_stage(process_args, process_queue);
            process_queue.pop(0);

        elif process == "Wait" or process == "wait":
            if process_args < 0:
                process_queue.pop(0);
            else:
                process_queue[0][1] = process_args - time_delta;

        elif process == "Stop" or process == "stop":
            pass;

        elif process == "Goodbye" or process == "goodbye":
            print("goodbye");
            is_running = False;
            break;

        else:
            # print(process, process_args);
            process(process_args);
            process_queue.pop(0);

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False;
            if event.type == pygame.MOUSEBUTTONDOWN:
                pass;
                
            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                # if state == "monopoly":
                #     pass;
                # elif state == "battle":
                #     if process == "stop":
                #         process_queue.extend(battle_theme.handle_button_press(event.ui_element));
                #         process_queue.pop(0);
                process_queue.extend(current_theme.handle_button_press(event.ui_element));
                process_queue.pop(0);
                # print(process_queue);

            manager.process_events(event);
        manager.update(time_delta);
        
        window_surface.fill(WHITE);
        manager.draw_ui(window_surface);
        
        pygame.display.update();

if __name__ == "__main__":
    main();