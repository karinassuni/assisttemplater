import json

from assistscraper.courses_parser import tokenize_section

from .utils import *


__all__ = [
    "create_vuejs_template",
    "jsonify",
    "tokenize",
]


def tokenize(articulation_html_lines):
    tokens = []
    states = {'courses': '', 'paragraph': '', 'header': '', 'divider': ''}
    previous_state_name = ''


    def reset_other_states(*, current_state_name):
        nonlocal previous_state_name

        if previous_state_name and current_state_name != previous_state_name:
            tokens.append({previous_state_name: states[previous_state_name]})
            states[previous_state_name] = ''
        previous_state_name = current_state_name


    # Skip surrounding <pre> tag
    articulation_html_lines = articulation_html_lines[1:-1]

    for line in articulation_html_lines:
        if is_major_header(line) or "END OF MAJOR" in line:
            continue

        if is_course_line(line):
            reset_other_states(current_state_name='courses')
            states['courses'] += strip_html(line) + '\n'

        elif is_divider_line(line):
            reset_other_states(current_state_name='divider')

        elif is_text_centered(line):
            reset_other_states(current_state_name='header')
            states['header'] = strip_html(line.strip()).strip()

        else:
            reset_other_states(current_state_name='paragraph')
            states['paragraph'] += line.strip() + ' '

    reset_other_states(current_state_name='done')

    return tokens


def create_vuejs_template(tokens):
    template_html = ''
    slot_number = 0


    def tag(element_name, text):
        return f'<{element_name}>{text}</{element_name}>'


    for token in tokens:
        if key_of(token) == 'paragraph':
            template_html += tag('p', token['paragraph'])

        elif key_of(token) == 'courses':
            template_html += f'<slot name={slot_number}></slot>'
            slot_number += 1

        elif key_of(token) == 'divider':
            template_html += '<hr>'

        elif key_of(token) == 'header':
            template_html += tag('h2', strip_asterisks(token['header']))

    return f'<article class="articulation">{template_html}</article>'


def jsonify(tokens):

    course_sections = [tokenize_section(token['courses'].splitlines())
                       for token in tokens if key_of(token) == 'courses']

    dictionary = {
        'template': create_vuejs_template(tokens),
        'courseSections': course_sections,
    }

    return json.dumps(dictionary, indent=4)
