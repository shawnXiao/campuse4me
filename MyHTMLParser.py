from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self, html):
        HTMLParser.__init__(self)
        self.html = html;
    def print_contents(self, tagName, selector):
        self.tag_stack = []
        self.tagName = tagName
        self.selector = selector
        self.feed(self.html)
        return self.content

    def handle_starttag(self, tag, attrs):
        if self.selector is not None:
            for attr in attrs:
                if attr == self.selector:
                     self.tag_stack.append(tag.lower())
        else:
            self.tag_stack.append(tag.lower())

    def handle_endtag(self, tag):
        if len(self.tag_stack):
            self.tag_stack.pop()

    def handle_data(self, data):
        if len(self.tag_stack) and self.tag_stack[-1] == self.tagName:
            self.content = data