#!/usr/bin/env python

# This script parses output from Telegram channel and converts each post to 
# jekyll-applicable post in markdown.
#
# Telegram creates result.json file, as well as different directories containing
# multimedia, photos, etc. This script creates new directory and populates it 
# with formatted posts ready to publish.
#
# TODO summary:
# - replies
# - single/muliple tags
# - forwarded posts

import os
# import sys
import json
from datetime import datetime

# post:
# header
# [photo?]
# text
# [media?]

# text:
# [str|list(str|obj, ...)]

def print_post_header(post_title, post_date, post_tag):
    # TODO: handle post tag/tags
    post_header = '---\ntitle: {title}\ndate: {date}\n\
tag: {tag}\nlayout: post\n---\n'.format(\
            title=post_title, date=post_date, tag=post_tag)

    return post_header

def parse_post_photo(post):
    post_photo = '![image]({src})\n\n'.format(src=post['photo'])

    return post_photo

def md_str(string):
    string = string.replace('\n','\n\n')
    string = string.replace('. ', '.\n')

    return string


def parse_text_object(obj):
    '''
    Parse object from post text.

    Objects are text links, plain links, underlined text, strikethrough text,
    italic text, bold text, code blocks and hashtags.

    This is a mess, but what is better?
    '''

    obj_type = obj['type']
    obj_text = obj['text']

    if obj_type == 'hashtag':
        post_tag = obj_text
        return post_tag

    elif obj_type == 'text_link':
        post_text_link = '[{text}]({href})'.format(text=obj_text, \
                href=obj['href'])
        return post_text_link

    elif obj_type == 'link':
        post_link = '[link]({href})'.format(href=obj_text)
        return post_link

    # I dunno how this appeared, but it seems like hyphenated numbers
    # are treated as phone numbers, so return them as plain text.
    elif obj_type == 'phone':
        return obj_text

    elif obj_type == 'bold':
        post_inline_bold = '**{text}**'.format(text=obj_text)
        return post_inline_bold

    elif obj_type == 'italic':
        post_inline_italic = '*{text}*'.format(text=obj_text)
        return post_inline_italic

    elif obj_type == 'underline':
        post_inline_underline = '<u>{text}</u>'.format(text=obj_text)
        return post_inline_underline

    elif obj_type == 'strikethrough':
        post_inline_strike = '<s>{text}</s>'.format(text=obj_text)
        return post_inline_strike

    elif obj_type == 'code':
        post_inline_code = '```\n{text}\n```'.format(text=obj_text)
        return post_inline_code


def parse_post_text(post):
    # TODO: handle reply-to
    post_raw_text = post['text']
    post_parsed_text = ''

    if type(post_raw_text) == str:
        return str(post_raw_text)

    else:
        for obj in post_raw_text:
            if type(obj) == str:
                post_parsed_text += obj
            else:
                post_parsed_text += str(parse_text_object(obj))

        return post_parsed_text


def parse_post_media(post):
    post_media = '<audio controls>\n \
    <source src="{src}" type="{mime_type}">\n \
    </audio>'.format(src=post['file'], mime_type=post['mime_type'])

    return post_media
    

def parse_post(post):
    post_output = ''
    
    # optional image
    if 'photo' in post:
        post_output += str(parse_post_photo(post))

    # post text
    post_output += md_str(parse_post_text(post))

    # optional media
    if 'media_type' in post:
        post_output += str(parse_post_media(post))

    return post_output


def main():
    # create output directory
    out_dir = './formatted_posts'
    try:
        os.mkdir(out_dir)
    except FileExistsError as e:
        pass

    # load json file
    with open('result.json', 'r') as f:
        data = json.load(f)

    # load only messages
    raw_posts = data['messages']

    for post in raw_posts:
    # TODO: handle forwarded posts
        if post['type'] == 'message' and 'forwarded_from' not in post:

            post_date = datetime.fromisoformat(post['date'])
            post_id = post['id']
            post_filename = out_dir + '/' + str(post_date.date()) + '-' \
                    + str(post_id) + '.md'

            with open (post_filename, 'w') as f:
                print(print_post_header(
                    post_id, post_date.date(), None), 
                    file=f)
                print(parse_post(post), file=f)


if __name__ == '__main__':
    main()

