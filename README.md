# texas
Texas hold'em poker toy

## Usage
python assistor.py -p 8   # 计算8个玩家时（目前）的胜率
- H2 H3                   # 输入2张手牌
- H2 H3 S10 D5 C4 DK      # 输入2张手牌，和4张公牌

牌面表示方法
- 字母 + 大小
- 字母
  - H(heart)    # 红桃
  - D(Diamond)  # 方块
  - S(Spade)    # 黑桃
  - C(Club)     # 梅花
- 大小
  - 数字2-10
  - J/Q/K/A
- 举例
 - H2，红桃2
 - C3，梅花3


## Implementation
### card
- (kind, digit)

#### digit
- 14 for A(ce)
- 13 for K(ing)
- 12 for Q(ueen)
- 11 for J(ack)