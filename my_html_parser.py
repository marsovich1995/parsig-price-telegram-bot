from html.parser import HTMLParser

class FindBookId(HTMLParser):

    def __init__(self, *, convert_charrefs=True, html):
        self.buk_id = None
        self.convert_charrefs = convert_charrefs
        self.reset()
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            for i in range(len(attrs)):
                if attrs[i][0] == 'data-book-id':
                    # print(attrs[i][1])
                    self.buk_id=attrs[i][1]