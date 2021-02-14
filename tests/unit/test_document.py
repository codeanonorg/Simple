import unittest
from Simple.htmlparser import (
    DocumentParser,
    Position,
    Range,
    Tag,
    TextNode,
    html,
    parse,
)


class DocumentTests(unittest.TestCase):
    def test_document_simple(self):
        doc = parse("<html></html>")
        self.assertEqual(len(doc.children), 1)

        html_tag: Tag = doc.children[0]
        self.assertIsInstance(html_tag, Tag)
        self.assertEqual(html_tag.name, "html")
        self.assertEqual(html_tag.children, [])

    def test_document_html_repr(self):
        tests = [
            "<html></html>",
            "<p>Text inserted here</p>",
            "<a href='/'>Link here</a>",
            "<img src='/images/etc.jpg' alt='Alternative text for image'/>",
        ]
        for i, text in enumerate(tests):
            with self.subTest(input=i + 1, text=text):
                doc = parse(text)
                rendered = html(doc)
                self.assertEqual(text, rendered)

    def test_document_parse_chunked(self):
        p = DocumentParser()
        p.feed("<html")
        p.feed("><body lang='en'>Hell")
        p.feed("o world!</b")
        p.feed("ody></html>")

        p.flush()
        doc = p.document
        root: Tag = doc.root
        body: Tag = root.children[0]
        text_node: TextNode = body.children[0]
        self.assertEqual(1, len(doc.children))
        self.assertIsInstance(root, Tag)
        self.assertIsInstance(body, Tag)
        self.assertIsInstance(text_node, TextNode)
        self.assertEqual(text_node.text, "Hello world!")
