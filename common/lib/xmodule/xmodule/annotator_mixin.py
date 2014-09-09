"""
Annotations Tool Mixin
This file contains global variables and functions used in the various Annotation Tools.
"""
from lxml import etree
from pkg_resources import resource_string
from urlparse import urlparse
from os.path import splitext, basename
from HTMLParser import HTMLParser

def get_instructions(xmltree):
    """ 
    Removes <instructions> from the xmltree and returns them as a string, otherwise None. 

    The instructor will input a set of instructions within the xml element listed above.
    The instructions need to be gathered and returned so they can be input within the
    appropriate HTML template and style.

    Arguments:
    	xmltree (string): a string with an HTML tree to be parsed.

    Returns:
    	string: a plaintext string without all the html elements
    """
    instructions = xmltree.find('instructions')
    if instructions is not None:
        instructions.tag = 'div'
        xmltree.remove(instructions)
        return etree.tostring(instructions, encoding='unicode')
    return None


def get_extension(srcurl):
    """
    Get the extension of a given url

    For use when trying to find the type of video used in the video annotation tool.
    The main goal is to differentiate between the youtube videos and those uploaded to the
    platform by the instructor.

    Arguments:
    	srcurl (string): a string with the full url of the video

    Returns:
    	string: either 'video/youtube' if it was a youtube video or the extension if it was uploaded
    """
    if 'youtu' in srcurl:
        return 'video/youtube'
    else:
        disassembled = urlparse(srcurl)
        file_ext = splitext(basename(disassembled.path))[1]
        return 'video/' + file_ext.replace('.', '')


class MLStripper(HTMLParser):
    """
    helper function for html_to_text below
    """
    def __init__(self):
        HTMLParser.__init__(self)
        self.reset()
        self.fed = []

    def handle_data(self, data):
        """
        takes the data in separate chunks
        """
        self.fed.append(data)

    def handle_entityref(self, name):
        """
        appends the reference to the body
        """
        self.fed.append('&%s;' % name)

    def get_data(self):
        """
        joins together the seperate chunks into one cohesive string
        """
        return ''.join(self.fed)


def html_to_text(html):
    """
    strips the html tags off of the text to return plaintext
    """
    htmlstripper = MLStripper()
    htmlstripper.feed(html)
    return htmlstripper.get_data()

ANNOTATOR_COMMON_JS = [
	resource_string(__name__, 'js/src/ova/annotator-full.js'),
	resource_string(__name__, 'js/src/ova/annotator-full-firebase-auth.js'),
    resource_string(__name__, 'js/src/ova/video.dev.js'),
	resource_string(__name__, 'js/src/ova/rangeslider.js'),
	resource_string(__name__, 'js/src/ova/share-annotator.js'),
	resource_string(__name__, 'js/src/ova/richText-annotator.js'),
	resource_string(__name__, 'js/src/ova/reply-annotator.js'),
	resource_string(__name__, 'js/src/ova/tags-annotator.js'),
	resource_string(__name__, 'js/src/ova/flagging-annotator.js'),
	resource_string(__name__, 'js/src/ova/diacritic-annotator.js'),
	resource_string(__name__, 'js/src/ova/grouping-annotator.js'),
	resource_string(__name__, 'js/src/ova/openseadragon.js'),
	resource_string(__name__, 'js/src/ova/OpenSeaDragonAnnotation.js'),
	resource_string(__name__, 'js/src/ova/ova.js'),
	resource_string(__name__, 'js/src/ova/catch/js/catch.js'),
	resource_string(__name__, 'js/src/ova/catch/js/handlebars-1.1.2.js')
]

ANNOTATOR_COMMON_CSS = [
	resource_string(__name__, 'css/ova/edx-annotator.css'),
	resource_string(__name__, 'css/ova/rangeslider.css'),
	resource_string(__name__, 'css/ova/share-annotator.css'),
	resource_string(__name__, 'css/ova/richText-annotator.css'),
	resource_string(__name__, 'css/ova/flagging-annotator.css'),
	resource_string(__name__, 'css/ova/diacritic-annotator.css'),
	resource_string(__name__, 'css/ova/grouping-annotator.css'),
	resource_string(__name__, 'css/ova/ova.css'),
	resource_string(__name__, 'css/ova/catch/css/main.css')
]
