import os
import sys
import pygame
import pygame_gui
import csv
import json
import numpy as np
import random
import SCLDgame

def rect(left, top, width, height):
    return pygame.rect.Rect(left, top, width, height);

def load_image(image_path):
    try:
        image = pygame.image.load(image_path);
    except Exception as err:
        print("An error occured while loading image: " + str(err));
        image = pygame.image.load("./img/blank.png");
    return image;

def push(func, time = 0, **kwargs):
    kwargs["func"] = func;
    t = time;

    if (time == 0):
        print("Someone is trolling when calling push: ", func);

    pygame.time.set_timer(pygame.event.Event(pygame.event.custom_type(), kwargs), int(t*1000), 1);

# def load_text_file(path):
#     pass;

# UI 介面

class UIButton(pygame_gui.elements.UIButton):
    def __init__(self, rect, text = "", func = None):
        super().__init__(rect, text);
        if func:
            self.onclick = func;
        else:
            self.disable();

class UI_Multi_Selection:
    def __init__(self, prob, img, ans, res, tl, shuf = True):
        ui_manager.clear_and_reset();
        self.problem_statement = pygame_gui.elements.UITextBox(prob, rect(100, 50, 600, 300));
        if img != "":
            self.problem_image = pygame_gui.elements.UIImage(rect(300, 250, 200, 120), load_image(img));
        self.answer_button = [];
        pos = [(100, 400), (420, 400), (100, 500), (420, 500)];
        if shuf:
            random.shuffle(pos);
        for i in range(4):
            btn = UIButton(rect(pos[i][0], pos[i][1], 280, 80), ans[i], res[i]);
            self.answer_button.append(btn);

        if tl > 0:
            self.timer = pygame_gui.elements.UIImage(rect(670, 20, 20, 20), load_image("./img/clock.png"));
            self.timer_text = pygame_gui.elements.UITextBox(self.num_to_time(tl), rect(700, 20, 70, 50));
        
    def num_to_time(self, t):
        m, s = t // 60, t % 60;
        mm = str(m) if m >= 10 else "0"+str(m);
        ss = str(s) if s >= 10 else "0"+str(s);
        return mm + ":" + ss;

    def count(self, t):
        new_time = t;
        # print(new_time);
        self.timer_text.set_text(self.num_to_time(new_time));

    def show_right(self, args):
        for b in self.answer_button:
            b.disable();
        self.res_img = pygame_gui.elements.UIImage(rect(300, 200, 200, 200), load_image("./img/right_ans.png"));

    def show_wrong(self, args):
        for b in self.answer_button:
            b.disable();
        self.res_img = pygame_gui.elements.UIImage(rect(300, 200, 200, 200), load_image("./img/wrong_ans.png"));

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
        self.ui_theme = UI_Start_Menu(self.btn_select_players, self.btn_rules);

    def btn_select_players(self):
        ans = ["1", "2", "3", "4"];
        res = [];
        for i in range(1, 5):
            res.append(self.btn_start(i));
        self.ui_theme = UI_Multi_Selection("請選擇玩家數量:", "", ans, res, -1, False);

    def btn_start(self, player_cnt):
        def func():
            pygame.event.post(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":player_cnt}));
        return func;

    def btn_rules(self):
        self.ui_theme = UI_Rules_Menu(self.btn_back);

    def btn_back(self):
        self.ui_theme = UI_Start_Menu(self.btn_select_players, self.btn_rules);

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
        # ui_manager.clear_and_reset();
        self.name = "Battle";
        self.player = player;
        self.round = 0;

        self.student_state = {"hp":50, "defending":False, "reflecting":False, "debuffing":False, 
        "good_at_programming": self.player.score["計程"] >= 80, 
        "has_vpy_repo": "vpython_repo" in self.player.items.keys()};

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
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":(self.player.id,-1)}), int(self.timer*1000), 1);
            return -1;
        elif self.professor_state["hp"] <= 0:
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":(self.player.id, 1)}), int(self.timer*1000), 1);
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

        elif stat_name == "投石器":
            damage = 10;
            if self.student_state["debuffing"]:
                damage //= 5;
            self.generate_weapon_animation(0, damage);

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
                self.push(self.ui_theme.show_text, text = "因為你擁有 vpython 的 repository，所以絲毫不受影響!");
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

        elif weapon_type == 4: # bomb_explode
            x = 200;
            y = 0.005 * (x-350) ** 2 + 200;
            self.push(self.ui_theme.show_rock, image = "./img/bomb.png", pos = (x, y));
            self.timer += 0.5;
            self.push(self.ui_theme.show_rock, image = "./img/bomb_explode.png", pos = (x, y));
            self.timer += 1;

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
        # print(res);
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
            self.ui_theme.count(t = t);
            if t == 0:
                self.push(self.time_is_up);
            else:
                self.push(self.do_count, time = 1, t = t - 1);

    def right_answer(self):
        self.in_problem = False;
        self.timer = 0;
        self.push(self.ui_theme.show_right);
        self.timer += 2;
        self.push(self.return_as_right);
    
    def return_as_right(self, args):
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "恭喜你答對了，成功躲避了傷害!");
        self.timer += 2;
        self.check_win_condition();
        self.reset_round();

    def wrong_answer(self):
        self.in_problem = False;
        self.timer = 0;
        self.push(self.ui_theme.show_wrong);
        self.timer += 2;
        self.push(self.return_as_wrong);

    def return_as_wrong(self, args):
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "你答錯了!");
        self.timer += 2;
        damage = 30;
        if self.professor_state["raging"] > 0:
            damage = 45;
        if self.student_state["defending"]:
            damage //= 2;
        self.generate_weapon_animation(4, damage);
        self.student_state["hp"] -= damage;
        self.push(self.ui_theme.damage, id = 0, dmg = damage);
        res = self.check_win_condition();
        if res != 0:
            return;
        self.reset_round();

    def time_is_up(self, args):
        self.in_problem = False;
        self.timer = 0;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.professor_state, self.stats, self.button_functions);
        self.push(self.ui_theme.show_text, text = "時間到了!");
        self.timer += 2;
        damage = 30;
        if self.professor_state["raging"] > 0:
            damage = 45;
        if self.student_state["defending"]:
            damage //= 2;
        self.generate_weapon_animation(4, damage);
        self.student_state["hp"] -= damage;
        self.push(self.ui_theme.damage, id = 0, dmg = damage);
        res = self.check_win_condition();
        if res != 0:
            return;
        self.reset_round();


class UI_map:
    def __init__(self, list_of_players, which_round, x_list, y_list, imgs, roll_func, pack_func, data_func, lb_data):
        ui_manager.clear_and_reset();
        self.current_id = which_round;
        self.current_player = list_of_players[which_round];
        self.img_path = imgs[which_round];
        self.map_image = pygame_gui.elements.UIImage(rect(110, 10, 400, 400), load_image("./img/map.png"));
        self.chess_image = [pygame_gui.elements.UIImage(rect(x_list[i], y_list[i], 30, 30), load_image(imgs[i])) for i in range(len(imgs))];
        self.cur_player_name = pygame_gui.elements.UILabel(rect(75, 450, 150, 100), self.current_player.name);
        self.cur_player_image = pygame_gui.elements.UIImage(rect(40, 480, 60, 60), load_image(self.img_path))
        self.roll_btn = UIButton(rect(250, 450, 150, 100), "擲骰子", roll_func);
        self.backpack_btn = UIButton(rect(425, 450, 150, 100), "背包", pack_func);
        self.data_btn = UIButton(rect(600, 450, 150, 100), "玩家資訊", data_func);
        self.leaderboard = [pygame_gui.elements.UITextBox(lb_data[i], rect(550, 50 + i * 70, 150, 60)) for i in range(len(lb_data))];
        self.dice_image = pygame_gui.elements.UIImage(rect(200, 100, 250, 150), load_image("./img/dice_1.png"));
        self.dice_image.hide();
        self.walking_options_buttons = [];

    def hide_everything(self, args):
        self.roll_btn.hide();
        self.backpack_btn.hide();
        self.data_btn.hide();

    def show_dice(self, args):
        points = args["pts"];
        self.dice_image.show();
        self.dice_image.set_image(load_image("./img/dice_"+str(points)+".png"));

    def hide_dice(self, args):
        self.dice_image.hide();

    def show_walking_options(self, args):
        pos, func = args["pos"], args["btn_func"];
        self.walking_options_buttons.clear();
        for i in range(len(pos)):
            self.walking_options_buttons.append(UIButton(rect(pos[i][0], pos[i][1], 30, 30), "v", func[i]));

    def hide_walking_options(self, args):
        for each_b in self.walking_options_buttons:
            each_b.kill();

    def move_to(self, args):
        pos = args["pos"];
        self.chess_image[self.current_id].set_position(pos);

    def show_info(self, args):
        text = args["text"]
        self.info = pygame_gui.elements.UITextBox(text, rect(300, 200, 200, 100));

    def hide_info(self, args):
        self.info.kill();


class UI_Backpack:
    def __init__(self, player, pack_element, lb_func, rb_func, return_func, item_data):
        ui_manager.clear_and_reset();

        self.title = pygame_gui.elements.UILabel(rect(300, 25, 200, 100), player.name + "的背包");
        self.items_list = [];
        name, cnt, img ,desc, usable, func = pack_element["name"], pack_element["cnt"], pack_element["img"], pack_element["desc"], pack_element["usable"], pack_element["func"];
        for i in range(len(name)):
            obj_name = name[i];
            obj_cnt = "數量: " + str(cnt[i]);
            obj_img = img[i];
            obj_desc = desc[i];
            obj_usable = usable[i];
            obj_func = func[i];
            
            self.items_list.append(pygame_gui.elements.UITextBox(obj_name, rect(150, 150+90*i, 100, 80)));
            if obj_img != "":
                self.items_list.append(pygame_gui.elements.UIImage(rect(50, 150+90*i, 80, 80), load_image(obj_img)));
            if obj_usable == "Y" or obj_usable == "y":
                self.items_list.append(pygame_gui.elements.UITextBox(obj_desc, rect(250, 150+90*i, 320, 80)));
                self.items_list.append(pygame_gui.elements.UITextBox(obj_cnt, rect(570, 150+90*i, 80, 80)));
                self.items_list.append(UIButton(rect(670, 150+90*i, 80, 80), "使用", obj_func));
            else:
                self.items_list.append(pygame_gui.elements.UITextBox(obj_desc, rect(250, 150+90*i, 400, 80)));


        self.left_btn = UIButton(rect(200, 520, 100, 50), "<", lb_func);
        self.right_btn = UIButton(rect(500, 520, 100, 50), ">", rb_func);

        self.return_btn = UIButton(rect(720, 540, 60, 40), "返回", return_func);


class UI_Info:
    def __init__(self, player, return_func):
        ui_manager.clear_and_reset();
        
        self.title = pygame_gui.elements.UILabel(rect(300, 25, 200, 100), player.name + "的玩家資訊");
        info_text = "";
        info_text += "錢:"+str(player.money);
        info_text += "\n體力:"+str(player.health);
        info_text += "\n學分數:"+str(player.total_degree);
        info_text += "\n微積分成績:"+str(player.score["微積分"]);
        info_text += "\n普物成績:"+str(player.score["普物"]);
        info_text += "\n計算機程式成績:"+str(player.score["計程"]);
        info_text += "\n交電成績:"+str(player.score["交電"]);
        info_text += "\n普化成績:"+str(player.score["普化"]);
        info_text += "\n個性簽名:這個人很懶什麼都沒留下來\n"
        self.info = pygame_gui.elements.UITextBox(info_text, rect(200, 150, 400, 350));

        self.return_btn = UIButton(rect(720, 540, 60, 40), "返回", return_func);

class Monopoly:
    def __init__(self, list_of_players, which_round, ret_from = "Normal", ret_val = 0):
        self.name = "Monopoly";
        self.map_data = self.load_map_data();
        self.item_data = self.load_item_data();
        self.list_of_players = list_of_players;
        self.current_id = which_round;
        self.player_cnt = len(list_of_players);
        self.current_player = self.list_of_players[self.current_id];

        self.init_main_ui();

        if ret_from == "SCLD":
            push(self.ui_theme.show_info, 0.1, text = "時間到!\n" + str(self.current_player.name) + "這次的分數是" + str(ret_val) + "分");
            self.current_player.change_score("交電", ret_val);
            push(self.ui_theme.hide_info, 2);
            push(self.next_player, 2.1);
        
        elif ret_from == "MF":
            if ret_val == 1:
                push(self.ui_theme.show_info, 0.1, text = "你贏了!\n你獲得了普物成績40分+金幣*100");
                self.current_player.change_score("普物", 40);
                self.current_player.money += 100;
            elif ret_val == -1:
                push(self.ui_theme.show_info, 0.1, text = "你輸了，下次繼續努力!");

            push(self.ui_theme.hide_info, 2);
            push(self.next_player, 2.1);

    def init_main_ui(self):
        sorted_players_list = sorted(self.list_of_players, key = lambda player : player.total_degree, reverse = True);
        leaderboard_data = [];
        idx = 1;
        for i in range(self.player_cnt):
            if i > 0 and sorted_players_list[i].total_degree < sorted_players_list[i-1].total_degree:
                idx = i+1;
            leaderboard_data.append("#"+str(idx)+" "+sorted_players_list[i].name+" "+str(sorted_players_list[i].total_degree));
        # print(self.map_data);
        real_x, real_y = list(), list();
        for player in self.list_of_players:
            real_x.append(self.to_real_pos(player.pos)[0]);
            real_y.append(self.to_real_pos(player.pos)[1]);
        imgs = ["./img/player_"+str(i+1)+".png" for i in range(self.player_cnt)];

        self.ui_theme = UI_map(self.list_of_players, self.current_id, real_x, real_y, imgs, self.roll, self.pack, self.dt, leaderboard_data);

    def load_map_data(self, mypath = "./data/map.csv"):
        map_data = [];
        with open(mypath) as f:
            reader = csv.reader(f);
            for r in reader:
                if len(r) < 5 or r[0] == "":
                    continue;
                temp = {"id":int(r[0]), "x":int(r[1]), "y":int(r[2]), "next":[int(t) for t in r[3].split(";")], "type":r[4]};
                # if temp["type"] == "起點":
                #     print(temp["id"]);
                map_data.append(temp);

        return map_data;

    def to_real_pos(self, idx):
        return (self.map_data[idx]["y"] * 36.5 + 110, self.map_data[idx]["x"] * 33.8 + 10);

    def load_item_data(self, mypath = "./data/items.csv"):
        item_data = {};
        with open(mypath) as f:
            reader = csv.DictReader(f);
            for r in reader:
                item_data[r["name"]] = r;
        
        return item_data;

    def roll(self):
        timer = 0.1;
        push(self.ui_theme.hide_everything, 0.05);
        if self.current_player.dice == "teleport":
            real_pos, funcs = list(), list();
            for i in range(1, len(self.map_data)):
                real_pos.append(self.to_real_pos(i));
                funcs.append(self.get_teleport_buttons(i));

            push(self.ui_theme.show_info, 0.1, text = "你使用了傳送門，請選擇你要傳送到的地點");
            push(self.ui_theme.hide_info, 2);
            push(self.ui_theme.show_walking_options, 2.1, pos = real_pos, btn_func = funcs);

        elif self.current_player.dice == "scld":
            pts = random.randint(0, 1);
            for i in range(10):
                push(self.ui_theme.show_dice, timer, pts = random.randint(0, 1));
                timer += 0.1;
            push(self.ui_theme.show_dice, timer, pts = pts);
            timer += 2;
            push(self.ui_theme.hide_dice, timer);
            push(self.try_to_walk, timer, steps_left = pts);

        else:
            pts = random.randint(1, 6);
            for i in range(10):
                push(self.ui_theme.show_dice, timer, pts = random.randint(1, 6));
                timer += 0.1;
            push(self.ui_theme.show_dice, timer, pts = pts);
            timer += 2;
            push(self.ui_theme.hide_dice, timer);
            push(self.try_to_walk, timer, steps_left = pts);

        self.current_player.dice = "normal"

    def get_teleport_buttons(self, pos):
        def func():
            push(self.ui_theme.hide_walking_options, 0.05);
            push(self.ui_theme.move_to, 0.1, pos = self.to_real_pos(pos));
            self.current_player.from_pos = 0;
            self.current_player.pos = pos;
            push(self.generate_round_event, 1);
        return func;

    def try_to_walk(self, args):
        steps_left = args["steps_left"];
        if steps_left == 0:
            push(self.generate_round_event, 1);
            return;

        cur_pos, last_pos = self.current_player.pos, self.current_player.from_pos;
        next_list = [];
        for i in self.map_data[cur_pos]["next"]:
            if i != last_pos:
                next_list.append(i);
        
        # debug
        # print("steps_left: ", steps_left);
        # print(cur_pos, last_pos);
        # print(next_list);

        if len(next_list) == 1:
            real_pos = self.to_real_pos(next_list[0]);
            push(self.ui_theme.move_to, 0.1, pos = real_pos);
            push(self.try_to_walk, 0.5, steps_left = steps_left - 1);
            self.current_player.from_pos = cur_pos;
            self.current_player.pos = next_list[0];
        
        else:
            real_pos = [self.to_real_pos(i) for i in next_list];
            funcs = [self.get_walking_options_buttons(i, steps_left - 1) for i in next_list];
            push(self.ui_theme.show_walking_options, 0.1, pos = real_pos, btn_func = funcs);

    def get_walking_options_buttons(self, pos, steps_left):
        def func():
            push(self.ui_theme.hide_walking_options, 0.05);
            push(self.ui_theme.move_to, 0.1, pos = self.to_real_pos(pos));
            push(self.try_to_walk, 0.5, steps_left = steps_left);
            self.current_player.from_pos = self.current_player.pos;
            self.current_player.pos = pos;
        return func;

    def pack(self):
        self.max_pages = max(1, (len(self.current_player.items.keys())+3) // 4);
        self.ui_theme = UI_Backpack(self.current_player, self.get_backpack_items(1), self.pack_lrbtn_func(0), self.pack_lrbtn_func(2), self.init_main_ui, self.item_data);

    def pack_lrbtn_func(self, pg):
        if pg < 1 or pg > self.max_pages:
            return None;
        def func():
            # self.current_backpack_page = pg;
            self.ui_theme = UI_Backpack(self.current_player, self.get_backpack_items(pg), self.pack_lrbtn_func(pg-1), self.pack_lrbtn_func(pg+1), self.init_main_ui, self.item_data);
        return func;

    def get_backpack_items(self, page):
        self.full_items_list = [(i, self.current_player.items[i]) for i in sorted(self.current_player.items.keys())];
        l, r = (page-1)*4, min(page*4, len(self.full_items_list));
        obj_name, obj_img, obj_desc, obj_cnt, obj_usable, obj_btn_func = list(), list(), list(), list(), list(), list();
        for i in range(r-l):
            obj = self.full_items_list[l+i][0];
            obj_name.append(obj);
            obj_cnt.append(self.full_items_list[l+i][1]);
            if obj in self.item_data.keys():
                obj_img.append(self.item_data[obj]["img"]);
                obj_desc.append(self.item_data[obj]["desc"]);
                obj_usable.append(self.item_data[obj]["usable"]);
                obj_btn_func.append(self.get_backpack_use_btn_func(obj));
            else:
                obj_img.append("");
                obj_desc.append("來源不明");
                obj_usable.append("N");
                obj_btn_func.append(None);

        return {"name":obj_name, "img":obj_img, "desc":obj_desc, "cnt":obj_cnt, "usable":obj_usable, "func":obj_btn_func};

    def get_backpack_use_btn_func(self, obj):
        if self.item_data[obj]["usable"]:
            return lambda:self.use_item(obj);
        else:
            return None;

    def use_item(self, item_name):
        if item_name == "交電骰":
            self.current_player.add_item(item_name, -1);
            self.current_player.dice = "scld";
        elif item_name == "傳送門":
            self.current_player.add_item(item_name, -1);
            self.current_player.dice = "teleport";
        self.pack()

    def dt(self):
        self.ui_theme = UI_Info(self.current_player, self.init_main_ui);

    def generate_round_event(self, args):
        event_now = self.map_data[self.current_player.pos]["type"];
        print(self.map_data[self.current_player.pos]["type"]);
        list_of_event_types = ['起點', '計程', '體育', '普物', '微積分', '交電',\
            '普化', '國文', 'BOSS', '愛心', '機會命運', '道具', '事件']
        # l_of_event_types = set();
        # for i in self.map_data:
        #     l_of_event_types.add(i["type"]);

        # print(l_of_event_types);
        if event_now == "起點":
            push(self.ui_theme.show_info, 0.1, text = "恭喜你回到了起點，獲得金幣*10與體力*5");
            push(self.ui_theme.hide_info, 2);
            self.current_player.money += 10;
            self.current_player.health += 5;
            push(self.next_player, 2.1);

        elif event_now == "微積分" or event_now == "普物" or event_now == "普化":
            push(self.ui_theme.show_info, 0.1, text = event_now + "題目!!");
            push(self.ui_theme.hide_info, 2);
            push(self.generate_selecting_problem, 2.1, name = event_now);

        elif event_now == "道具" or event_now == "事件" or event_now == "機會命運":
            push(self.ui_theme.show_info, 0.1, text = "機會命運!!");
            push(self.ui_theme.hide_info, 2);
            push(self.generate_pick, 2.1);

        elif event_now == "交電":
            push(self.ui_theme.show_info, 0.1, text = "交電CSWAP遊戲!!");
            push(self.ui_theme.hide_info, 2);
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":(self.current_player, "SCLD")}), 2100, 1);

        elif event_now == "MF":
            push(self.ui_theme.show_info, 0.1, text = "?????");
            push(self.ui_theme.hide_info, 2);
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":(self.current_player, "MF")}), 2100, 1);

            # push(self.next_player, 2.1);
        
        else:
            push(self.ui_theme.show_info, 0.1, text = "這裡沒有任何東西，姑且給你一個金幣作為補償");
            push(self.ui_theme.hide_info, 2);
            self.current_player.money += 1;
            push(self.next_player, 2.1);

    def next_player(self, args):
        self.current_id = (self.current_id + 1) % self.player_cnt;
        self.current_player = self.list_of_players[self.current_id];
        self.init_main_ui();

    def generate_pick(self, args):
        self.event_data, self.nl, self.pl = self.load_pick_data();
        pick = np.random.choice(self.nl, 1, self.pl)[0];
        push(self.ui_theme.show_info, 0.1, text = self.event_data[pick]["desc"]);
        '''
黃教授
頭盔
交電骰
傳送門
X
強制停修
投石器
vpython
文湖線停擺了
教授確診了'''
  
        if pick == "腳踏車":
            self.current_player.health -= 1;
        elif pick == "投石器":
            self.current_player.add_item("投石器", 1);
        elif pick == "黃教授":
            self.current_player.add_item("電神的守護", 1);
        elif pick == "頭盔":
            self.current_player.add_item("星爆氣流斬", 1);
        elif pick == "交電骰":
            self.current_player.add_item("交電骰", 1);
        elif pick == "傳送門":
            self.current_player.add_item("傳送門", 1);
        elif pick == "強制停修":
            self.current_player.add_item("停修單", 1);
        elif pick == "vpython":
            self.current_player.add_item("vpython_repo", 1);
        elif pick == "文湖線停擺了":
            self.current_player.health -= 2;
        elif pick == "教授確診了":
            self.current_player.health += 2;

        push(self.ui_theme.hide_info, 4.9);
        push(self.next_player, 5);
        
    def load_pick_data(self, mypath = "./data/event.csv"):
        pick_data = self.load_item_data(mypath);
        nl, pl = list(), list();
        for key in pick_data.keys():
            nl.append(key);
            pl.append(pick_data[key]["chance"]);

        return pick_data, nl, pl;

    def generate_selecting_problem(self, args):
        self.in_problem = True;
        self.which_problemset = args["name"];
        if args["name"] == "微積分":
            self.problemset = self.get_problemset("./data/calculus.csv");
        elif args["name"] == "普物":
            self.problemset = self.get_problemset("./data/physics.csv");
        elif args["name"] == "普化":
            self.problemset = self.get_problemset("./data/chemistry.csv");

        idx = random.randint(0, len(self.problemset)-1);
        text, img, ans, res = self.problemset[idx][0], self.problemset[idx][1], self.problemset[idx][2:6], self.problemset[idx][6:10];
        func_list = [];
        for i in range(4):
            if res[i] == "1":
                func_list.append(self.right_answer);
            else:
                func_list.append(self.wrong_answer);
        
        self.ui_theme = UI_Multi_Selection(text, img, ans, func_list, 120);
        push(self.do_count, 0.1,t = 120);
        
    def get_problemset(self, path):
        temp = [];
        with open(path) as file:
            reader = csv.reader(file);
            for each_row in reader:
                temp.append(each_row);
        return temp;

    def do_count(self, args):
        t = args["t"];
        if self.in_problem:
            self.ui_theme.count(t = t);
            if t == 0:
                push(self.time_is_up, 0.1);
            else:
                push(self.do_count, 1, t = t - 1);

    def right_answer(self):
        self.in_problem = False;
        push(self.ui_theme.show_right, 0.1);
        push(self.return_as_right, 2);

    def return_as_right(self, args):
        self.init_main_ui();
        push(self.ui_theme.show_info, 0.1, text = "恭喜你答對了，你的" + self.which_problemset + "加10分!");
        self.current_player.change_score(self.which_problemset, 10);
        push(self.ui_theme.hide_info, 2);
        push(self.next_player, 2.1);

    def wrong_answer(self):
        self.in_problem = False;
        push(self.ui_theme.show_wrong, 0.1);
        push(self.return_as_wrong, 2);

    def return_as_wrong(self, args):
        self.init_main_ui();
        push(self.ui_theme.show_info, 0.1, text = "你答錯了，你的" + self.which_problemset + "扣10分!");
        self.current_player.change_score(self.which_problemset, -10);
        push(self.ui_theme.hide_info, 2);
        push(self.next_player, 2.1);

    def time_is_up(self, args):
        self.in_problem = False;
        self.init_main_ui();
        push(self.ui_theme.show_info, 0.1, text = "時間到了!你的" + self.which_problemset + "扣10分!");
        self.current_player.change_score(self.which_problemset, -10);
        push(self.ui_theme.hide_info, 2);
        push(self.next_player, 2.1);

    

class CSWAP:
    def __init__(self, player):
        self.name = "CSWAP";
        ui_manager.clear_and_reset();
        self.current_player = player;
        self.timer = 180;
        difficulty = [2, 3, 3, 4, 4, 5, 5, 6];
        self.score = 0;
        i = 0;
        while True:
            ret_val = SCLDgame.SCLDgame(difficulty[i], self.timer);
            print(ret_val);
            if ret_val == -1:
                break;
            else:
                self.timer -= ret_val;

            self.score += 5 * difficulty[i];
            i += 1;
            i = min(i, len(difficulty)-1);

        pygame.event.post(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":(self.current_player.id, self.score)}));

# Player Data

class Player:
    def __init__(self, i, nm, spos):
        self.id = i;
        self.name = nm;
        self.pos = spos;
        self.from_pos = 0;
        self.money = 10;
        self.health = 5;
        self.total_degree = 0;
        self.dice = "normal";
        self.items = {""};
        self.items = {"傳送門":1, "交電骰":1};
        self.score = {"微積分":0, "普物":0, "計程":0, "交電":0, "普化":0, "生物":0};

    def add_item(self, item_name, count):
        if item_name in self.items.keys():
            self.items[item_name] += count;
        else:
            self.items[item_name] = count;
        if self.items[item_name] == 0:
            self.items.pop(item_name, None);

    def change_score(self, subject, delta):
        if subject == "交電":
            self.score[subject] = max(self.score[subject], delta);
            self.score[subject] = min(100, self.score[subject]);

        else:
            self.score[subject] += delta;
            self.score[subject] = max(0, self.score[subject]);
            self.score[subject] = min(100, self.score[subject]);
            self.calculate_degree();

    def calculate_degree(self):
        temp = 0;
        if self.score["微積分"] >= 90:
            temp += 4;
        elif self.score["微積分"] >= 60:
            temp += 2;
        if self.score["普物"] >= 60:
            temp += 4;
        if self.score["計程"] >= 60:
            temp += 5;
        if self.score["交電"] >= 60:
            temp += 3;
        if self.score["普化"] >= 60:
            temp += 4;
        self.total_degree = temp;


# debug 用
player0 = Player(99, "test", 0);
player0.add_item("投石器", 1);
player0.add_item("電神的守護", 1);
player0.add_item("星爆氣流斬", 1);


class Game:
    def __init__(self):
        self.player_list = [];
        self.start_list = [1, 9, 61, 72];
        self.stage_name = "Start_Menu";
        self.current_game_stage = Start_Menu();

    def initialize_new_stage(self, args = dict()):
        Stage, return_value = args["name"], args["value"];
        
        if Stage == "Start_Menu":
            # 如果你要測試大富翁 就uncomment下面這兩行
            self.new_game(return_value);
            self.current_game_stage = Monopoly(self.player_list, 0);

            # 如果你要測試明豐Battle 就uncomment下面這一行
            # self.current_game_stage = Battle(player0);

            # 如果你要測試交電CSWAP 就uncomment下面這一行
            # self.current_game_stage = CSWAP(player0);

            pass;

        if Stage == "Monopoly":
            if return_value[1] == "SCLD":
                self.current_game_stage = CSWAP(return_value[0]);
            elif return_value[1] == "MF":
                self.current_game_stage = Battle(return_value[0]);
            else:
                print("Something's wrong!!!", Stage, return_value);

        if Stage == "Battle":
            player_id, player_score = return_value;
            self.current_game_stage = Monopoly(self.player_list, player_id, "MF", player_score);
            if player_score == 1:
                print("You won!");
            elif player_score == -1:
                print("You lose!");

        if Stage == "CSWAP":
            player_id, player_score = return_value;
            self.current_game_stage = Monopoly(self.player_list, player_id, "SCLD", player_score);


    def new_game(self, player_cnt):
        self.player_list = [];
        for i in range(player_cnt):
            self.player_list.append(Player(i, "Player" + str(i+1), self.start_list[i]));

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
                # try:
                #     event.ui_element.onclick();
                # except Exception as err:
                #     print(str(Exception));
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