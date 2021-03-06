import json

from assistparser import parse_section

from utils import *


__all__ = [
    "create_vuejs_template",
    "jsonify",
    "tokenize",
]


def tokenize(articulation_text_lines):
    tokens = []
    states = {'courses': '', 'paragraph': '', 'header': '', 'divider': ''}
    previous_state_name = ''


    def set_current_state(state_name, value=''):
        switch_state_to(state_name)
        states[state_name] = value


    def append_current_state(state_name, value):
        switch_state_to(state_name)
        states[state_name] += value


    def end_previous_state():
        tokens.append({previous_state_name: states[previous_state_name]})
        states[previous_state_name] = ''


    def switch_state_to(current_state_name):
        nonlocal previous_state_name

        if previous_state_name and current_state_name != previous_state_name:
            end_previous_state()
        previous_state_name = current_state_name


    # Skip blanks where the enclosing <pre> tags should be
    for line in articulation_text_lines[1:-1]:
        if is_major_header(line) or "END OF MAJOR" in line:
            continue

        if is_course_line(line):
            append_current_state('courses', line + '\n')

        elif is_divider_line(line):
            set_current_state('divider')

        elif is_text_centered(line):
            set_current_state('header', line.strip())

        else:
            append_current_state('paragraph', line.strip() + ' ')

    end_previous_state()

    return tokens


def create_vuejs_template(tokens):
    template_html = ''
    slot_number = 0


    def tag(element_name, text):
        return f'<{element_name}>{text}</{element_name}>'


    for token in tokens:
        key = key_of(token)

        if key == 'paragraph':
            template_html += tag('p', token['paragraph'])

        elif key == 'courses':
            template_html += f'<slot name={slot_number}></slot>'
            slot_number += 1

        elif key == 'divider':
            template_html += '<hr>'

        elif key == 'header':
            template_html += tag('h2', strip_asterisks(token['header']))

    return f'<article class="articulation">{template_html}</article>'


def jsonify(tokens):

    course_sections = [parse_section(token['courses'].splitlines())
                       for token in tokens
                       if key_of(token) == 'courses']

    dictionary = {
        'template': create_vuejs_template(tokens),
        'courseSections': course_sections,
    }

    return json.dumps(dictionary, indent=4)
