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
# - custom post header

import os
import sys
import json
from datetime import datetime


def print_post_header(post_title, post_date, post_tag):
    # TODO: handle post tag/tags
    # TODO: support for custom header
    post_header = '---\ntitle: {title}\ndate: {date}\n\
tag: {tag}\nlayout: post\n---\n'.format(\
            title=post_title, date=post_date, tag=post_tag)

    return post_header


def parse_post_photo(post, media_dir):
    post_photo_src = post['photo'][7:]
    post_photo_src = media_dir + '/' + post_photo_src
    post_photo = '![image]({src})\n\n'.format(\
            src=post_photo_src)

    return post_photo


# def md_str(string):
    # string = string.replace('\n','\n\n')
    # string = string.replace('. ', '.\n')

    # return string


def text_format(string, fmt):
    if fmt in ('*', '**', '***', '`', '```'):
        output = '{fmt}{txt}{fmt}'
    elif fmt == '```':
        output = '{fmt}\n{txt}\n{fmt}'
    else:
        output = '<{fmt}>{txt}</{fmt}>'

    output = output.format(fmt=fmt, txt=string.strip())
    output += '\n' * string.split('\n').count('') * string.endswith('\n')
    return output

def text_link_format(text, link):
    link_fmt = '[{text}]({href})'
    link_fmt = link_fmt.format(text=text.strip(), href=link)
    link_fmt += '\n' * text.count('\n') * text.endswith('\n')
    return link_fmt


def parse_text_object(obj):

    obj_type = obj['type']
    obj_text = obj['text']

    if obj_type == 'hashtag':
        post_tag = obj_text
        return post_tag

    elif obj_type == 'text_link':
        return text_link_format(obj_text, obj['href'])

    elif obj_type == 'link' or obj_type == 'email':
        post_link = '<{href}>'.format(href=obj_text.strip())
        return post_link

    elif obj_type == 'phone':
        return obj_text

    elif obj_type == 'italic':
        return text_format(obj_text, '*')

    elif obj_type == 'bold':
        return text_format(obj_text, '**')

    elif obj_type == 'code':
        return text_format(obj_text, '`')

    elif obj_type == 'pre':
        return text_format(obj_text, '```')

    elif obj_type == 'underline':
        return text_format(obj_text, 'u')

    elif obj_type == 'strikethrough':
        return text_format(obj_text, 's')


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


def parse_post_media(post, media_dir):
    # get filename without parent directory
    post_media_src = post['file'][post['file'].rfind("/") + 1:]

    # add parent directory
    post_media_src = media_dir + '/' + post_media_src
    post_media = '\n<audio controls>\n \
        <source src="{src}" type="{mime_type}">\n \
        </audio>'.format(src=post_media_src, mime_type=post['mime_type'])

    return post_media
    

def parse_post(post):
    post_output = ''
    
    # optional image
    photo_dir = '/photos'
    if 'photo' in post:
        post_output += str(parse_post_photo(post, photo_dir))

    # post text
    post_output += str(parse_post_text(post))

    # optional media
    media_dir = '/files'
    if 'media_type' in post:
        post_output += str(parse_post_media(post, media_dir))

    return post_output


def main():
    # try directory from first argument
    try:
        input_dir = sys.argv[1]
    except IndexError as e:
        # if it's not specified, use current directory
        input_dir = '.'

    # create output directory
    out_dir = input_dir + '/' + 'formatted_posts'
    try:
        os.mkdir(out_dir)
    except FileExistsError as e:
        pass

    # load json file
    json_path = input_dir + '/' + 'result.json'
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except FileNotFoundError as e:
        sys.exit('result.json not found.\nPlease, specify right directory')

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
                    post_id, post_date, None), 
                    file=f)
                print(parse_post(post), file=f)


if __name__ == '__main__':
    main()

