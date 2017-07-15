import html
import re


def strip_html(string):
    return re.sub('<[^>]*>', '', html.unescape(string))


def strip_asterisks(string):
    return re.sub('\*', '', string)


def bold_to_strong(string):
    with_changed_tag = re.sub('<b>', '<strong>', string)
    with_changed_tag = re.sub('</b>', '</strong>', with_changed_tag)
    return with_changed_tag


def is_major_header(line):
    return "====" in line and "<b>" in line


def is_course_line(line):
    return '|' in line


def is_divider_line(line):
    return bool(re.match('-{80}', line))


def is_ordered_list(line):
    return bool(re.search('^[1-9][.)](?![0-9]+| {2,})', line.lstrip()))


def is_unordered_list(line):
    BULLETS = ('-', '+')
    return line.lstrip()[0] in BULLETS


def num_leading_spaces(string):
    return len(re.match(' *', string).group(0))


def is_text_centered(line):
    return (line.strip() != line
            and not line.strip() == ''
            and not is_ordered_list(line)
            and not is_unordered_list(line)
            and num_leading_spaces(line) > 1
            )


def key_of(dictionary):
    [(key, value)] = dictionary.items()
    return key
