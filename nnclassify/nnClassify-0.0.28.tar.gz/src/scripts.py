from src.Main_ import Main
from src.ImageCropper_ import ImageCropper
import argparse

def create_model():
    parser = argparse.ArgumentParser()
    parser.add_argument("Model_Name", help="What would you" 
            + "like your model to be called")
    args = parser.parse_args()

    Main.create_model(args.Model_Name)
    return

def crop():
    parser = argparse.ArgumentParser()
    parser.add_argument("Source_Folder", help="The path to the folder"
            + " you want cropped")
    parser.add_argument("Destination", help="The path to destination location")
    args = parser.parse_args()
    ImageCropper.crop_all_images(args.Source_Folder, args.Destination)
    return

def predict():
    parser = argparse.ArgumentParser()
    parser.add_argument("Set_Name", help="The name of the set of wells to predict")
    parser.add_argument("Model_Name", help="The name of the neural network to use")
    parser.add_argument("Image_Confidance",
            help="A floating point number between 0 and 1. The neural network" 
            + " must be at least this confident to believe this images is a "
            + "normal image")
    parser.add_argument("Frame_Count",
            help= "An integer greater than zero."
            + " We must see this many normal frames to predict the well as normal")
    parser.add_argument("Maybe_Count",
            help= "An integer greate than zero and less than Frame Count. "
            + "If we see at least this many normal frames but less than Frame_Count"
            + " then predict Not_Sure")

    args = parser.parse_args()
    Main.predict(args.Set_Name, args.Model_Name, args.Image_Confidance,
            args.Frame_Count, args.Maybe_Count)
    return

def test_individual():
    parser = argparse.ArgumentParser()
    parser.add_argument("Set_Name", help="The name of the test set")
    parser.add_argument("Model_Name", help="The name of the neural network to use")
    args = parser.parse_args()
    Main.test_individual(args.Set_Name, args.Model_Name)
    return

def test_wells():
    parser = argparse.ArgumentParser()
    parser.add_argument("Set_Name", help="The name of the test set")
    parser.add_argument("Model_Name", help="The name of the neural network to use")
    parser.add_argument("Image_Confidance",
             help="A floating point number between 0 and 1. The neural network" 
             + " must be at least this confident to believe this images is a "
             + "normal image")
    parser.add_argument("Frame_Count",
             help= "An integer greater than zero."
             + " We must see this many normal frames to predict the well as normal")
    parser.add_argument("Maybe_Count",
             help= "An integer greate than zero and less than Frame Count. "
             + "If we see at least this many normal frames but less than Frame_Count"
             + " then predict Not_Sure")

    args = parser.parse_args()
    Main.test_wells(args.Set_Name, args.Model_Name, args.Image_Confidance,
            args.Frame_Count, args.Maybe_Count)
    return

def train():
    parser = argparse.ArgumentParser()
    parser.add_argument("Training_Set", help="The name of the training set"
            + " that you want to train on")
    parser.add_argument("Model_Name", help="The model you want to train")
    parser.add_argument("Epochs", help="The number of epochs you want to train on",
            type=int)
    args = parser.parse_args()
    Main.train(args.Training_Set, args.Model_Name, args.Epochs)
    return


