
yes_no_questions = [
    ("Can integers and floats be added using the `+` operator?", 'y'),
    ('Strings can be iterated over using the `for` loop?', 'y'),
    ('A string can be interpolated (values inserted) using the `$` operator?', 'n'),
    ('mystr.startswith(pat) returns True if mystr starts with alphanumeric pattern, otherwise False.', 'n'),
    ('mystr.find() raises a NotFoundError if substring is not found?', 'n'),
    ('mystr.format() is an alternative to f-strings?', 'y'),
    ('mystr.join() is an alternative to f-strings?', 'n'),
    ('mystr.join() joins values of a dictionary together?', 'n'),
    ('mystr.join() joins strings contained in a sequence?', 'y'),
    ('mystr.join() will cast items in a sequence to str?', 'n'),
]

choice_questions = [
    ('What is the operator to get remainder of division?', ['%', '//'], 0),
    ('Mutable objects can be modified:', ['during initialization', 'at any time'], 1),
    ('Strings can be split using this method:', ['split()', 'chunk()'], 0),
    ('When a string a split, following type is returned:', ['tuple', 'list'], 1),
    ('"abba".lstrip("ab") =>', ['"ba"', '""'], 1),
    ('mystr.encode() encodes into which type?', ['bytes', 'unicode'], 0),
    ('mystr.decode() decodes into which type?', ['bytes', 'unicode'], 1),
    ('mystr.islower() returns True if:', ['the string is slower to render', 'the string is in lowercase'], 1),
    ('mystr.join() will:', ['cast items in a sequence to str', 'require items to be instances of str'], 1),
]

class Question:
    def __init__(self, q):
        self.q = q

    def ask(self, term):
        import sys
        if len(self.q) == 2:
            sys.stdout.write(self.q[0] + ' [y/n]')
            sys.stdout.flush()
            a = term.getch()
            if a.lower()==self.q[1]:
                return True
        elif len(self.q) == 3:
            print(self.q[0])
            choices = self.q[1]
            for i,a in enumerate(choices):
                print(f'{i+1}) {a}')
            print('> ')
            while 1:
                a = term.getch()
                if a.isdigit() and 1 <= int(a) <=len(choices):
                    return int(a)-1 == self.q[2]


questions = [Question(q) for q in yes_no_questions + choice_questions]

asked = set()

def get_question(term):
    from random import choice
    to_ask = [q for q in questions if q not in asked]
    if not to_ask:
        asked.clear()
        to_ask = questions

    q = choice(to_ask)
    asked.add(q)
    return q.ask(term)

