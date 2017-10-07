#----------------------------------------
class Square:
	''' Describe a square on the board. It should draw itself and understand if (mouse) coordinates are inside its bounds'''
	position = (col,row) = (0,0)
	color = ''					#the primary color
	alternate = ''				#an alternate color, for showing turn order
	highlight = ''				#highlight color
	highlighted = False
	dim = (x1,y1,x2,y2) = (0,0,0,0)
	size = (w,h) = (0,0)
	def __init__(self, position, color, alternate, highlight, dim):
		''' Initialize the square. Assign colors and position attributes (as well as pixel dimensions)'''
		(col,row) = position
		(w,h) = dim
		self.position = (self.col,self.row) = (col,row)
		self.color = color
		self.alternate = alternate
		self.highlight = highlight
		self.dim = (self.x1,self.y1,self.x2,self.y2) = (col*w,row*h,(col+1)*w,(row+1)*h)
		self.size = (self.w,self.h) = (w,h)
	def in_square(self,xy):
		''' Determine if pixel x/y coordinates are in this square'''
		(x,y) = xy
		if x >= self.x1 and x <= self.x2 and y >= self.y1 and y <= self.y2:
			return True
		return False
	def draw(self, draw, screen, alternate):
		c = self.color 
		if alternate:
			c = self.alternate
		draw.rect(screen, c,(self.x1,self.y1,self.w,self.h))
		if self.highlighted:
			draw.rect(screen, self.highlight, (self.x1,self.y1,self.w,self.h),5)
		
#----------------------------------------
class Board:
	''' Describe the board as a whole. Draw itself and maintain (and return) any requested board squares'''
	colors = []
	alternate = []
	highlight = ''
	dim = (w,h) = (0,0)
	squares = []
	red_starting_positions = []
	black_starting_positions = []
	
	def __init__(self,size,dimensions,colors,alternate,highlight):
		'''	initialize the board
			Arguments:
				dimensions: tuple, number of rows and columns on the board
				colors: list of tuples, alternating colors (RGB) for the checkerboard pattern
				alternate: list of tuples, alternating colors for the other color pattern (switches when players change)
				highlight: tuple: RGB for highlighted color
		
		'''
		(width,height) = size
		(cols,rows) = dimensions
		self.dim = (self.w,self.h) = (width//cols,height//rows)
		self.colors = colors
		self.alternate = alternate
		self.highlight = highlight
		pos = 0
		for r in range(rows):
			pos += 1
			temp = []
			for c in range(cols):
				square = Square((c,r),self.colors[pos % len(self.colors)],self.alternate[pos % len(self.alternate)],self.highlight,(width//cols,height//rows))
				temp.append(square)
				if r in (0,1) and pos % 2 == 0:
					self.black_starting_positions.append((c,r))
				if r in (rows-2,rows-1) and pos % 2 == 0:
					self.red_starting_positions.append((c,r))
				pos += 1
			self.squares.append(temp)
	def get_squares(self):
		''' Return a linear list of squares'''
		to_return = []
		for r in self.squares:
			for s in r:
				to_return.append(s)
		return to_return
	def get_square(self, pos):
		''' Return the square at the (tuple) position'''
		for r in self.squares:
			for s in r:
				if s.in_square(pos):
					return s
	def get_square_coord(self, coord):
		''' Return the square at the (tuple) coordinates'''
		if coord[1] < 0 or coord[1] >= len(self.squares):
			return None
		if coord[0] < 0 or coord[0] >= len(self.squares[coord[1]]):
			return None
		return self.squares[coord[1]][coord[0]]
	def draw(self, draw, screen, alternate):
		''' Draw board, including highlighted squares '''
		screen.fill((0,0,0))
		for r in self.squares:
			for c in r:
				c.draw(draw, screen, alternate)
		return draw
#----------------------------------------
class Piece:
	''' Describe a player piece. Each piece can be alive or dead and can crowned a king'''
	position = (col,row) = (0,0)
	player = ''
	color = ''
	pos = (x,y) = (0,0)
	dimensions = (w,h) = (0,0)
	radius = 0
	direction = 0
	selected = False
	king = False
	alive = True
	highlight = ''
	font = ''

	def __init__(self, pos, player, color, highlight, dimensions, direction, font):
		self.position = (self.col,self.row) = pos
		self.player = player
		self.color = color
		self.highlight = highlight
		self.dimensions = (self.w,self.h) = dimensions
		self.pos = (self.x,self.y) = ((self.col*self.w)+(self.w//2),(self.row*self.h)+(self.h//2))
		self.radius = int(round(self.w*0.4))
		self.direction = direction
		self.font = font
		
	def draw(self, draw, screen):
		''' Draw the piece, including highlight and king indicator, if needed'''
		if not self.alive:
			return draw
		draw.circle(screen, self.color, (self.x,self.y), self.radius)
		if self.selected:
			draw.circle(screen, self.highlight, (self.x,self.y), self.radius, 5)
		if self.king:
			f = self.font.render('K',True,(255,255,255))
			(fwidth,fheight) = self.font.size('K')
			#center the font
			(fx,fy) = (self.x - (fwidth/2),self.y - (fheight/2))
			screen.blit(f,(fx,fy))
		return draw

	def check_king(self,rows):
		''' Should the piece be kinged? Requires that you pass in the size of the board. Sorry'''
		if self.king:
			return
		if self.direction < 0 and self.row == 0:
			self.king = True
		if self.direction > 0 and self.row == rows-1:
			self.king = True

	def get_possibilities(self, squares):
		''' Get possible moves '''
		to_return = []
		(col,row) = (self.col,self.row)
		possibilities = [(col-1,row+self.direction),(col+1,row+self.direction)]
		if self.king:
			possibilities += [(col-1,row-self.direction),(col+1,row-self.direction)]
		for p in possibilities:
			for s in squares:
				if p == s.position:		#the possibility is still on the board
					to_return.append(p)
		return to_return
		
	
	def move(self, pos): #col,row):
		self.position = (self.col,self.row) = pos#(col,row)
		self.pos = (self.x,self.y) = ((self.col*self.w)+(self.w//2),(self.row*self.h)+(self.h//2))
	
	def check_jump(self, pieces, squares):
		''' Check what jumps are available '''
		to_return = []
		possibilities = self.get_possibilities(squares)
		for p in possibilities:
			(x,y) = self.position
			(px,py) = p
			(dx,dy) = (px-x,py-y)
			position2 = (p2x,p2y) = (x+2*dx,y+2*dy) 
			on_board = False
			for s in squares:
				if s.position == position2:
					on_board = True
			if on_board:
				for pi in pieces:
					if pi.alive and p == pi.position and pi.player != self.player:
						empty_spot = True
						for pi2 in pieces:
							if pi2.alive and position2 == pi2.position:
								empty_spot = False
						if empty_spot:
							temp = {'position':position2,'piece':pi}
							to_return.append(temp)
		return to_return
