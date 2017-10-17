"""Utility functions for the parsers.
"""

def getval(node, tag, doc):
    """Retreive the value from a child (tag) of the node.

    node: obj, An xml node element
    tag: str, path to targeted value -- the path is relative to node.
    doc is the full page -- used to extract other parts of the doc that element references.
    """

    element = node.find(tag)

    if element is not None:
        if element.find('footnoteId') is not None:
            footnotes = doc.find('footnotes').findall('footnote')
            sub = element.find('footnoteId')

            # Find the footnote with the id that the value references.
            for footnote in footnotes:
                if footnote.get('id') == sub.get('id'):
                    return footnote.text
        else:
            return element.text
    else:
        return None


def getnval(node, tag, doc):
    """
    an element in the doc -- will look through it's children for tag.
    tag is the path from the element
    doc is the full page -- used to extract other parts of the doc that element references.
    """

    element = node.find(tag)

    if element is not None and element.find('value') is not None:
        return element.find('value').text
    elif element is not None and element.find('footnoteId') is not None:
        footnotes = doc.find('footnotes').findall('footnote')
        sub = element.find('footnoteId')

        # Find the footnote with the id that the value references.
        for footnote in footnotes:
            if footnote.get('id') == sub.get('id'):
                return footnote.text


def to_binary(val):
    return 1 if val and val.lower() == 'true' else 0
