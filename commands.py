#Functions command returns command string in expected format

#LOGIN:nick@haslo - login/register user with name nick
def command_login(login,password):
    return ''.join(["LOGIN:",login,"@",password,'\0'])

#JOIN:room_name - join room
def command_join(room_name):
    return ''.join(["JOIN:",room_name,'\0'])

#KICK:yournick:nick - disconnect user with name nick
def command_kick(your_nick,kick_nick):
    return ''.join(["KICK:",your_nick,":",kick_nick,'\0'])

#BAN:yournick:nick - disconnect and pernamently ban usr with name nick
def command_ban(your_nick,ban_nick):
    return ''.join(["BAN:",your_nick,":",ban_nick,'\0'])

#CREATE:yournick:room_name - create room with name room_name
def command_create(your_nick,new_room_name):
    return ''.join(["CREATE:",your_nick,":",new_room_name,'\0'])

#DELETE:yournick:room_name - delete room with name room_name
def command_delete(your_nick,room_to_delete):
    return ''.join(["CREATE:",your_nick,":",room_to_delete,'\0'])

#ME:yournick - get info about yourself
def command_me(your_nick):
    return ''.join(["ME:",your_nick,'\0'])

#LIST - get rooms list
def command_list():
    return ''.join(["LIST",'\0'])

#MSG:yournick@message - send message in courent room
def command_message(your_nick,message):
    return ''.join(["MSG:",your_nick,"@",message,'\0'])

login= "elton"
password= "123"

print command_message(login,password)
