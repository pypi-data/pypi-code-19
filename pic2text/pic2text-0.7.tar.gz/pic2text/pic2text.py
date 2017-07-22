from PIL import Image
import argparse


class Pic_2_Text():
    def __init__(self, output_file=False):
        self.max_val = 765
        self.output_file = output_file

    def get_image(self, image_path, scale):
        im = Image.open(image_path, 'r')
        width, height = im.size
        ratio = round(width / height)
        try:
            scaled_height = round(height * scale)
        except:
            scaled_height = 1
        im = im.resize((round(scaled_height*ratio), round(scaled_height *.35))) #makes the image look correct in cmd line
        width, height = im.size
        pixel_values = list(im.getdata())
        return pixel_values, width

    def pretty_print(self, arr, outfile):
        if self.output_file == False:
            for line in arr:
                line_string = ""
                for pix in line:
                    line_string = line_string + str(pix)
                print(line_string)
        else:
            with open(outfile, 'w') as text_pic:
                for line in arr:
                    line_string = ""
                    for pix in line:
                        line_string = line_string + str(pix)
                    print(line_string)
                    text_pic.write(line_string + '\n')
    
    def convert(self, path, scale):
        """This Converts the pic to the text rep, use a string path eg. './path/to/pic.jpg' """
        pic = path
        outfile = path+'.txt'
        simplified_list = []
        temp_list = []
        count = 0
        raw_data, width = self.get_image(pic, scale)

        for pixel in raw_data:
            total = 0
            for val in pixel:
                total += val
            
            temp_list.append(round((abs(self.max_val - total) * .01)))
            count+=1

            if len(temp_list) == width:
                simplified_list.append(temp_list)
                temp_list = []
        
        self.pretty_print(simplified_list, outfile) # writes to file
    

def main(args):
    converter = Pic_2_Text() #init class
    #convert vith path, args.path is the cmd argument string. feel free to use any path, if using this class
    converter.convert(args.path, args.scale)
    print('completed script')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--path", help="str path to picture eg: --path './path/to/pic.jpg'", default="./pic.png", type=str)
    parser.add_argument("--scale", help="0-1 new scale (.2 is not 20% less)", default=.4, type=float)
    args = parser.parse_args()
    main(args)