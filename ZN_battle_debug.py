import os
import sys
import pygame
import pygame_gui
import csv
import json
import numpy
import random
import copy

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
        self.title = pygame_gui.elements.UILabel(rect(200, 100, 400, 150), "普林斯頓保衛戰");
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

          
class UI_Battle_Theme_ZN:
    def __init__(self, ZN, TA,student, stats, btn_func):
        ui_manager.clear_and_reset();
        self.student = pygame_gui.elements.UIImage(rect(50,300,150,250), load_image("./img/student.png"));
        self.ZN = pygame_gui.elements.UIImage(rect(400,50,150,250), load_image("./img/ZN.png"));
        self.TA=pygame_gui.elements.UIImage(rect(200,50,150,250), load_image("./img/12345.png"));
        #圖片
        self.ZN.health_capacity = ZN["hp_max"];
        self.ZN.current_health = ZN["hp"];
        self.ZN_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(rect(400,300,150,30), sprite_to_monitor = self.ZN);
        self.TA.health_capacity = TA["hp_max"];
        self.TA.current_health = TA["hp"];
        self.TA_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(rect(400,300,150,30), sprite_to_monitor = self.TA);
        self.student.health_capacity = student["hp_max"];
        self.student.current_health = student["hp"];
        self.student_hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(rect(50,550,150,30), sprite_to_monitor = self.student);
        self.textbox = pygame_gui.elements.UITextBox("", rect(250, 400, 250, 150));

        self.stats_buttons = [];
        for i in range(4):
            btn = UIButton(rect(600,350+i*50,150,40), stats[i], btn_func[i]);
            # btn.btnid = i;
            self.stats_buttons.append(btn);

        # self.show_student(student);
        # self.show_TA(TA);
        # self.show_ZN(ZN);


    def show_clear(self):
        # self.rock.hide();
        # self.c8763.hide();
        self.textbox.hide();
        for b in self.stats_buttons:
            b.hide();

    def show_ZN(self, args):
        self.show_clear();
        self.ZN.set_image(load_image("./img/ZN.png"));

    def show_TA(self, args):
        self.show_clear();
        args = args["TA_state"];
        print(args)
        print("TA_live" in args)
        if args['TA_live'] :
            self.TA.set_image(load_image("./img/"+str(args["stage"])+".png"));


    def show_student(self, args):
        self.show_clear();
        self.student.set_image(load_image("./img/student.png"));
        
    def show_text(self, args):
        text = args["text"];
        self.show_clear();
        self.textbox.set_text(text);
        self.textbox.show();

    def show_stats_buttons(self, args = None):
        self.show_clear();
        for b in self.stats_buttons:
            b.show();
    
    def damage(self):
        if self.ZN.current_health <0:
            self.student.current_health = 0;
        if self.TA.current_health <0:
            self.TA.current_health = 0;
        if self.student.current_health <0:
            self.student.current_health = 0;

    def reset(self, args = None):
        self.show_ZN(args);
        self.show_TA(args);
        self.show_student(args);
        self.show_stats_buttons();


class ZN_Battle:
    def __init__(self, player):
        ui_manager.clear_and_reset();
        self.name = "ZN_Battle";
        self.player = player;
        self.round = 1;

        self.student_state = {"hp":50, "hp_max":50,"buff":False,"buff_2":False,"four_spirit":False,"reverse":False};
        self.TA_state= {"hp":50,"hp_max":50,"TA_live":False,"stage":0,"attack_fail":False};
        self.ZN_state = {"hp":500, "hp_max":500,"attack_fail":False};

        
        self.ZN_stats=[];
        self.TA_stats=[];
        self.student_stats = [];
        self.button_functions = [];
        self.ZN_get_stat();#創造技能
        self.TA_get_stat();        
        self.student_get_stat();

        self.ZN_damage=0
        self.TA_damage=0
        self.student_damage=0


        self.problemset = self.get_problemset();

        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme_ZN(self.ZN_state,self.TA_state,self.student_state, self.student_stats, self.button_functions);

        self.timer = 0;
        self.get_intro();
        self.push(self.ui_theme.reset, TA_state = self.TA_state);

    def ZN_get_stat(self):
        skill=["睡覺","滑手機","去外面講電話"]
        if(self.TA_state["stage"]>=4 and self.TA_state["TA_live"]==False):
            skill.append("認真上課")
        else:
            skill.append("召喚助教")
        self.ZN_stats=copy.copy(skill) 
    def TA_get_stat(self):
        skill=["城堡","公寓","你多換行","你多空一格"]
        if(self.TA_state["stage"]==1):
            skill=["城堡","公寓","你多換行","你多空一格"]
        elif(self.TA_state["stage"]==2):
            skill=["範例測資","資料夾","乾坤大挪移","正式測資"]
        elif(self.TA_state["stage"]==3):
            skill=["美編","滾球球","aMAZEng","限制十五分鐘"]
        elif(self.TA_state["stage"]==4):
            skill=["溫柔地回答你問題","給你上機考考古題","非常非常會講課","召喚OJ2助教"]
        self.TA_stats=copy.copy(skill)
    def student_get_stat(self):
        if(self.TA_state["TA_live"]==True and 5<self.round<11):
            skill=["認真蓋城堡","二分搜","暴力","助教拜託期末專題讓我過"]
        elif(self.TA_state["TA_live"]==True and 10<self.round<16):
            skill=["set recursion limit","dfs/bfs","大驚","長期肩負重大的任務"]
        elif(self.TA_state["TA_live"]==True and 15<self.round<21):
            skill=["郭教授確診了","電神演算法","copy","DIJKSTRA"]
        elif(self.TA_state["TA_live"]==True and 15<self.round<21):
            skill=["安裝venv","印海報","上機考卡常","python好棒棒"]
        elif(self.student_state["four_spirit"]==True):
            skill=["呈卷，即面署第一","目光如炬","視學京畿","為除不潔者"]
        else:
            skill=["python好棒棒","某某男教授","正課蹺掉","我要去謝班"]
        for name in skill :
            self.student_stats.append(name);
            self.button_functions.append(lambda:self.new_round(name));

 
    
    def new_round(self,stat):
        print("hello!");
        self.ZN_get_stat();#創造技能
        self.TA_get_stat();        
        self.student_get_stat();



        professor_stat_num = self.get_ZN_stat();#決定技能
        TA_stat_num=self.get_TA_stat();


        self.timer = 0;

        self.generate_enemy_atk_event(professor_stat_num,TA_stat_num);
        self.student_state["hp"]-=self.student_damage
        self.student_damage=0
        res = self.check_win_condition();
        if res !=0:
            return;
        
        damage=self.generate_student_atk_event(stat);
        if(self.student_state["reverse"]==True):
            self.student_state["hp"]-=damage
        else:
            if(self.TA_state["TA_live"]==True):
                if(self.TA_state["attack_fail"]==True):
                    self.TA_state["attack_fail"]=False
                    damage=0
                self.TA_state["hp"]-=damage*self.student_state["buff"]
                self.student_state["buff"]=self.student_state["buff_2"]
                self.student_state["buff_2"]=1
            else:
                if(self.ZN_state["attack_fail"]==True):
                    self.ZN_state["attack_fail"]=False
                    damage=0
                self.ZN_state["hp"]-=damage*self.student_state["buff"]
                self.student_state["buff"]=self.student_state["buff_2"]
                self.student_state["buff_2"]=1
        

        res = self.check_win_condition();
        if res != 0:
            return;

        self.round += 1
        self.push(self.ui_theme.reset, TA_state = self.TA_state);


    def get_ZN_stat(self):
        if(self.round<20 and self.round%5==1):
            return 3 
        if(self.round<20):
            return random.randint(0,2)
        else:
            return random.randint(0,3)     
    def get_TA_stat(self):
        if(self.TA_state["TA_live"]==False):
            return -1
        else:
            if(self.TA_state["stage"]<=3):
                return random.randint(0,3)
            if(self.TA_state["stage"]==4):
                if(self.round==17):
                    return 3
                else:
                    return random.randint(0,2)    
    def generate_enemy_atk_event(self, ZN_stat_num,TA_stat_num):
        # self.timer += 2;
        ZN_stat_name=self.ZN_stats[ZN_stat_num]
        if(TA_stat_num==-1):
            TA_stat_name="No enemy"
        else:
            TA_stat_name=self.TA_stats[TA_stat_num]
        if ZN_stat_name == "睡覺":
            self.student_damage= 0
            self.push(self.ui_theme.show_text, text = f"助教在臺上，林宗男在睡覺!");
            self.timer+=2
            self.push(self.ui_theme.show_text, text = f"什麼事也沒有發生");

        elif ZN_stat_name == "滑手機":
            self.student_damage=0
            self.push(self.ui_theme.show_text, text = f"助教在臺上，林宗男在滑手機!");
            self.timer+=2
            self.push(self.ui_theme.show_text, text = f"什麼事也沒有發生");
            
        elif ZN_stat_name== "去外面講電話":
            self.student_damage=0
            self.push(self.ui_theme.show_text, text = f"林林林林！");
            self.timer+=1
            self.push(self.ui_theme.show_text, text = f"林宗男的手機響了，吵到助教上課了！");
            self.timer+=1
            self.ZN_state["attack_fail"]=True
        elif ZN_stat_name== "認真上課":
            self.push(self.ui_theme.show_text, text = f"林宗男站起來了，他要認真上課了！");
            self.student_damage=5
        elif ZN_stat_name== "召喚助教":
            I_love_TAs=["HW1助教龔鈺翔","HW2助教游弘毅","HW3助教卓寧文","大助教郭哲璁"]
            IIIIII=self.TA_state["stage"]
            self.push(self.ui_theme.show_text, text = f"林宗男在第{self.round}回合召喚了{I_love_TAs[IIIIII]}，好可怕！");
            self.student_damage=0
            self.timer += 2;
            if(self.TA_state["stage"]==0):
                self.TA_state= {"hp":50,"hp_max":50,"TA_live":True,"stage":1,"attack_fail":False};
                self.push(self.ui_theme.show_text, text = f"哈哈剛上大一的小菜雞，看我還不用簡單的python語法電爆你們！");                
            elif(self.TA_state["stage"]==1):
                self.TA_state= {"hp":100,"hp_max":100,"TA_live":True,"stage":2,"attack_fail":False};
                self.push(self.ui_theme.show_text, text = f"md，怎麼會有人現在還不會用cmd、ls、cd。 ");             
            elif(self.TA_state["stage"]==2):
                self.TA_state= {"hp":150,"hp_max":150,"TA_live":True,"stage":3,"attack_fail":False};
                self.push(self.ui_theme.show_text, text = f"在做計程期末專題的同時，不要忘了HW3快截止了喔！");             
            elif(self.TA_state["stage"]==3):
                self.TA_state= {"hp":400,"hp_max":400,"TA_live":True,"stage":4,"attack_fail":False};
                self.push(self.ui_theme.show_text, text = f"這個套件很簡單，我來教你們怎使用。");             
            else:
                print("1")   
        if(TA_stat_name!="No enemy"):
            if(self.TA_state["stage"] ==1):
                if(TA_stat_name=="城堡"):
                    self.push(self.ui_theme.show_text, text = f"助教躲進城堡裡了");
                    self.TA_state["attack_fail"]=True
                elif(TA_stat_name=="公寓"):
                    self.push(self.ui_theme.show_text, text = f"龔鈺翔在公寓和城堡中選擇了公寓想，房租比較便宜喔");
                    self.timer+=2
                    self.push(self.ui_theme.show_text, text = f"什麼事也沒發生");
                elif(TA_stat_name=="你多換行"):
                    self.push(self.ui_theme.show_text, text = f"你在HW1多換了一行，哭哭。");
                    self.student_damage+=8
                elif(TA_stat_name=="你多空一格"):
                    self.push(self.ui_theme.show_text, text = f"你在HW1多空了一個空格，哭哭。");
                    self.student_damage+=15
                else:
                    print("2")
            elif(self.TA_state["stage"] ==2):
                if(TA_stat_name=="範例測資"):
                    self.push(self.ui_theme.show_text, text = f"助教給你很小的範例測資讓你以為你可以十分全拿。");
                    if(self.TA_state["hp_max"]-self.TA_state["hp"]<10):
                        self.TA_state["hp"]=self.TA_state["hp_max"]
                    else:
                        self.TA_state["hp"] += 10
                elif(TA_stat_name=="資料夾"):
                    self.push(self.ui_theme.show_text, text = f"你的HW2的zip檔解壓縮後多了一個資料夾。");
                    self.student_damage+=5
                elif(TA_stat_name=="乾坤大挪移"):
                    self.push(self.ui_theme.show_text, text = f"乾坤大挪移：助教把zip跟txt的順序對調讓你抓不到正確的檔案。");
                    self.student_damage+=20
                elif(TA_stat_name=="正式測資"):
                    self.push(self.ui_theme.show_text, text = f"正式測資超大讓你的testcase02、testcase03 recursion limit exceeded.");
                    self.student_damage+=30
                else:
                    print("3")
            elif(self.TA_state["stage"] ==3):
                if(TA_stat_name=="美編"):
                    self.push(self.ui_theme.show_text, text = f"助教覺得你的美編不及格，本回合你的傷害將被反彈。");
                    self.student_state["reverse"]=True
                elif(TA_stat_name=="滾球球"):
                    self.push(self.ui_theme.show_text, text = f"你的上機考第二題一直Runtime error，球球滾不下來。");
                    self.student_damage+=30
                elif(TA_stat_name=="aMAZEng"):
                    self.push(self.ui_theme.show_text, text = f"你在HW3的迷宮裡陷入無限迴圈,aMAZEng。");
                    self.student_damage+=50
                elif(TA_stat_name=="限制十五分鐘"):
                    self.push(self.ui_theme.show_text, text = f"你在迷宮走了一個小時。");
                    self.student_damage+=50                   
                else:
                    print("4")
            elif(self.TA_state["stage"] ==4):
                if(TA_stat_name=="溫柔地回答你問題"):
                    self.push(self.ui_theme.show_text, text = f"助教溫柔地回答你問題。你的知識增加了，本回合你的攻擊力兩倍！");
                    self.student_state["buff"]=2
                elif(TA_stat_name=="召喚OJ2助教"):
                    self.push(self.ui_theme.show_text, text = f"郭哲璁受到了OJ2助教的附身，你受到了極大的傷害！");
                    self.student_damage+=120
                elif(TA_stat_name=="給你上機考考古題"):
                    self.push(self.ui_theme.show_text, text = f"助教給你上機考考古題。你的力量增加了！本回合你的攻擊力三倍！");
                    self.student_state["buff"]=3
                elif(TA_stat_name=="非常非常會講課"):
                    self.push(self.ui_theme.show_text, text = f"助教非常非常會講課。你的程式能力大幅提升，本回合你的攻擊力2.5倍！");
                    self.student_state["buff"]=2.5
    def generate_student_atk_event(self,student_stat_name):
        self.timer += 2;
        damage=0
        if(self.TA_state["stage"]==1):
            if student_stat_name== "認真蓋城堡" :
                self.push(self.ui_theme.show_text, text = f"for迴圈用好用滿，最後一層還要加門");
                damage=10
            elif student_stat_name== "二分搜" :
                self.push(self.ui_theme.show_text, text = f"上機考第一題你花了大量時間寫二分搜，雖然最後有AC，不值得。");
                damage=5
            elif student_stat_name== "暴力AC" :
                self.push(self.ui_theme.show_text, text = f"上機考第一題暴力寫會AC不會partial accepted，好爽。");
                damage=20
            elif student_stat_name== "助教拜託期末專題讓我過" :
                self.push(self.ui_theme.show_text, text = f"助教覺得你們的期末專題進度超前好棒棒。");
                damage=20
        elif(self.TA_state["stage"]==2):
            if student_stat_name== "Set recursion limit" :
                self.push(self.ui_theme.show_text, text = f"testcase02部份給分。");
                damage = 16
            elif student_stat_name== "dfs/bfs" :
                self.push(self.ui_theme.show_text, text = f"演算法寫爛了。");
                if(self.student_state["hp"]<10):
                    self.student_state["hp"] = 0 
                else:
                    self.student_state["hp"] -= 10
            elif student_stat_name== "大驚" :
                self.push(self.ui_theme.show_text, text = f"油弘毅幾班？大驚！助教覺得你的梗好冷，助教感冒了。");
                damage = 35
            elif student_stat_name== "長期肩負重大的任務" :
                self.push(self.ui_theme.show_text, text = f"士不可以不「弘毅」，任重而道遠。助教改HW2很辛苦阿！助教扛起責任，好累。");
                damage = 39
        elif(self.TA_state["stage"]==3):
            if student_stat_name== "郭教授確診了" :
                self.push(self.ui_theme.show_text, text = f"只好換卓助教上台教課。壓力大大。");
                damage = 60
            elif student_stat_name== "電神演算法" :
                self.push(self.ui_theme.show_text, text = f"你聽從電神的建議，輸出在一秒之內跑出來了，把HW3當兒戲。");
                damage = 100
            elif student_stat_name== "copy" :
                self.push(self.ui_theme.show_text, text = f"你import了copy，總分0.6倍");
                self.student_state["hp"] *= 0.6
            elif student_stat_name== "DIJKSTRA" :
                self.push(self.ui_theme.show_text, text = f"你使用了DIJKSTRA卻跑很久。");
                self.timer+=2;
                self.push(self.ui_theme.show_text, text = f"演算法寫爛了。");
                if(self.student_state["hp"]<40):
                    self.student_state["hp"] = 0 
                else:
                    self.student_state["hp"] -= 40
        elif(self.TA_state["stage"]==4):
            if student_stat_name== "安裝venv" :
                self.push(self.ui_theme.show_text, text = f"你成功安裝了venv。");
                if(self.student_state["hp_max"]-self.student_state["hp"]<50):
                    self.student_state["hp"]=self.student_state["hp_max"]
                else:
                    self.student_state["hp"] +=50
            elif student_stat_name== "印海報" :
                self.push(self.ui_theme.show_text, text = f"你選擇組內自己印海報，來換取做專題的時間，好貴。");
                self.timer+=2
                self.push(self.ui_theme.show_text, text = f"什麼事都沒發生");
            elif student_stat_name== "上機考卡常" :
                self.push(self.ui_theme.show_text, text = f"郭教授一走過來你的程式就AC了！郭教授好棒！");
                damage=399
            elif student_stat_name== "python好棒棒" :
                self.push(self.ui_theme.show_text, text = f"我想不出技能了，pyhton好棒棒，耶！");
                damage=50
        elif(self.student_state["four_spirit"]==False):    
            if student_stat_name == "Python好棒棒":
                self.push(self.ui_theme.show_text, text = f"pyhton好棒棒");
                damage=10
            elif student_stat_name == "某某男教授":
                self.push(self.ui_theme.show_text, text = f"你讓林宗男在Dcard上被炎上了，雖然他感覺不怎麼在乎。");
                damage = 30
            elif student_stat_name == "正課蹺掉":
                self.push(self.ui_theme.show_text, text = f"爽啦");
                if(self.student_state["hp_max"]-self.student_state["hp"]<10):
                    self.student_state["hp"]=self.student_state["hp_max"]
                else:
                    self.student_state["hp"] += 10
            elif student_stat_name== "我要去謝班":
                self.push(self.ui_theme.show_text, text = f"你想要逃去謝班，但其實謝班更慘，都不用睡覺。");
                if(self.student_state["hp"]<10):
                    self.student_state["hp"] = 0 
                else:
                    self.student_state["hp"] -= 10
        elif(self.student_state["four_spirit"]==True):    
            if student_stat_name == "呈卷，即面署第一":
                self.push(self.ui_theme.show_text, text = f"您上機考破臺了，好電好電");
                damage=200
            elif student_stat_name == "目光如炬":
                self.push(self.ui_theme.show_text, text = f"怒曰：庸奴！此何地也？國家之事，糜爛至此。好嗆好嗆。");
                damage = 100
            elif student_stat_name == "視學京畿":
                self.push(self.ui_theme.show_text, text = f"京畿：國都及其附近的地方。禮拜四晚上的學新，大家總是好認真。你覺得普林斯頓王國的未來很有希望。下回合你的攻擊力兩倍。");
                self.student_state["buff_2"]=True
            elif student_stat_name== "為除不潔者":
                self.push(self.ui_theme.show_text, text = f"汝復輕身而昧大義，天下事誰可支拄者！今天很嗆是吧。");
                damage=299
        return damage
    def check_win_condition(self):
        if self.ZN_state["hp"] <= 0:
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":"win"}), int(self.timer*1000), 1);
            return "win";
        elif self.TA_state["hp"] <= 0:
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":0}), int(self.timer*1000), 1);
            self.TA_state["TA_live"]=False;
            return 0
        elif(self.student_state["hp"]<=0):
            pygame.time.set_timer(pygame.event.Event(NEW_STAGE, {"name":self.name, "value":"lose"}), int(self.timer*1000), 1);
            return "lose";
        return 0;
           


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

    '''def generate_weapon_animation(self, weapon_type, total_damage):
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

        self.timer += 0.2;'''

    def get_intro(self):
        self.push(self.ui_theme.show_text, text = "林宗男出現了!");
        self.timer += 2;
    '''
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
    '''
    
    def do_count(self, args):
        t = args["t"];
        if self.in_problem:
            self.push(self.ui_theme.count, t = t);
            if t == 0:
                self.push(self.time_is_up);
            else:
                self.push(self.do_count, time = 1, t = t - 1);
    '''
    def right_answer(self):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.ZN_state, self.stats, self.button_functions);
        self.timer = 0;
        self.push(self.ui_theme.show_text, text = "恭喜你答對了，成功躲避了傷害!");
        self.timer += 2;
        self.check_win_condition();
        self.round += 1;

    def wrong_answer(self):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.ZN_state, self.stats, self.button_functions);
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
        self.round += 1;

    def time_is_up(self, args):
        self.in_problem = False;
        self.ui_theme = UI_Battle_Theme(self.student_state, self.ZN_state, self.stats, self.button_functions);
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
        self.round += 1;'''
        



class UI_CSWAP_Theme:
    def __init__(self):
        pass;
'''
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
        self.length = len(self.problem_list);'''

    


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
                self.current_game_stage = ZN_Battle(player0);

        if Stage == "Battle":
            if return_value == "win":
                print("You won!");
            elif return_value == "lose":
                print("You lost!");


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