"""
无限德扑

Solution1:
state: probability + amount
action: check/bet/raise/raise_more/all_in/fold
phase: pre-flop/flop/Turn/river
"""
import random
import enum
import numpy as np

from .poker import PokerKind, PokerConst
from .judge import TexasJudge


class AgentWrongBetError(Exception):
    def __init__(self, agent, src_bid, state, bid):
        self._str = "{0} {1} {2}({3})".format(agent, state, bid, src_bid)

    def __str__(self):
        return self._str


class InnerUnexpectedScanningOverError(Exception):
    pass


class AgentState(enum.IntEnum):
    Blind = 0
    Fold = 1
    Check = 2
    Bet = 3
    Call = 4
    Raise = 5
    Raise_more = 6
    All_in = 7

    def is_hand_over(self):
        return self == AgentState.Fold or self == AgentState.All_in

    def is_ready_for_round_end(self):
        return self in {AgentState.Check, AgentState.Call, AgentState.Fold, AgentState.All_in}


class TexasRound(enum.IntEnum):
    PreFlop = 0
    Flop = 1
    Turn = 2
    River = 3


class TexasContext(object):
    def __init__(self, num):
        self.num = num

        # history
        self.round_state_records = [[]] * 4
        self.round_bet_records = [[]] * 4

        # last states
        self.round = TexasRound.PreFlop
        self.cum_bets = [0] * num
        self.latest_states = [AgentState.Blind] * num
        # the total amount of money in main pot when the agent all-in
        self.all_in_main_pots = [None] * num
        self.total_pot = 0

    def finish_a_scan(self, round_, states, cur_bets, is_round_over):
        if not is_round_over and len(states) != self.num:
            raise InnerUnexpectedScanningOverError()
        if len(states) < self.num:
            for n in range(len(states), self.num):
                states.append(self.round_state_records[round_][-1][n])
                cur_bets.append(self.round_bet_records[round_][-1][n])
        if is_round_over:
            for n in range(self.num):
                if states[n] == AgentState.All_in and (
                    round_ == TexasRound.PreFlop or self.round_state_records[round_ - 1][-1][n] != AgentState.All_in
                ):
                    main_pot = self.total_pot
                    for m in range(self.num):
                        main_pot += min(cur_bets[m], cur_bets[n])
                    self.all_in_main_pots[n] = main_pot
            for n in range(self.num):
                self.cum_bets[n] += cur_bets[n]
        for n in range(self.num):
            self.total_pot += cur_bets[n]
        self.round_state_records[round_].append(states)
        self.round_bet_records[round_].append(cur_bets)
        return

    def is_hand_over(self):
        num_active = 0
        for n in range(self.num):
            if self.latest_states[n].is_hand_over():
                continue
            num_active += 1
        return num_active == 1


class NoLimitTexasGame(object):
    def __init__(self, judge, big_blind=20):
        self._big_blind = big_blind
        self._small_blind = big_blind // 2
        self._rand = random.Random(0)
        self._judge = judge

        digits = np.arange(PokerConst.MIN_DIGIT, PokerConst.MAX_DIGIT + 1, 1)
        kinds = [PokerKind.heart.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.diamond.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.spade.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.club.value] * PokerConst.DIGIT_NUM
        self.total_cards = np.array([kinds, list(digits) * 4]).T

    def run_a_hand(self, agents):
        agent_cards = []
        context = TexasContext(len(agents))
        # shuffle
        np.random.shuffle(self.total_cards)
        # pre-flop
        for n, agent in enumerate(agents):
            agent.get_hole_cards(self.total_cards[n * 2: n * 2 + 2, :])
            agent_cards.append(self.total_cards[n * 2: n * 2 + 2, :].tolist())
        self.run_a_round(TexasRound.PreFlop, agents, context)
        if context.is_hand_over():
            return self.shutdown(agent_cards, [], context)
        # flop
        card_index = len(agents) * 2 + 1
        community_cards = self.total_cards[card_index: card_index + 3, :].tolist()
        for agent in agents:
            agent.get_community_cards(community_cards)
        self.run_a_round(TexasRound.Flop, agents, context)
        if context.is_hand_over():
            return self.shutdown(agent_cards, community_cards, context)
        # turn
        card_index = card_index + 3 + 1
        community_cards.append(self.total_cards[card_index])
        for agent in agents:
            agent.get_community_cards(community_cards)
        self.run_a_round(TexasRound.Turn, agents, context)
        if context.is_hand_over():
            return self.shutdown(agent_cards, community_cards, context)
        # river
        card_index = card_index + 1 + 1
        community_cards.append(self.total_cards[card_index])
        for agent in agents:
            agent.get_community_cards(community_cards)
        self.run_a_round(TexasRound.River, agents, context)
        # over
        return self.shutdown(agent_cards, community_cards, context)

    def _check_bet(self, bet, last_bet, state, cur_bet):
        if state == AgentState.Fold:
            return cur_bet == last_bet
        if state == AgentState.Check:
            return bet == 0 and cur_bet == 0
        if state == AgentState.Bet:
            return bet == 0 and cur_bet >= self._big_blind
        if state == AgentState.Call:
            return cur_bet == bet > 0
        if state == AgentState.Raise:
            return cur_bet >= bet * 2 > 0
        if state == AgentState.Raise_more:
            return cur_bet > bet * 2 > 0
        # all in
        if state == AgentState.All_in:
            return 0 <= cur_bet <= bet
        return NotImplementedError()

    def run_a_round(self, round_, agents, context):
        latest_bets = [0] * len(agents)
        latest_states = context.latest_states
        if round_ == TexasRound.PreFlop:
            states = [AgentState.Blind] * 2
            bets = [self._small_blind, self._big_blind]
            latest_bets[0] = self._small_blind
            latest_bets[1] = self._big_blind
            latest_states[0] = AgentState.Blind
            latest_states[1] = AgentState.Blind
            hand_bet = self._big_blind
            start_index = 2
        else:
            states = []
            bets = []
            hand_bet = 0
            start_index = 0

        num_ready = 0
        num_alive = 0
        for s in latest_states:
            if s.is_hand_over():
                continue
            num_alive += 1
        while True:
            # scan
            for n in range(start_index, len(agents) + start_index):
                index = n % len(agents)
                agent = agents[index]
                latest_bet = latest_bets[index]
                latest_state = latest_states[index]
                if latest_state.is_hand_over():
                    state, bet = latest_state, latest_bet
                else:
                    state, bet = agent.get_bet(hand_bet, context, index)
                if not self._check_bet(hand_bet, latest_bet, state, bet):
                    raise AgentWrongBetError(agent, hand_bet, state, bet)
                states.append(state)
                bets.append(bet)
                hand_bet = max(hand_bet, bet)
                if latest_state != state and state.is_hand_over():
                    num_alive -= 1
                latest_states[index] = state
                latest_bets[index] = bet
                if state.is_ready_for_round_end():
                    num_ready += 1
                else:
                    num_ready = 1
                if num_ready == len(agents) or num_alive == 1:
                    context.finish_a_scan(round_, states, bets, is_round_over=True)
                    return
                if index == len(agents) - 1:
                    # new scan
                    context.finish_a_scan(round_, states, bets, is_round_over=False)
                    states = []
                    bets = []
                pass
            pass
        pass

    def shutdown(self, agent_cards, community_cards, context):
        pass