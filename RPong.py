import os, sys, rgraphics as rgr, curses,time
__author__ = "Riedler"
__version__ = "2019.03.18-17.24"
shds=rgr.shades()
class Pad(rgr.graphic):
	def __init__(self,fp):
		rgr.graphic.__init__(self)
		self.up=True
		self.fp=fp
		self.init(1,5,shds.a)
		if fp==True:
			self.posx=0
		else:
			self.posx=19
		self.posy=5
	def move(self):
		if self.up==True and self.posy>0:
			self.posy-=1
		elif self.up==False and self.posy+len(self.content)<15:
			self.posy+=1
	def keyfunc(self,key):
		if key=="w" and self.fp==True:
			self.up=True
			self.move()
		elif key=="s" and self.fp==True:
			self.up=False
			self.move()
		elif key=="KEY_UP" and self.fp==False:
			self.up=True
			self.move()
		elif key=="KEY_DOWN" and self.fp==False:
			self.up=False
			self.move()
class Ball(rgr.graphic):
	def __init__(self):
		rgr.graphic.__init__(self)
		self.dr=1
		self.init(1,1,"\033[31m"+shds.a+"\033[29m")
		self.posx=10
		self.posy=7
	def move(self):
		if self.dr==0:
			self.posx+=1
			self.posy-=1
		elif self.dr==1:
			self.posx+=1
			self.posy+=1
		elif self.dr==2:
			self.posx-=1
			self.posy+=1
		elif self.dr==3:
			self.posx-=1
			self.posy-=1
	def bouncewalls(self):
		if self.posx>19:
			return ("win",True)
		elif self.posx<0:
			return ("win",False)
		if self.posy>13:
			if self.dr==1:
				self.dr=0
			else:
				self.dr=3
		elif self.posy<1:
			if self.dr==0:
				self.dr=1
			else:
				self.dr=2
	def bouncepads(self,pads):
		if self.posx<=1 or self.posx>=18:
			for pad in pads:
				if self.posy-pad.posy in range(len(pad.content)):
					if self.dr==2 and pad.fp:
						self.dr=1
					elif self.dr==3 and pad.fp:
						self.dr=0
					elif self.dr==0 and not pad.fp:
						self.dr=3
					elif self.dr==1 and not pad.fp:
						self.dr=2
class NewGame(Exception):
	pass
class EndGame(Exception):
	pass
def win(fp):
	global score
	if fp:
		score[0]+=1
	else:
		score[1]+=1
class SpeedLimiter():
	def __init__(self,speed,changespeed):
		self.spd=speed
		self.cspd=changespeed
		self.stime=time.time()
		self.slow=False
	def start(self):
		self.stime=time.time()
	def sleep(self):
		self.spd+=self.cspd
		if time.time()-self.stime>=1/self.spd:
			self.slow=True
		else:
			self.slow=False
			while time.time()-self.stime<1/self.spd:
				pass
def globkeyfunc(key):
	if key=="r":
		raise NewGame("")
	elif key=="q":
		raise EndGame("")
def main(stdscr):
	global score
	screen=rgr.graphic()
	screen.init(20,15,shds.d)
	score=[0,0]
	stdscr.nodelay(1)
	pada=Pad(True)
	padb=Pad(False)
	ball=Ball()
	spdlimiter=SpeedLimiter(5,0.005)
	while not stdscr.getch()==10:
		screen.draw(pada)
		screen.draw(padb)
		screen.draw(ball)
		screen.display()
		print("\033[16;0H"+str(score[0])+"\033[16;14HPress ENTER to Start\033[16;40H"+str(score[1]))
	print("\033[16;14H                    ")
	while True:
		for x in range(100):
			try:
				key=(stdscr.getkey())
			except curses.error:
				key=None
			globkeyfunc(key)
			pada.keyfunc(key)
			padb.keyfunc(key)
		ball.bouncepads((pada,padb))
		ball.move()
		status=ball.bouncewalls()
		if type(status)==tuple and status[0]=="win":
			win(fp=status[1])
			del ball
			ball=Ball()
			spdlimiter.spd=5
		screen.draw(pada)
		screen.draw(padb)
		screen.draw(ball)
		screen.display()
		spdlimiter.sleep()
		spddisp=str(round(spdlimiter.spd*100))
		if spdlimiter.slow:
			spddisp="\033[31m"+spddisp+"\033[0m"
		print("\033[16;0H"+str(score[0])+"\033[16;14HSpeed:"+spddisp+"\033[16;"+str(41-len(str(score[1])))+"H"+str(score[1]))
		spdlimiter.start()
running=True
while running==True:
	running=False
	try:
		curses.wrapper(main)
	except NewGame:
		print("\033[2J")
		running=True
	except EndGame:
		print("\033[2J")
		running=False
	except KeyboardInterrupt:
		raise Warning("Don't do this. It can mess with your console. Press q instead.")
