from PIL import Image, ImageOps
from xml.etree import ElementTree
from pytesseract import image_to_alto_xml
from typing import List
from sys import platform

if platform == 'win32':
    from pytesseract import pytesseract
    pytesseract.tesseract_cmd = "C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

PYTESSERACT_LANGUAGE = "jpn"
SPEECH_BUBBLE_PADDING = 8
SPEECH_BUBBLE_COLORS = {
    "井上トロ": (224, 224, 192)
}


def alto_xml_to_text_blocks(xml: bytes) -> List[dict]:
    xml = xml.decode("utf-8")
    xml = ElementTree.fromstring(xml)

    text_blocks = []

    # xml[-1] is {http://www.loc.gov/standards/alto/ns-v3#}Layout
    for page in xml[-1]:
        for print_space in page:
            for printed_element in print_space:
                if printed_element.tag != "{http://www.loc.gov/standards/alto/ns-v3#}ComposedBlock":
                    continue

                for text_block in printed_element:
                    if text_block.tag != "{http://www.loc.gov/standards/alto/ns-v3#}TextBlock":
                        continue

                    text_blocks.append(text_block)
    
    for text_block_idx, text_block in enumerate(text_blocks):
        text_block_content = ""

        for text_line_idx, text_line in enumerate(text_block):
            for text_line_string in text_line:
                if text_line_string.tag == '{http://www.loc.gov/standards/alto/ns-v3#}String':
                    text_block_content += text_line_string.attrib["CONTENT"]
            
            if text_line_idx + 1 != len(text_block):
                text_block_content += "\n"

        text_blocks[text_block_idx] = {
            "width": int(text_block.attrib["WIDTH"]),
            "vertical_position": int(text_block.attrib["VPOS"]),
            "height": int(text_block.attrib["HEIGHT"]),
            "horizontal_position": int(text_block.attrib["HPOS"]),
            "content": text_block_content
        }
    
    return text_blocks


def image_to_speech_bubbles(image: Image) -> List[dict]:
    alto_xml = image_to_alto_xml(image=image, lang=PYTESSERACT_LANGUAGE)
    text_blocks = alto_xml_to_text_blocks(xml=alto_xml)

    speech_bubbles = []
    for text_block in text_blocks:
        y = text_block["horizontal_position"] - SPEECH_BUBBLE_PADDING
        y1 = text_block["vertical_position"] - SPEECH_BUBBLE_PADDING
        x = text_block["horizontal_position"] + text_block["width"] + SPEECH_BUBBLE_PADDING * 1.5
        x1 = text_block["vertical_position"] + text_block["height"] + SPEECH_BUBBLE_PADDING * 1.5
        speech_bubble_image = image.crop((y, y1, x, x1))

        _, speech_bubble_image_height = speech_bubble_image.size
        y0 = speech_bubble_image_height - SPEECH_BUBBLE_PADDING
        checkboxes = [
            (0, 0, SPEECH_BUBBLE_PADDING, SPEECH_BUBBLE_PADDING),
            (y0, 0, y0 + SPEECH_BUBBLE_PADDING, SPEECH_BUBBLE_PADDING)
        ]
        
        for checkbox_idx, checkbox in enumerate(checkboxes):
            checkbox_image = speech_bubble_image.crop(checkbox)
            checkbox_image = checkbox_image.convert("RGB")
            checkbox_image = ImageOps.posterize(checkbox_image, 3)

            center_color = checkbox_image.getpixel((SPEECH_BUBBLE_PADDING / 2, SPEECH_BUBBLE_PADDING / 2))
            for character_name, character_color in SPEECH_BUBBLE_COLORS.items():
                checkboxes[checkbox_idx] = character_name if center_color == character_color else None

        if None not in checkboxes:
            left_top_checkbox_result, left_bottom_checkbox_result = checkboxes

            if left_top_checkbox_result == left_bottom_checkbox_result:
                character_name = left_top_checkbox_result
                speech_bubble = {
                    "character_name": character_name,
                    "speech_bubble_text": text_block["content"]
                }
                speech_bubbles.append(speech_bubble)
    
    return speech_bubbles


print(image_to_speech_bubbles(image=Image.open("screenshot.png")))
