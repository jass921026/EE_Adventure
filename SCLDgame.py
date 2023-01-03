import pygame  
import sys
from pygame.locals import QUIT, MOUSEBUTTONDOWN
import random
import time
def SCLDgame(N, time_limit): #N是初始有N個CSWAP
    #初始化 
    pygame.init()
    window=pygame.display.set_mode((800,600))
    pygame.display.set_caption('SCLD挑戰!!!')
    window.fill([0,0,0])
    pygame.display.update()
    start_time = time.time();

    #函數庫
    Lc= 800//(4*N+6) #CS的長度和寬度(CS是正方形)，調整的時候請調成偶數

    Lb=Lc//2 #Btm(或是叫做燈號)的長度和寬度，不要動他

    Ls=2*Lc #一組CS和Btm的長度，一樣不要動他

    Fi=2*N-1 #最後一直排的座標

    Color=[[255,255,255],[255,0,0],[0,255,0],[0,0,255],[255,255,0],[255,0,255],[0,255,255],[127,127,0],[127,0,127],[0,127,127],[127,0,0],[0,127,0],[0,0,127],[64,0,0],[0,64,0],[0,0,64]]
    class Ru(pygame.sprite.Sprite):
        def __init__(itself):
            itself.raw_image=pygame.image.load('./img/scld_rule.png')
            itself.image=pygame.transform.scale(itself.raw_image,(800,300))
            itself.rect=itself.image.get_rect()
            itself.rect.topleft=(0,300)

    class CS(pygame.sprite.Sprite):
        def __init__(itself,x,y,t=0):
            pygame.sprite.Sprite.__init__(itself)
            if N<4:
                itself.raw_image=pygame.image.load('./img/CSWAP.png')
            else:
                itself.raw_image=pygame.image.load('./img/CSWAP2.png')
            itself.image=pygame.transform.scale(itself.raw_image,(Lc,Lc))
            itself.rect=itself.image.get_rect()
            itself.rect.topleft=(x,y)
            itself.x=x
            itself.y=y
            itself.t=t
    class Btm(pygame.sprite.Sprite):
        def __init__(itself,x,y,color):
            pygame.sprite.Sprite.__init__(itself)
            itself.image=pygame.Surface([Lb,Lb])
            itself.image.fill(color)
            itself.c=color
            itself.rect=itself.image.get_rect()
            itself.rect.topleft=(x,y)
            itself.x=x
            itself.y=y
        def C_c(itself,nc): #改顏色函數，nc是你要改的顏色
            itself.image.fill(nc)
            itself.c=nc
        def __eq__(itself,other):
            if itself.c[0]==other.c[0] and itself.c[1]==other.c[1] and itself.c[2]==other.c[2]:
                return True
    class Li(pygame.sprite.Sprite):
        def __init__(itself,x,y,color):
            pygame.sprite.Sprite.__init__(itself)
            itself.image=pygame.Surface([Ls,Lb])
            itself.image.fill(color)
            itself.rect=itself.image.get_rect()
            itself.rect.topleft=(x,y)
            itself.x=x
            itself.y=y
    def CS_c(Co:CS): #如果是他被按到，按下按鍵後改變CS的狀態 (t=0:不交換，t=1:交換)
        if Co.x+Lc>=pygame.mouse.get_pos()[0]>=Co.x and Co.y+Lc>=pygame.mouse.get_pos()[1]>=Co.y:
            if Co.t==0:
                Co.t=1
            else:
                Co.t=0
    def trans(Co:CS ,I1:Btm ,I2:Btm ,O1:Btm ,O2:Btm ,N1:Btm ,N2:Btm): #CS的顏色傳遞 (I -> O -> N))
        if Co.t==0:
            Btm.C_c(O1,I1.c)
            Btm.C_c(O2,I2.c)
        else:
            Btm.C_c(O1,I2.c)
            Btm.C_c(O2,I1.c)
        Btm.C_c(N1,O1.c)
        Btm.C_c(N2,O2.c)
    
    def UDC(I:Btm,L:Li):
        L.image.fill(I.c)

    #導航，就是你要怎樣把CS接起來

    def NVG(i,j): #輸入CS的座標，輸出N的座標以及要接到上面(1)還是下面(2)
        if i%2==0:    
            if j==0:
                return (i+2,j), 1, (i+1,j) , 1
            elif j==N-1:
                return (i+1,j-1), 2, (i+2,j), 2
            else:
                return (i+1,j-1), 2, (i+1,j), 1
        else:
            return (i+1,j) , 2, (i+1,j+1), 1


    #布置場地~~~~~~~~~~
    CsDict=dict()
    rule=Ru()
    window.blit(rule.image,rule.rect)
    pygame.display.update()
    #i為偶數時
    for i in range(0,Fi+1,2):     #橫向上第幾個
        for j in range(N): #直向上第幾個
            C=CS(Ls+Lb+Ls*i,Lc+Lc*j,t=0)
            window.blit(C.image,C.rect)
            I1=Btm(Ls+Ls*i,Lc+Lc*j,[0,0,0])
            I2=Btm(Ls+Ls*i,Lc+Lb+Lc*j,[0,0,0])
            O1=Btm(Ls+Lb+Lc+Ls*i,Lc+Lc*j,[0,0,0])
            O2=Btm(Ls+Lb+Lc+Ls*i,Lc+Lb+Lc*j,[0,0,0])
            CsDict[(i,j)]=[C,I1,I2,O1,O2] #(i,j)可以理解為 CS的"個數座標"
    #i為奇數時
    for i in range(1,Fi+1,2):     #橫向上第幾個
        for j in range(N-1): #直向上第幾個
            C=CS(Ls+Lb+Ls*i,Lb+Lc+Lc*j,t=0)
            window.blit(C.image,C.rect)
            I1=Btm(Ls+Ls*i,Lb+Lc+Lc*j,[0,0,0])
            I2=Btm(Ls+Ls*i,Lb+Lc+Lb+Lc*j,[0,0,0])
            O1=Btm(Ls+Lb+Lc+Ls*i,Lb+Lc+Lc*j,[0,0,0])
            O2=Btm(Ls+Lb+Lc+Ls*i,Lb+Lc+Lb+Lc*j,[0,0,0])
            CsDict[(i,j)]=[C,I1,I2,O1,O2] #(i,j)可以理解為 CS的"個數座標"
    
    #上面和下面的電線
    Lu=dict()
    Ld=dict()
    for i in range(0,Fi,2):
        l=Li(Ls+Lc+Lc+Ls*i,Lc,[0,0,0])
        Lu[i]=l
        l=Li(Ls+Lc+Lc+Ls*i,Lb+Lc*N,[0,0,0])
        Ld[i]=l

    # 區塊間隔=10
    '''
    i1=Btm(10,10,[255,255,255])
    i2=Btm(10,20,[255,0,0])
    i3=Btm(10,40,[0,255,0])
    i4=Btm(10,50,[0,0,255])
    '''
    '''
    for i in range(3):     #橫向上第幾個
        for j in range(2): #直向上第幾個
            C=CS(150+375*i,75+225*j,t=0)
            window.blit(C.image,C.rect)
            I1=Btm(75+375*i,75+225*j,[0,0,0])
            I2=Btm(75+375*i,150+225*j,[0,0,0])
            O1=Btm(300+375*i,75+225*j,[0,0,0])
            O2=Btm(300+375*i,150+225*j,[0,0,0])
            CsDict[(i,j)]=[C,I1,I2,O1,O2] #(i,j)可以理解為 CS的"個數座標"
    '''
    #初始輸入，調整成你要的顏色
    for i in range(N):
        Btm.C_c(CsDict[(0,i)][1],Color[2*i])
        Btm.C_c(CsDict[(0,i)][2],Color[2*i+1])




    #終點
    for i in range(N):
        F1=Btm(Ls*(2*N+1),Lc+Lb*2*i,[0,0,0])
        F2=Btm(Ls*(2*N+1),Lc+Lb*(2*i+1),[0,0,0])
        CsDict[(Fi+1,i)]=[0,F1,F2,0,0]




    #初始顯示
    for i in range(Fi+1):
        if i%2==0:
            for j in range(N):
                trans(CsDict[i,j][0],CsDict[i,j][1],CsDict[i,j][2],CsDict[i,j][3],CsDict[i,j][4],CsDict[NVG(i,j)[0]][NVG(i,j)[1]],CsDict[NVG(i,j)[2]][NVG(i,j)[3]])
                window.blit(CsDict[i,j][1].image,CsDict[i,j][1].rect)
                window.blit(CsDict[i,j][2].image,CsDict[i,j][2].rect)
                window.blit(CsDict[i,j][3].image,CsDict[i,j][3].rect)
                window.blit(CsDict[i,j][4].image,CsDict[i,j][4].rect)
        else:
            for j in range(N-1):
                trans(CsDict[i,j][0],CsDict[i,j][1],CsDict[i,j][2],CsDict[i,j][3],CsDict[i,j][4],CsDict[NVG(i,j)[0]][NVG(i,j)[1]],CsDict[NVG(i,j)[2]][NVG(i,j)[3]])
                window.blit(CsDict[i,j][1].image,CsDict[i,j][1].rect)
                window.blit(CsDict[i,j][2].image,CsDict[i,j][2].rect)
                window.blit(CsDict[i,j][3].image,CsDict[i,j][3].rect)
                window.blit(CsDict[i,j][4].image,CsDict[i,j][4].rect)
    for i in range(0,Fi,2):
        UDC(CsDict[i,0][3],Lu[i])
        UDC(CsDict[i,N-1][4],Ld[i])
        window.blit(Lu[i].image,Lu[i].rect)
        window.blit(Ld[i].image,Ld[i].rect)



    for i in range(N):
        window.blit(CsDict[Fi+1,i][1].image,CsDict[Fi+1,i][1].rect)
        window.blit(CsDict[Fi+1,i][2].image,CsDict[Fi+1,i][2].rect)

    #判斷用的pin，白話來說就是答案 (改題目從這裡改)
    Ans=dict()
    AnsNum=list()
    AnsNumCompare=list()
    for i in range(2*N):
        AnsNum.append(i)
        AnsNumCompare.append(i)
    while AnsNum==AnsNumCompare:
        random.shuffle(AnsNum)
    for i in range(N):
        T1=Btm(Ls*2*N+Lb+Ls,Lc+Lb*2*i,Color[AnsNum[2*i]])
        T2=Btm(Ls*2*N+Lb+Ls,Lc+Lb*(2*i+1),Color[AnsNum[2*i+1]])
        window.blit(T1.image,T1.rect)
        window.blit(T2.image,T2.rect)
        Ans[i]=[T1,T2]
        pygame.display.update()
    
    #判斷是否勝利的函數
    def Win(i,N):
        if CsDict[Fi+1,i][1]==Ans[i][0] and  CsDict[Fi+1,i][2]==Ans[i][1]:
            if i<N-1:
                return Win(i+1,N)
            else:
                return True
        else:
            return False

    count=0

    #主程式運作的函數
    def Main():
        for i in range(Fi+1):
            if i%2==0:     
                for j in range(N): 
                    CS_c(CsDict[(i,j)][0])
            else:     
                for j in range(N-1): 
                    CS_c(CsDict[(i,j)][0])
        for i in range(Fi+1):
            if i%2==0:
                for j in range(N):
                    trans(CsDict[i,j][0],CsDict[i,j][1],CsDict[i,j][2],CsDict[i,j][3],CsDict[i,j][4],CsDict[NVG(i,j)[0]][NVG(i,j)[1]],CsDict[NVG(i,j)[2]][NVG(i,j)[3]])
                    window.blit(CsDict[i,j][1].image,CsDict[i,j][1].rect)
                    window.blit(CsDict[i,j][2].image,CsDict[i,j][2].rect)
                    window.blit(CsDict[i,j][3].image,CsDict[i,j][3].rect)
                    window.blit(CsDict[i,j][4].image,CsDict[i,j][4].rect)
            else:
                for j in range(N-1):
                    trans(CsDict[i,j][0],CsDict[i,j][1],CsDict[i,j][2],CsDict[i,j][3],CsDict[i,j][4],CsDict[NVG(i,j)[0]][NVG(i,j)[1]],CsDict[NVG(i,j)[2]][NVG(i,j)[3]])
                    window.blit(CsDict[i,j][1].image,CsDict[i,j][1].rect)
                    window.blit(CsDict[i,j][2].image,CsDict[i,j][2].rect)
                    window.blit(CsDict[i,j][3].image,CsDict[i,j][3].rect)
                    window.blit(CsDict[i,j][4].image,CsDict[i,j][4].rect)
        for i in range(0,Fi,2):
            UDC(CsDict[i,0][3],Lu[i])
            UDC(CsDict[i,N-1][4],Ld[i])
            window.blit(Lu[i].image,Lu[i].rect)
            window.blit(Ld[i].image,Ld[i].rect)
        for i in range(N):
            window.blit(CsDict[Fi+1,i][1].image,CsDict[Fi+1,i][1].rect)
            window.blit(CsDict[Fi+1,i][2].image,CsDict[Fi+1,i][2].rect)




    #主程式

    while True:
        for event in pygame.event.get():
            if event.type==QUIT:
                pygame.quit()
                sys.exit()
            elif event.type==MOUSEBUTTONDOWN:
                
                Main()     

                pygame.display.update()
                count+=1
                # print(count)
                if Win(0,N):
                    return time.time() - start_time;

        if time.time() - start_time > time_limit:
            return -1;

if __name__=="__main__":
    ret_val = SCLDgame(4, 777)
    print(ret_val);
            
                

        
        