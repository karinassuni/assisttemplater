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


    # Skip surrounding <pre> tag
    articulation_html_lines = articulation_html_lines[1:-1]

    for line in articulation_html_lines:
        if is_major_header(line) or "END OF MAJOR" in line:
            continue

        if is_course_line(line):
            formatted_line = strip_html(line) + '\n'
            append_current_state('courses', formatted_line)

        elif is_divider_line(line):
            set_current_state('divider')

        elif is_text_centered(line):
            formatted_line = strip_html(line.strip()).strip()
            set_current_state('header', formatted_line)

        else:
            formatted_line = bold_to_strong(line.strip()) + ' '
            append_current_state('paragraph', formatted_line)

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

    course_sections = [tokenize_section(token['courses'].splitlines())
                       for token in tokens if key_of(token) == 'courses']

    dictionary = {
        'template': create_vuejs_template(tokens),
        'courseSections': course_sections,
    }

    return json.dumps(dictionary, indent=4)
