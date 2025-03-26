from typing import List, Dict, Optional
import random
from enum import Enum

class CardSuit(Enum):
    SPADES = "♠"
    HEARTS = "♥"
    DIAMONDS = "♦"
    CLUBS = "♣"
    JOKER = "🃏"

class CardRank(Enum):
    TWO = "2"
    THREE = "3"
    FOUR = "4"
    FIVE = "5"
    SIX = "6"
    SEVEN = "7"
    EIGHT = "8"
    NINE = "9"
    TEN = "10"
    JACK = "J"
    QUEEN = "Q"
    KING = "K"
    ACE = "A"
    JOKER_SMALL = "小王"
    JOKER_BIG = "大王"

class Card:
    def __init__(self, suit: CardSuit, rank: CardRank):
        self.suit = suit
        self.rank = rank

    def __str__(self):
        if self.suit == CardSuit.JOKER:
            return self.rank.value
        return f"{self.suit.value}{self.rank.value}"

class CardType(Enum):
    SINGLE = "单张"
    PAIR = "对子"
    TRIPLE = "三张"
    TRIPLE_WITH_PAIR = "三带二"
    STRAIGHT = "顺子"
    CONSECUTIVE_PAIRS = "连对"
    CONSECUTIVE_TRIPLES = "三连三"
    BOMB = "炸弹"
    STRAIGHT_FLUSH = "同花顺"

class GameState:
    def __init__(self):
        self.deck = []
        self.players_hands = [[], [], [], []]  # 4个玩家的手牌
        self.current_level = 2  # 当前等级
        self.current_player = 0  # 当前玩家索引
        self.last_played_cards = None  # 上一次出的牌
        self.last_played_type = None  # 上一次出的牌型
        self.last_played_player = None  # 上一个出牌的玩家
        self.game_started = False
        self.initialize_deck()

    def initialize_deck(self):
        """初始化两副牌"""
        self.deck = []
        # 添加两副普通牌
        for _ in range(2):
            for suit in [CardSuit.SPADES, CardSuit.HEARTS, CardSuit.DIAMONDS, CardSuit.CLUBS]:
                for rank in [CardRank.TWO, CardRank.THREE, CardRank.FOUR, CardRank.FIVE,
                           CardRank.SIX, CardRank.SEVEN, CardRank.EIGHT, CardRank.NINE,
                           CardRank.TEN, CardRank.JACK, CardRank.QUEEN, CardRank.KING,
                           CardRank.ACE]:
                    self.deck.append(Card(suit, rank))
            # 添加大小王
            self.deck.append(Card(CardSuit.JOKER, CardRank.JOKER_SMALL))
            self.deck.append(Card(CardSuit.JOKER, CardRank.JOKER_BIG))

    def shuffle(self):
        """洗牌"""
        random.shuffle(self.deck)

    def deal_cards(self):
        """发牌"""
        self.shuffle()
        for i in range(27):  # 每人27张牌
            for player in range(4):
                self.players_hands[player].append(self.deck.pop())

    def get_card_type(self, cards: List[Card]) -> Optional[CardType]:
        """判断牌型"""
        if not cards:
            return None

        # 单张
        if len(cards) == 1:
            return CardType.SINGLE

        # 对子
        if len(cards) == 2 and cards[0].rank == cards[1].rank:
            return CardType.PAIR

        # 三张
        if len(cards) == 3 and all(c.rank == cards[0].rank for c in cards):
            return CardType.TRIPLE

        # 三带二
        if len(cards) == 5:
            ranks = [c.rank for c in cards]
            if ranks.count(ranks[0]) == 3 and ranks.count(ranks[3]) == 2:
                return CardType.TRIPLE_WITH_PAIR

        # 顺子
        if len(cards) >= 5:
            ranks = sorted([c.rank.value for c in cards])
            if all(int(ranks[i+1]) - int(ranks[i]) == 1 for i in range(len(ranks)-1)):
                return CardType.STRAIGHT

        # 连对
        if len(cards) >= 6:
            pairs = []
            for i in range(0, len(cards), 2):
                if i+1 < len(cards) and cards[i].rank == cards[i+1].rank:
                    pairs.append(cards[i].rank)
            if len(pairs) >= 3 and all(pairs[i+1].value - pairs[i].value == 1 for i in range(len(pairs)-1)):
                return CardType.CONSECUTIVE_PAIRS

        # 炸弹
        if len(cards) >= 4 and all(c.rank == cards[0].rank for c in cards):
            return CardType.BOMB

        # 同花顺
        if len(cards) >= 5:
            if all(c.suit == cards[0].suit for c in cards):
                ranks = sorted([c.rank.value for c in cards])
                if all(int(ranks[i+1]) - int(ranks[i]) == 1 for i in range(len(ranks)-1)):
                    return CardType.STRAIGHT_FLUSH

        return None

    def get_card_value(self, card: Card) -> int:
        """获取牌的大小值"""
        if card.rank == CardRank.JOKER_BIG:
            return 16
        elif card.rank == CardRank.JOKER_SMALL:
            return 15
        elif card.rank == CardRank.ACE:
            return 14
        elif card.rank == CardRank.KING:
            return 13
        elif card.rank == CardRank.QUEEN:
            return 12
        elif card.rank == CardRank.JACK:
            return 11
        elif card.rank.value == str(self.current_level):
            return 10
        else:
            return int(card.rank.value)

    def compare_cards(self, cards1: List[Card], cards2: List[Card]) -> bool:
        """比较两组牌的大小，返回cards1是否大于cards2"""
        type1 = self.get_card_type(cards1)
        type2 = self.get_card_type(cards2)

        # 炸弹可以打任何牌
        if type1 == CardType.BOMB and type2 != CardType.BOMB:
            return True
        if type1 != CardType.BOMB and type2 == CardType.BOMB:
            return False
        if type1 == CardType.BOMB and type2 == CardType.BOMB:
            return len(cards1) > len(cards2)

        # 同花顺大于普通顺子
        if type1 == CardType.STRAIGHT_FLUSH and type2 == CardType.STRAIGHT:
            return True
        if type1 == CardType.STRAIGHT and type2 == CardType.STRAIGHT_FLUSH:
            return False

        # 其他牌型必须相同才能比较
        if type1 != type2:
            return False

        # 获取牌型的主牌值
        def get_main_value(cards: List[Card], card_type: CardType) -> int:
            if card_type == CardType.SINGLE:
                return self.get_card_value(cards[0])
            elif card_type == CardType.PAIR:
                return self.get_card_value(cards[0])
            elif card_type == CardType.TRIPLE:
                return self.get_card_value(cards[0])
            elif card_type == CardType.TRIPLE_WITH_PAIR:
                return self.get_card_value(cards[0])
            elif card_type == CardType.STRAIGHT:
                return max(self.get_card_value(c) for c in cards)
            elif card_type == CardType.CONSECUTIVE_PAIRS:
                return max(self.get_card_value(c) for c in cards)
            elif card_type == CardType.CONSECUTIVE_TRIPLES:
                return max(self.get_card_value(c) for c in cards)
            elif card_type == CardType.STRAIGHT_FLUSH:
                return max(self.get_card_value(c) for c in cards)
            return 0

        return get_main_value(cards1, type1) > get_main_value(cards2, type2)

    def can_play_cards(self, cards: List[Card], player_index: int) -> bool:
        """判断是否可以出牌"""
        if not self.last_played_cards:  # 第一手牌
            return True

        card_type = self.get_card_type(cards)
        if not card_type:
            return False

        if card_type == CardType.BOMB:
            if self.last_played_type == CardType.BOMB:
                return len(cards) > len(self.last_played_cards)
            return True

        if card_type != self.last_played_type:
            return False

        return self.compare_cards(cards, self.last_played_cards)

    def play_cards(self, cards: List[Card], player_index: int) -> bool:
        """出牌"""
        if not self.can_play_cards(cards, player_index):
            return False

        # 从玩家手牌中移除打出的牌
        for card in cards:
            self.players_hands[player_index].remove(card)

        self.last_played_cards = cards
        self.last_played_type = self.get_card_type(cards)
        self.last_played_player = player_index
        self.current_player = (player_index + 1) % 4

        return True

    def pass_turn(self, player_index: int) -> bool:
        """过牌"""
        if not self.last_played_cards:
            return False

        self.current_player = (player_index + 1) % 4
        return True

    def update_level(self, winner_team: int, positions: List[int]):
        """更新游戏等级"""
        # positions: 玩家名次列表 [0,1,2,3]
        # winner_team: 获胜队伍索引 0或1
        
        # 计算升级数
        upgrade_levels = 0
        
        # 头游和二游在同一队
        if positions[0] // 2 == positions[1] // 2:
            upgrade_levels = 3
        # 头游和三游在同一队
        elif positions[0] // 2 == positions[2] // 2:
            upgrade_levels = 1
        # 头游和末游在同一队
        elif positions[0] // 2 == positions[3] // 2:
            upgrade_levels = 0
        # 末游在对手队
        elif positions[3] // 2 != winner_team:
            upgrade_levels = 1
        
        # 更新等级
        if upgrade_levels > 0:
            new_level = self.current_level + upgrade_levels
            if new_level > 14:  # A级是最高级
                new_level = 14
            self.current_level = new_level

    def check_game_end(self) -> Optional[Dict]:
        """检查游戏是否结束，返回游戏结果"""
        positions = []
        for i in range(4):
            if not self.players_hands[i]:
                positions.append(i)
        
        if len(positions) == 4:  # 所有玩家都出完牌
            winner_team = positions[0] // 2
            self.update_level(winner_team, positions)
            return {
                "winner_team": winner_team,
                "positions": positions,
                "new_level": self.current_level
            }
        return None 