import os
import sys
import pygame
import pygame_gui
import csv
import json
import numpy
import random

def rect(left, top, width, height):
    return pygame.rect.Rect(left, top, width, height);

def load_image(image_path):
    try:
        image = pygame.image.load(image_path);
    except Exception as err:
        print("An error occured while loading image: " + str(err));
        image = pygame.image.load("./img/blank.png");
    return image;

# def load_text_file(path):
#     pass;

# UI 介面

class UIButton(pygame_gui.elements.UIButton):
    def __init__(self, rect, text = "", func = None):
        super().__init__(rect, text);
        self.onclick = func;

class UI_Multi_Selection:
    def __init__(self, prob, img, ans, res, tl):
        print("hello");
        ui_manager.clear_and_reset();
        self.problem_statement = pygame_gui.elements.UITextBox(prob, rect(100, 50, 600, 300));
        if img != "":
            self.problem_image = pygame_gui.elements.UIImage(rect(300, 250, 200, 120), load_image(img));
        self.answer_button = [];
        pos = [(100, 400), (420, 400), (100, 500), (420, 500)];
        random.shuffle(pos);
        for i in range(4):
            btn = UIButton(rect(pos[i][0], pos[i][1], 280, 80), ans[i], res[i]);
            self.answer_button.append(btn);

        if tl > 0:
            self.timer = pygame_gui.elements.UIImage(rect(700, 20, 20, 20), load_image("./img/clock.png"));
            self.timer_text = pygame_gui.elements.UILabel(rect(730, 20, 50, 20), self.num_to_time(tl));
        
    def num_to_time(self, t):
        m, s = t // 60, t % 60;
        mm = str(m) if m >= 10 else "0"+str(m);
        ss = str(s) if s >= 10 else "0"+str(s);
        return mm + ":" + ss;

    def count(self, args):
        new_time = args["t"];
        print(new_time);
        self.timer_text.set_text(self.num_to_time(new_time));

    

class UI_Start_Menu:
    def __init__(self, start_func, rules_func):
        ui_manager.clear_and_reset();
        self.title = pygame_gui.elements.UILabel(rect(200, 100, 400, 150), "電機系大冒險");
        self.start_button = UIButton(rect(200, 400, 180, 100), "開始遊戲", start_func);
        self.rules_button = UIButton(rect(420, 400, 180, 100), "規則說明", rules_func);

class UI_Rules_Menu:
    def __init__(self, back_func):
        ui_manager.clear_and_reset();
        with open("./data/rules.txt", encoding="utf8") as file:
            self.text = pygame_gui.elements.UITextBox(file.read(), rect(100, 50, 600, 350));
            self.back_button = UIButton(rect(300, 450, 200, 100), "返回", back_func);
        
class Start_Menu:
    def __init__(self):
        self.name = "Start_Menu";
        self.ui_theme = UI_Start_Menu(self.btn_start, self.btn_rules);

    def btn_start(self):
        pygame.event.post(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":0}));
    
    def btn_rules(self):
        self.ui_theme = UI_Rules_Menu(self.btn_back);

    def btn_back(self):
        self.ui_theme = UI_Start_Menu(self.btn_start, self.btn_rules);

    def handle_button_press(self, button):
        button.onclick();

          
class UI_Battle_Theme:
    def __init__(self, stu, pro, stats, btn_func):
        ui_manager.clear_and_reset();

        self.student = pygame_gui.elements.UIImage(rect(50,300,150,250), load_image("./img/student.png"));
        self.professor = pygame_gui.elements.UIImage(rect(400,50,150,250), load_image("./img/shimingfeng.png"));
        self.shield = pygame_gui.elements.UIImage(rect(50,300,150,250), load_image("./img/student_noshield.png"));

        self.rock = pygame_gui.elements.UIImage(rect(0,0,30,30), load_image("./img/rock.png"));
        self.c8763 = pygame_gui.elements.UIImage(rect(0,0,150,100), load_image("./img/c8763_1.png"));
        self.textbox = pygame_gui.elements.UITextBox("", rect(250, 400, 250, 150));

        self.student.health_capacity = 50;
        self.student.current_health = stu["hp"];
        self.student_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(rect(50,550,150,30), sprite_to_monitor = self.student);
        self.professor.health_capacity = 50;
        self.professor.current_health = pro["hp"];
        self.professor_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(rect(400,300,150,30), sprite_to_monitor = self.professor);
       
        self.stats_buttons = [];
        for i in range(4):
            btn = UIButton(rect(600,350+i*50,150,40), stats[i], btn_func[i]);
            # btn.btnid = i;
            if stats[i] == "???":
                btn.disable();
            self.stats_buttons.append(btn);

        self.show_student(stu);
        self.show_professor(pro);
        self.show_shield(stu);

    def show_clear(self):
        self.rock.hide();
        self.c8763.hide();
        self.textbox.hide();
        for b in self.stats_buttons:
            b.hide();

    def show_student(self, args):
        self.show_clear();
        if args["debuffing"]:
            self.student.set_image(load_image("./img/student_debuff.png"));
        else:
            self.student.set_image(load_image("./img/student.png"));

    def show_professor(self, args):
        self.show_clear();
        if args["raging"] > 0:
            self.professor.set_image(load_image("./img/shimingfeng_rage.png"));
        else:
            self.professor.set_image(load_image("./img/shimingfeng.png"));

    def show_shield(self, args):
        self.show_clear();
        if args["defending"]:
            self.shield.set_image(load_image("./img/student_defend.png"));
        elif args["reflecting"]:
            self.shield.set_image(load_image("./img/student_reflect.png"));
        else:
            self.shield.set_image(load_image("./img/student_noshield.png"));


    def show_text(self, args):
        text = args["text"];
        self.show_clear();
        self.textbox.set_text(text);
        self.textbox.show();

    def show_stats_buttons(self, args = None):
        self.show_clear();
        for b in self.stats_buttons:
            b.show();

    def show_rock(self, args):
        image = load_image(args["image"]);
        pos = args["pos"];
        self.show_clear();
        self.rock.set_image(image);
        self.rock.set_position(pos);
        self.rock.show();

    def show_c8763(self, args):
        image = load_image(args["image"]);
        pos = args["pos"];
        self.show_clear();
        self.c8763.set_image(image);
        self.c8763.set_position(pos);
        self.c8763.show();

    def damage(self, args):
        id, damage = args["id"], args["dmg"];
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

    def reset(self, args = None):
        self.show_student(args);
        self.show_professor(args);
        self.show_shield(args);
        self.show_stats_buttons();


class Battle:
    def __init__(self, player):
        ui_manager.clear_and_reset();
        self.name = "Battle";
        self.player = player;
        self.round = 0;

        self.student_state = {"hp":50, "defending":False, "reflecting":False, "debuffing":False, 
        "good_at_programming": self.player.score["計算機程式設計"] >= 80, 
        "has_vpy_repo": "資訊部長的vpython github repository" in self.player.items.keys()};

        self.professor_state = {"hp":50, "raging":0};

        self.stats = [];
        self.button_functions = [];
        self.get_stat("投石器", "丟石頭");
        self.get_stat("防守", "防守");
        self.get_stat("電神的守護", "???");
        self.get_stat("星爆氣流斬", "???");

        self.problemset = self.get_problemset();

        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);

        self.timer = 0;
        self.get_intro();
        self.reset_round();

    def get_stat(self, name1, name2):
        if name1 in self.player.items.keys():
            self.stats.append(name1);
            self.button_functions.append(lambda:self.new_round(name1));
        else:
            self.stats.append(name2);
            self.button_functions.append(lambda:self.new_round(name2));

    def get_problemset(self):
        temp = [];
        with open("./data/physics.csv") as file:
            reader = csv.reader(file);
            for each_row in reader:
                temp.append(each_row);
        return temp;


    def push(self, func, time = -1, **kwargs):
        kwargs["func"] = func;
        if time != -1:
            t = time;
        else:
            t = self.timer + 0.1;
        pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(), kwargs), int(t*1000), 1);
    
    def new_round(self, stat):
        student_stat = stat;
        professor_stat = self.get_professor_stat(student_stat);

        self.timer = 0;

        temp = self.generate_student_atk_event(student_stat);
        res = self.check_win_condition();
        if temp != 0 or res != 0:
            return;

        temp = self.generate_professor_atk_event(professor_stat);
        res = self.check_win_condition();
        if temp != 0 or res != 0:
            return;
            
        self.reset_round();

    def check_win_condition(self):
        if self.student_state["hp"] <= 0:
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":-1}), int(self.timer*1000), 1);
            return -1;
        elif self.professor_state["hp"] <= 0:
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":1}), int(self.timer*1000), 1);
            return 1;
        else:
            return 0;

    def reset_round(self):
        self.round += 1;
        self.student_state["defending"] = False;
        self.student_state["reflecting"] = False;
        self.professor_state["raging"] = max(self.professor_state["raging"]-1, 0);

        self.push(self.ui_theme.reset, defending = False, reflecting = False, debuffing = self.student_state["debuffing"], raging = self.professor_state["raging"]);

    def get_professor_stat(self, stat):
        seed = random.randint(1,10);
        if self.round == 1:
            return "投石器";
        elif self.round == 2:
            return "定時炸彈";
        elif self.round == 3: #vpython
            return "vpython作業";
        elif stat == "電神的守護": # 若沒rage則rage, 否則50%炸彈50%投石器
            if self.professor_state["raging"] > 0:
                if seed <= 5:
                    return "定時炸彈";
                else:
                    return "投石器";
            else:
                return "盪鞦韆";
        else: # 20% rage(若沒rage), 20% bomb, 否則投石器
            if seed <= 2 and self.professor_state["raging"] == 0:
                return "盪鞦韆";
            elif seed <= 4:
                return "定時炸彈";
            else:
                return "投石器";
            
    def generate_student_atk_event(self, stat_name):
        self.push(self.ui_theme.show_text, text = f"你使用了 {stat_name} !");
        self.timer += 2;

        damage = 0;
        if stat_name == "丟石頭":
            damage = 5;
            if self.student_state["debuffing"]:
                damage //= 5;
            self.generate_weapon_animation(0, damage);
            # if damage <= 5:
            #     queue.append([self.show_text, "效果不是很好..."]);
            #     queue.append(["wait", 2]);
        elif stat_name == "投石器":
            damage = 10;
            if self.student_state["debuffing"]:
                damage //= 5;
            self.generate_weapon_animation(0, damage);
            # if damage <= 5:
            #     queue.append([self.show_text, "效果不是很好..."]);
            #     queue.append(["wait", 2]);
        elif stat_name == "防守":
            self.student_state["defending"] = True;
            self.push(self.ui_theme.show_shield, defending = True, reflecting = False);
            self.timer += 1;
            self.push(self.ui_theme.show_text, text = "你這回合受到的傷害將減少50%!");
            self.timer += 2;

        elif stat_name == "電神的守護":
            self.student_state["reflecting"] = True;
            self.push(self.ui_theme.show_shield, reflecting = True, defending = False);
            self.timer += 1;

        elif stat_name == "星爆氣流斬":
            damage = 16;
            self.generate_weapon_animation(2, damage);

        self.professor_state["hp"] -= damage;
        return 0;

    def generate_professor_atk_event(self, stat_name):
        self.push(self.ui_theme.show_text, text = f"石明豐使用了 {stat_name} !");
        self.timer += 2;

        damage = 0;
        reverse = False;

        if stat_name == "投石器":
            damage = 10;
            if self.professor_state["raging"] > 0:
                damage = 15;
            if self.student_state["defending"]:
                damage //= 2;
            if self.student_state["reflecting"]:
                if random.randint(1,2) == 1: # success
                    reverse = True;
                    self.generate_weapon_animation(1, 0);
                    self.generate_weapon_animation(0, damage);
                    self.push(self.ui_theme.show_text, text = "反擊成功!");
                    self.timer += 2;
                else: # fail
                    self.generate_weapon_animation(1, damage);
                    self.push(self.ui_theme.show_text, text = "反擊失敗...");
                    self.timer += 2;

            else:
                self.generate_weapon_animation(1, damage);

        elif stat_name == "盪鞦韆":
            self.professor_state["raging"] = 4;
            self.push(self.ui_theme.show_professor, raging = 4);
            self.timer += 1;
            self.push(self.ui_theme.show_text, text = "石明豐的傷害增加了!");
            self.timer += 2;
            
        elif stat_name == "vpython作業":
            if self.student_state["good_at_programming"]:
                self.push(self.ui_theme.show_text, text = "因為你很會寫程式，所以絲毫不受影響!");
                self.timer += 2;
            elif self.student_state["has_vpy_repo"]:
                self.push(self.ui_theme.show_text, text = "因為你擁有「資訊部長的vpython github repository」，所以絲毫不受影響!");
                self.timer += 2;
            else:
                self.student_state["debuffing"] = True;
                self.push(self.ui_theme.show_student, debuffing = True);
                self.timer += 1;
                self.push(self.ui_theme.show_text, text = "你的 {} 傷害減少80%!".format(self.stats[0]));
                self.timer += 2;

        elif stat_name == "定時炸彈":
            damage = 0;
            self.generate_weapon_animation(3, damage);
            return 1;

        if reverse:
            self.professor_state["hp"] -= damage;
        else:
            self.student_state["hp"] -= damage;

        return 0;

    def generate_weapon_animation(self, weapon_type, total_damage):
        if weapon_type == 0: # rock
            for i in range(10):
                x = 200 + i * 15;
                y = 0.005 * (x-350)**2 + 200;
                self.push(self.ui_theme.show_rock, image = "./img/rock.png", pos = (x, y));
                self.timer += 0.05;

            self.push(self.ui_theme.damage, id = 1, dmg = total_damage);

        elif weapon_type == 1: # professor rock
            for i in range(10):
                x = 200 + (10-i) * 15;
                y = 0.005 * (x-350)**2 + 200;
                self.push(self.ui_theme.show_rock, image = "./img/rock.png", pos = (x, y));
                self.timer += 0.05;

            self.push(self.ui_theme.damage, id = 0, dmg = total_damage);
            
        elif weapon_type == 2: # c8763
            for i in range(8):
                self.push(self.ui_theme.show_c8763, image = "./img/c8763_1.png", pos = (400, 150));
                self.push(self.ui_theme.damage, id = 1, dmg = total_damage // 16);
                self.timer += 0.05;
                self.push(self.ui_theme.show_c8763, image = "./img/c8763_2.png", pos = (400, 150));
                self.push(self.ui_theme.damage, id = 1, dmg = total_damage // 16);
                self.timer += 0.05;

        elif weapon_type == 3: # bomb
            for i in range(10):
                x = 200 + (10-i) * 15;
                y = 0.005 * (x-350)**2 + 200;
                self.push(self.ui_theme.show_rock, image = "./img/bomb.png", pos = (x, y));
                self.timer += 0.05;

            self.timer += 0.1;
            self.push(self.generate_selecting_problem);

        self.timer += 0.2;

    def get_intro(self):
        self.push(self.ui_theme.show_text, text = "石明豐出現了!");
        self.timer += 2;

    def generate_selecting_problem(self, args):
        self.timer = 0;
        self.in_problem = True;
        idx = random.randint(0, len(self.problemset)-1);
        text, img, ans, res = self.problemset[idx][0], self.problemset[idx][1], self.problemset[idx][2:6], self.problemset[idx][6:10];
        func_list = [];
        print(res);
        for i in range(4):
            if res[i] == "1":
                func_list.append(self.right_answer);
            else:
                func_list.append(self.wrong_answer);
        
        self.ui_theme = UI_Multi_Selection(text, img, ans, func_list, 10);
        self.push(self.do_count, t = 10);

    def do_count(self, args):
        t = args["t"];
        if self.in_problem:
            self.push(self.ui_theme.count, t = t);
            if t == 0:
                self.push(self.time_is_up);
            else:
                self.push(self.do_count, time = 1, t = t - 1);

    def right_answer(self):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "恭喜你答對了，成功躲避了傷害!");
        self.timer += 2;
        self.check_win_condition();
        self.reset_round();

    def wrong_answer(self):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "你答錯了!");
        self.timer += 2;
        damage = 30;
        if self.professor_state["raging"] > 0:
            damage = 45;
        if self.student_state["defending"]:
            damage //= 2;
        self.student_state["hp"] -= damage;
        self.push(self.ui_theme.damage, id = 0, dmg = damage);
        res = self.check_win_condition();
        if res != 0:
            return;
        self.reset_round();

    def time_is_up(self, args):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "時間到了!");
        self.timer += 2;
        damage = 30;
        if self.professor_state["raging"] > 0:
            damage = 45;
        if self.student_state["defending"]:
            damage //= 2;
        self.student_state["hp"] -= damage;
        self.push(self.ui_theme.damage, id = 0, dmg = damage);
        res = self.check_win_condition();
        if res != 0:
            return;
        self.reset_round();

        



class UI_CSWAP_Theme:
    def __init__(self):
        pass;

class Selecting_Problem:
    def __init__(self, path):
        self.problem_list = [];
        with open(path) as file:
            # 題目敘述 圖片連結 A B C D 答案
            try:
                reader = csv.reader(file);
                for each_row in reader:
                    self.problem_list.append(each_row);

            except Exception as err:
                print("An error occured while importing data files: " + str(err));
        self.length = len(self.problem_list);

    


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

class Game:
    def __init__(self):
        self.player_list = [];
        self.current_game_stage = Start_Menu();

    def initialize_new_stage(self, args = dict()):
        Stage, return_value = args["name"], args["value"];
        
        if Stage == "Start_Menu":
            if return_value == 0:
                self.current_game_stage = Battle(player0);

        if Stage == "Battle":
            if return_value == 1:
                print("You won!");
            elif return_value == -1:
                print("You lose!");


def main():
    pygame.init();

    WINDOW_WIDTH = 800;
    WINDOW_HEIGHT = 600;
    WHITE = (255,255,255);
    FPS = 60;
    is_running = True;
    # state = None; # 目標是不要用到這個state，但可做為debug用
    # process_queue = list(); # 可以存入文字或類別的方法
    # animation_queue = [];

    window_surface = pygame.display.set_mode((WINDOW_WIDTH,WINDOW_HEIGHT));
    pygame.display.set_caption("電機系大冒險");
    clock = pygame.time.Clock();

    global ui_manager, NEW_STAGE, RUN_ANIMATION, TIME_IS_UP;

    ui_manager = pygame_gui.UIManager((800,600), "./data/theme.json");
    ui_manager.set_locale("zh");

    NEW_STAGE = pygame.event.custom_type();
    TIME_IS_UP = pygame.event.custom_type();

    # start game
    game = Game();

    while is_running:
        time_delta = clock.tick(FPS) / 1000;

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                is_running = False;

            elif event.type == pygame.MOUSEBUTTONDOWN:
                pass;
                
            elif event.type == pygame_gui.UI_BUTTON_PRESSED:
                # game.current_game_stage.handle_button_press(event.ui_element);
                event.ui_element.onclick();

            elif event.type == NEW_STAGE:
                game.initialize_new_stage(event.__dict__);
            
            elif event.type == TIME_IS_UP:
                pass;

            else:
                if "func" in event.__dict__:
                    event.func(event.__dict__);


            ui_manager.process_events(event);

        ui_manager.update(time_delta);
        
        window_surface.fill(WHITE);
        ui_manager.draw_ui(window_surface);
        
        pygame.display.update();


if __name__ == "__main__":
    main();