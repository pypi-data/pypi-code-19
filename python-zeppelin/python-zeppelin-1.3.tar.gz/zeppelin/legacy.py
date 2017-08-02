import re
import os
import json
import cairosvg
import sys

index = 0


def build_image(msg):
    global index

    result = re.search('xml version', msg)

    if result is None:
        return

    index +=1

    images_path = 'images'

    if not os.path.isdir(images_path):
        os.makedirs(images_path)

    # print (msg)

    print (result.group(0))

    with open('{0}/output_{1}.png'.format(images_path, index), 'wb') as fh:
        cairosvg.svg2png(bytestring=msg.encode('utf-8'),write_to=fh)
        fh.close()

    # with open('{0}/output_{1}.png'.format(images_path, index), 'wb') as fh:
    #     fh.write(result.group(1).encode('utf-8').decode('base64'))

    # self.out.append('\n![png]({0}/output_{1}.png\n'.format(images_path, self.index))
def build_markdown_body(text):
    for paragraph in text['paragraphs']:
        # if 'user' in paragraph:
        #     self.user = paragraph['user']
        # if 'dateCreated' in paragraph:
        #     self.process_date_created(paragraph['dateCreated'])
        # if 'dateUpdated' in paragraph:
        #     self.process_date_updated(paragraph['dateUpdated'])
        # if 'title' in paragraph:
        #     self.process_title(paragraph['title'])
        # if 'text' in paragraph:
        #     self.process_input(paragraph['text'])
        if 'result' in paragraph:
            if paragraph['result']['msg']:
                build_image(paragraph['result']['msg'])
            # process_results(paragraph)

def convert(filename):
        """Convert json to markdown.

        Takes in a .json file as input and convert it to Markdown format,
        saving the generated .png images into ./images.
        """

        try:
            with open(filename, 'rb') as raw:
                t = json.load(raw)
                # full_path = os.path.join(self.directory, self.output_filename + self.MD_EXT)
                # with open(full_path, 'w') as fout:
                #     self.build_markdown_body(t)  # create the body
                #     self.build_header(t['name'])  # create the md header
                #     self.build_output(fout)  # write body and header to output file
                build_markdown_body(t)

        except ValueError as err:
            print (err)
            sys.exit(1)

convert("legacy_test.json")