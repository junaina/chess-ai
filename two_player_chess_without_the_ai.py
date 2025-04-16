from colorama import Fore, Style, init
init(autoreset=True)  # Automatically reset color after each print

# 8x8 board, each cell is a string: "wP" for white pawn, "bK" for black king, etc.
def create_initial_board():
    return [
        ["bR","bN","bB","bQ","bK","bB","bN","bR"],
        ["bP"]*8,
        ["  "]*8,
        ["  "]*8,
        ["  "]*8,
        ["  "]*8,
        ["wP"]*8,
        ["wR","wN","wB","wQ","wK","wB","wN","wR"]
    ]
piece_weights = {
    'P': 1, 'N': 3, 'B': 3,
    'R': 5, 'Q': 9, 'K': 1000
}
def evaluate_board(board, me):
    them='b' if me=='w' else 'w'
    score=0;
    for row in board:
        for cell in row:
           if cell.strip()=="":
            continue
           kind = cell[1]
           belongs_to=cell[0]
           value= piece_weights.get(kind, 0)

           if belongs_to==me:
            score+=value
           else:
            score-= value

    #bonus for when they are in check or checkmate
    status=checkmate_or_stalemate(board,them)
    if status=="checkmate":
        score+=10000
    elif status=="stalemate":
        score+=3 #not rlly huge but i reckon a lil pressure has got to be good

    return score    

def print_board(board):
    #col indices
    print("   a  b  c  d  e  f  g  h")
    for i, row in enumerate(board):
        #row indices
        print(8-i,end=" ")
        for cell in row:
            if cell.startswith("w"):
                #foreground
                piece=Fore.WHITE+cell
            elif cell.startswith("b"):
                piece=Fore.BLUE+cell
            else:
                piece = "--"
            print(piece+Style.RESET_ALL,end=" ")
        print()
print_board(create_initial_board())
#parsing/processing i/p
def parse_move_input(move_str):
    try:
        start, end=move_str.strip().split()
        #here i'm mapping letters to nums for easier indexing
        start_col=ord(start[0])-ord('a') 
        start_row=8-int(start[1])        
        end_col=ord(end[0])-ord('a')
        end_row=8-int(end[1])
        return(start_row,start_col),(end_row, end_col)
    #error handling for rubbish i/p
    except:
        return None,None

def is_legal_move(board,piece,start,end):
    piece_type=piece[1]
    if piece_type=='P':
        return is_pawn_move_legal(board,piece,start,end)
    elif piece_type=='R':
        return is_rook_move_legal(board,piece,start,end)
    elif piece_type=='N':
      return is_knight_move_legal(board,piece,start,end)
    elif piece_type=='B':
        return is_bishop_move_legal(board,piece,start,end)
    elif piece_type=='Q':
      return is_queen_move_legal(board,piece,start,end)
    elif piece_type=='K':
      return is_king_move_legal(board,piece,start,end)

    #note to self: add more piece types here
    return False

def is_pawn_move_legal(board,piece,start,end):
    if start == end:
        return False
    sr,sc=start
    er,ec=end
    direction=-1 if piece[0]=='w' else 1# white moves up, black down
    # regular single step forward rule
    if sc==ec and er==sr+direction and board[er][ec]=="  ":
        return True
    # two steps forward in the beginning rule
    start_row=6 if piece[0]=='w' else 1
    if sr==start_row and sc==ec and er==sr+2*direction:
        if board[sr+direction][sc] == "  " and board[er][ec]=="  ":
            return True
    #capture rule
    if abs(sc-ec)==1 and er==sr+direction:
        if board[er][ec]!="  " and board[er][ec][0]!=piece[0]:
            return True

    return False

def is_knight_move_legal(board,piece,start,end):
    if start == end:
        return False
    sr,sc=start
    er,ec=end
    dr,dc=abs(er-sr),abs(ec-sc)
    #L move
    if(dr,dc) not in [(2,1),(1,2)]:
        return False
    target=board[er][ec]
    #capture or empty cell rule
    return target=="  " or target[0]!=piece[0]

def is_rook_move_legal(board,piece,start,end):
    if start == end:
        return False
    sr,sc=start
    er,ec=end
    # move straight rule
    if sr!=er and sc!=ec:
        return False
    #determining direction of movement
    step_r=(er-sr)//max(1,abs(er-sr))if sr!=er else 0
    step_c=(ec-sc)//max(1,abs(ec-sc))if sc!=ec else 0
    r,c=sr+step_r,sc+step_c
    while(r,c)!=(er,ec):
        if board[r][c]!="  ":
            return False
        r+=step_r
        c+=step_c
    # capture or empty cell rule
    target=board[er][ec]
    return target=="  "or target[0]!=piece[0]

def is_bishop_move_legal(board,piece,start,end):
    if start == end:
        return False
    sr,sc=start
    er,ec=end
    dr,dc=abs(er-sr),abs(ec-sc)
    #move diagonal rule
    if dr!=dc:
      return False
    #direction
    step_r=(er-sr)//dr
    step_c=(ec-sc)//dc
    r,c=sr+step_r,sc+step_c


    while(r,c)!=(er,ec):
        if board[r][c]!="  ":
          return False
        r+=step_r
        c+=step_c
    #can capture or move to empty
    target=board[er][ec]


    return target=="  " or target[0]!=piece[0]
def is_queen_move_legal(board, piece, start, end):
    return is_rook_move_legal(board,piece,start,end) or is_bishop_move_legal(board,piece,start,end)

def is_king_move_legal(board, piece, start, end):
    if start == end:
        return False
    sr,sc=start
    er,ec=end

    dr,dc=abs(er-sr),abs(ec-sc)
    #only 1 square in any direction rule
    if max(dr,dc)>1:
        return False
    target=board[er][ec]

    return target=="  " or target[0]!=piece[0]

def check_check(board, player_color):
    king_pos=None
    for r in range(8):
        for c in range(8):
            piece=board[r][c]
            if piece==f"{player_color}K":
                king_pos=(r,c)
                break
        if king_pos:
            break
    if not king_pos:
        return True#in check
    #any valid move on to the king position?
    for r in range(8):
      for c in range(8):
        piece=board[r][c]
        if piece!="  " and piece[0]!=player_color:
          if is_legal_move(board,piece,(r,c),king_pos):
            return True#check
    return False#unchecked

#getting all movs
def get_all_moves(board, player):
    all_moves=[]
    for r in range(8):
        for c in range(8):
            piece=board[r][c]
            if piece.strip()=="" or piece[0]!=player:
                continue
            for target_row in range(8):
                for target_col in range(8):
                    start=(r,c)
                    end=(target_row,target_col)
                    if not is_legal_move(board,piece,start,end):
                        continue
                    #test run to see if move puts own king in check
                    taken=board[target_row][target_col]
                    board[target_row][target_col]=piece
                    board[r][c]="  "

                    if not check_check(board,player):
                        all_moves.append((start,end))
                    #rolling back
                    board[r][c]=piece
                    board[target_row][target_col]=taken

    return all_moves

#moving pieces
def make_move(board, start, end, current_player):
    sr,sc=start # sr stands for start row, and so on
    er,ec=end
    piece=board[sr][sc]
    if piece.strip()=="":
        print("empty cell 🕳️")
        return False
    if piece[0]!=current_player:
        print("get your crusty, dusty, nasty hands off my piece😠 ")
        return False
    if not is_legal_move(board,piece,start,end):
        print("illegal move for",piece)
        return False

    #test run to see if move puts own king in check
    captured_piece = board[er][ec]

    board[er][ec]=piece
    board[sr][sc]="  "
    if check_check(board, current_player):
        print("you're still in check sweetheart🥰🧠")
        #rolling bak
        board[sr][sc]=piece
        board[er][ec]=captured_piece
        return False
    return True

#######TBD###########3
#############check/stalemate###############
# Has no legal moves
# AND is in check means checkmate
# AND NOT in check means stalemate
def checkmate_or_stalemate( board,player_color):
    for r in range(8):
        for c in range(8):
            piece=board[r][c]
            if piece=="  " or piece[0]!=player_color:
                continue
            for er in range(8):
                for ec in range(8):
                    start=(r, c)
                    end=(er, ec)
                    if not is_legal_move(board, piece,start,end):
                        continue
###################simulating move################
                    captured=board[er][ec]
                    board[er][ec]=piece
                    board[r][c]="  "
                    #if i can manage to get atleast one move, checkmate's in the clear
                    if not check_check(board,player_color):
                        board[r][c]=piece
                        board[er][ec]=captured
                        return None
                    #reset
                    board[r][c]=piece
                    board[er][ec]=captured
    #gets check at every possibemove
    if check_check(board,player_color):
        return "checkmate"
    else:
        return "stalemate"

def minimax(board,depth,alpha,beta,maxing,ai_side):
    them='b' if ai_side=='w' else 'w'
    turn=ai_side if maxing else them
    
    #eol?
    status=checkmate_or_stalemate(board,turn)
    if status=="checkmate":
        return (-10000 if maxing else 10000), None
    
    if status=="stalemate" or depth==0:
        return evaluate_board(board,ai_side), None
    
    #evaluating possible options
    possible_moves=get_all_moves(board,turn)
    best_move=None
    if maxing:
        max_score=-float('inf')
        for move in possible_moves:
            src,dst=move
            taken=board[dst[0]][dst[1]]
            piece=board[src[0]][src[1]]
            board[dst[0]][dst[1]]=piece
            board[src[0]][src[1]]="  "
            guess, idksmth=minimax(board,depth-1,alpha,beta,False,ai_side)
            board[src[0]][src[1]]=piece
            board[dst[0]][dst[1]]=taken
            if guess>max_score:
                max_score=guess
                best_move=move
            alpha=max(alpha,max_score)
            if beta<=alpha:
                break#pointless to check further

        return max_score,best_move
    else:
        min_score=float('inf')
        for move in possible_moves:
            src,dst=move
            taken=board[dst[0]][dst[1]]
            piece=board[src[0]][src[1]]
            board[dst[0]][dst[1]]=piece
            board[src[0]][src[1]]="  "
            guess, idksmth=minimax(board,depth-1,alpha,beta,True,ai_side)
            board[src[0]][src[1]]=piece
            board[dst[0]][dst[1]]=taken
            if guess<min_score:
                min_score=guess
                best_move=move
            beta=min(beta,min_score)
            if beta<=alpha:
                break

        return min_score,best_move

#game loop
def play_game():
    board=create_initial_board()
    current_player='w'
    while True:
        print_board(board)
        move_str=input(f"{Fore.GREEN}{'White' if current_player=='w' else 'Black'}'s move (enter source to destination e.g.,e2 e4):{Style.RESET_ALL}")
        start,end=parse_move_input(move_str)
        if start is None or end is None:
            print("❌invalid move. have another go(example:e2 e4).")
            continue
        moved=make_move(board,start,end,current_player)
        if moved:

            current_player = 'b' if current_player == 'w' else 'w'
            state = checkmate_or_stalemate(board, current_player)
            if state=="checkmate":
                print_board(board)
                print(f"{Fore.RED}💀 checkmate! {'White' if current_player == 'w' else 'Black'} loses.{Style.RESET_ALL}")
                break
            elif state=="stalemate":
                print_board(board)
                print(f"{Fore.YELLOW} aha stalemate! looks like you couldn't lose fully either{Style.RESET_ALL}")
                break

            if check_check(board,current_player):
                print(f"{Fore.RED}⚠️{'player white' if current_player=='w' else 'player black'} is in check!{Style.RESET_ALL}")


play_game();