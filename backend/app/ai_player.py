from typing import List, Optional, Tuple, Dict
from .game import Card, CardType, GameState

class AIPlayer:
    def __init__(self, game_state: GameState, player_index: int):
        self.game_state = game_state
        self.player_index = player_index
        self.hand = game_state.players_hands[player_index]

    def make_decision(self) -> Dict:
        """做出决策，返回动作字典 {"action": "play/pass", "cards": [...]}"""
        if not self.game_state.last_played_cards:
            return self.play_first_hand()
        return self.play_against_last_hand()

    def play_first_hand(self) -> Dict:
        """第一手牌，选择最小的单张"""
        if not self.hand:
            return {"action": "pass"}
        
        # 找出最小的单张
        min_card = min(self.hand, key=lambda c: self.game_state.get_card_value(c))
        return {"action": "play", "cards": [min_card]}

    def play_against_last_hand(self) -> Dict:
        """根据上家出的牌做出回应"""
        last_cards = self.game_state.last_played_cards
        last_type = self.game_state.last_played_type

        # 尝试找到可以压过上家的牌
        playable_cards = self.find_playable_cards(last_cards, last_type)
        if playable_cards:
            return {"action": "play", "cards": playable_cards}

        # 尝试出炸弹
        bomb = self.find_bomb()
        if bomb and self.should_play_bomb():
            return {"action": "play", "cards": bomb}

        return {"action": "pass"}

    def find_playable_cards(self, last_cards: List[Card], last_type: CardType) -> Optional[List[Card]]:
        """找出可以压过上家的牌"""
        if last_type == CardType.SINGLE:
            return self.find_single(last_cards[0])
        elif last_type == CardType.PAIR:
            return self.find_pair(last_cards[0])
        elif last_type == CardType.TRIPLE:
            return self.find_triple(last_cards[0])
        elif last_type == CardType.TRIPLE_WITH_PAIR:
            return self.find_triple_with_pair(last_cards[0])
        elif last_type == CardType.STRAIGHT:
            return self.find_straight(len(last_cards), last_cards[-1])
        elif last_type == CardType.CONSECUTIVE_PAIRS:
            return self.find_consecutive_pairs(len(last_cards) // 2, last_cards[-1])
        elif last_type == CardType.CONSECUTIVE_TRIPLES:
            return self.find_consecutive_triples(len(last_cards) // 3, last_cards[-1])
        elif last_type == CardType.STRAIGHT_FLUSH:
            return self.find_straight_flush(len(last_cards), last_cards[-1])
        return None

    def find_single(self, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的单张"""
        for card in sorted(self.hand, key=lambda c: self.game_state.get_card_value(c)):
            if self.game_state.get_card_value(card) > self.game_state.get_card_value(target_card):
                return [card]
        return None

    def find_pair(self, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的对子"""
        for i in range(len(self.hand) - 1):
            if (self.hand[i].rank == self.hand[i + 1].rank and 
                self.game_state.get_card_value(self.hand[i]) > self.game_state.get_card_value(target_card)):
                return [self.hand[i], self.hand[i + 1]]
        return None

    def find_triple(self, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的三张"""
        for i in range(len(self.hand) - 2):
            if (self.hand[i].rank == self.hand[i + 1].rank == self.hand[i + 2].rank and 
                self.game_state.get_card_value(self.hand[i]) > self.game_state.get_card_value(target_card)):
                return [self.hand[i], self.hand[i + 1], self.hand[i + 2]]
        return None

    def find_triple_with_pair(self, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的三带二"""
        # 先找三张
        for i in range(len(self.hand) - 2):
            if self.hand[i].rank == self.hand[i + 1].rank == self.hand[i + 2].rank:
                # 再找对子
                for j in range(len(self.hand)):
                    if j < i or j > i + 2:
                        for k in range(j + 1, len(self.hand)):
                            if (self.hand[j].rank == self.hand[k].rank and 
                                self.game_state.get_card_value(self.hand[i]) > self.game_state.get_card_value(target_card)):
                                return [self.hand[i], self.hand[i + 1], self.hand[i + 2], 
                                        self.hand[j], self.hand[k]]
        return None

    def find_straight(self, length: int, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的顺子"""
        # 按点数排序
        sorted_cards = sorted(self.hand, key=lambda c: self.game_state.get_card_value(c))
        for i in range(len(sorted_cards) - length + 1):
            if all(self.game_state.get_card_value(sorted_cards[j]) == 
                   self.game_state.get_card_value(sorted_cards[i]) + j - i 
                   for j in range(i, i + length)):
                if self.game_state.get_card_value(sorted_cards[i + length - 1]) > self.game_state.get_card_value(target_card):
                    return sorted_cards[i:i + length]
        return None

    def find_consecutive_pairs(self, pair_count: int, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的连对"""
        # 找出所有对子
        pairs = []
        for i in range(len(self.hand) - 1):
            if self.hand[i].rank == self.hand[i + 1].rank:
                pairs.append([self.hand[i], self.hand[i + 1]])
        
        # 找出连续的连对
        for i in range(len(pairs) - pair_count + 1):
            if all(self.game_state.get_card_value(pairs[j][0]) == 
                   self.game_state.get_card_value(pairs[i][0]) + j - i 
                   for j in range(i, i + pair_count)):
                if self.game_state.get_card_value(pairs[i + pair_count - 1][0]) > self.game_state.get_card_value(target_card):
                    result = []
                    for pair in pairs[i:i + pair_count]:
                        result.extend(pair)
                    return result
        return None

    def find_consecutive_triples(self, triple_count: int, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的三连三"""
        # 找出所有三张
        triples = []
        for i in range(len(self.hand) - 2):
            if self.hand[i].rank == self.hand[i + 1].rank == self.hand[i + 2].rank:
                triples.append([self.hand[i], self.hand[i + 1], self.hand[i + 2]])
        
        # 找出连续的三连三
        for i in range(len(triples) - triple_count + 1):
            if all(self.game_state.get_card_value(triples[j][0]) == 
                   self.game_state.get_card_value(triples[i][0]) + j - i 
                   for j in range(i, i + triple_count)):
                if self.game_state.get_card_value(triples[i + triple_count - 1][0]) > self.game_state.get_card_value(target_card):
                    result = []
                    for triple in triples[i:i + triple_count]:
                        result.extend(triple)
                    return result
        return None

    def find_straight_flush(self, length: int, target_card: Card) -> Optional[List[Card]]:
        """找出大于目标牌的同花顺"""
        # 按花色分组
        suits = {}
        for card in self.hand:
            if card.suit not in suits:
                suits[card.suit] = []
            suits[card.suit].append(card)
        
        # 对每个花色找顺子
        for suit_cards in suits.values():
            sorted_cards = sorted(suit_cards, key=lambda c: self.game_state.get_card_value(c))
            for i in range(len(sorted_cards) - length + 1):
                if all(self.game_state.get_card_value(sorted_cards[j]) == 
                       self.game_state.get_card_value(sorted_cards[i]) + j - i 
                       for j in range(i, i + length)):
                    if self.game_state.get_card_value(sorted_cards[i + length - 1]) > self.game_state.get_card_value(target_card):
                        return sorted_cards[i:i + length]
        return None

    def find_bomb(self) -> Optional[List[Card]]:
        """找出炸弹"""
        # 找出4张或以上的同点数牌
        for i in range(len(self.hand) - 3):
            if all(self.hand[j].rank == self.hand[i].rank for j in range(i, i + 4)):
                return self.hand[i:i + 4]
        
        # 找出大小王
        jokers = [card for card in self.hand if card.rank in ['小王', '大王']]
        if len(jokers) >= 4:
            return jokers[:4]
        
        return None

    def should_play_bomb(self) -> bool:
        """判断是否应该出炸弹"""
        # 如果手牌数量较少，更倾向于出炸弹
        if len(self.hand) <= 5:
            return True
        
        # 如果对手手牌数量较少，更倾向于出炸弹
        opponent_hands = [len(self.game_state.players_hands[i]) 
                         for i in range(4) 
                         if i != self.player_index and i // 2 != self.player_index // 2]
        if any(hand <= 5 for hand in opponent_hands):
            return True
        
        return False 