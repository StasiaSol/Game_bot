import telebot
from telebot.types import Message, InlineKeyboardButton as IB
from Setting_bot import SeyKeys
from db import is_new_user,users
from time import sleep
from random import choice, randint


class Player:
    
    def __init__(self) -> None:
        self.dic = {'огонь':(120,50),
                    'вода':(100,70),
                    'воздух':(110,60),
                    'земля':(90,80),}
        self.name = ''
        self.power = ''
        self.hp = 0
        self.dmg = 0
class Enemy:
    def __init__(self):
        self.dic = {'Allon': (40,30),
                    'Svet': (100,5),
                    'tihon': (60,20),
                    'Vladim': (70,20),
                    'Hallo': (120,10),
                    }
        
        self.name = choice(list(self.dic.keys()))
        self.hp = self.dic[self.name][0]
        self.damage = self.dic[self.name][1]
if __name__ == '__main__':
    bot = telebot.TeleBot(SeyKeys)
    player_new = Player()
    enemy = Enemy()
    dic = {'огонь':(120,50),
            'вода':(100,70),    
            'воздух':(110,60),
            'земля':(90,80),}
    super_enemys = {'misha':(150,50),
                'pvp':(200,30),
                'банить':(500,7)}

def reg_1(msg: Message):
    global player_new
    player_new = Player()
    bot.send_message(msg.chat.id, 'Добро пожаловать!\nКак тебя зовут?')
    bot.register_next_step_handler(msg, reg_2)
    
def reg_2(msg:Message):
    if player_new.name == '':
        player_new.name = msg.text
    kb = telebot.types.ReplyKeyboardMarkup(True,False)
    kb.row('Земля','Вода')
    kb.row('Огонь','Воздух')
    bot.send_message(msg.chat.id,"Выберите стихию: ",reply_markup=kb)
    bot.register_next_step_handler(msg,reg_3)
def reg_3(msg: Message):
    text = msg.text.lower()
    if text in list(dic.keys()):
        player_new.power=text
        clear = telebot.types.ReplyKeyboardRemove()
        users.write([msg.chat.id,player_new.name,player_new.power,player_new.dic[player_new.power][0],player_new.dic[player_new.power][1],False])
        bot.send_message(msg.chat.id, f'Вы вошли в игру под именем {player_new.name}\nДля дальнейшей игры нажмите /menu',reply_markup=clear)
    else:
        reg_2(msg)

@bot.message_handler(['start'])
def start(msg: Message):
    if is_new_user(msg):
        reg_1(msg)
    else:        
        play = users.read('userid',msg.chat.id)
        bot.send_message(msg.chat.id, f'Вы вошли в игру под именем {play[1]}\nУ вас здоровья - {play[3]} и урона - {play[4]}'
                         f'\nДля дальнейшей игры нажмите /menu')
        
@bot.message_handler(['sleep'])  #функция отдыха для игрока
def start(msg: Message):  
    play =  users.read('userid',msg.chat.id)
    low = (dic[play[2]][0] - play[3])//3 
    kb = telebot.types.InlineKeyboardMarkup()
    if low > 0 :
        kb.row(IB(f"Вздремнуть — +{low}❤️", callback_data=f"sleep_{low}"))
    high = int(dic[play[2]][0] - play[3]) 
    if high > 0 :
        kb.row(IB(f"Поспать — +{high}❤️", callback_data=f"sleep_{high}"))
    if len(kb.keyboard) == 0:
        kb.row(IB('Спать не хочется', callback_data= '0'))
    bot.send_message(msg.chat.id, "Выберите, сколько будешь отдыхать:", reply_markup=kb)
    
@bot.callback_query_handler(lambda call:True)
def callback(call):
    global enemy
    play = users.read('userid',call.message.chat.id)
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
    if call.data.startswith("sleep_"):
        bot.send_message(call.message.chat.id,'Необходимо подождать пока идёт отдых\nМожете пойти попить чаю.')
        play = users.read("userid", call.message.chat.id)
        if play[3]< dic[play[2]][0]:
            text = call.data[6:]
            play[3] += int(text)
            if play[3] > dic[play[2]][0]:
                play[3] = dic[play[2]][0]
            
            sleep(int(text))
            bot.send_message(call.message.chat.id,"Вы отдохнули.")
            users.write(play)
        else:
            bot.send_message(call.message.chat.id,"Вам спать не положено.")
        menu(call.message)
    if call.data == '0':
        menu(call.message)
    if call.data.startswith("trener"):
        if play[3]>0:
            enemy = Enemy()
            kb = telebot.types.InlineKeyboardMarkup()
            kb.row(IB('Атаковать',callback_data='atack'),IB('Попробовать сбежать',callback_data='run'))
            bot.send_message(call.message.chat.id,f'Вам встретился {enemy.name}\n у него здоровья {enemy.hp} и урона {enemy.damage}\n'
                            f'Что будете делать?',reply_markup=kb)
        else:
            bot.send_message(call.message.chat.id,'Идите отдыхать. Так как вы мертвы! \n/home')
    if call.data.startswith("power"): #встреча с супер врагом
        
        #bot.send_message(call.message.chat.id,"Код не дописан.")
        if play[3]>0:
            
            attack_1(call.message)
        else:
            bot.send_message(call.message.chat.id,'Идите отдыхать. Так как вы ещё мертвы! \n/home')
        
    if call.data.startswith("run"):
        if play[3]>0:
            num = randint(1,100)
            if num in range(40):
                bot.send_message(call.message.chat.id,f"Вы смогли сбежать от врага")
            else:
                bot.send_message(call.message.chat.id,f"Вы не смогли сбежать от врага")
                while enemy.hp>0 and play[3]>0:
                    play[3] -= enemy.damage
                    bot.send_message(call.message.chat.id,"Вас атаковал враг.")
                    if enemy.hp >0:
                        enemy.hp -= play[4]
                        bot.send_message(call.message.chat.id,"Вы нанесли ответный удар.") 
            users.write(play)   
            if play[3]<40:
                bot.send_message(call.message.chat.id,"Вам стоит сходить в дом (/home) и отдонуть")
            else:
                kb = telebot.types.InlineKeyboardMarkup()
                kb.row(IB('Снова тренироваться?',callback_data='trener'),IB('Закончить тренировку',callback_data='0'))
                bot.send_message(call.message.chat.id,f"У вас здоровья {play[3]}. Что делать будем дальше?",reply_markup=kb)
        else:
            bot.send_message(call.message.chat.id,'Вы не можете ничего делать. Идите отдыхать. Так как вы мертвы! \n/home')
    if call.data.startswith("atack"):
        if play[3]>0:
            play = users.read('userid',call.message.chat.id)
            while enemy.hp>0 and play[3]>0:
                enemy.hp -= play[4]
                bot.send_message(call.message.chat.id,"Вы атаковали врага.")
                if enemy.hp >0:
                    play[3] -= enemy.damage
                    bot.send_message(call.message.chat.id,"Враг нанёс ответный удар.")
            sleep(1)
            users.write(play)
            if play[3]<40:
                bot.send_message(call.message.chat.id,"Вам стоит сходить в дом (/home) и отдонуть")
            else:
                kb = telebot.types.InlineKeyboardMarkup()
                kb.row(IB('Снова тренироваться?',callback_data='trener'),IB('Закончить тренировку',callback_data='0'))
                bot.send_message(call.message.chat.id,f"Вы победили врага. У вас здоровья {play[3]}. Что делать будем дальше?",reply_markup=kb)
        else:
            bot.send_message(call.message.chat.id,'Вы не можете ничего делать. Идите отдыхать. Так как вы мертвы! \n/home')
@bot.message_handler(['menu'])
def menu(msg: Message):
    clear = telebot.types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Что будешь делать?\n/square — площадь\n/home — лагерь\n/stats — статистика',
                     reply_markup=clear)
    
@bot.message_handler(['stats'])     #статистика игрока
def square(msg: Message):
    play = users.read("userid", msg.chat.id)
    # if play[5]:
    #     defend = 'Вы можете защищать город'
    # else: 
    #     defend = 'Вы не можете защищать город'
    text = f'Здоровье - {play[3]}\nУрон - {play[4]}\nВы маг с силой {play[2]}'   #\n{defend}'
    bot.send_message(msg.chat.id, text)
    
def attack_1(msg):
    global enemy
    play = users.read('userid',msg.chat.id)
    if play[3]>10:
        enemy = Enemy()
        enemy.name = choice(list(super_enemys.keys()))
        enemy.hp, enemy.damage = super_enemys[enemy.name][0],super_enemys[enemy.name][1]
        kb = telebot.types.ReplyKeyboardMarkup(True,True)
        kb.row('Атаковать','Попробовать сбежать')
        bot.send_message(msg.chat.id,f'Вам встретился {enemy.name}\n у него здоровья {enemy.hp} и урона {enemy.damage}\n'
                        f'Что будешь делать?',reply_markup=kb)
        
        bot.register_next_step_handler(msg,attack)
    else: 
        bot.send_message(msg.chat.id,f'У вас мало здоровья! Идите в /home. Вам необходимо поспать.')
        
def attack(msg):
    global enemy
    play = users.read('userid',msg.chat.id)
    if msg.text == 'Атаковать':
        while enemy.hp>0 and play[3]>0:
            enemy.hp -= play[4]
            bot.send_message(msg.chat.id,"Вы атаковали врага.")
            if enemy.hp >0:
                play[3] -= enemy.damage
                bot.send_message(msg.chat.id,"Враг нанёс ответный удар.")
        if enemy.hp <= 0 :
            bot.send_message(msg.chat.id,f'Вы смогли победить одного из супер босов!!!\nУ вас осталось {play[3]} здоровья.')
        elif play[3] <= 0 :
            bot.send_message(msg.chat.id,'Вы погибли!!!')
        users.write(play)
    else:
        num = randint(1,100)
        if num in range(40):
            bot.send_message(msg.chat.id,f"Вы смогли сбежать от врага")
        else:
            bot.send_message(msg.chat.id,f"Вы не смогли сбежать от врага")
            while enemy.hp>0 and play[3]>0:
                play[3] -= enemy.damage
                bot.send_message(msg.chat.id,"Вас атаковал враг.")
                if enemy.hp >0:
                    enemy.hp -= play[4]
                    bot.send_message(msg.chat.id,"Вы нанесли ответный удар.") 
        if enemy.hp <= 0 :
            bot.send_message(msg.chat.id,f'Вы смогли победить одного из супер босов!!!\nУ вас осталось {play[3]} здоровья.')
        elif play[3] < 0 :
            bot.send_message(msg.chat.id,'Вы погибли!')
        users.write(play)
    menu(msg)

@bot.message_handler(['square'])
def square(msg: Message):
    kb = telebot.types.InlineKeyboardMarkup()
    kb.row(IB("Тренироваться",callback_data='trener'))
    kb.row(IB("Проверить силы",callback_data='power'))
    bot.send_message(msg.chat.id, "Ты на площади. Что будешь делать?", reply_markup=kb)
    

@bot.message_handler(['home'])
def home(msg: Message):
    clear = telebot.types.ReplyKeyboardRemove()
    bot.send_message(msg.chat.id, 'Здесь ты можешь поспать и восстановить силы(/sleep) или вернуть в меню (/menu)',reply_markup=clear)

bot.infinity_polling()
