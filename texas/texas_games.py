"""
无限德扑

Solution1:
state: probability + amount
action: check/bet/raise/raise_more/all_in/fold
phase: pre-flop/flop/Turn/river
"""
import random
import numpy as np

from .poker import PokerKind, PokerConst, PokerCard
from .common import AgentState, TexasRound


class AgentWrongBetError(Exception):
    def __init__(self, agent, src_bet, state, bet):
        self._str = "{0} {1} {2}({3})".format(agent, state, bet, src_bet)

    def __str__(self):
        return self._str


class GameUnexpectedScanningOverError(Exception):
    pass


class GameNoWinnerError(Exception):
    pass


class TexasContext(object):
    def __init__(self, num, big_blind):
        # basic info
        self.num = num
        self.big_blind = big_blind

        # history
        self.round_state_records = [[], [], [], []]
        self.round_bet_records = [[], [], [], []]

        self.round = None
        self.cum_bets = [0] * num  # cumulative bets before this round
        # latest states in this round
        self.latest_bets = [0] * num
        self.latest_states = [AgentState.Blind] * num

        # the total amount of money in main pot when the agent all-in
        self.all_in_main_pots = [None] * num
        self.total_pot = 0

    def finish_a_scan(self, round_, states, cur_bets, is_round_over):
        if not is_round_over and len(states) != self.num:
            raise GameUnexpectedScanningOverError()
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
            for n in range(self.num):
                if not self.latest_states[n].is_hand_over():
                    self.latest_states[n] = AgentState.Blind
                self.latest_bets[n] = 0
        self.round_state_records[round_].append(states)
        self.round_bet_records[round_].append(cur_bets)
        return

    def is_hand_over(self):
        num_active = 0
        for n in range(self.num):
            if self.latest_states[n].is_hand_over():
                continue
            num_active += 1
        return num_active <= 1


class NoLimitTexasGame(object):
    def __init__(self, judge, big_blind=20, minimal_unit=10):
        self._big_blind = big_blind
        self._minimal_unit = 10
        self._small_blind = max(big_blind // minimal_unit // 2, 1) * minimal_unit
        self._rand = random.Random(0)
        self._judge = judge

        digits = np.arange(PokerConst.MIN_DIGIT, PokerConst.MAX_DIGIT + 1, 1)
        kinds = [PokerKind.heart.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.diamond.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.spade.value] * PokerConst.DIGIT_NUM
        kinds += [PokerKind.club.value] * PokerConst.DIGIT_NUM
        self.total_cards = np.array([kinds, list(digits) * 4]).T

    def run_a_hand(self, agents, is_verbose, is_public):
        if is_verbose:
            print("Starting a new hand...")
        agent_cards = []
        context = TexasContext(len(agents), self._big_blind)
        # shuffle
        np.random.seed(0)
        np.random.shuffle(self.total_cards)
        # pre-flop
        for n, agent in enumerate(agents):
            hole_cards = self.total_cards[n * 2: n * 2 + 2, :].tolist()
            agent.get_hole_cards(hole_cards)
            agent_cards.append(hole_cards)
            if is_public:
                print("Agent%d" % n, " ".join(str(PokerCard(*c)) for c in hole_cards))
        self._run_a_round(TexasRound.PreFlop, agents, context, is_verbose)
        if context.is_hand_over():
            return self.shut_down(agent_cards, [], context, is_verbose)
        # flop
        card_index = len(agents) * 2 + 1
        community_cards = self.total_cards[card_index: card_index + 3, :].tolist()
        if is_verbose:
            print("Flop - Community cards: ", ' '.join(str(PokerCard(*c)) for c in community_cards))
        for agent in agents:
            agent.get_community_cards(community_cards)
        self._run_a_round(TexasRound.Flop, agents, context, is_verbose)
        if context.is_hand_over():
            return self.shut_down(agent_cards, community_cards, context, is_verbose)
        # turn
        card_index = card_index + 3 + 1
        community_cards.append(self.total_cards[card_index])
        if is_verbose:
            print("Turn - Community cards: ", ' '.join(str(PokerCard(*c)) for c in community_cards))
        for agent in agents:
            agent.get_community_cards(community_cards)
        self._run_a_round(TexasRound.Turn, agents, context, is_verbose)
        if context.is_hand_over():
            return self.shut_down(agent_cards, community_cards, context, is_verbose)
        # river
        card_index = card_index + 1 + 1
        community_cards.append(self.total_cards[card_index])
        if is_verbose:
            print("River - Community cards: ", ' '.join(str(PokerCard(*c)) for c in community_cards))
        for agent in agents:
            agent.get_community_cards(community_cards)
        self._run_a_round(TexasRound.River, agents, context, is_verbose)
        # over
        return self.shut_down(agent_cards, community_cards, context, is_verbose)

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
            return 0 <= cur_bet
        return NotImplementedError()

    def _run_a_round(self, round_, agents, context, is_verbose):
        # states/bets is redundant, but kept for clarity
        context.round = round_
        latest_bets = context.latest_bets
        latest_states = context.latest_states
        if round_ == TexasRound.PreFlop:
            states = [AgentState.Blind] * 2
            bets = [self._small_blind, self._big_blind]
            latest_bets[0] = self._small_blind
            latest_bets[1] = self._big_blind
            latest_states[0] = AgentState.Blind
            latest_states[1] = AgentState.Blind
            agents[0].set_bet(self._small_blind)
            agents[1].set_bet(self._big_blind)
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
            if s == AgentState.Fold:
                continue
            num_alive += 1
        while True:
            # scan
            for index in range(start_index, len(agents)):
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
                latest_states[index] = state
                latest_bets[index] = bet

                if latest_state != state and state == AgentState.Fold:
                    num_alive -= 1
                if bet > hand_bet:
                    num_ready = 1
                elif state.is_ready_for_round_end():
                    num_ready += 1
                hand_bet = max(hand_bet, bet)

                if is_verbose:
                    print("\tAgent%d" % index, state.name, bet)
                if num_ready == len(agents) or num_alive == 1:
                    context.finish_a_scan(round_, states, bets, is_round_over=True)
                    for agent in agents:
                        agent.round_over()
                    return
            # new scan
            context.finish_a_scan(round_, states, bets, is_round_over=False)
            states = []
            bets = []
            start_index = 0
        pass

    def shut_down(self, agent_cards, community_cards, context, is_verbose):
        indexes = []
        for n, state in enumerate(context.latest_states):
            if state != AgentState.Fold:
                indexes.append(n)
        if len(indexes) == 0:
            raise GameNoWinnerError()
        amounts = np.zeros(len(agent_cards), dtype=int)
        if len(indexes) == 1:
            amounts[indexes[0]] = context.total_pot
        else:
            card_lists = []
            all_in_main_pots = []
            for index in indexes:
                card_lists.append(agent_cards[index] + community_cards)
                all_in_main_pots.append(context.all_in_main_pots[index])
            ranks = self._judge.rank(card_lists)
            shares = self._divide_the_money(context.total_pot, all_in_main_pots, ranks)
            for n, index in enumerate(indexes):
                amounts[index] = shares[n]
        if is_verbose:
            print("End of the game")
            for index in indexes:
                print("\tAgent%d" % index, context.latest_states[index].name, end=" ")
                if len(indexes) > 1:
                    print(" ".join(str(PokerCard(*x)) for x in agent_cards[index]))
                else:
                    print()
            if len(indexes) > 1:
                print("Community cards", " ".join(str(PokerCard(*x)) for x in community_cards))
            print("Winners")
            for n, amount in enumerate(amounts):
                if amount > 0:
                    print("\tAgent%d" % n, amount)
            print("***Details***")
            print("States")
            for n, state_records in enumerate(context.round_state_records):
                for record in state_records:
                    print(TexasRound(n).name, '\t'.join(x.name for x in record), sep="\t")
            print("Bets")
            for n, bet_records in enumerate(context.round_bet_records):
                for record in bet_records:
                    print(TexasRound(n).name, '\t'.join(str(x) for x in record), sep="\t")
            print("Cumulative bets")
            print(context.cum_bets)
            print(context.total_pot)
        return amounts

    def _divide_the_money(self, total_pot, all_in_main_pots, ranks):
        ranks = np.array(ranks)
        org_indexes = np.arange(len(ranks), dtype=int)
        share_amounts = np.zeros(len(ranks), dtype=int)
        exhausted_pot = 0
        rank_level = ranks.min() - 1
        while exhausted_pot < total_pot:
            rank_level += 1
            best_indexes = org_indexes[ranks == rank_level]
            winner_all_in_pots = []
            for index in best_indexes:
                main_pot = all_in_main_pots[org_indexes[index]]
                winner_all_in_pots.append(main_pot if main_pot else total_pot)
            indexes = np.argsort(winner_all_in_pots)
            best_indexes = np.array(best_indexes)[indexes]
            winner_all_in_pots = np.array(winner_all_in_pots)[indexes]
            share_num = len(best_indexes) + 1
            for n, index in enumerate(best_indexes):
                share_num -= 1
                main_pot = winner_all_in_pots[n]
                to_be_share = main_pot - exhausted_pot
                if to_be_share <= 0:
                    continue
                shares = self._divide_evenly(to_be_share, share_num)
                for m in range(len(shares)):
                    share_amounts[org_indexes[best_indexes[m + n]]] += shares[m]
                exhausted_pot = main_pot
        return share_amounts

    def _divide_evenly(self, amount, num):
        if num == 1:
            return [amount]
        share = (amount // self._minimal_unit // num) * self._minimal_unit
        last_share = amount - share * (num - 1)
        return [last_share] + [share] * (num - 1)
