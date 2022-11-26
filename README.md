# Texas
This project includes
- Texas Hold'em poker
- Go game
- Other simple games

## Texas Usage
python start_texas_assistor.py -p 8   # 计算8个玩家时（目前）的胜率
- -p number of player
- -h help

e.g.
- (input) H2 H3                       # 输入2张手牌
- (input) H2 H3 S10 D5 C4 DK          # 输入2张手牌，和4张公牌

python start_texas_game.py
- -p you can see everyone's hole cards 
- -n number of players
- -h help

### Poker
- Symbol(Suit) + Digit(Rank)
- Symbol
  - H(heart)    # 红桃
  - D(Diamond)  # 方块
  - S(Spade)    # 黑桃
  - C(Club)     # 梅花
- Digit
  - 2-10
  - J/Q/K/A
- e.g.
  - H2，红桃2
  - CA，梅花A

## Texas Implementation
### card
- (symbol, digit)

### digit
- 14 for A(ce)
- 13 for K(ing)
- 12 for Q(ueen)
- 11 for J(ack)


## Go Game Usage
python start_go_game.py
- -b board_size
- -h help

e.g.
- (input) 1,1 put a stone to the top-left corner

## Go implementation

### Stone & Board
- White 'o'
- Black 'x'
- Empty '.'
- Guard
  - around the real board for computation efficiency
  - will not be printed

e.g. The board in memory & the printed board
```
G G G G G G G
G E W E W B G     . o . o x
G W W W W B G     o o o o x
G B B B B B G     x x x x x
G B B B E B G     x x x . x
G B B . B B G     x x . x x
G G G G G G G
```
- logic position: (lx, ly)
  - 1 ≤ lx ≤ N, 1 ≤ ly ≤ N
  - used in input, GoBasicBoard 
- position index: n
  - n = (lx * (N + 2)) + ly 
  - preferred for computation efficiency

### Action
- usually Action = position
- Go game allows players to pass (do nothing)
  - logic position: None
  - position index: PASS_INDEX(0)  
