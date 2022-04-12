import enum


class PokerKind(enum.IntEnum):
    unknown = 0
    heart = 1    # 红桃
    diamond = 2  # 方块
    spade = 3    # 黑桃
    club = 4     # 梅花

    @staticmethod
    def short_format(kind):
        return {
            PokerKind.heart: "H",
            PokerKind.diamond: "D",
            PokerKind.spade: "S",
            PokerKind.club: "C"
        }.get(kind, "UNKNOWN")

    @staticmethod
    def long_format(kind):
        return str(PokerKind(kind))

    @staticmethod
    def try_parse(s):
        return {
            "h": PokerKind.heart,
            "d": PokerKind.diamond,
            "s": PokerKind.spade,
            "c": PokerKind.club,
        }.get(s.lower(), None)


class PokerDigit(object):
    unknown = 0
    A = 14
    K = 13
    Q = 12
    J = 11
    A_MINUS = 1

    _digit_s = {
        14: "A",
        13: "K",
        12: "Q",
        11: "J",
    }
    _s_digits = {
        "a": 14,
        "k": 13,
        "q": 12,
        "j": 11,
    }

    @staticmethod
    def format(digit):
        return PokerDigit._digit_s.get(digit, str(digit))

    @staticmethod
    def try_parse(s):
        s = s.lower()
        if s in PokerDigit._s_digits:
            return PokerDigit._s_digits.get(s)
        try:
            return int(s)
        except:
            return None


class PokerCard(object):
    """
    This class is only used for repr
    """
    def __init__(self, kind, digit):
        self._kind = kind
        self._digit = digit

    def __repr__(self):
        return PokerCard.short_format(self._kind, self._digit)

    def get_data(self):
        return self._kind, self._digit

    @staticmethod
    def short_format(kind, digit):
        return PokerKind.short_format(kind) + PokerDigit.format(digit)

    @staticmethod
    def long_format(kind, digit):
        return PokerKind.long_format(kind) + '-' + PokerDigit.format(digit)

    @staticmethod
    def try_parse(s):
        if len(s) < 2:
            return None
        kind = PokerKind.try_parse(s[0])
        digit = PokerDigit.try_parse(s[1:])
        if kind is not None and digit is not None:
            return PokerCard(kind, digit)
        return None


class PokerConst(object):
    MIN_DIGIT = 2
    MAX_DIGIT = 14
    DIGIT_NUM = 13
