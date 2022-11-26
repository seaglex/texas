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
- 为了避免if/else，边上使用Guard类型的边界棋子
- 为了简单判断气/禁入点等，每一片连着的棋子，用BasicChain维护
- BasicChain
  - 维护连成一片的棋子
  - 维护和自己连在一起的其他basicChain，这样被提的时候可以通知更新liberty
  
## FastBoard - Design
- 基于1-dimensional array
- 用FastChain，可以维护判断一个点是不是只有一口气了
- FastChain
  - 基于环，维护连成一片的棋子
  - FastChainStat维护状态
