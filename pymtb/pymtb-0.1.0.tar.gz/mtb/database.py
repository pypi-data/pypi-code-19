from .utils import Folder

__all__ = ["cherbourg","elle","LUT_LIB"]

def cherbourg():
    a = Folder("/Volumes/4TB/PROJETS/Video/Valerie Massadian/Milla/MEL REPERAGE/RAWS & H264")
    a.accepted_types = [".MOV"]
    return a.files

def elle():

    a = Folder("/Volumes/4TB/PROJETS/Video/Mel Massadian/Films/elle/rushs")
    a.recursive = True
    a.accepted_types = [".MOV"]
    return a.files


def LUT_LIB():

    a = Folder("/Volumes/4TB/PROJETS/Code/PyQT/MTB_QT_Widgets/_libs/mtb/mtb/assets/LUTS")
    a.recursive = True
    a.accepted_types = [".cube"]
    return a.files