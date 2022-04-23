# Go - game

## Naming

围棋术语
- 棋盘 Board
- 棋子 Stone
- 气 Liberty
- 眼 Eye

## Convention
abbreviation
 - oppo: opponent
 
## BasicBoard - Design
- 为了避免if/else，边上使用Guard类型的边界棋子，但是在接口初转为0-based
- 为了简单判断气/禁入点等，每一片连着的棋子，用BasicChain维护
- BasicChain
  - 维护连成一片的棋子
  - 维护和自己连在一起的其他basicChain，这样被提的时候可以通知更新liberty