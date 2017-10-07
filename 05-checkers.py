#!/Library/Frameworks/Python.framework/Versions/3.6/bin

import sys, pygame, time, random
from Board import Board, Piece, Square
assert sys.version_info >= (3,4), 'This script requires at least Python 3.4'

pygame.init()
font = pygame.font.SysFont("arial",30)
#easy to divide by sixteen
size = (width,height) = (800,800)

gameBoardSize = 8
constraints = (cols,rows) = (gameBoardSize, gameBoardSize)


#----------------------------------------
# helper functions

def draw_board(board, alternate, pieces, draw, screen):
        board.draw(draw,screen,alternate)
        for p in pieces:
                p.draw(draw,screen)
        pygame.display.flip()
#----------------------------------------
def checkForJump(jumps, pieces, opponents, board, restrictToPiece = False):
        jumps = []
        for p in pieces:
                if p.alive == True:
                        for i in p.check_jump(opponents, board.get_squares()):
                                #print(str(i))
                                emptySpace = True
                                for pi in pieces:
                                        if pi.alive and pi.position == i.get('position'):
                                                emptySpace = False
                                if emptySpace:
                                        board.get_square_coord(i.get('position')).highlighted = True
                                        if [p, i.get('position'), i.get('piece')] not in jumps:
                                                if restrictToPiece == False or restrictToPiece == p:
                                                        #if you just jumped, then you can only make jumps with the piece that just moved.
                                                        jumps.append([p, i.get('position'), i.get('piece')])
                                #possibleSquares.remove(i.get('piece').position)

        return jumps
#----------------------------------------


def main():
        print("Time to play Baby Chess")
        
        screen = pygame.display.set_mode(size)
        pygame.display.set_caption("Checkers")

        moves = 0

        # feel free to come up with your own colors. They are in (R,G,B) tuples 
        red = (224,49,49)
        black = (33,37,41)
        board_colors = [(98,80,87),(222,226,230)]
        board_alternate = [(73,80,87),(222,226,230)]
        board_highlight = (255,224,102)

        board = Board(size,constraints,board_colors,board_alternate,board_highlight)
        

        red_pieces = []
        for p in board.red_starting_positions:
                piece = Piece(p, 'Red', red, board_highlight, board.dim,-1,font)
                red_pieces.append(piece)
        black_pieces = []
        for p in board.black_starting_positions:
                piece = Piece(p, 'Black', black, board_highlight, board.dim,1,font)
                black_pieces.append(piece)
        all_pieces = red_pieces + black_pieces
        #for p in all_pieces:
        #       if p.alive == False:
        #               all_pieces.remove(p)

        draw_board(board, 0, all_pieces, pygame.draw, screen)
        
        selected = False
        jumping = None
        jumps = []
        playing = True
        players = ["Red","Black"]

        #---------------------------
        redAI = False
        blackAI = True
        #---------------------------

        selectedPiece = all_pieces[0]
        selectedJumpPiece = False
        
        while playing:
                for s in board.get_squares():
                        for p in all_pieces:
                                if s.position == p.position and p.alive == True:
                                        s.highlighted = False
                time.sleep(0.1) #a 100 ms delay, so we don't max out the CPU
                currentPlayer = players[moves % len(players)]
                if currentPlayer == "Red":
                        pieces = red_pieces
                        opponents = black_pieces
                else:
                        pieces = black_pieces
                        opponents = red_pieces

                jumps = checkForJump(jumps, pieces, opponents, board, selectedJumpPiece)
                
                if len(jumps) > 0:
                        selected = True
                        jumping = True
                else:
                        jumping = False
                        selectedJumpPiece = False


                if (currentPlayer == "Black" and blackAI) or (currentPlayer == "Red" and redAI):
                        opponentHasMoved = False
                        FailSafeCounter = 999
                        while opponentHasMoved == False and FailSafeCounter > 0:
                                FailSafeCounter -= 1
                                opponentJumped = False
                                opponentJumps = checkForJump(jumps, pieces, opponents, board)
                                #AI jumping
                                if len(opponentJumps) > 0:
                                        if len(opponentJumps) == 1:
                                                j = opponentJumps[0]
                                        else:
                                                j = opponentJumps[random.randrange(0, len(opponentJumps) - 1)]

                                        FailSafeCounter_2 = 999
                                        while len(opponentJumps) > 0 and FailSafeCounter_2 > 0:
                                                FailSafeCounter_2 -= 1
                                                #print(str(j))
                                                j[0].move(j[1])
                                                j[0].check_king(constraints[1])
                                                j[2].alive = False
                                                opponentJumps = checkForJump(jumps, pieces, opponents, board, j[0])

                                                time.sleep(0.15) #add delay so you can see the AI's jump path
                                                                        
                                                if len(opponentJumps) == 0:
                                                        moves += 1
                                                        opponentJumped = True
                                                        opponentHasMoved = True
                                                else:
                                                        if len(opponentJumps) == 1:
                                                                j = opponentJumps[0]
                                                        else:
                                                                j = opponentJumps[random.randrange(0, len(opponentJumps) - 1)]
                                #AI moving
                                if opponentJumped == False:# and opponentHasMoved == False:
                                                
                                        p = pieces[random.randrange(0, len(pieces))]
                                        
                                        if p.alive:
                                                possibleSquares = p.get_possibilities(board.get_squares())
                                                
                                                if len(possibleSquares) > 0:
                                                        if len(possibleSquares) == 1:
                                                                s = possibleSquares[0]
                                                        else:
                                                                s = possibleSquares[random.randrange(0, len(possibleSquares))]
                                                        opponentEmptySpace = True
                                                        for pi in all_pieces:
                                                                if pi.alive and s == pi.position:
                                                                        opponentEmptySpace = False
                                                        if opponentEmptySpace:
                                                                #print(str(s))
                                                                p.move(s)
                                                                p.check_king(constraints[1])
                                                                moves += 1
                                                                opponentHasMoved = True
                                                                #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                        for p in all_pieces:
                                p.selected = False
                        for s in board.get_squares():
                                s.highlighted = False
                        if FailSafeCounter <= 0:
                                print("OOPS!")
                                moves += 1
                        playing = False
                        for o in opponents:
                                if o.alive:
                                        playing = True

      
                                

                draw_board(board, 0, all_pieces, pygame.draw, screen)
                
                                        
                for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                                sys.exit()
                        # handle MOUSEBUTTONUP
                        if event.type == pygame.MOUSEBUTTONUP:
                                pos = pygame.mouse.get_pos()
                                square = board.get_square(pos)
                                if not selected:                                        
                                        for p in pieces:
                                                if p.position == square.position and p.alive:                            
                                                        selected = True
                                                        selectedPiece = p
                                                        p.selected = True
                                                        possibleSquares = p.get_possibilities(board.get_squares())

                                                        for s in possibleSquares:
                                                                for pi in pieces:
                                                                        if pi.alive and s == pi.position:
                                                                                possibleSquares.remove(s)
                                                                                
                                                        
                                                        for i in p.check_jump(all_pieces, board.get_squares()):
                                                                #print(str(i))
                                                                #possibleSquares.append(i.get('position'))
                                                                possibleSquares.remove(i.get('piece').position)
                                                                #jumping = True
                                                                #jumps.append(i.get('piece'))
                                                                
                                                        for s in possibleSquares:
                                                                board.get_square_coord(s).highlighted = True
                                                        for s in board.get_squares():
                                                                for p in all_pieces:
                                                                        if s.position == p.position and p.alive == True:
                                                                                s.highlighted = False
                                else:
                                        if square.highlighted and not jumping: #MOVE!
                                                selectedPiece.move(square.position)
                                                selectedPiece.check_king(constraints[1])
                                                moves += 1
                                        if square.highlighted and jumping:
                                                for j in range(0, len(jumps)):
                                                        #print(j)
                                                        #print("square: " + str(square.position) + " Jumps[j][0]: " + str(jumps[j][1]))
                                                        if j < len(jumps):
                                                                if square.position == jumps[j][1]:
                                                                        jumps[j][0].move(jumps[j][1])
                                                                        jumps[j][0].check_king(constraints[1])
                                                                        jumps[j][2].alive = False
                                                                        selectedJumpPiece = jumps[j][0]
                                                                        jumps = checkForJump(jumps, pieces, opponents, board, jumps[j][0])
                                                                        
                                                                        
                                                if len(jumps) == 0:
                                                        moves += 1
                                                        jumping = False
                                                #else:
                                                #       print(str(jumps))
                                                
                                        selected = False
                                        for p in all_pieces:
                                                p.selected = False
                                        for s in board.get_squares():
                                                s.highlighted = False
                                        playing = False
                                        for o in opponents:
                                                if o.alive:
                                                        playing = True
                                                
                                                
                                                
                                draw_board(board, 0, all_pieces, pygame.draw, screen)
                                for s in board.get_squares():
                                        for p in all_pieces:
                                                if s.position == p.position and p.alive == True:
                                                        s.highlighted = False

        print(currentPlayer + ' won in only ' + str(moves//2) + ' turns! Good job!')

if __name__ == "__main__":
        # execute only if run as a script
        main()

